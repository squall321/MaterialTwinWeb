#!/usr/bin/env python
# 데이터시트 PDF → 물성 텍스트 추출. 텍스트 레이어 우선, 없으면 OCR(이미지 전용 PDF 대응).
#
# 사용:
#   extract_datasheet.py <pdf|url> [--ocr] [--dpi 300] [--lang eng] [--grep "tensile|CTE"]
#
# 배경: 업체 데이터시트는 Illustrator로 만든 이미지 전용 PDF가 흔해 pdftotext가 빈 결과를
# 낸다(예: Kuraray FCCL 브로슈어). 그 경우 렌더 후 OCR해야 물성표를 얻을 수 있다.
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

UA = "MaterialTwinWeb/1.0 (mailto:squall321@gmail.com)"
# 물성표에서 흔한 키워드 — 관련 페이지만 추려 보여준다.
DEFAULT_KEYS = (r"tensile|modulus|elongation|absorption|dielectric|dissipation|CTE|expansion|"
                r"conductivity|density|melting|glass transition|Tg|Td|peel|flexural|"
                r"breakdown|resistivity|haze|transmission|refractive|ppm|GHz|MPa|GPa")


def fetch(src: str) -> Path:
    """URL이면 내려받아 임시 파일로. 실패 시 트레이스백 대신 원인을 한 줄로 알린다."""
    if not re.match(r"^https?://", src):
        return Path(src)
    dst = Path(tempfile.mkdtemp()) / "datasheet.pdf"
    # 일부 업체 사이트는 브라우저 UA·Accept 헤더가 없으면 403을 준다.
    req = urllib.request.Request(src, headers={
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
        "Accept": "application/pdf,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r, open(dst, "wb") as f:
            f.write(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"✗ HTTP {e.code} {e.reason} — {src}")
    except Exception as e:
        raise SystemExit(f"✗ 다운로드 실패({type(e).__name__}: {e}) — {src}")
    if dst.stat().st_size < 1024:
        raise SystemExit(f"✗ 받은 파일이 너무 작음({dst.stat().st_size}B) — URL이 PDF가 아닐 수 있음")
    return dst


def text_layer(pdf: Path) -> str:
    try:
        out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                             capture_output=True, text=True, timeout=120)
        return out.stdout or ""
    except Exception:
        return ""


def ocr(pdf: Path, dpi: int, lang: str) -> str:
    """이미지 전용 PDF를 렌더 후 OCR. pdf2image+pytesseract 필요."""
    import pytesseract
    from pdf2image import convert_from_path

    pages = convert_from_path(str(pdf), dpi=dpi)
    chunks = []
    for i, im in enumerate(pages, 1):
        chunks.append(f"\n===== [OCR p{i}] =====\n" + pytesseract.image_to_string(im, lang=lang))
    return "".join(chunks)


def main() -> int:
    ap = argparse.ArgumentParser(description="데이터시트 PDF에서 물성 텍스트 추출(텍스트→OCR 폴백)")
    ap.add_argument("src", help="PDF 경로 또는 URL")
    ap.add_argument("--ocr", action="store_true", help="텍스트 레이어가 있어도 강제로 OCR")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--lang", default="eng", help="tesseract 언어(eng, kor, eng+kor)")
    ap.add_argument("--grep", default=DEFAULT_KEYS, help="표시할 줄의 정규식(기본: 물성 키워드)")
    ap.add_argument("--all", action="store_true", help="필터 없이 전체 출력")
    a = ap.parse_args()

    pdf = fetch(a.src)
    if not pdf.exists():
        print(f"✗ 파일 없음: {pdf}", file=sys.stderr)
        return 2

    txt = "" if a.ocr else text_layer(pdf)
    used = "텍스트 레이어"
    if len(txt.strip()) < 200:                    # 사실상 비었으면 이미지 PDF로 판단.
        print("· 텍스트 레이어가 비어 있음 → OCR 수행", file=sys.stderr)
        txt = ocr(pdf, a.dpi, a.lang)
        used = f"OCR({a.dpi}dpi, {a.lang})"
    print(f"· 추출 방식: {used} / {len(txt)}자", file=sys.stderr)

    if a.all:
        print(txt)
        return 0
    pat = re.compile(a.grep, re.I)
    for line in txt.splitlines():
        s = " ".join(line.split())
        if s and pat.search(s):
            print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
