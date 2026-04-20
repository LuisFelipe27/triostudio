"""
TrioStudio - Halftone DTF processing.

Pure-Pillow halftone renderer optimised for Direct-To-Film (DTF) output:

* Respects the source alpha channel: transparent pixels stay transparent
  in the result, so the white-ink layer "breathes" on the garment.
* Applies an automatic curve / contrast pre-pass so blacks become deep
  and dot edges remain crisp.
* Generates dots whose area is proportional to local ink coverage,
  rotated by the user-selected screen angle (classic 45° default).
* Two screen geometries: round dots (`circle`) or parallel ruling
  (`lines`) for more textured looks.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from io import BytesIO
from typing import Optional, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageOps

# Pillow >= 9.1 moved resampling constants under Image.Resampling.
try:
    _LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # pragma: no cover - older Pillow
    _LANCZOS = Image.LANCZOS

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CM_PER_INCH = 2.54
PREVIEW_MAX_WIDTH = 900  # px - keeps the live preview snappy
MIN_DOT_PX = 2.0         # below this dots collapse to noise


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
    knockout_enable: bool = True
    knockout_color: str = '#000000'
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
            bg_color=job.bg_color,
            dot_shape=job.dot_shape,
            dot_size=float(job.dot_size),
            dot_angle=float(job.dot_angle),
            print_width_cm=float(job.print_width_cm),
            export_dpi=int(job.export_dpi),
            contrast_boost=float(job.contrast_boost),
        )


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------

def _prepare_input(img: Image.Image, contrast_boost: float):
    """Return (rgba, gray, alpha) with autocontrast / curve applied."""
    rgba = img.convert('RGBA')
    alpha = rgba.split()[-1]

    # Drop alpha for tonal work, then re-apply mask at the end.
    rgb = rgba.convert('RGB')
    gray = rgb.convert('L')

    # Auto curves: stretch tonal range so blacks stay punchy.
    gray = ImageOps.autocontrast(gray, cutoff=2)
    if contrast_boost and abs(contrast_boost - 1.0) > 1e-3:
        gray = ImageEnhance.Contrast(gray).enhance(contrast_boost)

    return rgba, gray, alpha


def _build_canvas(size, params: HalftoneParams) -> Image.Image:
    if params.knockout_enable:
        # DTF best practice: keep background fully transparent.
        return Image.new('RGBA', size, (0, 0, 0, 0))
    bg = hex_to_rgb(params.bg_color)
    return Image.new('RGBA', size, bg + (255,))


def render_halftone(
    src: Image.Image,
    params: HalftoneParams,
    dot_size_override: Optional[float] = None,
) -> Image.Image:
    """Render a halftone version of `src` using `params`.

    `dot_size_override` lets the preview pipeline reuse the same routine
    while scaling the cell size to the preview resolution.
    """
    rgba, gray, alpha = _prepare_input(src, params.contrast_boost)
    w, h = rgba.size

    cell = float(dot_size_override if dot_size_override is not None else params.dot_size)
    cell = max(MIN_DOT_PX, cell)

    canvas = _build_canvas((w, h), params)
    draw = ImageDraw.Draw(canvas)

    ink_rgb = hex_to_rgb(params.knockout_color)
    angle_rad = math.radians(params.dot_angle)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

    gray_px = gray.load()
    alpha_px = alpha.load()

    # Iterate over a rotated grid that fully covers the image.
    diag = int(math.hypot(w, h)) + int(cell) * 2
    half_cell = cell / 2.0
    cx_img, cy_img = w / 2.0, h / 2.0

    u = -diag
    while u < diag:
        v = -diag
        while v < diag:
            # Cell centre mapped from rotated (u, v) into image (x, y).
            uu = u + half_cell
            vv = v + half_cell
            cx = uu * cos_a - vv * sin_a + cx_img
            cy = uu * sin_a + vv * cos_a + cy_img

            ix, iy = int(cx), int(cy)
            if 0 <= ix < w and 0 <= iy < h:
                a = alpha_px[ix, iy]
                if a > 8:  # respect source transparency
                    luminance = gray_px[ix, iy]
                    coverage = (255 - luminance) / 255.0
                    if coverage > 0.02:
                        ink = ink_rgb + (int(a),)
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
                            # area = pi r^2 = coverage * cell^2
                            r = cell * math.sqrt(coverage / math.pi)
                            draw.ellipse(
                                [cx - r, cy - r, cx + r, cy + r],
                                fill=ink,
                            )
            v += cell
        u += cell

    # Final alpha mask: never paint where the source was transparent.
    out_alpha = canvas.split()[-1]
    final_alpha = ImageChops.multiply(out_alpha, alpha)
    canvas.putalpha(final_alpha)
    return canvas


# ---------------------------------------------------------------------------
# Pipelines used by Celery tasks
# ---------------------------------------------------------------------------

def render_preview(src: Image.Image, params: HalftoneParams) -> Image.Image:
    """Fast preview for the studio canvas (HTMX live update)."""
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
    """Print-ready halftone at the requested DPI / print width."""
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
