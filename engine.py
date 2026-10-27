"""
CLOAK try-on engine.

Wraps the open-weight Leffa virtual try-on models (MIT licence,
https://github.com/franciszzj/Leffa) so they can:
  * run on a free Google Colab T4 GPU (memory-safe loading),
  * accept everyday phone photos and vendor screenshots (EXIF rotation,
    transparent PNGs, odd aspect ratios),
  * dress a person in a full outfit: bottom + top, or a dress/gown.

Pipeline for one garment (all models open-weight):
  1. Human parsing (SCHP ONNX)  -> which pixels are hair, face, arms, clothes
  2. OpenPose body keypoints    -> where shoulders, elbows, hips are
  3. Agnostic mask              -> the region the new garment will occupy
  4. DensePose                  -> a map of the body surface
  5. Leffa diffusion model      -> paints the garment onto the person,
                                   using flow fields in attention to keep
                                   the garment's patterns and details.

Set CLOAK_MOCK=1 to run without a GPU or checkpoints (UI development only;
mock output is clearly watermarked and must never be shown as a real result).
"""

from __future__ import annotations

import gc
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

WIDTH, HEIGHT = 768, 1024

# Where setup.sh puts the Leffa source code and checkpoints.
ROOT = Path(__file__).resolve().parents[1]
LEFFA_DIR = Path(os.environ.get("CLOAK_LEFFA_DIR", ROOT / "third_party" / "Leffa"))
CKPT_DIR = Path(os.environ.get("CLOAK_CKPT_DIR", ROOT / "ckpts"))

# "both": VITON-HD model for tops + DressCode model for bottoms/dresses (best quality)
# "dc":   DressCode model only (half the memory; use if Colab runs out of RAM)
MODELS = os.environ.get("CLOAK_MODELS", "both").lower()
MOCK = os.environ.get("CLOAK_MOCK", "0") == "1"

GARMENT_TYPES = ("upper_body", "lower_body", "dresses")


# --------------------------------------------------------------------------
# Image helpers
# --------------------------------------------------------------------------

def load_image(img) -> Image.Image:
    """Accept a path or PIL image; fix phone rotation; flatten transparency on white."""
    if img is None:
        return None
    if isinstance(img, (str, Path)):
        img = Image.open(img)
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        white = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(white, img)
    return img.convert("RGB")


@dataclass
class Fit:
    """How an image was placed inside the 768x1024 canvas, so we can undo it."""
    left: int
    top: int
    width: int
    height: int


def fit_to_canvas(img: Image.Image) -> tuple[Image.Image, Fit]:
    """Resize to fit 768x1024 keeping aspect ratio, pad with white (same as Leffa)."""
    scale = min(HEIGHT / img.height, WIDTH / img.width)
    w, h = int(img.width * scale), int(img.height * scale)
    canvas = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    left, top = (WIDTH - w) // 2, (HEIGHT - h) // 2
    canvas.paste(img.resize((w, h), Image.BICUBIC), (left, top))
    return canvas, Fit(left, top, w, h)


def crop_back(img: Image.Image, fit: Fit) -> Image.Image:
    """Remove the white padding so the result has the user's original framing."""
    return img.crop((fit.left, fit.top, fit.left + fit.width, fit.top + fit.height))


def portrait_frame(img_w: int, img_h: int, box, margin: float = 0.08) -> tuple[int, int, int, int]:
    """A 3:4 frame around a person's bounding box, kept inside the photo.

    The model works on a 768x1024 portrait canvas. In a wide or distant photo
    the person would be shrunk to a small part of that canvas, losing detail.
    Cropping to the person first gives the model the full resolution.
    """
    x0, y0, x1, y1 = box
    pad = margin * (y1 - y0)
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    w, h = x1 - x0, y1 - y0
    aspect = WIDTH / HEIGHT
    if w / h < aspect:
        w = h * aspect
    else:
        h = w / aspect
    w, h = min(w, img_w), min(h, img_h)  # if the photo is too small, padding handles the rest
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    left = min(max(cx - w / 2, 0), img_w - w)
    top = min(max(cy - h / 2, 0), img_h - h)
    return int(round(left)), int(round(top)), int(round(left + w)), int(round(top + h))


