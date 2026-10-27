"""Visual design for CLOAK.

A mix of two directions: a clean, light, editorial layout (cream paper, serif
headlines, rounded white cards) with Gen Z energy (a vivid purple accent, a lime
call-to-action, soft pink-to-lavender gradients and a handwritten sticker note).

Colours, fonts and the HTML pieces live here so app.py stays about behaviour.
"""

import base64
import html
import inspect
import io

import gradio as gr

# ---- design tokens -------------------------------------------------------
CREAM = "#F7F2EC"     # page background, warm paper
PAPER = "#FFFFFF"     # cards
SOFT = "#FBF8F4"      # inputs and image wells
INK = "#17151C"       # text and dark buttons
MUTED = "#6F6A75"
LINE = "#ECE5DC"
PURPLE = "#7A3CF0"    # signature accent ("you.")
LIME = "#D9F95D"      # the CLOAK IT button
PINK = "#F8CFEA"
LAVENDER = "#E3D8FF"

FONTS_HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Caveat:wght@500;600&display=swap" rel="stylesheet">
"""


def supported(fn, **kwargs):
    """Keep only the keyword arguments this Gradio version understands."""
    params = inspect.signature(fn).parameters
    return {k: v for k, v in kwargs.items() if k in params}


def build_theme():
    theme = gr.themes.Base(
        primary_hue=gr.themes.colors.violet,
        neutral_hue=gr.themes.colors.stone,
        font=["Plus Jakarta Sans", "ui-sans-serif", "system-ui", "sans-serif"],
        font_mono=["ui-monospace", "monospace"],
        radius_size=gr.themes.sizes.radius_lg,
    )
    values = dict(
        body_background_fill=CREAM,
        body_text_color=INK,
        body_text_color_subdued=MUTED,
        background_fill_primary=PAPER,
        background_fill_secondary=SOFT,
        border_color_primary=LINE,
        border_color_accent=PURPLE,
        color_accent=PURPLE,
        color_accent_soft=LAVENDER,
        block_background_fill=SOFT,
        block_border_color=LINE,
        block_border_width="1px",
        block_radius="16px",
        block_shadow="none",
        block_label_background_fill=PAPER,
        block_label_text_color=MUTED,
        block_label_border_color=LINE,
        block_title_text_color=MUTED,
        panel_background_fill=PAPER,
        panel_border_color=LINE,
        input_background_fill=SOFT,
        input_border_color=LINE,
        input_border_color_focus=PURPLE,
        checkbox_label_background_fill=SOFT,
        checkbox_label_background_fill_hover=LAVENDER,
        checkbox_label_background_fill_selected=INK,
        checkbox_label_text_color=INK,
        checkbox_label_text_color_selected=PAPER,
        checkbox_label_border_color=LINE,
        checkbox_label_border_color_selected=INK,
        checkbox_border_color_selected=PAPER,
        checkbox_background_color_selected=INK,
        button_primary_background_fill=LIME,
        button_primary_background_fill_hover=LIME,
        button_primary_text_color=INK,
        button_primary_text_color_hover=INK,
        button_primary_border_color=LIME,
        button_secondary_background_fill=PAPER,
        button_secondary_background_fill_hover=LAVENDER,
        button_secondary_text_color=INK,
        button_secondary_border_color=LINE,
        loader_color=PURPLE,
        slider_color=PURPLE,
        link_text_color=PURPLE,
        link_text_color_hover=INK,
        accordion_text_color=MUTED,
    )
    # Same values in light and dark mode, so the design never flips.
    values.update({f"{k}_dark": v for k, v in list(values.items())})
    return theme.set(**supported(theme.set, **values))


CSS = f"""
html {{ scroll-behavior: smooth; }}
body, gradio-app {{ background: {CREAM} !important; }}
.gradio-container {{ max-width: 1240px !important; margin: 0 auto !important;
                     padding: 0 clamp(12px, 3vw, 28px) !important; background: {CREAM} !important; }}
footer {{ opacity: .45; }}
.ck-html, .ck-html > div, .ck-html .prose {{ padding-left:0 !important; padding-right:0 !important; }}
.ck-html .prose {{ max-width: none !important; }}

