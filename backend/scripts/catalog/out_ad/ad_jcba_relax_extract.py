#!/usr/bin/env python3
# JCBA 応力緩和特性 그림 PDF 에서 곡선 좌표를 벡터 경로로 직접 뽑는다(래스터 디지타이즈가 아니다).
#
# 왜 — `bjr004xxx.pdf` 는 Excel 4.0 이 그린 **벡터** 그림이라 픽셀을 세지 않아도 된다.
#      데이터점이 마커 도형의 중심 좌표로 스트림 안에 그대로 들어 있고, 축은 격자선이 잡아 준다.
#      그래도 인쇄된 숫자가 아니라 그림에서 읽은 값이므로 `method="digitized"` 다(브리프 447·448).
#
# 계열 동정은 **범례를 읽어서** 한다 — 색을 우리가 지어내지 않는다.
#   범례 한 항목 = (선 견본) + (마커 견본) + (Shift_JIS 텍스트) 순서로 그려진다.
# 사용:  ad_jcba_relax_extract.py <pdf> [<pdf> ...]
from __future__ import annotations

import json
import re
import sys
import zlib

NUM = re.compile(r"^-?\d*\.?\d+$")


def content(path: str) -> str:
    data = open(path, "rb").read()
    out = []
    for s in re.findall(rb"stream\r?\n(.*?)endstream", data, re.S):
        try:
            out.append(zlib.decompress(s).decode("latin-1"))
        except Exception:
            pass
    return "".join(out)


OPS = ["BDC", "BMC", "SCN", "scn", "EMC", "B*", "b*", "f*", "W*", "T*", "BI", "BT", "BX",
       "cm", "cs", "CS", "d0", "d1", "Do", "DP", "EI", "ET", "EX", "gs", "ID", "MP",
       "re", "RG", "rg", "ri", "sc", "SC", "sh", "Tc", "Td", "TD", "Tf", "Tj", "TJ",
       "TL", "Tm", "Tr", "Ts", "Tw", "Tz", "b", "B", "c", "d", "f", "F", "g", "G",
       "h", "i", "j", "J", "k", "K", "l", "m", "M", "n", "q", "Q", "s", "S", "v",
       "w", "W", "y", "'", '"']
NUMTOK = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)")


def lex(cs: str):
    """PDF 콘텐츠 스트림은 연산자끼리 공백 없이 붙는다(`TjET` · `re f121.2`).
    `\\S+` 로 자르면 연산자를 통째로 잃는다 — 알려진 연산자 집합에서 최장일치로 읽어야 한다."""
    i, n = 0, len(cs)
    while i < n:
        ch = cs[i]
        if ch in " \t\r\n\f\x00":
            i += 1; continue
        if ch == "%":
            j = cs.find("\n", i); i = n if j < 0 else j + 1; continue
        if ch == "<":
            if cs[i + 1:i + 2] == "<":
                yield ("dict", "<<"); i += 2; continue
            j = cs.index(">", i); yield ("hex", cs[i:j + 1]); i = j + 1; continue
        if ch == ">":
            yield ("dict", ">>"); i += 2 if cs[i + 1:i + 2] == ">" else 1; continue
        if ch == "(":
            j, depth = i + 1, 1
            while j < n and depth:
                if cs[j] == "\\":
                    j += 2; continue
                depth += (cs[j] == "(") - (cs[j] == ")")
                j += 1
            yield ("str", cs[i:j]); i = j; continue
        if ch == "/":
            j = i + 1
            while j < n and cs[j] not in " \t\r\n/[]<>(){}%":
                j += 1
            yield ("name", cs[i:j]); i = j; continue
        if ch in "[]{}":
            yield ("delim", ch); i += 1; continue
        m = NUMTOK.match(cs, i)
        if m and (ch.isdigit() or ch in "+-." ):
            yield ("num", float(m.group())); i = m.end(); continue
        for op in OPS:
            if cs.startswith(op, i):
                yield ("op", op); i += len(op); break
        else:
            i += 1


def parse(cs: str):
    """(op, 인자, 그래픽상태) 목록을 그린 순서대로 돌려준다."""
    st = {"RG": (0, 0, 0), "rg": (1, 1, 1), "w": 0.24}
    gs, stack, cur, ops = [], [], [], []
    for kind, tok in lex(cs):
        if kind != "op":
            stack.append(tok); continue
        t = tok
        try:
            if t == "m":
                cur = [(stack[-2], stack[-1])]
            elif t in ("l", "v", "y", "c"):
                cur.append((stack[-2], stack[-1]))
            elif t == "re":
                cur = [("RE",) + tuple(stack[-4:])]
            elif t in ("S", "s", "f", "F", "f*", "B", "B*", "b", "b*"):
                if cur:
                    ops.append({"op": t, "pts": cur, **{k: st[k] for k in ("RG", "rg", "w")}})
                cur = []
            elif t == "n":
                cur = []
            elif t == "RG":
                st["RG"] = tuple(stack[-3:])
            elif t == "rg":
                st["rg"] = tuple(stack[-3:])
            elif t == "w":
                st["w"] = stack[-1]
            elif t == "q":
                gs.append(dict(st))
            elif t == "Q":
                if gs:
                    st = gs.pop()
            elif t == "Tj":
                h = stack[-1]
                if isinstance(h, str) and h.startswith("<"):
                    txt = bytes.fromhex(h[1:-1]).decode("cp932", "replace")
                else:
                    txt = str(h)
                ops.append({"op": "Tj", "text": txt, "tm": st.get("Tm")})
            elif t == "Tm":
                st["Tm"] = tuple(stack[-6:])
        except IndexError:
            pass
        stack = []
    return ops


