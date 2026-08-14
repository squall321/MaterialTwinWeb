#!/usr/bin/env bash
# snowball_papers_structured.tar.gz(7,347편)를 코퍼스에 편입하고 색인을 다시 만든다.
set -euo pipefail

INC=/data/paper_patent_corpus/_incoming
STRUCT=/data/paper_patent_corpus/structured
TAR="$INC/snowball_papers_structured.tar.gz"
CAT=/home/koopark/claude/MaterialTwinWeb/backend/scripts/catalog

[[ -f "$TAR" ]] || { echo "[ERROR] $TAR 이 없다"; exit 1; }
[[ -f "$TAR.partial" ]] && { echo "[ERROR] 아직 받는 중이다"; exit 1; }

echo "== 1. 최상위 디렉터리 확인 (덮어쓰기 사고 방지)"
# **압축을 풀기 전에 최상위 이름을 본다.** 기존 갈래를 덮으면 되돌릴 수 없다.
TOP=$(tar -tzf "$TAR" | head -400 | awk -F/ '{print $1}' | sort -u)
echo "$TOP"
if [[ $(echo "$TOP" | wc -l) -ne 1 ]]; then
  echo "[WARN] 최상위가 하나가 아니다 — 손으로 확인해라"
fi
for d in $TOP; do
  if [[ -e "$STRUCT/$d" ]]; then
    echo "[ERROR] $STRUCT/$d 가 이미 있다. 덮어쓰지 않는다."; exit 1
  fi
done

echo "== 2. 압축 해제"
mkdir -p "$STRUCT"
tar -xzf "$TAR" -C "$STRUCT"

echo "== 3. 편수 확인"
for d in $TOP; do
  n_md=$(find "$STRUCT/$d" -name '*.md' -not -path '*/tables/*' | wc -l)
  n_dir=$(find "$STRUCT/$d" -mindepth 2 -maxdepth 2 -type d | wc -l)
  echo "  $d — md ${n_md}편 · 논문 폴더 ${n_dir}개"
done

echo "== 4. FTS5 색인 재생성 (전체 재구축, 약 8분)"
cd "$CAT"
python3 corpus_index.py build

echo "== 5. 물성표 스캔 재생성 (약 8분)"
python3 corpus_index.py scan

echo "== 6. 결과"
python3 - <<'PY'
import sqlite3
c = sqlite3.connect("/data/paper_patent_corpus/_index/corpus_fts.db")
n = c.execute("select count(*) from doc").fetchone()[0]
print(f"  고유 논문 {n}편")
try:
    m = c.execute("select count(distinct doc_id) from ptab").fetchone()[0]
    print(f"  물성표 보유 논문 {m}편")
except sqlite3.OperationalError:
    print("  (ptab 없음 — scan 을 확인해라)")
for dom, k in c.execute("select domain, count(*) from doc group by 1 order by 2 desc"):
    print(f"    {k:6d}  {dom}")
PY
echo "== 완료. 아카이브는 남겨 둔다 — 지우려면 손으로 지워라."
