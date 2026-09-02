#!/usr/bin/env bash
# Doosan CCL 제품 페이지 55장을 코퍼스에 떨군다 — 57차 SD 가 받은 15장(TDS v9 밖 등급) 말고
# **TDS v9 안 등급**의 페이지는 아무도 안 열었다(§601 — 벤더 문서는 등급마다 층이 다르다).
# 없는 슬러그에 500 을 주는 사이트라 200 한 장이 곧 실재 확인이다.
set -uo pipefail
DEST=/data/paper_patent_corpus/standards_appnotes/pcb
BASE=https://www.doosanelectromaterials.com/en/product/Copper_Clad_Laminate
STAMP=2026-09-02
for slug in "$@"; do
  out="$DEST/Doosan_CCL_${slug}_ProductPage_en_${STAMP}.html"
  code=$(curl -sSL -A "Mozilla/5.0" --retry 2 --max-time 60 -o "$out" -w "%{http_code}|%{content_type}|%{size_download}" "$BASE/$slug")
  printf '%s  %s\n' "$code" "$slug"
  [ "${code%%|*}" = "200" ] || rm -f "$out"
  sleep 1
done
