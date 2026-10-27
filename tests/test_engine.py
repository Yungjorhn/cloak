import pytest
from PIL import Image

from cloak.engine import HEIGHT, WIDTH, TryOnEngine, crop_back, fit_to_canvas, load_image


def test_transparent_png_goes_on_white_not_black():
    img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))  # fully transparent
    out = load_image(img)
    assert out.mode == "RGB"
    assert out.getpixel((5, 5)) == (255, 255, 255)


def test_phone_photo_rotation_is_applied():
    img = Image.new("RGB", (40, 20))
    exif = img.getexif()
    exif[0x0112] = 6  # "rotate 90° clockwise", common on phone photos
    img = Image.open(_roundtrip(img, exif))
    assert load_image(img).size == (20, 40)


def _roundtrip(img, exif):
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    buf.seek(0)
    return buf


@pytest.mark.parametrize("size", [(600, 1200), (1200, 600), (768, 1024), (300, 300)])
def test_fit_then_crop_restores_framing(size):
    img = Image.new("RGB", size, (10, 120, 30))
    canvas, fit = fit_to_canvas(img)
    assert canvas.size == (WIDTH, HEIGHT)
    back = crop_back(canvas, fit)
    # same aspect ratio as the original (within rounding)
    assert abs(back.width / back.height - size[0] / size[1]) < 0.02
    assert back.getpixel((back.width // 2, back.height // 2)) == (10, 120, 30)


@pytest.fixture(scope="module")
def engine():
    return TryOnEngine()  # mock mode


def person():
    return Image.new("RGB", (500, 900), (120, 80, 60))


def garment():
    return Image.new("RGB", (400, 400), (200, 30, 30))


def test_top_and_bottom_runs_bottom_first(engine):
    out, log = engine.dress_outfit(person(), top=garment(), bottom=garment())
    assert [line.split(":")[0] for line in log] == ["bottom", "top"]
    assert out.size[0] / out.size[1] == pytest.approx(500 / 900, abs=0.02)


def test_dress_replaces_top_and_bottom(engine):
    _, log = engine.dress_outfit(person(), top=garment(), bottom=garment(), dress=garment())
    assert [line.split(":")[0] for line in log] == ["dress/gown"]


def test_needs_a_person(engine):
    with pytest.raises(ValueError, match="photo of yourself"):
        engine.dress_outfit(None, top=garment())


def test_needs_a_garment(engine):
    with pytest.raises(ValueError, match="at least one clothing item"):
        engine.dress_outfit(person())


def test_moodboard_shows_before_and_after_for_each_look():
    from cloak.ui_style import moodboard_html, to_data_uri
    uri = to_data_uri(person())
    looks = [{"no": i, "time": "10:00", "before": uri, "after": uri,
              "items": [("Top", to_data_uri(garment(), 120))]} for i in (1, 2)]
    page = moodboard_html(looks)
    assert page.count('class="ck-card"') == 2
    assert page.count(">Before<") == 2 and page.count(">After<") == 2
    assert page.index("Look 02") < page.index("Look 01")  # newest first
    assert "Nothing pinned yet" in moodboard_html([])