def blend_clothing_only(original: Image.Image, generated: Image.Image,
                        mask: Image.Image) -> Image.Image:
    """Take only the clothing area from the model; keep every other pixel original.

    The diffusion model redraws the whole image through its compressor (VAE),
    which slightly changes faces, hands and backgrounds. Blending with the
    garment mask keeps the person exactly as photographed, at full resolution.
    The mask is grown a little and softened so the seam isn't visible.
    """
    # Grow and soften at the model's own resolution (fast), then scale up.
    feather = max(2, mask.height // 200)
    mask = mask.convert("L").filter(ImageFilter.MaxFilter(2 * feather + 1))
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    mask = mask.resize(original.size, Image.BILINEAR)
    generated = generated.resize(original.size, Image.LANCZOS)
    return Image.composite(generated, original, mask)


# --------------------------------------------------------------------------
# Engine
# --------------------------------------------------------------------------

class TryOnEngine:
    def __init__(self):
        self.ready = False
        self.load_seconds = 0.0
        if MOCK:
            self.ready = True
            return
        t0 = time.time()
        self._import_leffa()
        self._load_preprocessors()
        self._load_tryon_models()
        self.load_seconds = time.time() - t0
        self.ready = True

    # ---- loading ---------------------------------------------------------

    def _import_leffa(self):
        if not LEFFA_DIR.exists():
            raise RuntimeError(
                f"Leffa source not found at {LEFFA_DIR}. Run `bash setup.sh` first."
            )
        # Leffa's modules (leffa, densepose, detectron2, preprocess) import
        # each other as top-level packages, so its folder goes on sys.path.
        sys.path.insert(0, str(LEFFA_DIR))
        global torch, LeffaTransform, LeffaModel, LeffaInference
        global DensePosePredictor, Parsing, OpenPose
        global get_agnostic_mask_hd, get_agnostic_mask_dc
        import torch  # noqa: F401
        from leffa.transform import LeffaTransform
        from leffa.model import LeffaModel
        from leffa.inference import LeffaInference
        from leffa_utils.densepose_predictor import DensePosePredictor
        from leffa_utils.utils import get_agnostic_mask_hd, get_agnostic_mask_dc
        from preprocess.humanparsing.run_parsing import Parsing
        from preprocess.openpose.run_openpose import OpenPose

        if not torch.cuda.is_available():
            print("WARNING: no GPU found. Try-on will be extremely slow. "
                  "In Colab: Runtime > Change runtime type > T4 GPU.")

    def _load_preprocessors(self):
        c = CKPT_DIR
        print("Loading body analysis models (parsing, pose, DensePose)...")
        self.parsing = Parsing(
            atr_path=str(c / "humanparsing" / "parsing_atr.onnx"),
            lip_path=str(c / "humanparsing" / "parsing_lip.onnx"),
        )
        self.openpose = OpenPose(body_model_path=str(c / "openpose" / "body_pose_model.pth"))
        self.densepose = DensePosePredictor(
            config_path=str(c / "densepose" / "densepose_rcnn_R_50_FPN_s1x.yaml"),
            weights_path=str(c / "densepose" / "model_final_162be9.pkl"),
        )

    def _build_leffa(self, weights_file: str):
        """Build one Leffa model with low peak RAM (Colab free tier has ~12 GB).

        Each Leffa model has ~1.8B parameters. Built the default way (float32
        first, then halved) it needs ~7.2 GB of RAM before the weights are even
        loaded, which can crash a free Colab session. Two changes fix that:
          * the model is created directly in float16 (~3.6 GB), which gives the
            same final model because Leffa converts it to float16 anyway;
          * torch.load(mmap=True) reads weights straight from disk instead of
            holding a second full copy in RAM.
        Measured: peak RAM for construction drops from >7 GB to ~4.3 GB.
        """
        real_load = torch.load

        def mmap_load(f, *args, **kwargs):
            try:
                return real_load(f, *args, mmap=True, **kwargs)
            except Exception:
                return real_load(f, *args, **kwargs)

        torch.load = mmap_load
        torch.set_default_dtype(torch.float16)
        try:
            model = LeffaModel(
                pretrained_model_name_or_path=str(CKPT_DIR / "stable-diffusion-inpainting"),
                pretrained_model=str(CKPT_DIR / weights_file),
                dtype="float16",
            )
            inference = LeffaInference(model=model)  # moves the model to GPU
            # Leffa's pipeline hard-codes "cuda"; keep it in sync with the real device.
            inference.pipe.device = inference.device
        finally:
            torch.load = real_load
            torch.set_default_dtype(torch.float32)
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return inference

    def _load_tryon_models(self):
        print("Loading Leffa DressCode model (bottoms, dresses)...")
        self.model_dc = self._build_leffa("virtual_tryon_dc.pth")
        self.model_hd = None
        if MODELS == "both":
            print("Loading Leffa VITON-HD model (tops)...")
            self.model_hd = self._build_leffa("virtual_tryon.pth")

    # ---- inference -------------------------------------------------------

    def _pick_model(self, garment_type: str):
        """VITON-HD was trained on tops only, so it is used for tops when loaded.
        DressCode was trained on tops, bottoms and dresses."""
        if garment_type == "upper_body" and self.model_hd is not None:
            return self.model_hd, "viton_hd"
        return self.model_dc, "dress_code"

    def dress_one(self, person: Image.Image, garment: Image.Image, garment_type: str,
                  steps: int = 30, seed: int = 42, scale: float = 2.5,
                  on_step=None) -> tuple[Image.Image, Image.Image]:
        """Put one garment on a 768x1024 person image.

        Returns (generated 768x1024 image, mask of the area that was repainted).

        on_step(done, total) is called after every diffusion step, so the
        interface can show real progress instead of a frozen bar.
        """
        assert garment_type in GARMENT_TYPES, garment_type
        garment_canvas, _ = fit_to_canvas(garment)
        if MOCK:
            for k in range(int(steps)):  # imitate the model's step loop
                time.sleep(float(os.environ.get("CLOAK_MOCK_STEP_SECONDS", "0.05")))
                if on_step:
                    on_step(k + 1, int(steps))
            return _mock_result(person, garment_canvas, garment_type)

        inference, model_type = self._pick_model(garment_type)
        small = person.resize((384, 512))
        model_parse, _ = self.parsing(small)
        keypoints = self.openpose(small)

        if model_type == "viton_hd":
            mask = get_agnostic_mask_hd(model_parse, keypoints, garment_type)
        else:
            mask = get_agnostic_mask_dc(model_parse, keypoints, garment_type)
        mask = mask.resize((WIDTH, HEIGHT))

        person_arr = np.array(person)
        if model_type == "viton_hd":
            seg = self.densepose.predict_seg(person_arr)[:, :, ::-1]
            densepose = Image.fromarray(seg)
        else:
            iuv = self.densepose.predict_iuv(person_arr)
            seg = np.concatenate([iuv[:, :, 0:1]] * 3, axis=-1)
            densepose = Image.fromarray(seg)

        data = LeffaTransform()({
            "src_image": [person],
            "ref_image": [garment_canvas],
            "mask": [mask],
            "densepose": [densepose],
        })
        with _report_steps(on_step):
            out = inference(
                data,
                ref_acceleration=False,
                num_inference_steps=int(steps),
                guidance_scale=float(scale),
                seed=int(seed),
                repaint=False,
            )
        return out["generated_image"][0], mask

    def _person_frame(self, photo: Image.Image):
        """Find the person in the photo and return a 3:4 frame around them."""
        full = (0, 0, photo.width, photo.height)
        if MOCK:
            return full
        canvas, fit = fit_to_canvas(photo)
        parse, _ = self.parsing(canvas.resize((WIDTH // 2, HEIGHT // 2)))
        ys, xs = np.nonzero(np.array(parse) > 0)  # 0 = background
        if len(xs) < 500:  # nobody found; use the whole photo
            return full
        scale = fit.width / photo.width
        to_photo_x = lambda x: (x * 2 - fit.left) / scale
        to_photo_y = lambda y: (y * 2 - fit.top) / scale
        box = (max(0, to_photo_x(xs.min())), max(0, to_photo_y(ys.min())),
               min(photo.width, to_photo_x(xs.max() + 1)), min(photo.height, to_photo_y(ys.max() + 1)))
        return portrait_frame(photo.width, photo.height, box)

    def dress_outfit(self, person, top=None, bottom=None, dress=None,
                     steps: int = 30, seed: int = 42, progress=None):
        """Dress a person in a full outfit.

        Order matters: bottoms go on first, then the top, so the top's hem
        is drawn last and can sit naturally over the waistband.
        A dress/gown replaces both top and bottom.
        Returns (result_image, log_lines).
        """
        person = load_image(person)
        if person is None:
            raise ValueError("Please add a photo of yourself first.")
        top, bottom, dress = load_image(top), load_image(bottom), load_image(dress)

        if dress is not None:
            plan = [("dresses", dress, "dress/gown")]
        else:
            plan = []
            if bottom is not None:
                plan.append(("lower_body", bottom, "bottom"))
            if top is not None:
                plan.append(("upper_body", top, "top"))
        if not plan:
            raise ValueError("Add at least one clothing item (a top, a bottom, or a dress).")

        # 1. Zoom in: crop a portrait frame around the person at full resolution.
        frame = self._person_frame(person)
        crop = person.crop(frame)
        canvas, fit = fit_to_canvas(crop)
        repainted = Image.new("L", (WIDTH, HEIGHT), 0)  # everything any garment touched
        log = []
        n = len(plan)
        for i, (gtype, garment, label) in enumerate(plan):
            prefix = f"Fitting the {label}" + (f" ({i + 1} of {n})" if n > 1 else "")

            def on_step(done, total, i=i, prefix=prefix):
                if progress is not None:
                    # overall fraction across every garment in the outfit
                    progress((i + done / total) / n, desc=f"{prefix} · step {done}/{total}")

            if progress is not None:
                progress(i / n, desc=f"{prefix} · reading body shape")
            t0 = time.time()
            generated, mask = self.dress_one(canvas, garment, gtype, steps=steps, seed=seed,
                                             on_step=on_step)
            # Keep untouched areas clean before the next garment goes on.
            canvas = blend_clothing_only(canvas, generated, mask)
            repainted = ImageChops.lighter(repainted, mask.convert("L"))
            log.append(f"{label}: {time.time() - t0:.1f}s")

        # 2. Put the result back into the original photo at its full resolution,
        #    taking only the clothing area from the model.
        dressed = blend_clothing_only(crop, crop_back(canvas, fit), crop_back(repainted, fit))
        result = person.copy()
        result.paste(dressed, frame[:2])
        return result, log


# --------------------------------------------------------------------------
# Live progress from inside Leffa's step loop
# --------------------------------------------------------------------------

class _report_steps:
    """Temporarily swap the progress bar Leffa's pipeline uses (tqdm) for one
    that also calls on_step(done, total). Leffa's code itself is untouched."""

    def __init__(self, on_step):
        self.on_step = on_step

    def __enter__(self):
        if self.on_step is None:
            return self
        import types
        import leffa.pipeline as pipeline_module
        import tqdm as real_tqdm

        on_step = self.on_step

        class StepBar(real_tqdm.tqdm):
            def update(self, n=1):
                result = super().update(n)
                self._cloak_done = getattr(self, "_cloak_done", 0) + (n or 0)
                try:
                    on_step(int(self._cloak_done), int(self.total or 0) or 1)
                except Exception:
                    pass  # progress display must never break a try-on
                return result

        self.module = pipeline_module
        self.original = pipeline_module.tqdm
        pipeline_module.tqdm = types.SimpleNamespace(tqdm=StepBar)
        return self

    def __exit__(self, *exc):
        if self.on_step is not None:
            self.module.tqdm = self.original
        return False


# --------------------------------------------------------------------------
# Mock output for UI development without a GPU. Watermarked on purpose.
# --------------------------------------------------------------------------

def _mock_result(person: Image.Image, garment: Image.Image, garment_type: str):
    out = person.copy()
    mask = Image.new("L", out.size, 0)
    thumb = garment.copy()
    thumb.thumbnail((WIDTH // 3, HEIGHT // 3))
    y = {"upper_body": HEIGHT // 4, "lower_body": HEIGHT // 2, "dresses": HEIGHT // 4}[garment_type]
    x = (WIDTH - thumb.width) // 2
    out.paste(thumb, (x, y))
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, WIDTH, 60), fill=(200, 0, 0))
    d.text((20, 20), "MOCK MODE - NOT A REAL TRY-ON (UI testing only)", fill=(255, 255, 255))
    # The "repainted" area includes the warning banner so it always survives blending.
    ImageDraw.Draw(mask).rectangle((x, y, x + thumb.width, y + thumb.height), fill=255)
    ImageDraw.Draw(mask).rectangle((0, 0, WIDTH, 60), fill=255)
    return out, mask
