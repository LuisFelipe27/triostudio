"""
TrioStudio - Halftone DTF processing (v2: color + auto background removal).

Pure-Pillow halftone renderer optimised for Direct-To-Film (DTF) output:

* **Automatic background removal**: when the source has no real alpha
  channel (fully opaque), we infer a soft mask by measuring how similar
  each pixel is to the dominant corner colour. Dark or bright flat
  backgrounds disappear cleanly.
* **Color preservation**: each dot is painted with the RGB sampled from
  the original image at the cell centre, so the blue aura stays blue,
  skin stays skin, etc. A "single-ink" override is available.
* **Transparency is sacred**: the final alpha is multiplied with the
  inferred mask so the DTF white-ink layer breathes correctly.
* **Curve pre-pass**: autocontrast + gentle contrast boost on luminance
  so blacks are deep and dot coverage is well defined.
* Dots whose area is proportional to local ink coverage, rotated by the
  user-selected screen angle (classic 45Â° default). Two geometries:
  round dots (`circle`) or parallel ruling (`lines`).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from io import BytesIO
from typing import Optional, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

# Pillow >= 9.1 moved resampling constants under Image.Resampling.
try:
    _LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # pragma: no cover - older Pillow
    _LANCZOS = Image.LANCZOS

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CM_PER_INCH = 2.54
PREVIEW_MAX_WIDTH = 900     # px - keeps the live preview snappy
MIN_DOT_PX = 2.0            # below this dots collapse to noise

# Auto background removal thresholds (in 0..255 colour distance).
BG_TOL_LOW = 28.0            # below this -> fully background (alpha=0)
BG_TOL_HIGH = 70.0           # above this -> fully subject    (alpha=255)
MIN_COVERAGE = 0.06          # below this no dot is drawn
MIN_ALPHA = 40               # below this the cell is skipped entirely


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    """Parse `#rrggbb` / `#rgb` -> (r, g, b)."""
    if not value:
        return (0, 0, 0)
    v = value.strip().lstrip('#')
    if len(v) == 3:
        v = ''.join(c * 2 for c in v)
    if len(v) < 6:
        return (0, 0, 0)
    try:
        return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    except ValueError:
        return (0, 0, 0)


def cm_to_px(cm: float, dpi: int) -> int:
    return max(1, int(round(cm * dpi / CM_PER_INCH)))


@dataclass
class HalftoneParams:
    knockout_enable: bool = True        # transparent background (DTF)
    knockout_color: str = '#000000'     # single-ink override colour
    use_single_ink: bool = False        # if True, paint every dot with knockout_color
    bg_color: str = '#FFFFFF'
    dot_shape: str = 'circle'
    dot_size: float = 10.0
    dot_angle: float = 45.0
    print_width_cm: float = 25.0
    export_dpi: int = 300
    contrast_boost: float = 1.2

    @classmethod
    def from_model(cls, job) -> 'HalftoneParams':
        return cls(
            knockout_enable=job.knockout_enable,
            knockout_color=job.knockout_color,
            # Default: preserve source colours. Power users can flip this
            # from the "Advanced" panel if we ever expose it.
            use_single_ink=False,
            bg_color=job.bg_color,
            dot_shape=job.dot_shape,
            dot_size=float(job.dot_size),
            dot_angle=float(job.dot_angle),
            print_width_cm=float(job.print_width_cm),
            export_dpi=int(job.export_dpi),
            contrast_boost=float(job.contrast_boost),
        )


# ---------------------------------------------------------------------------
# Background detection
# ---------------------------------------------------------------------------

def _corner_bg_color(rgb: Image.Image) -> Tuple[int, int, int]:
    """Estimate the dominant background colour from the four corners."""
    w, h = rgb.size
    sample = 6
    patches = [
        rgb.crop((0, 0, sample, sample)),
        rgb.crop((w - sample, 0, w, sample)),
        rgb.crop((0, h - sample, sample, h)),
        rgb.crop((w - sample, h - sample, w, h)),
    ]
    r = g = b = 0
    for p in patches:
        px = p.resize((1, 1), _LANCZOS).getpixel((0, 0))
        r += px[0]
        g += px[1]
        b += px[2]
    n = len(patches)
    return (r // n, g // n, b // n)


def _build_auto_alpha(rgb: Image.Image, bg: Tuple[int, int, int]) -> Image.Image:
    """Return an L-mode mask: 0 = background, 255 = subject.

    Uses per-channel absolute difference from the background colour with
    a soft threshold so edges stay smooth.
    """
    br, bg_g, bb = bg
    r, g, b = rgb.split()
    dr = ImageChops.difference(r, Image.new('L', rgb.size, br))
    dg = ImageChops.difference(g, Image.new('L', rgb.size, bg_g))
    db = ImageChops.difference(b, Image.new('L', rgb.size, bb))
    diff = ImageChops.lighter(ImageChops.lighter(dr, dg), db)

    # Soft threshold LUT: BG_TOL_LOW..BG_TOL_HIGH -> 0..255
    span = max(1.0, BG_TOL_HIGH - BG_TOL_LOW)
    lut = []
    for i in range(256):
        v = (i - BG_TOL_LOW) / span
        if v < 0:
            v = 0.0
        elif v > 1:
            v = 1.0
        lut.append(int(round(v * 255)))
    mask = diff.point(lut)
    # Morphological opening: erosion kills 1-px sparkles, dilation
    # restores the true silhouette. Then a tiny blur for soft edges.
    mask = mask.filter(ImageFilter.MinFilter(3))
    mask = mask.filter(ImageFilter.MaxFilter(3))
    mask = mask.filter(ImageFilter.GaussianBlur(radius=0.8))
    return mask


def _resolve_alpha(rgba: Image.Image) -> Tuple[Image.Image, Tuple[int, int, int]]:
    """Return (mask, bg_color). Uses the source alpha when it already
    carries information, otherwise auto-detects the background."""
    alpha = rgba.split()[-1]
    rgb = rgba.convert('RGB')
    extrema = alpha.getextrema()  # (min, max)
    if extrema and extrema[0] < 245:
        # Source has real transparency - corner sampling is pointless, use
        # the average of fully-transparent pixels as a neutral bg reference.
        return alpha, (0, 0, 0)
    bg = _corner_bg_color(rgb)
    return _build_auto_alpha(rgb, bg), bg


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def _prepare_input(img: Image.Image, contrast_boost: float):
    """Return (rgb, gray, alpha, bg_color) all aligned, with curves applied."""
    rgba = img.convert('RGBA')
    alpha, bg_color = _resolve_alpha(rgba)

    rgb = rgba.convert('RGB')

    gray = rgb.convert('L')
    gray = ImageOps.autocontrast(gray, cutoff=2)
    if contrast_boost and abs(contrast_boost - 1.0) > 1e-3:
        gray = ImageEnhance.Contrast(gray).enhance(contrast_boost)

    # Mild saturation boost so colours stay punchy after screening.
    rgb = ImageEnhance.Color(rgb).enhance(1.15)

    return rgb, gray, alpha, bg_color


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------

def _build_canvas(size, params: HalftoneParams) -> Image.Image:
    if params.knockout_enable:
        return Image.new('RGBA', size, (0, 0, 0, 0))
    bg = hex_to_rgb(params.bg_color)
    return Image.new('RGBA', size, bg + (255,))


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------

def render_halftone(
    src: Image.Image,
    params: HalftoneParams,
    dot_size_override: Optional[float] = None,
) -> Image.Image:
    rgb, gray, alpha, bg_color = _prepare_input(src, params.contrast_boost)
    w, h = rgb.size

    cell = float(dot_size_override if dot_size_override is not None else params.dot_size)
    cell = max(MIN_DOT_PX, cell)

    canvas = _build_canvas((w, h), params)
    draw = ImageDraw.Draw(canvas)

    ink_override = hex_to_rgb(params.knockout_color) if params.use_single_ink else None
    angle_rad = math.radians(params.dot_angle)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

    gray_px = gray.load()
    rgb_px = rgb.load()
    alpha_px = alpha.load()

    # Luminance of the background decides the "ink direction":
    #   dark bg (e.g. black neon poster) -> brighter = more ink
    #   light bg (e.g. white paper)       -> darker  = more ink
    bg_lum = (bg_color[0] + bg_color[1] + bg_color[2]) / 3.0
    light_on_dark = bg_lum < 128
    inv_bg = max(1.0, 255.0 - bg_lum)
    inv_light = max(1.0, bg_lum)

    diag = int(math.hypot(w, h)) + int(cell) * 2
    half_cell = cell / 2.0
    cx_img, cy_img = w / 2.0, h / 2.0

    u = -diag
    while u < diag:
        v = -diag
        while v < diag:
            uu = u + half_cell
            vv = v + half_cell
            cx = uu * cos_a - vv * sin_a + cx_img
            cy = uu * sin_a + vv * cos_a + cy_img

            ix, iy = int(cx), int(cy)
            if 0 <= ix < w and 0 <= iy < h:
                a = alpha_px[ix, iy]
                if a >= MIN_ALPHA:
                    luminance = gray_px[ix, iy]
                    if light_on_dark:
                        # Brighter than bg means more ink.
                        signal = (luminance - bg_lum) / inv_bg
                    else:
                        signal = (bg_lum - luminance) / inv_light
                    if signal < 0:
                        signal = 0.0
                    elif signal > 1:
                        signal = 1.0
                    # Modulate by the soft mask so fringes fade gracefully.
                    coverage = signal * (a / 255.0)
                    if coverage >= MIN_COVERAGE:
                        if ink_override is not None:
                            rr, gg, bb = ink_override
                        else:
                            px = rgb_px[ix, iy]
                            rr, gg, bb = px[0], px[1], px[2]
                        ink = (rr, gg, bb, 255)
                        if params.dot_shape == 'lines':
                            line_len = cell * 1.05
                            line_w = max(1, int(round(coverage * cell)))
                            dx = cos_a * line_len / 2.0
                            dy = sin_a * line_len / 2.0
                            draw.line(
                                [(cx - dx, cy - dy), (cx + dx, cy + dy)],
                                fill=ink, width=line_w,
                            )
                        else:
                            r = cell * math.sqrt(coverage / math.pi)
                            draw.ellipse(
                                [cx - r, cy - r, cx + r, cy + r],
                                fill=ink,
                            )
            v += cell
        u += cell

    # Final alpha: respect the auto/source mask so the DTF background
    # stays fully transparent no matter what.
    out_alpha = canvas.split()[-1]
    final_alpha = ImageChops.multiply(out_alpha, alpha)
    canvas.putalpha(final_alpha)
    return canvas


def render_mask(src: Image.Image) -> Image.Image:
    """Return the subject mask as an RGBA image for the 'Máscara' tab."""
    rgba = src.convert('RGBA')
    alpha, _ = _resolve_alpha(rgba)
    # Compose white-on-transparent so the user sees the silhouette.
    out = Image.new('RGBA', rgba.size, (0, 0, 0, 0))
    white = Image.new('RGBA', rgba.size, (255, 255, 255, 255))
    out.paste(white, (0, 0), alpha)
    return out


# ---------------------------------------------------------------------------
# Pipelines used by Celery tasks
# ---------------------------------------------------------------------------

def render_preview(src: Image.Image, params: HalftoneParams) -> Image.Image:
    img = src
    if img.width > PREVIEW_MAX_WIDTH:
        scale = PREVIEW_MAX_WIDTH / img.width
        new_size = (PREVIEW_MAX_WIDTH, max(1, int(img.height * scale)))
        img = img.resize(new_size, _LANCZOS)
        scaled_dot = max(MIN_DOT_PX, params.dot_size * scale)
    else:
        scaled_dot = params.dot_size
    return render_halftone(img, params, dot_size_override=scaled_dot)


def render_export(src: Image.Image, params: HalftoneParams) -> Image.Image:
    target_w = cm_to_px(params.print_width_cm, params.export_dpi)
    if target_w != src.width:
        scale = target_w / src.width
        target_h = max(1, int(round(src.height * scale)))
        src = src.resize((target_w, target_h), _LANCZOS)
    return render_halftone(src, params)


def image_to_png_bytes(img: Image.Image, dpi: Optional[int] = None) -> bytes:
    buf = BytesIO()
    save_kwargs = {'format': 'PNG', 'optimize': True}
    if dpi:
        save_kwargs['dpi'] = (dpi, dpi)
    img.save(buf, **save_kwargs)
    return buf.getvalue()