/* ---------- navigation ---------- */
.ck-nav {{ display:flex; align-items:center; justify-content:space-between; padding: 22px 0; }}
.ck-logo {{ font-family:'Instrument Serif', Georgia, serif; font-size: 30px; letter-spacing:.22em;
           color:{INK}; text-decoration:none; }}
.ck-links {{ display:flex; align-items:center; gap: 28px; font-size: 14px; font-weight:500; }}
.ck-links a {{ color:{INK}; text-decoration:none; opacity:.8; }}
.ck-links a:hover {{ opacity:1; color:{PURPLE}; }}
.ck-pill {{ display:inline-flex; align-items:center; gap:8px; padding: 12px 22px; border-radius: 999px;
           font-weight:600; font-size:14px; text-decoration:none !important; transition: transform .15s ease, box-shadow .2s ease; }}
.ck-pill:hover {{ transform: translateY(-1px); }}
.ck-pill.dark {{ background:{INK}; color:{PAPER} !important; opacity:1 !important; }}
.ck-pill.lime {{ background:{LIME}; color:{INK} !important; box-shadow: 0 8px 24px rgba(160,200,30,.35); }}
.ck-pill.ghost {{ background:transparent; color:{INK} !important; border:1px solid {LINE}; }}

/* ---------- hero ---------- */
.ck-hero {{ display:grid; grid-template-columns: 1.05fr 1fr; gap: 48px; align-items:center;
           padding: 36px 0 64px; }}
.ck-chip {{ display:inline-flex; align-items:center; gap:8px; padding: 7px 14px; border-radius:999px;
           background:{PAPER}; border:1px solid {LINE}; font-size:12px; font-weight:600;
           letter-spacing:.12em; text-transform:uppercase; color:{MUTED}; }}
.ck-chip i {{ width:8px; height:8px; border-radius:50%; background:{PURPLE}; display:inline-block; }}
.ck-hero h1 {{ font-family:'Instrument Serif', Georgia, serif; font-weight:400; color:{INK};
              font-size: clamp(52px, 6.6vw, 92px); line-height:.98; letter-spacing:-.015em; margin: 22px 0 22px; }}
.ck-hero h1 em {{ color:{PURPLE}; font-style:italic; }}
.ck-hero .sub {{ font-size:17px; line-height:1.65; color:{MUTED}; max-width: 470px; margin:0 0 30px; }}
.ck-cta {{ display:flex; gap:12px; flex-wrap:wrap; }}
.ck-feats {{ display:flex; gap: 30px; margin-top: 42px; flex-wrap:wrap; }}
.ck-feat {{ display:flex; flex-direction:column; gap:10px; font-size:13px; font-weight:500; color:{INK}; max-width: 110px; }}
.ck-feat svg {{ width:22px; height:22px; stroke:{INK}; }}

