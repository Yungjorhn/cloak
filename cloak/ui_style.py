"""Visual design for CLOAK: fashion-editorial type on a sleek dark interface.

Colours, fonts and the moodboard markup live here so app.py stays about behaviour.
"""

import base64
import html
import io
import inspect

import gradio as gr

# ---- design tokens -------------------------------------------------------
BG = "#0A0A0B"        # page
SURFACE = "#131315"   # panels
SURFACE_2 = "#1B1B1F" # inputs, hover
LINE = "#2A2A2F"      # hairlines
TEXT = "#F2EFE9"      # warm off-white, like paper
MUTED = "#8E8B85"
ACCENT = "#D4FF4F"    # electric lime, used sparingly

FONTS_HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
"""


def supported(fn, **kwargs):
    """Keep only the keyword arguments this Gradio version understands."""
    params = inspect.signature(fn).parameters
    return {k: v for k, v in kwargs.items() if k in params}


def build_theme():
    theme = gr.themes.Base(
        primary_hue=gr.themes.colors.lime,
        neutral_hue=gr.themes.colors.zinc,
        font=["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        font_mono=["JetBrains Mono", "ui-monospace", "monospace"],
        radius_size=gr.themes.sizes.radius_sm,
    )
    values = dict(
        body_background_fill=BG,
        body_text_color=TEXT,
        body_text_color_subdued=MUTED,
        background_fill_primary=SURFACE,
        background_fill_secondary=SURFACE_2,
        border_color_primary=LINE,
        border_color_accent=ACCENT,
        color_accent=ACCENT,
        color_accent_soft=SURFACE_2,
        block_background_fill=SURFACE,
        block_border_color=LINE,
        block_border_width="1px",
        block_radius="4px",
        block_shadow="none",
        block_label_background_fill=SURFACE,
        block_label_text_color=MUTED,
        block_label_border_color=LINE,
        block_title_text_color=MUTED,
        panel_background_fill=SURFACE,
        panel_border_color=LINE,
        input_background_fill=SURFACE_2,
        input_border_color=LINE,
        input_border_color_focus=ACCENT,
        checkbox_label_background_fill=SURFACE_2,
        checkbox_label_background_fill_selected=TEXT,
        checkbox_label_text_color=MUTED,
        checkbox_label_text_color_selected=BG,
        checkbox_label_border_color=LINE,
        checkbox_border_color_selected=BG,
        checkbox_background_color_selected=BG,
        button_primary_background_fill=TEXT,
        button_primary_background_fill_hover=ACCENT,
        button_primary_text_color=BG,
        button_primary_text_color_hover=BG,
        button_primary_border_color=TEXT,
        button_secondary_background_fill="transparent",
        button_secondary_background_fill_hover=SURFACE_2,
        button_secondary_text_color=TEXT,
        button_secondary_border_color=LINE,
        loader_color=ACCENT,
        slider_color=ACCENT,
        link_text_color=ACCENT,
        link_text_color_hover=TEXT,
        accordion_text_color=MUTED,
    )
    # Same values in light and dark mode, so the look never flips.
    values.update({f"{k}_dark": v for k, v in list(values.items())})
    return theme.set(**supported(theme.set, **values))


CSS = f"""
:root {{ --ck-accent:{ACCENT}; --ck-text:{TEXT}; --ck-muted:{MUTED}; --ck-line:{LINE};
        --ck-surface:{SURFACE}; --ck-surface2:{SURFACE_2}; --ck-bg:{BG}; }}
.gradio-container {{ max-width: 1280px !important; margin: 0 auto !important;
                     padding: 0 28px !important; background: {BG} !important; }}
body, gradio-app {{ background: {BG} !important; }}
footer {{ opacity: .35; }}
.ck-html, .ck-html > div, .ck-html .prose {{ padding-left:0 !important; padding-right:0 !important; }}

/* ---------- navigation + hero ---------- */
.ck-nav {{ display:flex; justify-content:space-between; align-items:center;
          padding: 22px 0; border-bottom: 1px solid {LINE}; }}
.ck-logo {{ font-family:'Instrument Serif', Georgia, serif; font-size: 34px;
           letter-spacing: .14em; color:{TEXT}; line-height:1; }}
.ck-meta {{ font-family:'JetBrains Mono', monospace; font-size: 11px; letter-spacing:.18em;
           color:{MUTED}; text-transform:uppercase; display:flex; gap:18px; align-items:center; }}
.ck-dot {{ width:7px; height:7px; border-radius:50%; background:{ACCENT};
          box-shadow:0 0 12px {ACCENT}; display:inline-block; margin-right:8px; }}
.ck-hero {{ display:grid; grid-template-columns: 1.4fr 1fr; gap: 40px; align-items:end;
           padding: 56px 0 44px; border-bottom: 1px solid {LINE}; }}
.ck-kicker {{ font-family:'JetBrains Mono', monospace; font-size:11px; letter-spacing:.2em;
             color:{ACCENT}; text-transform:uppercase; margin:0 0 18px; }}
