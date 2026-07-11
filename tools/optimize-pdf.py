#!/usr/bin/env python3
"""Optimize a PDF for the docs hub: downsample oversized images to screen
resolution, keep text and vector art untouched, strip private app data.

InDesign/press exports carry print-resolution images (often 200-6000px,
20MB+ each); on a web docs hub they should be ~2400px JPEGs. Text stays
vector — only raster images are touched, so the deck stays sharp.

Usage:
    python3 optimize-pdf.py input.pdf output.pdf [--max-edge 2400] [--quality 82]

Requires: pip install pikepdf pillow  (no Homebrew or Ghostscript needed)
Verify after: page count unchanged, spot-render pages, check size.
"""
import argparse
import io
import sys

import pikepdf
from PIL import Image, ImageChops, ImageCms

SRGB = ImageCms.createProfile("sRGB")

# Fallback press profile for /DeviceCMYK images that embed no ICC profile —
# PIL's naive CMYK->RGB formula oversaturates badly. First match wins.
CMYK_PROFILE_PATHS = [
    "/Library/Application Support/Adobe/Color/Profiles/Recommended/USWebCoatedSWOP.icc",
    "/System/Library/ColorSync/Profiles/Generic CMYK Profile.icc",
]


def _fallback_cmyk_profile():
    import os
    for p in CMYK_PROFILE_PATHS:
        if os.path.exists(p):
            return ImageCms.ImageCmsProfile(p)
    return None


FALLBACK_CMYK = _fallback_cmyk_profile()

Image.MAX_IMAGE_PIXELS = None  # press-res images exceed PIL's default bomb guard


def optimize(src, dst, max_edge=2400, quality=82, min_bytes=300_000):
    pdf = pikepdf.open(src)
    n_pages = len(pdf.pages)
    done, skipped, saved = 0, 0, 0

    for obj in pdf.objects:
        try:
            if not isinstance(obj, pikepdf.Stream):
                continue
            if obj.get("/Subtype") != pikepdf.Name.Image:
                continue
            raw = len(obj.read_raw_bytes())
            w, h = int(obj.get("/Width", 0)), int(obj.get("/Height", 0))
            if raw < min_bytes and max(w, h) <= max_edge:
                skipped += 1
                continue
            cs = str(obj.get("/ColorSpace", ""))
            if "/Indexed" in cs or "/Separation" in cs:
                # palette and spot-color images don't survive a JPEG
                # round-trip faithfully — leave them exactly as exported
                # (soft masks are fine: /SMask is a separate stream, untouched)
                skipped += 1
                continue
            pimg = pikepdf.PdfImage(obj)
            pil = pimg.as_pil_image()
            if pil.mode not in ("RGB", "L", "CMYK"):
                skipped += 1
                continue
            if pil.mode == "CMYK":
                # Adobe (InDesign) CMYK JPEGs store inverted ink values and
                # PIL does not flip them back — invert before converting.
                pil = ImageChops.invert(pil)
                # Convert through the image's own ICC press profile when it
                # has one; a naive .convert("RGB") oversaturates.
                icc = None
                try:
                    icc = pimg.icc
                except Exception:
                    pass
                if icc is None:
                    icc = FALLBACK_CMYK
                if icc is not None:
                    pil = ImageCms.profileToProfile(pil, icc, SRGB, outputMode="RGB")
                else:
                    pil = pil.convert("RGB")
            elif pil.mode not in ("RGB", "L"):
                pil = pil.convert("RGB")
            if max(pil.size) > max_edge:
                pil.thumbnail((max_edge, max_edge), Image.LANCZOS)
            buf = io.BytesIO()
            pil.save(buf, format="JPEG", quality=quality, optimize=True)
            if buf.tell() >= raw:  # no win — leave the original alone
                skipped += 1
                continue
            obj.write(
                buf.getvalue(),
                filter=pikepdf.Name.DCTDecode,
            )
            obj.Width, obj.Height = pil.size
            obj.ColorSpace = (
                pikepdf.Name.DeviceRGB if pil.mode == "RGB" else pikepdf.Name.DeviceGray
            )
            obj.BitsPerComponent = 8
            for k in ("/DecodeParms", "/Decode", "/Intent"):
                if k in obj:
                    del obj[k]
            saved += raw - buf.tell()
            done += 1
        except Exception as e:  # an undecodable image is left as-is, never dropped
            skipped += 1
            print(f"  skipped one image ({type(e).__name__}: {e})", file=sys.stderr)

    for page in pdf.pages:  # private InDesign data and embedded thumbnails
        for k in ("/PieceInfo", "/Thumb"):
            if k in page:
                del page[k]

    pdf.save(dst, recompress_flate=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    out_pages = len(pikepdf.open(dst).pages)
    assert out_pages == n_pages, f"page count changed: {n_pages} -> {out_pages}"
    print(f"pages {n_pages} | images recompressed {done}, left alone {skipped} | saved {saved/1e6:.1f} MB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--max-edge", type=int, default=2400)
    ap.add_argument("--quality", type=int, default=82)
    args = ap.parse_args()
    optimize(args.src, args.dst, args.max_edge, args.quality)