.ck-visual {{ position:relative; min-height: 520px; }}
.ck-blob {{ position:absolute; inset: 20px 0 0 30px; border-radius: 48% 52% 44% 56% / 52% 44% 56% 48%;
           background: radial-gradient(circle at 30% 25%, {PINK}, transparent 60%),
                       radial-gradient(circle at 75% 70%, {LAVENDER}, transparent 62%),
                       linear-gradient(140deg, #FCE7F4, #EEE6FF); }}
.ck-arch {{ position:absolute; left: 18%; top: 4%; width: 58%; height: 86%; border-radius: 999px 999px 28px 28px;
           overflow:hidden; background:{PAPER}; box-shadow: 0 30px 60px rgba(60,30,90,.18); }}
.ck-arch img {{ width:100%; height:100%; object-fit:cover; object-position: top center; display:block; }}
.ck-arch.empty {{ display:flex; align-items:center; justify-content:center;
                 font-family:'Instrument Serif', Georgia, serif; font-size: 160px; color:{PURPLE};
                 background: linear-gradient(160deg, #FFFFFF, #F4EEFF); }}
.ck-sticker {{ position:absolute; right: 2%; top: 14%; width: 30%; padding: 10px; background:{PAPER};
              border-radius: 18px; transform: rotate(6deg); box-shadow: 0 18px 40px rgba(60,30,90,.18); }}
.ck-sticker img {{ width:100%; aspect-ratio: 3/4; object-fit:contain; display:block; border-radius: 10px; background:{SOFT}; }}
.ck-sticker span {{ display:block; text-align:center; font-size:11px; font-weight:600; letter-spacing:.1em;
                   text-transform:uppercase; color:{MUTED}; margin-top:8px; }}
.ck-note {{ position:absolute; left: 0; bottom: 6%; font-family:'Caveat', cursive; font-size: 30px;
           color:{INK}; transform: rotate(-6deg); line-height:1; }}
.ck-note b {{ color:{PURPLE}; font-weight:600; }}
.ck-badge {{ position:absolute; right: 6%; bottom: 10%; background:{LIME}; color:{INK}; border-radius: 999px;
            padding: 10px 16px; font-weight:700; font-size: 13px; box-shadow: 0 12px 28px rgba(160,200,30,.35);
            transform: rotate(-4deg); }}

/* ---------- try-on section ---------- */
.ck-sec-head {{ display:flex; align-items:end; justify-content:space-between; gap: 20px; flex-wrap:wrap;
               padding: 8px 0 22px; }}
.ck-sec-head h2 {{ font-family:'Instrument Serif', Georgia, serif; font-weight:400; font-size: clamp(38px, 4.4vw, 56px);
                  margin:0; color:{INK}; line-height:1; }}
.ck-sec-head h2 em {{ color:{PURPLE}; font-style:italic; }}
.ck-sec-head p {{ margin: 10px 0 0; color:{MUTED}; font-size:15px; }}
.ck-stepper {{ display:flex; align-items:center; gap: 10px; font-size: 13px; font-weight:600; color:{MUTED}; }}
.ck-stepper .s {{ display:flex; align-items:center; gap:8px; }}
.ck-stepper .n {{ width:28px; height:28px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
                 background:{PAPER}; border:1px solid {LINE}; color:{INK}; font-size:12px; }}
.ck-stepper .s.on .n {{ background:{INK}; color:{PAPER}; border-color:{INK}; }}
.ck-stepper .s.on {{ color:{INK}; }}
.ck-stepper .bar {{ width: 36px; height:1px; background:{LINE}; }}

.ck-card {{ background:{PAPER} !important; border:1px solid {LINE} !important; border-radius: 24px !important;
           padding: 20px !important; box-shadow: 0 1px 0 rgba(0,0,0,.02), 0 20px 50px rgba(70,40,90,.06) !important;
           gap: 14px !important; }}
.ck-card-head {{ display:flex; align-items:center; gap:12px; }}
.ck-card-head .n {{ width:34px; height:34px; border-radius:50%; background:{LAVENDER}; color:{PURPLE};
                   display:inline-flex; align-items:center; justify-content:center; font-weight:700; font-size:14px; }}
.ck-card-head .t {{ font-family:'Instrument Serif', Georgia, serif; font-size: 28px; color:{INK}; line-height:1; }}
.ck-card-head .h {{ display:block; font-size:12.5px; color:{MUTED}; margin-top:4px; }}
.ck-slot {{ font-size: 12px; font-weight:600; letter-spacing:.1em; text-transform:uppercase; color:{MUTED}; margin: 2px 0 -4px; }}
.ck-img {{ border-radius: 16px !important; overflow:hidden; }}
.ck-img img {{ object-fit: contain; }}
.ck-tabs, .ck-tabs > *, .ck-tabs fieldset {{ background: transparent !important; border: none !important; padding: 0 !important; box-shadow:none !important; }}
.ck-tabs .wrap {{ gap: 6px !important; background:{SOFT}; border:1px solid {LINE}; border-radius: 999px; padding: 5px; width: fit-content; }}
.ck-tabs label {{ border-radius: 999px !important; border:none !important; padding: 9px 18px !important;
                 font-weight:600 !important; font-size: 13.5px !important; box-shadow:none !important; }}
.ck-tabs input[type=radio] {{ display:none !important; }}
#ck-go {{ border-radius: 999px !important; min-height: 58px; font-size: 16px !important; font-weight: 800 !important;
         letter-spacing: .14em; box-shadow: 0 10px 26px rgba(160,200,30,.38); transition: transform .15s ease, box-shadow .2s ease; }}
#ck-go:hover {{ transform: translateY(-1px); box-shadow: 0 0 0 3px {LAVENDER}, 0 14px 30px rgba(122,60,240,.25); }}
.ck-status, .ck-status p {{ font-size: 13px !important; color:{MUTED} !important; text-align:center; min-height: 18px; }}
.ck-examples-label {{ font-size: 12px; font-weight:600; color:{MUTED}; letter-spacing:.08em; text-transform:uppercase; }}

.form:has(.ck-filters), .form:has(.ck-tabs) {{ background: transparent !important; border: none !important;
    box-shadow: none !important; }}

/* ---------- progress (on the result image) ---------- */
.progress-level-inner {{ font-size: 13px !important; font-weight: 600 !important; color:{INK} !important;
                        font-family:'Plus Jakarta Sans', sans-serif !important; margin-bottom: 14px !important; }}
.progress-bar-wrap {{ width: 72% !important; height: 6px !important; border:none !important;
                     background: {LAVENDER} !important; border-radius: 999px; overflow:hidden; }}
.progress-bar {{ background: linear-gradient(90deg, {PURPLE}, #C04DF0) !important; border-radius:999px;
                transition: transform .35s ease, width .35s ease !important; }}
.meta-text, .meta-text-center {{ font-size:12px !important; color:{MUTED} !important;
                                font-family:'Plus Jakarta Sans', sans-serif !important; }}
.eta-bar {{ background: rgba(122,60,240,.05) !important; }}

/* ---------- moodboard ---------- */
.ck-board-head {{ display:flex; align-items:end; justify-content:space-between; gap:16px; flex-wrap:wrap;
                 padding: 72px 0 6px; }}
.ck-board-head h2 {{ font-family:'Instrument Serif', Georgia, serif; font-weight:400; font-size: clamp(38px, 4.4vw, 56px);
                    margin:0; color:{INK}; line-height:1; }}
.ck-board-head h2 em {{ color:{PURPLE}; font-style:italic; }}
.ck-board-head p {{ margin: 10px 0 0; color:{MUTED}; font-size:15px; }}
.ck-count {{ font-size:13px; font-weight:600; color:{MUTED}; }}
.ck-filters, .ck-filters > *, .ck-filters fieldset, .ck-filters .wrap {{ background: transparent !important; border:none !important; padding:0 !important; box-shadow:none !important; }}
.ck-filters .wrap {{ gap: 8px !important; }}
.ck-filters label {{ border-radius: 999px !important; padding: 8px 16px !important; font-size: 13px !important;
                    font-weight:600 !important; border:1px solid {LINE} !important; background:{PAPER} !important; }}
.ck-filters label.selected {{ background:{INK} !important; color:{PAPER} !important; border-color:{INK} !important; }}
.ck-filters input[type=radio] {{ display:none !important; }}
.ck-board {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(min(320px, 100%), 1fr)); gap: 22px; }}
.ck-look {{ background:{PAPER}; border:1px solid {LINE}; border-radius: 22px; overflow:hidden; padding: 12px;
           box-shadow: 0 20px 50px rgba(70,40,90,.06); transition: transform .2s ease, box-shadow .2s ease; }}
.ck-look:hover {{ transform: translateY(-3px); box-shadow: 0 26px 60px rgba(70,40,90,.12); }}
.ck-pair {{ display:grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
.ck-shot {{ position:relative; background:{SOFT}; aspect-ratio: 3 / 4; overflow:hidden; border-radius: 14px; }}
.ck-shot img {{ width:100%; height:100%; object-fit:cover; object-position: top center; display:block; }}
.ck-tag {{ position:absolute; left:50%; bottom:10px; transform: translateX(-50%); padding:5px 12px; border-radius:999px;
          font-size:11.5px; font-weight:700; background:{PAPER}; color:{INK}; box-shadow: 0 4px 12px rgba(0,0,0,.08); }}
.ck-tag.after {{ background:{PURPLE}; color:{PAPER}; }}
.ck-look-foot {{ display:flex; align-items:center; justify-content:space-between; gap:10px; padding: 12px 4px 2px; }}
.ck-look-title {{ font-weight:700; font-size: 14px; color:{INK}; }}
.ck-look-title span {{ display:block; font-weight:500; font-size:12px; color:{MUTED}; margin-top:2px; }}
.ck-items {{ display:flex; gap:6px; }}
.ck-items img {{ width:38px; height:38px; object-fit:contain; background:{SOFT}; border:1px solid {LINE}; border-radius: 10px; }}
.ck-empty {{ border:1.5px dashed #DCD2C6; border-radius: 22px; padding: 56px 24px; text-align:center; color:{MUTED};
            background: linear-gradient(140deg, rgba(248,207,234,.25), rgba(227,216,255,.35)); }}
.ck-empty .big {{ font-family:'Instrument Serif', Georgia, serif; font-size: 32px; color:{INK}; margin-bottom: 8px; }}

/* ---------- how it works / footer ---------- */
.ck-how {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 80px 0 24px; }}
.ck-how > div {{ background:{PAPER}; border:1px solid {LINE}; border-radius: 22px; padding: 24px; }}
.ck-how h4 {{ margin: 0 0 10px; font-size: 15px; font-weight:700; color:{INK}; }}
.ck-how h4 i {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:8px; background:{PURPLE}; }}
.ck-how > div:nth-child(2) h4 i {{ background:#C04DF0; }}
.ck-how > div:nth-child(3) h4 i {{ background:#9BC21C; }}
.ck-how p {{ margin:0; color:{MUTED}; font-size: 14px; line-height: 1.65; }}
.ck-mock {{ background:#FFE9E9; color:#9A1C1C; border:1px solid #F5C2C2; border-radius: 14px; padding: 10px 14px;
           font-size: 13px; font-weight:600; margin: 4px 0 18px; }}

@media (max-width: 900px) {{
  .ck-hero {{ grid-template-columns: 1fr; gap: 28px; padding-bottom: 40px; }}
  .ck-visual {{ min-height: 440px; }}
  .ck-links a.hide-sm {{ display:none; }}
  .ck-how {{ grid-template-columns: 1fr; }}
  .ck-card {{ padding: 14px !important; }}
  .ck-sec-head .ck-stepper .bar {{ width: 14px; }}
}}
"""

ICON_UPLOAD = ('<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
               '<rect x="3" y="3" width="18" height="18" rx="4"/><circle cx="9" cy="9" r="2"/>'
               '<path d="M21 15l-5-5L5 21"/></svg>')
ICON_SHIRT = ('<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
              '<path d="M8 3l4 2 4-2 5 4-3 3-2-1v12H8V9L6 10 3 7z"/></svg>')
ICON_HEART = ('<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
              '<path d="M12 20s-7-4.4-9-9a4.7 4.7 0 0 1 9-3 4.7 4.7 0 0 1 9 3c-2 4.6-9 9-9 9z"/></svg>')


def header_html(hero_person=None, hero_garment=None):
    """Navigation and hero. Sample images are optional; without them a styled
    placeholder is shown, so the page never depends on files being present."""
    if hero_person:
        arch = f'<div class="ck-arch"><img src="{hero_person}" alt="Sample person"></div>'
    else:
        arch = '<div class="ck-arch empty">C</div>'
    sticker = (f'<div class="ck-sticker"><img src="{hero_garment}" alt="Sample garment">'
               f'<span>From the vendor</span></div>') if hero_garment else ""
    return f"""
<nav class="ck-nav">
  <a class="ck-logo" href="#">CLOAK</a>
  <div class="ck-links">
    <a href="#try" class="hide-sm">Try on</a>
    <a href="#board" class="hide-sm">Moodboard</a>
    <a href="#how" class="hide-sm">How it works</a>
    <a href="#try" class="ck-pill dark">Get started</a>
  </div>
</nav>
<section class="ck-hero">
  <div>
    <span class="ck-chip"><i></i>Virtual fitting room</span>
    <h1>Try outfits that feel like <em>you.</em></h1>
    <p class="sub">Upload a photo, add any outfit from a vendor's page, and see how it looks on you.
      Mix, match and compare before you buy.</p>
    <div class="ck-cta">
      <a href="#try" class="ck-pill lime">Try it now &rarr;</a>
      <a href="#board" class="ck-pill ghost">See the moodboard</a>
    </div>
    <div class="ck-feats">
      <div class="ck-feat">{ICON_UPLOAD}Upload your photo</div>
      <div class="ck-feat">{ICON_SHIRT}Try any outfit</div>
      <div class="ck-feat">{ICON_HEART}Save to moodboard</div>
    </div>
  </div>
  <div class="ck-visual">
    <div class="ck-blob"></div>
    {arch}
    {sticker}
    <div class="ck-note">Real looks<br>for <b>real you</b> &#x2197;</div>
    <div class="ck-badge">Open-source AI</div>
  </div>
</section>
"""


def section_head(active=1):
    steps = [("1", "Photo"), ("2", "Outfit"), ("3", "Your look")]
    parts = []
    for i, (n, t) in enumerate(steps, start=1):
        parts.append(f'<span class="s{" on" if i <= active else ""}"><span class="n">{n}</span>{t}</span>')
    stepper = '<span class="bar"></span>'.join(parts)
    return f"""
<div class="ck-sec-head" id="try">
  <div><h2>Try it <em>on</em></h2><p>Three steps. About half a minute per piece.</p></div>
  <div class="ck-stepper">{stepper}</div>
</div>"""


def card_head(n, title, hint):
    return (f'<div class="ck-card-head"><span class="n">{n}</span>'
            f'<div><span class="t">{title}</span><span class="h">{hint}</span></div></div>')


HOW = """
<section class="ck-how" id="how">
  <div><h4><i></i>What it shows</h4><p>How a style, colour and print could look on your body,
    and which tops and bottoms work together. Everything except the clothes stays exactly as in your photo.</p></div>
  <div><h4><i></i>What it can't promise</h4><p>Size and real fabric fit. Cut and length follow the outfit
    in your photo, and loose native styles and accessories are less reliable.</p></div>
  <div><h4><i></i>Your photos</h4><p>Processed in this session only and never stored. CLOAK is open
    source and built on the open-weight Leffa model (MIT). Non-commercial research prototype.</p></div>
</section>
"""


# ---- moodboard -----------------------------------------------------------

FILTERS = {"All": None, "Tops": "Top", "Bottoms": "Bottom", "Dresses": "Dress"}


def to_data_uri(img, max_side=640):
    img = img.copy()
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def board_head(count):
    return (f'<div class="ck-board-head" id="board"><div><h2>My <em>moodboard</em></h2>'
            f'<p>Every look you try, next to the photo you started from.</p></div>'
            f'<span class="ck-count">{count} look{"s" if count != 1 else ""} saved</span></div>')


def moodboard_html(looks, filter_name="All"):
    wanted = FILTERS.get(filter_name)
    shown = [lk for lk in looks if wanted is None or any(lbl == wanted for lbl, _ in lk["items"])]
    if not looks:
        return ('<div class="ck-empty"><div class="big">Your moodboard is waiting.</div>'
                'Cloak your first outfit and it lands here, before and after.</div>')
    if not shown:
        return (f'<div class="ck-empty"><div class="big">No {html.escape(filter_name.lower())} yet.</div>'
                'Try one on, or switch the filter back to All.</div>')
    cards = []
    for look in reversed(shown):  # newest first
        names = " + ".join(lbl for lbl, _ in look["items"])
        thumbs = "".join(f'<img src="{uri}" alt="{html.escape(lbl)}" title="{html.escape(lbl)}">'
                         for lbl, uri in look["items"])
        cards.append(f"""
<article class="ck-look">
  <div class="ck-pair">
    <div class="ck-shot"><img src="{look['before']}" alt="Before"><span class="ck-tag">Before</span></div>
    <div class="ck-shot"><img src="{look['after']}" alt="After"><span class="ck-tag after">After</span></div>
  </div>
  <div class="ck-look-foot">
    <div class="ck-look-title">Look {look['no']:02d}<span>{html.escape(names)} · {html.escape(look['time'])}</span></div>
    <div class="ck-items">{thumbs}</div>
  </div>
</article>""")
    return '<div class="ck-board">' + "".join(cards) + "</div>"