.ck-hero h1 {{ font-family:'Instrument Serif', Georgia, serif; font-weight:400;
              font-size: clamp(48px, 7vw, 96px); line-height:.95; letter-spacing:-.01em;
              color:{TEXT}; margin:0; }}
.ck-hero h1 em {{ font-style: italic; color:{ACCENT}; }}
.ck-hero p.ck-sub {{ color:{MUTED}; font-size:16px; line-height:1.6; margin:0; max-width:420px; }}
.ck-steps-inline {{ font-family:'JetBrains Mono', monospace; font-size:11px; color:{MUTED};
                    letter-spacing:.14em; text-transform:uppercase; margin-top:22px; }}
.ck-steps-inline b {{ color:{TEXT}; font-weight:500; }}

/* ---------- step headers ---------- */
.ck-step {{ display:flex; align-items:baseline; gap:14px; padding: 30px 0 14px; }}
.ck-step .n {{ font-family:'JetBrains Mono', monospace; font-size:12px; color:{ACCENT};
              letter-spacing:.1em; }}
.ck-step .t {{ font-family:'Instrument Serif', Georgia, serif; font-size:30px; color:{TEXT}; }}
.ck-step .h {{ font-family:'JetBrains Mono', monospace; font-size:10.5px; color:{MUTED};
              letter-spacing:.14em; text-transform:uppercase; margin-left:auto; }}

/* ---------- panels and inputs ---------- */
.ck-panel {{ background:{SURFACE} !important; border:1px solid {LINE} !important;
            border-radius:4px !important; }}
.ck-img img {{ object-fit: contain; }}
.ck-mode label {{ font-family:'JetBrains Mono', monospace !important; font-size:12px !important;
                 letter-spacing:.08em; text-transform:uppercase; }}
.ck-slot-label {{ font-family:'JetBrains Mono', monospace; font-size:10.5px; letter-spacing:.16em;
                 text-transform:uppercase; color:{MUTED}; margin: 12px 0 6px; }}
#ck-go {{ font-family:'JetBrains Mono', monospace !important; letter-spacing:.2em;
         text-transform:uppercase; font-size:14px !important; min-height:58px; border-radius:2px !important;
         transition: background .2s ease, box-shadow .2s ease; }}
#ck-go:hover {{ box-shadow: 0 0 0 1px {ACCENT}, 0 0 28px rgba(212,255,79,.25); }}
.ck-status, .ck-status p {{ font-family:'JetBrains Mono', monospace !important; font-size:12px !important;
                           color:{MUTED} !important; letter-spacing:.04em; min-height: 18px; }}
.ck-examples .label, .ck-examples > .label-wrap, .ck-examples span {{
    font-family:'JetBrains Mono', monospace !important; font-size:10.5px !important;
    letter-spacing:.14em; text-transform:uppercase; color:{MUTED} !important; }}
.ck-examples button img {{ border-radius:2px; }}
.ck-examples button:hover img {{ outline: 1px solid {ACCENT}; }}

/* ---------- moodboard ---------- */
.ck-board-head {{ display:flex; align-items:end; justify-content:space-between;
                 padding: 64px 0 18px; border-bottom:1px solid {LINE}; margin-bottom: 22px; }}
.ck-board-head h2 {{ font-family:'Instrument Serif', Georgia, serif; font-weight:400;
                    font-size: clamp(40px, 5vw, 64px); margin:0; color:{TEXT}; line-height:1; }}
.ck-board-head h2 em {{ font-style:italic; color:{ACCENT}; }}
.ck-board-head p {{ color:{MUTED}; margin:8px 0 0; font-size:14px; }}
.ck-board {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(min(340px, 100%), 1fr)); gap: 22px; }}
.ck-card {{ background:{SURFACE}; border:1px solid {LINE}; border-radius:4px; overflow:hidden;
           transition: border-color .2s ease, transform .2s ease; }}
