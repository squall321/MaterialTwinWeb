# 곡선 Parquet 저장소 — 불변키 경로·원자적 쓰기·LTTB 다운샘플·고아 reaper(C4).
from __future__ import annotations

import os
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import RawCurveRef

settings = get_settings()


def curve_path(test_id: int) -> Path:
    """곡선 Parquet 절대경로. 불변키 test_id만 사용(C4)."""
    return settings.curves_dir / f"{test_id}.parquet"


def rel_curve_path(test_id: int) -> str:
    """DATA_DIR 기준 상대경로(raw_curve_ref.file_path 저장용, 절대경로 금지)."""
    return str(curve_path(test_id).relative_to(settings.data_dir))


def write_curve(test_id: int, dataframe: pd.DataFrame) -> str:
    """곡선 DataFrame을 Parquet으로 원자적 저장하고 DATA_DIR 상대경로를 반환한다(C4).

    .tmp.{uuid} 임시파일에 쓰고 fsync 후 os.replace로 atomic rename 한다.
    DB 트랜잭션 밖에서 호출되어야 한다(C2). 같은 test_id 재쓰기는 덮어쓴다.
    """
    final = curve_path(test_id)
    final.parent.mkdir(parents=True, exist_ok=True)
    tmp = final.with_name(f"{final.name}.tmp.{uuid.uuid4().hex}")

    dataframe.to_parquet(tmp, index=False)
    # 파일 본문 fsync로 디스크 영속화 후 rename(C4).
    fd = os.open(tmp, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, final)
    # 디렉터리 엔트리도 영속화(rename 가시성 보장).
    dir_fd = os.open(final.parent, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)
    return rel_curve_path(test_id)


def read_curve(test_id: int) -> pd.DataFrame:
    """저장된 곡선 Parquet을 DataFrame으로 읽는다."""
    return pd.read_parquet(curve_path(test_id))


def lttb_downsample(
    x: np.ndarray, y: np.ndarray, n_out: int = 2000
) -> tuple[np.ndarray, np.ndarray]:
    """LTTB(Largest-Triangle-Three-Buckets)로 (x,y)를 n_out 점으로 다운샘플한다.

    시각화용 형상 보존 다운샘플. n_out>=원본이거나 <3이면 원본 그대로 반환.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = x.size
    if n_out >= n or n_out < 3:
        return x, y

    sampled_idx = np.empty(n_out, dtype=int)
    sampled_idx[0] = 0
    sampled_idx[-1] = n - 1

    # 내부 n_out-2개 버킷(첫/마지막 점 제외).
    bucket_size = (n - 2) / (n_out - 2)
    a = 0  # 직전 선택점 인덱스
    for i in range(n_out - 2):
        # 다음 버킷 평균점(삼각형 셋째 꼭짓점 근사).
        next_lo = int(np.floor((i + 1) * bucket_size)) + 1
        next_hi = int(np.floor((i + 2) * bucket_size)) + 1
        next_hi = min(next_hi, n)
        if next_lo >= next_hi:
            avg_x = x[next_lo if next_lo < n else n - 1]
            avg_y = y[next_lo if next_lo < n else n - 1]
        else:
            avg_x = x[next_lo:next_hi].mean()
            avg_y = y[next_lo:next_hi].mean()

        # 현재 버킷 범위에서 직전점-평균점과 이루는 삼각형 넓이 최대 점 선택.
        cur_lo = int(np.floor(i * bucket_size)) + 1
        cur_hi = int(np.floor((i + 1) * bucket_size)) + 1
        cur_hi = min(cur_hi, n - 1)
        if cur_lo >= cur_hi:
            chosen = cur_lo if cur_lo < n - 1 else n - 2
        else:
            ax, ay = x[a], y[a]
            areas = np.abs(
                (ax - avg_x) * (y[cur_lo:cur_hi] - ay)
                - (ax - x[cur_lo:cur_hi]) * (avg_y - ay)
            )
            chosen = cur_lo + int(np.argmax(areas))
        sampled_idx[i + 1] = chosen
        a = chosen

    return x[sampled_idx], y[sampled_idx]


def reaper(session: Session, grace_seconds: float = 600.0) -> dict[str, int]:
    """curves 디렉터리를 DB 포인터와 대조해 고아/누락을 정리한다(C4).

    - DB raw_curve_ref가 가리키지 않는 .parquet/.tmp.* 파일 삭제(고아).
    - file_path가 가리키는 파일이 실제로 없으면 storage='missing' 마킹.
    반환: {"deleted_files": n, "marked_missing": n}.

    grace_seconds: 최근 수정된 파일은 삭제하지 않는다. 웹·MCP가 같은 디렉터리를
    공유하므로, 다른 프로세스에서 진행 중인 적재가 write_curve로 곡선을 먼저 쓰고
    RawCurveRef를 아직 커밋하지 않은 창에서 그 산 파일을 오삭제하는 경합을 막는다.
    """
    import time

    curves_dir = settings.curves_dir
    now = time.time()
    deleted = 0
    marked = 0

    refs = session.execute(
        select(RawCurveRef).where(RawCurveRef.storage == "parquet_fs")
    ).scalars().all()

    # DB가 가리키는 유효 파일 절대경로 집합.
    referenced: set[Path] = set()
    for ref in refs:
        if ref.file_path:
            referenced.add((settings.data_dir / ref.file_path).resolve())

    if curves_dir.exists():
        for f in curves_dir.iterdir():
            if not f.is_file():
                continue
            name = f.name
            is_tmp = ".tmp." in name
            is_parquet = name.endswith(".parquet")
            if not (is_tmp or is_parquet):
                continue
            # 유예기간 내 최근 파일은 in-flight 적재일 수 있어 건드리지 않는다.
            try:
                if now - f.stat().st_mtime < grace_seconds:
                    continue
            except OSError:
                continue
            # .tmp.* 는 항상 고아(완료된 쓰기는 final 이름). parquet은 미참조 시 고아.
            if is_tmp or f.resolve() not in referenced:
                try:
                    f.unlink()
                    deleted += 1
                except OSError:
                    pass

    # 파일이 사라진 raw_curve_ref는 missing 마킹.
    for ref in refs:
        if not ref.file_path:
            continue
        if not (settings.data_dir / ref.file_path).exists():
            ref.storage = "missing"
            marked += 1
    if marked:
        session.commit()

    return {"deleted_files": deleted, "marked_missing": marked}
