#!/usr/bin/env bash
# MaterialTwin → Google Drive 푸시: 데이터 번들(이식가능) + SIF(버전 보존).
#
# 데이터는 raw DB dump가 아니라 병합 가능한 번들로 내보낸다(sync-from-drive가 병합 임포트).
# SIF는 sha256 + latest 포인터 + retain N — 기존 버전을 덮어쓰지 않는다.
#
# 사용:
#   bash sync-to-drive.sh                 # 번들 + SIF
#   bash sync-to-drive.sh --dry-run       # 업로드 없이 시뮬레이션
#   bash sync-to-drive.sh --no-sif        # 번들만
#   bash sync-to-drive.sh --no-data       # SIF만
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

DRY=0; WITH_DATA=1; WITH_SIF=1
for a in "$@"; do case "$a" in
  --dry-run) DRY=1 ;; --no-sif) WITH_SIF=0 ;; --no-data) WITH_DATA=0 ;;
  -h|--help) sed -n '1,14p' "$0"; exit 0 ;;
  *) echo "[ERROR] unknown arg: $a" >&2; exit 2 ;;
esac; done

require_rclone
run() { if [[ $DRY -eq 1 ]]; then echo "  (dry) $*"; else "$@"; fi; }

STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT

# ── 1) 데이터 번들 ───────────────────────────────────────────────────────────
if [[ $WITH_DATA -eq 1 ]]; then
  BNAME="$(bundle_name)"; BPATH="$STAGE/$BNAME"
  echo "→ 데이터 번들 생성: $BNAME"
  MATERIALTWIN_DATA_DIR="$PROJ_DATA_DIR" MATERIALTWIN_DATABASE_URL="$PROJ_DB_URL" \
    "$PROJ_PY" -m app.sync export "$BPATH"
  ( cd "$STAGE" && sha256sum "$BNAME" > "${BNAME}.sha256" )
  echo "→ 업로드: $DRIVE_DATA/"
  run rclone copy "$BPATH"           "$DRIVE_DATA/"
  run rclone copy "${BPATH}.sha256"  "$DRIVE_DATA/"
  [[ $DRY -eq 0 ]] && prune_remote "$DRIVE_DATA" "$(bundle_glob)" "$PROJ_RETAIN"
fi

# ── 2) SIF (버전 보존) ───────────────────────────────────────────────────────
if [[ $WITH_SIF -eq 1 ]]; then
  if [[ ! -f "$PROJ_SIF_PATH" ]]; then
    echo "→ SIF 없음($PROJ_SIF_PATH) — SIF 스테이지 skip."
  else
    SHA="$(file_sha256 "$PROJ_SIF_PATH")"
    SNAME="${PROJ_PREFIX}-$(ts_now)-${SHA:0:12}.sif"
    # 이미 같은 sha가 Drive에 있으면 재업로드 skip(중복 방지).
    if rclone lsf "$DRIVE_SIF" --include "*-${SHA:0:12}.sif" 2>/dev/null | grep -q .; then
      echo "→ SIF 동일 sha 이미 존재 — 업로드 skip."
    else
      echo "→ SIF 업로드: $SNAME"
      cp "$PROJ_SIF_PATH" "$STAGE/$SNAME"
      echo "$SHA  $SNAME" > "$STAGE/${SNAME}.sha256"
      run rclone copy "$STAGE/$SNAME"          "$DRIVE_SIF/"
      run rclone copy "$STAGE/${SNAME}.sha256" "$DRIVE_SIF/"
      # latest 포인터(내용이 아닌 파일명만 기록 — 기존 SIF는 보존).
      echo "{\"latest\":\"$SNAME\",\"sha256\":\"$SHA\",\"ts\":\"$(ts_now)\"}" > "$STAGE/LATEST.json"
      run rclone copy "$STAGE/LATEST.json" "$DRIVE_SIF/"
      [[ $DRY -eq 0 ]] && prune_remote "$DRIVE_SIF" "${PROJ_PREFIX}-*.sif" "$PROJ_RETAIN"
    fi
  fi
fi

echo "✓ sync-to-drive 완료$([[ $DRY -eq 1 ]] && echo ' (dry-run)')."