.ck-card:hover {{ border-color:#3d3d44; transform: translateY(-2px); }}
.ck-card-top {{ display:flex; justify-content:space-between; padding: 12px 14px;
               font-family:'JetBrains Mono', monospace; font-size:11px; letter-spacing:.16em;
               text-transform:uppercase; color:{MUTED}; border-bottom:1px solid {LINE}; }}
.ck-card-top b {{ color:{TEXT}; font-weight:500; }}
.ck-pair {{ display:grid; grid-template-columns: 1fr 1fr; gap:1px; background:{LINE}; }}
.ck-shot {{ position:relative; background:#f4f2ee; aspect-ratio: 3 / 4; overflow:hidden; }}
.ck-shot img {{ width:100%; height:100%; object-fit:cover; object-position: top center; display:block; }}
.ck-tag {{ position:absolute; left:10px; top:10px; padding:4px 8px; border-radius:2px;
          font-family:'JetBrains Mono', monospace; font-size:10px; letter-spacing:.16em;
          background: rgba(10,10,11,.78); color:{TEXT}; backdrop-filter: blur(6px);
          text-transform: uppercase; }}
.ck-tag.after {{ background:{ACCENT}; color:{BG}; }}
.ck-items {{ display:flex; gap:10px; padding: 12px 14px; align-items:center; flex-wrap:wrap; }}
.ck-item {{ display:flex; align-items:center; gap:8px; font-family:'JetBrains Mono', monospace;
           font-size:10.5px; letter-spacing:.12em; text-transform:uppercase; color:{MUTED}; }}
.ck-item img {{ width:34px; height:34px; object-fit:contain; background:#f4f2ee; border-radius:2px; }}
.ck-empty {{ border:1px dashed {LINE}; border-radius:4px; padding: 56px 24px; text-align:center;
            color:{MUTED}; }}
.ck-empty .big {{ font-family:'Instrument Serif', Georgia, serif; font-size:28px; color:{TEXT};
                 margin-bottom:8px; }}

/* ---------- footer note ---------- */
.ck-foot {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 28px; margin-top: 64px;
           padding: 28px 0 10px; border-top:1px solid {LINE}; }}
.ck-foot h4 {{ font-family:'JetBrains Mono', monospace; font-size:11px; letter-spacing:.18em;
              text-transform:uppercase; color:{ACCENT}; margin:0 0 10px; font-weight:500; }}
.ck-foot p {{ color:{MUTED}; font-size:13.5px; line-height:1.65; margin:0; }}

@media (max-width: 860px) {{
  .ck-hero {{ grid-template-columns: 1fr; gap: 20px; padding: 36px 0 28px; }}
  .ck-foot {{ grid-template-columns: 1fr; }}
  .ck-meta .hide-sm {{ display:none; }}
  body .gradio-container {{ padding: 0 14px !important; }}
  body .gradio-container .main, body .gradio-container .fillable {{ padding-left: 0 !important; padding-right: 0 !important; }}
  .ck-board-head {{ flex-direction: column; align-items: flex-start; gap: 10px; padding-top: 44px; }}
  .ck-step .h {{ display:none; }}
}}
"""

HEADER = """
<nav class="ck-nav">
  <div class="ck-logo">CLOAK</div>
  <div class="ck-meta"><span><span class="ck-dot"></span>AI fitting room</span>
    <span class="hide-sm">Open-weight · Leffa</span></div>
</nav>
<section class="ck-hero">
  <div>
    <p class="ck-kicker">Virtual try-on · v0.1</p>
    <h1>See it on <em>you</em><br>before you pay.</h1>
  </div>
  <div>
    <p class="ck-sub">Screenshot the piece from the vendor's page, add a photo of yourself,
      and CLOAK dresses you in it. Mix tops and bottoms, then compare every look on your moodboard.</p>
    <div class="ck-steps-inline"><b>01</b> You &nbsp;/&nbsp; <b>02</b> The outfit &nbsp;/&nbsp; <b>03</b> The look</div>
  </div>
</section>
"""


def step(n, title, hint=""):
    return (f'<div class="ck-step"><span class="n">{n}</span><span class="t">{title}</span>'
            f'<span class="h">{hint}</span></div>')


FOOTER = """
<div class="ck-foot">
  <div><h4>What it shows</h4><p>How a style, colour and print could look on your body,
    and which combinations work together.</p></div>
  <div><h4>What it can't promise</h4><p>Size and real fabric fit. It's trained mostly on
    Western catalogue photos, so loose native styles and accessories are less reliable.</p></div>
  <div><h4>Your photos</h4><p>Processed in this session only and never stored. Open source,
    built on the Leffa model (MIT). Non-commercial research prototype.</p></div>
</div>
"""


# ---- moodboard -----------------------------------------------------------

def to_data_uri(img, max_side=640):
    img = img.copy()
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def moodboard_html(looks):
    count = len(looks)
    head = (f'<div class="ck-board-head"><div><h2>The <em>moodboard</em></h2>'
            f'<p>Every look you try, next to the photo you started from.</p></div>'
            f'<div class="ck-meta">{count:02d} look{"s" if count != 1 else ""}</div></div>')
    if not looks:
        return head + ('<div class="ck-empty"><div class="big">Nothing pinned yet.</div>'
                       'Try on your first outfit and it will appear here, before and after.</div>')
    cards = []
    for look in reversed(looks):  # newest first
        items = "".join(
            f'<span class="ck-item"><img src="{uri}" alt="">{html.escape(label)}</span>'
            for label, uri in look["items"]
        )
        cards.append(f"""
<article class="ck-card">
  <div class="ck-card-top"><b>Look {look['no']:02d}</b><span>{html.escape(look['time'])}</span></div>
  <div class="ck-pair">
    <div class="ck-shot"><img src="{look['before']}" alt="Before"><span class="ck-tag">Before</span></div>
    <div class="ck-shot"><img src="{look['after']}" alt="After"><span class="ck-tag after">After</span></div>
  </div>
  <div class="ck-items">{items}</div>
</article>""")
    return head + '<div class="ck-board">' + "".join(cards) + "</div>"
