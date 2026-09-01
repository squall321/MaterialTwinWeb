# pdftocairo SVG 의 <path> 를 matrix 변환까지 적용해 페이지 좌표(pt, y 아래로 증가)로 편다 — 곡선 판독의 입구다.
import re

PAT = re.compile(r'<path\s+style="([^"]*)"\s+d="([^"]*)"(?:\s+transform="matrix\(([^)]*)\)")?\s*/>')


def paths(svg_text):
    out = []
    for style, d, m in PAT.findall(svg_text):
        if m:
            a, b, c, dd, e, f = [float(x) for x in m.split(',')]
        else:
            a, b, c, dd, e, f = 1, 0, 0, 1, 0, 0
        P = []
        for xs, ys in re.findall(r'([-\d.]+)\s+([-\d.]+)', d):
            x, y = float(xs), float(ys)
            P.append((a * x + c * y + e, b * x + dd * y + f))
        col = re.search(r'stroke:rgb\(([\d.]+)%,([\d.]+)%,([\d.]+)%\)', style)
        out.append({"style": style, "pts": P, "n": len(P),
                    "rgb": tuple(round(float(v)) for v in col.groups()) if col else None,
                    "w": float(re.search(r'stroke-width:([\d.]+)', style).group(1))
                    if 'stroke-width' in style else None,
                    "dash": re.search(r'stroke-dasharray:([^;]*)', style).group(1)
                    if 'stroke-dasharray' in style else None})
    return out
