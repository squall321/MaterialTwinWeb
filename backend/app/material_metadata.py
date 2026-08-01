# 재료 카탈로그 메타데이터 규약 — attributes 표준 키로 추론(제조사·그레이드·계열·공정)을 지원.
"""재료를 "단단하게" 만드는 구조화 메타데이터 규약.

Material.attributes에 아래 표준 키를 쓰면 find_materials_by_metadata로 추론 검색이 된다
(예: 어느 업체 재료인지, 모든 COC 그레이드, 특정 공정·서브시스템). 값 프로비넌스의 업체는
Source.publisher(= manufacturer)에 남긴다.
"""
from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

# 재료 attributes 표준 키(모두 선택). 그레이드 단위 정합성의 핵심.
STANDARD_KEYS = (
    "manufacturer",    # 제조사(예: "Mitsui Chemicals", "3M", "Covestro")
    "grade",           # 그레이드/품번(예: "5014CL", "467MP", "N52")
    "trade_name",      # 상표/제품군(예: "APEL", "VHB", "Makrolon")
    "material_class",  # 재료 계열(예: "COC", "polycarbonate", "NdFeB", "aluminosilicate glass")
    "process",         # 공정(예: "injection molding", "sintered", "ion-exchanged", "ALD")
    "application",     # 용도/부품(예: "camera lens element", "haptic magnet")
    "subsystem",       # 서브시스템(camera·display·battery·packaging·magnetics …)
    "standard",        # 규격(예: "JIS", "IPC-4101")
    "composition",     # 조성 메모(예: "Nd2Fe14B", "SnAgCu 96.5/3/0.5")
)


def merge_metadata(material, **meta) -> None:
    """빈 값(None/"")은 무시하고 material.attributes에 표준 메타데이터를 얕은 병합.

    JSON 컬럼은 새 dict 재대입으로 변경을 감지시킨다(in-place 변경은 누락 위험).
    """
    clean = {k: v for k, v in meta.items() if k in STANDARD_KEYS and v not in (None, "")}
    if clean:
        material.attributes = {**(material.attributes or {}), **clean}


def infer_manufacturer_from_sources(session: Session, material_id: int) -> str | None:
    """재료 물성값들의 출처 publisher 중 최빈값을 manufacturer로 추정(백필용)."""
    from app.models import PropertyValue

    pubs: Counter = Counter()
    for pv in session.query(PropertyValue).filter_by(material_id=material_id).all():
        if pv.source and pv.source.publisher:
            pubs[pv.source.publisher] += 1
    return pubs.most_common(1)[0][0] if pubs else None
