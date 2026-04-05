#!/usr/bin/env python3
"""
메인 히어로용 이미지 처리: 좌측 검은 여백 제거 → 우측 오브젝트 추출
- Version A: 어두운 배경을 투명 처리한 PNG (RGBA)
- Version B: 동일 영역을 최소 검은 패딩으로 크롭한 PNG

사용:
  python3 process_main_hero_image.py /path/to/메인롤링시안.png
  python3 process_main_hero_image.py --demo   # 합성 소스로 파이프라인만 검증

출력 (기본):
  nexas/assets/img/hero/tai-hero-object.png
  nexas/assets/img/hero/tai-hero-object-crop.png
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

# nexas/tools → nexas 루트
NEXAS_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_OUT_A = os.path.join(NEXAS_ROOT, "assets", "img", "hero", "tai-hero-object.png")
DEFAULT_OUT_B = os.path.join(NEXAS_ROOT, "assets", "img", "hero", "tai-hero-object-crop.png")
DEFAULT_SOURCE = os.path.join(NEXAS_ROOT, "assets", "img", "hero", "source", "메인롤링시안.png")


def _ensure_rgba(im: Image.Image) -> Image.Image:
    if im.mode == "RGBA":
        return im
    return im.convert("RGBA")


def _luma(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0].astype(np.float32), rgb[..., 1].astype(np.float32), rgb[..., 2].astype(np.float32)
    return 0.299 * r + 0.587 * g + 0.114 * b


def find_content_columns(gray: np.ndarray, dark_thr: float = 28.0, min_run_ratio: float = 0.08) -> tuple[int, int]:
    """좌측 넓은 검은 영역을 건너뛰고, 실제 콘텐츠가 있는 열 구간을 추정."""
    h, w = gray.shape
    col_mean = gray.mean(axis=0)
    col_max = gray.max(axis=0)
    active = (col_mean > dark_thr) | (col_max > dark_thr + 35)
    if not np.any(active):
        return 0, w
    idx = np.where(active)[0]
    x0, x1 = int(idx[0]), int(idx[-1]) + 1
    # 좌측이 거의 순수 검정인 구간 스킵: 처음부터 스캔해 '의미 있는' 열 시작 찾기
    for x in range(0, w - 4):
        window = gray[:, x : x + 5]
        if window.mean() > dark_thr + 5 or window.max() > dark_thr + 40:
            x0 = min(x0, x)
            break
    # 우측 끝 트림
    for x in range(w - 1, max(x0, 0), -1):
        col = gray[:, max(0, x - 2) : x + 1]
        if col.mean() > dark_thr or col.max() > dark_thr + 30:
            x1 = x + 1
            break
    x1 = min(w, max(x1, x0 + int(w * min_run_ratio)))
    return x0, x1


def bbox_non_dark(rgb: np.ndarray, dark_thr: float = 22.0) -> tuple[int, int, int, int]:
    """남은 이미지에서 비-어두운 픽셀 바운딩 박스."""
    g = _luma(rgb)
    mask = g > dark_thr
    if not np.any(mask):
        return 0, rgb.shape[0], 0, rgb.shape[1]
    rows = np.where(np.any(mask, axis=1))[0]
    cols = np.where(np.any(mask, axis=0))[0]
    return int(rows[0]), int(rows[-1]) + 1, int(cols[0]), int(cols[-1]) + 1


def apply_transparency(rgba: Image.Image, dark_thr: int = 18) -> Image.Image:
    arr = np.array(rgba)
    rgb = arr[..., :3].astype(np.float32)
    a = arr[..., 3].astype(np.float32)
    lum = _luma(rgb)
    mx = np.max(rgb, axis=-1)
    mn = np.min(rgb, axis=-1)
    sat = np.where(mx < 1e-3, 0, (mx - mn) / np.maximum(mx, 1e-3))
    is_bg = (lum < dark_thr) & (sat < 0.12)
    new_a = np.where(is_bg, 0, a)
    out = np.dstack([rgb[..., 0], rgb[..., 1], rgb[..., 2], new_a]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def make_demo_source(path: str, size: tuple[int, int] = (1400, 720)) -> None:
    w, h = size
    im = Image.new("RGB", (w, h), (5, 6, 10))
    dr = ImageDraw.Draw(im)
    # 좌측 58% 검정 바
    dr.rectangle([0, 0, int(w * 0.58), h], fill=(4, 5, 8))
    # 우측 가상 '오브젝트'
    cx, cy = int(w * 0.78), h // 2
    dr.ellipse([cx - 180, cy - 200, cx + 180, cy + 200], fill=(30, 90, 200))
    dr.rounded_rectangle([cx - 220, cy - 120, cx + 240, cy + 160], radius=24, fill=(220, 140, 40))
    dr.rectangle([cx - 100, cy + 40, cx + 120, cy + 180], fill=(180, 185, 195))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "PNG")
    print("Wrote demo source:", path)


def process(input_path: str, out_a: str, out_b: str, max_side: int = 1100) -> None:
    im = Image.open(input_path)
    im = _ensure_rgba(im)
    rgb = np.array(im.convert("RGB"))
    gray = _luma(rgb)

    x0, x1 = find_content_columns(gray)
    cropped_rgb = rgb[:, x0:x1, :]
    y0, y1, x0b, x1b = bbox_non_dark(cropped_rgb)
    tight = cropped_rgb[y0:y1, x0b:x1b, :]
    tight_img = Image.fromarray(tight, "RGB")

    # 히어로용 최대 변 길이 (비율 유지)
    tw, th = tight_img.size
    scale = min(1.0, max_side / max(tw, th))
    if scale < 1.0:
        nw, nh = int(tw * scale), int(th * scale)
        tight_img = tight_img.resize((nw, nh), Image.Resampling.LANCZOS)

    # --- A: 배경 제거(어두운 영역 투명) PNG
    rgba_a = _ensure_rgba(tight_img)
    rgba_a = apply_transparency(rgba_a, dark_thr=20)
    os.makedirs(os.path.dirname(out_a), exist_ok=True)
    rgba_a.save(out_a, "PNG")
    print("Wrote", out_a, rgba_a.size)

    # --- B: 동일 크롭 RGB (검은 배경은 bbox로 이미 최소화, 알파 없음)
    os.makedirs(os.path.dirname(out_b), exist_ok=True)
    tight_img.save(out_b, "PNG")
    print("Wrote", out_b, tight_img.size)


def main() -> None:
    ap = argparse.ArgumentParser(description="Hero image: crop right object, export A/B PNGs")
    ap.add_argument("input", nargs="?", default=None, help="Source PNG path")
    ap.add_argument("--out-a", default=DEFAULT_OUT_A)
    ap.add_argument("--out-b", default=DEFAULT_OUT_B)
    ap.add_argument("--demo", action="store_true", help="Write synthetic source + process")
    ap.add_argument("--max-side", type=int, default=1100)
    args = ap.parse_args()

    src = args.input or DEFAULT_SOURCE
    if args.demo:
        make_demo_source(src)
    if not os.path.isfile(src):
        print("Source not found:", src, file=sys.stderr)
        print("Place 메인롤링시안.png at:", DEFAULT_SOURCE, file=sys.stderr)
        print("Or: python3 process_main_hero_image.py /path/to/your.png", file=sys.stderr)
        sys.exit(1)

    process(src, args.out_a, args.out_b, max_side=args.max_side)


if __name__ == "__main__":
    main()
