"""
CLOAK - try an outfit on yourself before you pay the vendor.

Run:  python app.py            (needs a GPU; see README / Colab notebook)
      CLOAK_MOCK=1 python app.py   (UI development without a GPU)
"""

import os
import time
from pathlib import Path

import gradio as gr

from cloak.engine import CKPT_DIR, MOCK, TryOnEngine

GR_MAJOR = int(gr.__version__.split(".")[0])

TITLE = "CLOAK 👗👔"
TAGLINE = "Screenshot it from the vendor's page. Try it on yourself. Then decide."

PHOTO_TIPS = """
**For the best result, your photo should:**
- show you facing the camera, standing straight, arms relaxed by your sides
- show at least your head to your knees (full body is best for trousers/gowns)
- have a plain background and good light
"""

CLOTH_TIPS = """
**Clothing photos work best when:**
- the item is shown alone on a plain background (flat-lay or "ghost mannequin")
- the whole item is visible and facing forward
- a screenshot from a vendor's Instagram or WhatsApp catalogue is fine, crop out other things first
"""

LIMITS = """
**Honest limitations:** CLOAK shows how the *style, colour and pattern* of an item could look on you.
It does not know your size or the fabric's real fit, so it can't promise the vendor's item will fit you.
The models were trained mostly on Western catalogue photos, so very loose native styles (agbada, wide
bubu) and accessories (caps, shoes) are less reliable. Photos are processed in this session only and are not stored.
"""

CSS = """
.gradio-container {max-width: 1200px !important; margin: auto;}
#title {text-align: center;}
#title h1 {font-size: 2.4em; margin-bottom: 0;}
#cloak-btn {font-size: 1.2em; min-height: 54px;}
"""

engine = None


def get_engine():
    global engine
    if engine is None:
        engine = TryOnEngine()
    return engine


def run_tryon(person, mode, top, bottom, dress, quality, seed, lookbook,
              progress=gr.Progress()):
    if person is None:
        raise gr.Error("Add a photo of yourself first (Step 1).")
    if mode == "Dress / gown":
        top = bottom = None
        if dress is None:
            raise gr.Error("Add a photo of the dress or gown.")
    else:
        dress = None
        if top is None and bottom is None:
            raise gr.Error("Add a top, a bottom, or both.")

    steps = {"Fast (~20 steps)": 20, "Balanced (30 steps)": 30, "Best (50 steps)": 50}[quality]
    progress(0, desc="Warming up the model...")
    t0 = time.time()
    try:
        result, log = get_engine().dress_outfit(
            person, top=top, bottom=bottom, dress=dress,
            steps=steps, seed=int(seed), progress=progress,
        )
    except ValueError as e:
        raise gr.Error(str(e))

    look_no = len(lookbook) + 1
    items = "dress" if dress is not None else " + ".join(
        x for x, v in (("bottom", bottom), ("top", top)) if v is not None)
    caption = f"Look {look_no}: {items}"
    lookbook = lookbook + [(result, caption)]
    status = f"✅ {caption} ready in {time.time() - t0:.0f}s ({', '.join(log)})"
    if MOCK:
        status = "⚠️ MOCK MODE: this is not a real try-on. " + status
    return result, lookbook, lookbook, status


def switch_mode(mode):
    two_piece = mode == "Top + bottom"
    return gr.Column(visible=two_piece), gr.Column(visible=not two_piece)


def clear_lookbook():
    return [], []


def example_files(sub):
    folder = CKPT_DIR / "examples" / sub
    if not folder.exists():
        return []
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    return [[str(p)] for p in files[:6]]


