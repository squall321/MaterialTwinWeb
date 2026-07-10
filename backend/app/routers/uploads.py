# 업로드 라우터 — sniff(미커밋)·파서목록·시편 업로드 적재·수동매핑 재파싱(C5·C7).
from __future__ import annotations

import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app import curve_store
from app.config import get_settings
from app.db import get_db
from app.ingest import ingest_upload
from app.models import Specimen, Test
from app.parsing import ColumnRole, dispatch
from app.parsing.registry import _registered

router = APIRouter(prefix="/api", tags=["uploads"])

settings = get_settings()


def _read_within_limit(content: bytes) -> bytes:
    """업로드 크기 상한(MAX_UPLOAD_MB) 검사(C7)."""
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"upload exceeds {settings.max_upload_mb} MB",
        )
    return content


def _specimen_summary(parsed) -> dict:
    if not parsed.specimens:
        return {}
    spec = parsed.specimens[0]
    return {
        "n_rows": int(spec.data.shape[0]),
        "columns": [
            {
                "index": c.index,
                "header": c.header,
                "role": c.role.value,
                "unit": c.unit,
                "confidence": c.confidence,
            }
            for c in spec.columns
        ],
        "meta": spec.meta,
    }


@router.post("/uploads/sniff")
async def sniff_upload(file: UploadFile = File(...)) -> dict:
    """파일을 파싱만 해보고 파서 후보·신뢰도·컬럼 매핑을 반환(미커밋, C5)."""
    content = _read_within_limit(await file.read())
    parser, parsed = dispatch(content)
    return {
        "filename": file.filename,
        "parser": parser.name,
        "confidence": parsed.confidence,
        "needs_manual_mapping": parsed.needs_manual_mapping,
        "raw_preview": parsed.raw_preview,
        "issues": [
            {"level": i.level, "code": i.code, "message": i.message}
            for i in parsed.issues
        ],
        "specimen": _specimen_summary(parsed),
    }


@router.get("/parsers")
def list_parsers() -> dict:
    """등록 파서 목록(hint UI). 역할 vocabulary도 함께 노출."""
    return {
        "parsers": [{"name": p.name} for p in _registered()],
        "roles": [r.value for r in ColumnRole],
    }


def _ingest_result_payload(res) -> dict:
    return {
        "test_id": res.test.id,
        "valid": res.test.valid,
        "invalid_reason": res.test.invalid_reason,
        "computed": res.computed,
        "issues": [
            {"level": i.level, "code": i.code, "message": i.message}
            for i in res.issues
        ],
    }


@router.post(
    "/specimens/{sid}/uploads", status_code=status.HTTP_201_CREATED
)
async def upload_to_specimen(
    sid: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    """원본 업로드 → 파싱 → 적재. test는 항상 생성, 저신뢰면 valid=False(C5)."""
    specimen = db.get(Specimen, sid)
    if specimen is None:
        raise HTTPException(status_code=404, detail="specimen not found")
    content = _read_within_limit(await file.read())
    res = ingest_upload(db, specimen, content, file.filename or "upload")
    return _ingest_result_payload(res)


@router.post("/uploads/{tid}/mapping")
async def remap_upload(
    tid: int,
    file: UploadFile = File(...),
    mapping: str = Form(...),
    db: Session = Depends(get_db),
) -> dict:
    """수동 매핑 재파싱(4·5단계). 기존 test를 곡선 동반 삭제 후 매핑 적용 재적재(C5).

    mapping은 {"header": "role"} JSON 문자열. tid는 재파싱 대상 test_id.
    """
    old = db.get(Test, tid)
    if old is None:
        raise HTTPException(status_code=404, detail="test not found")
    specimen = db.get(Specimen, old.specimen_id)
    if specimen is None:
        raise HTTPException(status_code=404, detail="specimen not found")
    try:
        mapping_dict = json.loads(mapping)
        if not isinstance(mapping_dict, dict):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=422, detail="mapping must be a JSON object")

    content = _read_within_limit(await file.read())

    # 새 데이터를 먼저 적재하고, 성공(valid)일 때만 원본을 교체한다.
    # (기존엔 원본을 먼저 삭제·커밋해 재적재가 실패하면 원본이 비가역 소실됐음.)
    res = ingest_upload(db, specimen, content, file.filename or "upload", mapping=mapping_dict)
    new_tid = res.test.id

    if not res.test.valid:
        # 재적재 실패 — 새 실패 스텁을 정리하고 원본을 보존한다.
        db.delete(res.test)
        db.commit()
        curve_store.curve_path(new_tid).unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail="재적재에 실패해 원본 시험 데이터를 유지했습니다. 매핑을 확인하세요.",
        )

    # 성공 — 원본 test(cascade)와 곡선 파일을 정리한다(새 곡선 경로와 다를 때만 unlink).
    old_curve = curve_store.curve_path(tid)
    db.delete(old)
    db.commit()
    if old_curve.exists() and old_curve != curve_store.curve_path(new_tid):
        old_curve.unlink()
    return _ingest_result_payload(res)
