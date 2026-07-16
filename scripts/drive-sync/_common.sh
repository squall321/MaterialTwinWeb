#!/usr/bin/env bash
# MaterialTwin Drive-Sync 공용 헬퍼 — PROJECT.conf 로드·rclone 추상화·번들/SIF 경로 규약.
# 호출자가 `set -euo pipefail` 후 source 한다.

DS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$DS_DIR/PROJECT.conf" ]]; then
  echo "[ERROR] $DS_DIR/PROJECT.conf 없음." >&2; exit 1
fi
# shellcheck source=/dev/null
source "$DS_DIR/PROJECT.conf"

: "${PROJ_DRIVE_REMOTE:=ApptainerImages}"
: "${PROJ_DRIVE_FOLDER:=MaterialTwin}"
: "${PROJ_RETAIN:=5}"

DRIVE_DATA="${PROJ_DRIVE_REMOTE}:${PROJ_DRIVE_FOLDER}/data-bundles"
DRIVE_SIF="${PROJ_DRIVE_REMOTE}:${PROJ_DRIVE_FOLDER}/sif"

require_rclone() {
  command -v rclone >/dev/null 2>&1 || { echo "[ERROR] rclone 미설치." >&2; exit 1; }
  rclone listremotes 2>/dev/null | grep -q "^${PROJ_DRIVE_REMOTE}:" \
    || { echo "[ERROR] rclone 리모트 '${PROJ_DRIVE_REMOTE}:' 미설정." >&2; exit 1; }
}

ts_now() { date -u +"%Y%m%d-%H%M%SZ"; }
bundle_name() { echo "${PROJ_PREFIX}-bundle-$(ts_now).tar.gz"; }
bundle_glob() { echo "${PROJ_PREFIX}-bundle-*.tar.gz"; }

file_sha256() { sha256sum "$1" | awk '{print $1}'; }

# Drive에서 접미사 glob에 맞는 파일들을 TS정렬 후 오래된 것부터 (총-보존) 개 삭제.
prune_remote() {
  # $1 = drive path, $2 = glob, $3 = retain
  local path="$1" glob="$2" retain="$3"
  local files; files=$(rclone lsf "$path" --include "$glob" 2>/dev/null | sort)
  local n; n=$(echo "$files" | grep -c . || true)
  if (( n > retain )); then
    echo "$files" | head -n $((n - retain)) | while read -r f; do
      [[ -z "$f" ]] && continue
      echo "  prune: $f"
      rclone deletefile "$path/$f" 2>/dev/null || true
      rclone deletefile "$path/${f}.sha256" 2>/dev/null || true
    done
  fi
}
