from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image


def _median_channel(samples: list[tuple[int, int, int, int]], idx: int) -> int:
    vals = sorted(s[idx] for s in samples)
    return vals[len(vals) // 2]


def _make_bg_transparent(
    src: Path,
    dst: Path,
    *,
    threshold: int = 45,
    feather_alpha: float = 0.85,
) -> None:
    im = Image.open(src).convert("RGBA")
    px = im.load()
    w, h = im.size

    corner_samples = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    bg = tuple(_median_channel(corner_samples, i) for i in range(4))  # type: ignore[assignment]

    thr2 = threshold * threshold

    def close_to_bg(rgba: tuple[int, int, int, int]) -> bool:
        r, g, b, a = rgba
        br, bgc, bb, _ = bg
        dr = r - br
        dg = g - bgc
        db = b - bb
        return (dr * dr + dg * dg + db * db) <= thr2 and a > 0

    mask = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))

    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h:
            continue
        if mask[y][x]:
            continue
        if not close_to_bg(px[x, y]):
            continue
        mask[y][x] = True
        q.append((x + 1, y))
        q.append((x - 1, y))
        q.append((x, y + 1))
        q.append((x, y - 1))

    for y in range(h):
        for x in range(w):
            if mask[y][x]:
                r, g, b, _a = px[x, y]
                px[x, y] = (r, g, b, 0)

    # 1px feather at the edge to avoid harsh halos
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if mask[y][x]:
                continue
            if any(mask[yy][xx] for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1)):
                r, g, b, a = px[x, y]
                br, bgc, bb, _ = bg
                dr = r - br
                dg = g - bgc
                db = b - bb
                d2 = dr * dr + dg * dg + db * db
                if d2 <= (thr2 * 2):
                    px[x, y] = (r, g, b, int(a * feather_alpha))

    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "PNG")


def main() -> int:
    p = argparse.ArgumentParser(description="Make near-white edge background transparent (flood fill).")
    p.add_argument("src", type=Path)
    p.add_argument("dst", type=Path)
    p.add_argument("--threshold", type=int, default=45)
    args = p.parse_args()

    _make_bg_transparent(args.src, args.dst, threshold=args.threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

