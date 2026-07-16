#!/usr/bin/env bash
# Google Drive → MaterialTwin 풀: 데이터 번들을 받아 **병합 임포트**(운영 추가분 보존).
#
# 핵심: raw restore가 아니라 union merge — 대상 DB의 기존 재료·시험을 절대 삭제하지 않고,
# 번들에만 있는 것만 추가한다(안정키·content-hash로 중복 skip).
# SIF는 latest를 받아 대상 경로에 저장(기존은 .bak로 보존, 덮어쓰기 아님).
#
# 사용:
#   bash sync-from-drive.sh                # 최신 번들 병합 + SIF latest 받기
#   bash sync-from-drive.sh --dry-run      # 어떤 파일을 받을지만
#   bash sync-from-drive.sh --no-sif       # 데이터만
#   bash sync-from-drive.sh --sif-dest PATH
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

DRY=0; WITH_SIF=1; SIF_DEST="$PROJ_SIF_PATH"
while [[ $# -gt 0 ]]; do case "$1" in
  --dry-run) DRY=1 ;; --no-sif) WITH_SIF=0 ;;
  --sif-dest) SIF_DEST="${2:?}"; shift ;;
  -h|--help) sed -n '1,16p' "$0"; exit 0 ;;
  *) echo "[ERROR] unknown arg: $1" >&2; exit 2 ;;
esac; shift; done

require_rclone
STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT

# ── 1) 최신 데이터 번들 → 병합 임포트 ────────────────────────────────────────
LATEST=$(rclone lsf "$DRIVE_DATA" --include "$(bundle_glob)" 2>/dev/null | sort | tail -1)
if [[ -z "$LATEST" ]]; then
  echo "→ Drive에 데이터 번들 없음 — 데이터 스테이지 skip."
else
  echo "→ 최신 번들: $LATEST"
  if [[ $DRY -eq 1 ]]; then
    echo "  (dry) 다운로드·병합 안 함."
  else
    rclone copy "$DRIVE_DATA/$LATEST"          "$STAGE/"
    rclone copy "$DRIVE_DATA/${LATEST}.sha256" "$STAGE/" 2>/dev/null || true
    if [[ -f "$STAGE/${LATEST}.sha256" ]]; then
      ( cd "$STAGE" && sha256sum -c "${LATEST}.sha256" ) || { echo "[ERROR] sha256 불일치." >&2; exit 1; }
    fi
    echo "→ 병합 임포트(기존 데이터 보존):"
    MATERIALTWIN_DATA_DIR="$PROJ_DATA_DIR" MATERIALTWIN_DATABASE_URL="$PROJ_DB_URL" \
      "$PROJ_PY" -m app.sync import "$STAGE/$LATEST"
  fi
fi

# ── 2) SIF latest (덮어쓰기 없이 보존) ───────────────────────────────────────
if [[ $WITH_SIF -eq 1 ]]; then
  SLATEST=$(rclone lsf "$DRIVE_SIF" --include "${PROJ_PREFIX}-*.sif" 2>/dev/null | sort | tail -1)
  if [[ -z "$SLATEST" ]]; then
    echo "→ Drive에 SIF 없음 — SIF 스테이지 skip."
  elif [[ $DRY -eq 1 ]]; then
    echo "  (dry) SIF 다운로드 안 함(최신: $SLATEST → $SIF_DEST)."
  else
    echo "→ SIF 받기: $SLATEST → $SIF_DEST"
    rclone copy "$DRIVE_SIF/$SLATEST" "$STAGE/"
    rclone copy "$DRIVE_SIF/${SLATEST}.sha256" "$STAGE/" 2>/dev/null || true
    if [[ -f "$STAGE/${SLATEST}.sha256" ]]; then
      ( cd "$STAGE" && sha256sum -c "${SLATEST}.sha256" ) || { echo "[ERROR] SIF sha256 불일치." >&2; exit 1; }
    fi
    mkdir -p "$(dirname "$SIF_DEST")"
    # 기존 SIF는 .bak로 보존(덮어쓰기 아님) 후 교체.
    [[ -f "$SIF_DEST" ]] && cp -f "$SIF_DEST" "${SIF_DEST}.bak"
    mv -f "$STAGE/$SLATEST" "$SIF_DEST"
    echo "  (기존 SIF는 ${SIF_DEST}.bak 로 보존)"
  fi
fi

echo "✓ sync-from-drive 완료$([[ $DRY -eq 1 ]] && echo ' (dry-run)')."
