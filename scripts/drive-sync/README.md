<!-- MaterialTwin Drive-Sync 키트 사용법 — 데이터 번들·SIF를 Google Drive로 손실 없이 주고받기. -->
# MaterialTwin Drive-Sync

Google Drive(rclone `ApptainerImages:` 리모트)를 통해 **데이터**와 **SIF**를 주고받는 키트. SignalForge drive-sync 패턴과 호환.

핵심 원칙 — **손실 없는 병합**. 데이터는 raw DB 덮어쓰기가 아니라 이식 가능한 번들로 내보내고, 받는 쪽은 **union 병합**한다: 대상 DB의 기존 재료·시험을 절대 삭제하지 않고, 번들에만 있는 것만 추가한다(안정키·content-hash로 중복 skip). 운영에서 추가된 데이터는 번들에 없어도 보존된다.

## 구성
| 파일 | 역할 |
|---|---|
| `PROJECT.conf` | 리모트·폴더·보존개수·백엔드/데이터 경로·SIF 경로 |
| `_common.sh` | rclone 추상화·번들명 규칙·retain prune·sha256 |
| `sync-to-drive.sh` | 번들 export + SIF(버전 보존) 푸시 |
| `sync-from-drive.sh` | 최신 번들 **병합 임포트** + SIF latest 받기 |

## 사용
```bash
cd scripts/drive-sync

# 푸시 (이 호스트 → Drive)
bash sync-to-drive.sh              # 데이터 번들 + SIF
bash sync-to-drive.sh --dry-run    # 시뮬레이션(번들은 실제 생성, 업로드만 skip)
bash sync-to-drive.sh --no-sif     # 데이터만
bash sync-to-drive.sh --no-data    # SIF만

# 풀 (Drive → 이 호스트, 병합)
bash sync-from-drive.sh            # 최신 번들 병합 + SIF latest
bash sync-from-drive.sh --dry-run  # 받을 파일만 확인
bash sync-from-drive.sh --no-sif   # 데이터만
```

배포(HEAXHub SIF) 환경에선 `HEAX_DATA_DIR`이 주입되면 그 볼륨의 DB에 병합된다. 개발은 `backend/var/data`.

## 저장 규약 (Drive)
- `MaterialTwin/data-bundles/mtw-bundle-<TS>.tar.gz` (+`.sha256`) — 최근 `PROJ_RETAIN`개 보존.
- `MaterialTwin/sif/mtw-<TS>-<sha12>.sif` (+`.sha256`) + `LATEST.json` — 동일 sha면 재업로드 skip, 기존 버전 보존.

## 데이터 번들 포맷
`tar.gz`: `manifest.json`(재료→시편→시험, 안정키·content_hash·물성·피팅) + `curves/<hash>.parquet`(내용 주소화, 중복 곡선 1개로 dedup).

병합 CLI 단독 사용:
```bash
python -m app.sync export out.tar.gz    # DB → 번들
python -m app.sync import bundle.tar.gz  # 번들 → DB (병합, 삭제 없음)
```

## 자동 백업 (cron)
포털 배포 데이터를 주기적으로 Drive에 백업한다(SignalForge와 동일 패턴). 등록 예:
```cron
# 배포 볼륨 데이터 → Drive, 30분마다 (retain 5)
*/30 * * * * HEAX_DATA_DIR=/…/HEAXHub/var/app_data/materialtwin_web /bin/bash /…/scripts/drive-sync/sync-to-drive.sh --no-sif >> ~/mtw-sync.log 2>&1
# SIF 이미지 → Drive, 매일 (동일 sha면 skip)
25 5 * * * /bin/bash /…/scripts/drive-sync/sync-to-drive.sh --no-data >> ~/mtw-sync.log 2>&1
```
`HEAX_DATA_DIR`를 배포 볼륨으로 줘야 개발 DB가 아닌 **포털 실데이터**를 백업한다.
복원은 `sync-from-drive.sh`(병합 — 운영 추가분 보존). 데이터 수명주기: 자동 백업(↑) + 병합 복원(↓).

## 사전 준비
- `rclone` + `ApptainerImages:` Google Drive 리모트 설정(SignalForge와 공유).
- 백엔드 `.venv`(Python 3.12).