def build_ui():
    theme = gr.themes.Soft(primary_hue="orange", secondary_hue="green")
    blocks_kwargs = {"title": "CLOAK"}
    if GR_MAJOR < 6:  # Gradio 6 moved theme/css to launch()
        blocks_kwargs.update(theme=theme, css=CSS)

    with gr.Blocks(**blocks_kwargs) as demo:
        lookbook = gr.State([])

        with gr.Column(elem_id="title"):
            gr.Markdown(f"# {TITLE}\n### {TAGLINE}")
        if MOCK:
            gr.Markdown("⚠️ **Mock mode is on.** Results are placeholders for UI testing, not real try-ons.")

        with gr.Row(equal_height=False):
            # ---------------- Step 1: you ----------------
            with gr.Column(scale=1):
                gr.Markdown("## 1. Your photo")
                person = gr.Image(label="You", type="pil",
                                  sources=["upload", "webcam"], height=420)
                ex = example_files("person1")
                if ex:
                    gr.Examples(ex, inputs=person, label="Or use a sample person")
                with gr.Accordion("Photo tips", open=False):
                    gr.Markdown(PHOTO_TIPS)

            # ---------------- Step 2: outfit ----------------
            with gr.Column(scale=1):
                gr.Markdown("## 2. The outfit")
                mode = gr.Radio(["Top + bottom", "Dress / gown"], value="Top + bottom",
                                label="What are you trying on?")
                with gr.Column(visible=True) as two_piece_col:
                    top = gr.Image(label="Top (shirt, blouse, T-shirt, jacket)",
                                   type="pil", sources=["upload", "clipboard"], height=200)
                    bottom = gr.Image(label="Bottom (trousers, skirt, shorts)",
                                      type="pil", sources=["upload", "clipboard"], height=200)
                with gr.Column(visible=False) as dress_col:
                    dress = gr.Image(label="Dress / gown / long native outfit",
                                     type="pil", sources=["upload", "clipboard"], height=420)
                exg = example_files("garment")
                if exg:
                    gr.Examples(exg, inputs=top, label="Or use a sample top")
                with gr.Accordion("Clothing photo tips", open=False):
                    gr.Markdown(CLOTH_TIPS)

            # ---------------- Step 3: result ----------------
            with gr.Column(scale=1):
                gr.Markdown("## 3. See yourself")
                result = gr.Image(label="You, wearing it", type="pil",
                                  height=420, interactive=False)
                go = gr.Button("Try it on ✨", variant="primary", elem_id="cloak-btn")
                status = gr.Markdown("")
                with gr.Accordion("Settings", open=False):
                    quality = gr.Radio(["Fast (~20 steps)", "Balanced (30 steps)", "Best (50 steps)"],
                                       value="Balanced (30 steps)", label="Quality")
                    seed = gr.Number(value=42, precision=0,
                                     label="Variation seed (change it for a different take)")

        gr.Markdown("## Your lookbook: compare the combinations you tried")
        gallery = gr.Gallery(label="Lookbook", columns=4, height=360, object_fit="contain")
        clear = gr.Button("Clear lookbook", size="sm")

        with gr.Accordion("What CLOAK can and can't tell you", open=False):
            gr.Markdown(LIMITS)

        mode.change(switch_mode, inputs=mode, outputs=[two_piece_col, dress_col])
        go.click(run_tryon,
                 inputs=[person, mode, top, bottom, dress, quality, seed, lookbook],
                 outputs=[result, lookbook, gallery, status])
        clear.click(clear_lookbook, outputs=[lookbook, gallery])

    return demo, theme


if __name__ == "__main__":
    demo, theme = build_ui()
    if not MOCK:
        print("Loading models (first time takes a few minutes)...")
        get_engine()
        print(f"Models ready in {engine.load_seconds:.0f}s")
    launch_kwargs = {
        "share": os.environ.get("CLOAK_SHARE", "1") == "1",
        "server_name": "0.0.0.0",
        "server_port": int(os.environ.get("PORT", 7860)),
        "allowed_paths": [str(CKPT_DIR / "examples")],
    }
    if GR_MAJOR >= 6:
        launch_kwargs.update(theme=theme, css=CSS)
    demo.queue(max_size=8).launch(**launch_kwargs)
