#!/usr/bin/env bash
# Doosan 제품 페이지 15장을 코퍼스에 떨군다 — 값의 근거가 거기 있는데 `local_path` 는 전제품 TDS 를 가리켰다.
# 전제품 TDS v9(55등급)에 **행 자체가 없는** 15등급이라(브리프 584 의 S3b · 56차 RC 가 두 문서를 다 열었다)
# TDS 를 아무리 열어도 그 값을 못 찾는다 — 계보가 끊긴 322행이다.
set -euo pipefail
DEST=/data/paper_patent_corpus/standards_appnotes/pcb
BASE=https://www.doosanelectromaterials.com/en/product/Copper_Clad_Laminate
for slug in DS-7409DYN DS-7409DYN2 DS-7409DYQ DS-7409HG DS-7409HG_KNF DS-9000 \
            DSF-900HT DSflex-600DI DSflex-600G DSflex-600H DSflex-600HF DSflex-600LUF \
            DSflex-900L DSflex-900U DSflex-900UM; do
  out="$DEST/Doosan_CCL_${slug}_ProductPage_en_2026-09-01.html"
  code=$(curl -sSL -A "Mozilla/5.0" --retry 2 -o "$out" -w "%{http_code}" "$BASE/$slug")
  printf '%s  %s  %s bytes\n' "$code" "$slug" "$(stat -c%s "$out")"
done
