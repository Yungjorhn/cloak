"""
CLOAK - see an outfit on yourself before you pay the vendor.

Run:  python app.py              (needs a GPU; see README / Colab notebook)
      CLOAK_MOCK=1 python app.py  (interface work without a GPU)
"""

import os
import time

import gradio as gr

from cloak.engine import CKPT_DIR, MOCK, TryOnEngine, load_image
from cloak.ui_style import (CSS, FONTS_HEAD, FOOTER, HEADER, build_theme,
                            moodboard_html, step, supported, to_data_uri)

GR_MAJOR = int(gr.__version__.split(".")[0])
QUALITY = {"Fast": 20, "Balanced": 30, "Best": 50}

engine = None


def get_engine():
    global engine
    if engine is None:
        engine = TryOnEngine()
    return engine


def H(value):
    """An HTML block with no inner padding, so text lines up with the panels."""
    return gr.HTML(value, elem_classes=["ck-html"],
                   **supported(gr.HTML.__init__, padding=False))


def image_input(placeholder, height, sources=("upload", "clipboard"), **extra):
    """An image box without Gradio's default label, in whatever form this version supports."""
    kwargs = supported(gr.Image.__init__, type="pil", sources=list(sources), height=height,
                       show_label=False, placeholder=placeholder, elem_classes=["ck-img"],
                       **extra)
    return gr.Image(**kwargs)


def run_tryon(person, mode, top, bottom, dress, quality, seed, looks,
              progress=gr.Progress()):
    if person is None:
        raise gr.Error("Add a photo of yourself first (step 01).")
    if mode == "Dress / gown":
        top = bottom = None
        if dress is None:
            raise gr.Error("Add a photo of the dress or gown.")
    else:
        dress = None
        if top is None and bottom is None:
            raise gr.Error("Add a top, a bottom, or both.")

    progress(0, desc="Preparing your photo")
    t0 = time.time()
    try:
        result, log = get_engine().dress_outfit(
            person, top=top, bottom=bottom, dress=dress,
            steps=QUALITY[quality], seed=int(seed), progress=progress,
        )
    except ValueError as e:
        raise gr.Error(str(e))

    items = [(label, img) for label, img in
             (("Dress", dress), ("Bottom", bottom), ("Top", top)) if img is not None]
    look = {
        "no": len(looks) + 1,
        "time": time.strftime("%H:%M"),
        "before": to_data_uri(load_image(person)),
        "after": to_data_uri(result),
        "items": [(label, to_data_uri(load_image(img), 120)) for label, img in items],
    }
    looks = looks + [look]
    status = f"Look {look['no']:02d} ready · {time.time() - t0:.0f}s · " + " · ".join(log)
    if MOCK:
        status = "MOCK MODE, NOT A REAL TRY-ON · " + status
    return result, looks, moodboard_html(looks), status


def switch_mode(mode):
    two_piece = mode == "Top + bottom"
    return gr.Column(visible=two_piece), gr.Column(visible=not two_piece)


def clear_board():
    return [], moodboard_html([])


def example_files(sub, n=6):
    folder = CKPT_DIR / "examples" / sub
    if not folder.exists():
        return []
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    return [[str(p)] for p in files[:n]]


def build_ui():
    theme = build_theme()
    blocks_kwargs = {"title": "CLOAK · AI fitting room"}
    if GR_MAJOR < 6:  # Gradio 6 moved theme/css/head to launch()
        blocks_kwargs.update(supported(gr.Blocks.__init__, theme=theme, css=CSS, head=FONTS_HEAD))

    with gr.Blocks(**blocks_kwargs) as demo:
        looks = gr.State([])
        H(HEADER)
        if MOCK:
            H('<p class="ck-kicker" style="margin-top:16px">Mock mode · results are '
                    'placeholders for interface testing, not real try-ons</p>')

        with gr.Row(equal_height=False):
            # 01 ------------------------------------------------------------
            with gr.Column(scale=1, min_width=300):
                H(step("01", "You", "front-facing · arms down"))
                person = image_input("Upload or snap a photo of yourself", 460,
                                     sources=("upload", "webcam"))
                ex = example_files("person1")
                if ex:
                    gr.Examples(ex, inputs=person, label="Samples",
                                **supported(gr.Examples.__init__, examples_per_page=6))

            # 02 ------------------------------------------------------------
            with gr.Column(scale=1, min_width=300):
                H(step("02", "The outfit", "clean product shots"))
                mode = gr.Radio(["Top + bottom", "Dress / gown"], value="Top + bottom",
                                show_label=False, elem_classes=["ck-mode"])
                with gr.Column(visible=True) as two_piece_col:
                    H('<div class="ck-slot-label">Top · shirt, blouse, tee, jacket</div>')
                    top = image_input("Drop the top here", 196)
                    H('<div class="ck-slot-label">Bottom · trousers, skirt, shorts</div>')
                    bottom = image_input("Drop the bottom here", 196)
                with gr.Column(visible=False) as dress_col:
                    H('<div class="ck-slot-label">Dress · gown, long native outfit</div>')
                    dress = image_input("Drop the dress here", 410)
                exg = example_files("garment")
                if exg:
                    gr.Examples(exg, inputs=top, label="Sample tops",
                                **supported(gr.Examples.__init__, examples_per_page=6))

            # 03 ------------------------------------------------------------
            with gr.Column(scale=1, min_width=300):
                H(step("03", "The look", "about 20 to 40 s"))
                result = gr.Image(**supported(
                    gr.Image.__init__, type="pil", height=460, interactive=False,
                    show_label=False, elem_classes=["ck-img"],
                    buttons=["download", "fullscreen"]))
                go = gr.Button("CLOAK IT", variant="primary", elem_id="ck-go")
                status = gr.Markdown("", elem_classes=["ck-status"])
                with gr.Accordion("Settings", open=False):
                    quality = gr.Radio(list(QUALITY), value="Balanced",
                                       label="Quality (more steps = sharper, slower)")
                    seed = gr.Number(value=42, precision=0,
                                     label="Variation (change for a different take)")

        board = H(moodboard_html([]))
        clear = gr.Button("Clear moodboard", variant="secondary", size="sm")
        H(FOOTER)

        mode.change(switch_mode, inputs=mode, outputs=[two_piece_col, dress_col])
        go.click(run_tryon,
                 inputs=[person, mode, top, bottom, dress, quality, seed, looks],
                 outputs=[result, looks, board, status],
                 # show the progress bar on the result panel only, not on every output
                 **supported(go.click, show_progress_on=[result]))
        clear.click(clear_board, outputs=[looks, board])

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
        launch_kwargs.update(theme=theme, css=CSS, head=FONTS_HEAD)
    demo.queue(max_size=8).launch(**supported(demo.launch, **launch_kwargs))