def rect(o):
    pts = o.get("pts")
    return pts[0][1:] if pts and pts[0][0] == "RE" else None


def centre(o):
    """도형의 **경계상자 중심**을 쓴다. `c` 로 그린 원은 시작점이 한 번 더 들어가므로
    좌표 평균을 쓰면 x 가 한쪽으로 밀린다(원 하나에서 0.6 pt = 시간축 1% 편향)."""
    pts = o.get("pts")
    if not pts:
        return (float("nan"), float("nan"))
    if pts[0][0] == "RE":
        x, y, w, h = pts[0][1:]
        return (x + w / 2.0, y + h / 2.0)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0)


def extract(path: str):
    ops = parse(content(path))
    # ── 차트 판: 흰 배경 사각형 중 폭 350pt 이상인 것
    plots = []
    for i, o in enumerate(ops):
        r = rect(o)
        if r and o["op"] == "f" and 350 < r[2] < 450 and 150 < r[3] < 250 and o["rg"] == (1, 1, 1):
            plots.append((i, r))
    charts = []
    for n, (i0, r) in enumerate(plots):
        i1 = plots[n + 1][0] if n + 1 < len(plots) else len(ops)
        charts.append({"span": (i0, i1), "rect": r})
    out = []
    for ch in charts:
        i0, i1 = ch["span"]
        seg = ops[i0:i1]
        x0, y0, w, h = ch["rect"]
        x1, y1 = x0 + w, y0 + h
        # ── y 축: 전폭 가로 격자선 → 0..100 %
        gy = sorted({round(o["pts"][0][1], 2) for o in seg
                     if o["op"] == "S" and o["w"] < 0.5 and len(o["pts"]) == 2
                     and abs(o["pts"][0][1] - o["pts"][1][1]) < 0.01
                     and abs(o["pts"][0][0] - x0) < 1.5 and abs(o["pts"][1][0] - x1) < 1.5})
        assert len(gy) == 10, (path, "가로 격자선이 10개가 아니다", gy)
        ppp = (gy[-1] - y0) / 100.0                     # 1% 당 pt
        # ── x 축: 로그. 십년 폭은 (오른끝-왼끝)/3
        dec = (x1 - x0) / 3.0
        # ── 제목(図 4.xx  <등급>材の応力緩和特性(<T>℃))
        title = ""
        for o in seg:
            if o["op"] == "Tj" and "応力緩和特性" in o["text"]:
                title = o["text"]
        # ── 범례: 흰 채움 + 검정 테두리 사각형('b')
        legs = [o for o in seg if o["op"] == "b" and rect(o) and rect(o)[2] > 80 and rect(o)[3] > 50]
        assert legs, (path, "범례 상자를 못 찾았다")
        lx, ly, lw, lh = rect(legs[0])
        li = seg.index(legs[0])
        # 범례 항목: 마커 견본 다음의 Tj 텍스트가 그 항목의 이름이다
        series, pend = [], None
        for o in seg[li + 1:]:
            if o["op"] == "Tj" and pend is not None:
                series.append({"name": o["text"].strip(), "key": pend})
                pend = None
            elif o["op"] in ("b", "f") and lx <= centre(o)[0] <= lx + lw and ly <= centre(o)[1] <= ly + lh:
                r = rect(o)
                shape = "bar" if (r and r[2] < 1.0) else ("blk" if r else "sym")
                if shape != "blk":
                    pend = (o["rg"], shape)
            if len(series) == 6:
                break
        assert len(series) == 6, (path, "범례 항목이 6개가 아니다", series)
        # ── 데이터 마커: 범례 상자 밖, 판 안. **그린 순서**가 계열 순서다.
        #    색+모양만으로 가르면 안 된다 — 한 그림 안에서 두 계열이 같은 색을 쓰는 판이 있다
        #    (C7701 120 ℃ 판은 `耐力値x0.8 T.D.` 와 `250N/mm2 T.D.` 가 둘 다 파란 막대다).
        marks = []
        for o in seg:
            if o["op"] != "b":
                continue
            cx, cy = centre(o)
            if lx - 3 <= cx <= lx + lw + 3 and ly - 3 <= cy <= ly + lh + 3:
                continue
            if not (x0 - 4 <= cx <= x1 + 4 and y0 - 8 <= cy <= y1 + 4):
                continue
            r = rect(o)
            marks.append(((o["rg"], "bar" if (r and r[2] < 1.0) else "sym"), cx, cy))
        runs = []
        for key, cx, cy in marks:
            if runs and runs[-1]["key"] == key and cx > runs[-1]["pts"][-1][0] + 1e-9:
                runs[-1]["pts"].append((cx, cy))
            else:
                runs.append({"key": key, "pts": [(cx, cy)]})
        assert len(runs) == 6, (path, title, "마커 계열이 6개가 아니다", [(r["key"], len(r["pts"])) for r in runs])
        got = []
        for s_, run in zip(series, runs):
            assert s_["key"] == run["key"], (path, title, "범례와 데이터의 색·모양이 어긋난다", s_, run["key"])
            assert len(run["pts"]) == 8, (path, title, s_["name"], "점이 8개가 아니다", len(run["pts"]))
            got.append({
                "series": s_["name"],
                "points": [{"hours": round(10 ** ((cx - x0) / dec), 4),
                            "relaxation_pct": round((cy - y0) / ppp, 4)} for cx, cy in run["pts"]],
            })
        out.append({"title": title, "plot_rect": ch["rect"], "pt_per_pct": round(ppp, 4),
                    "decade_pt": round(dec, 3), "series": got})
    return out


if __name__ == "__main__":
    res = {}
    for p in sys.argv[1:]:
        res[p] = extract(p)
    print(json.dumps(res, ensure_ascii=False, indent=1))
