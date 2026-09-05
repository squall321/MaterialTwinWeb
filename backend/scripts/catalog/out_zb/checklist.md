# 64차 ZB 체크리스트 — 니켈실버(Cu-Ni-Zn) 스프링 콘택트 합금

- [x] 브리프·방법론·파이프라인 정독(§0~§681 중 §586 §601 §604 §626 §634 §644 §645 및 §600~§681 전부)
- [x] §626 — 조달 전 코퍼스 검색(`corpus_index.py search/near`) · DB `notes` 전문검색
- [x] §635 — 세 줄 검사(우리 notes 0건 · 이미 쓰는 출처 0건 · 코퍼스 0건)
- [x] JIS H 3110(C7521) 규격 기계적성질 표 확보
- [x] JIS H 3130(C7701·C5210·C1990) 계보 확인
- [x] 일본신동협회(JCBA) 「伸銅品板条材料特性データベース」에서 조질×방향 실측 확보
- [x] 벤더 시트 확보 — 清峰金属工業(C7701·C7521) · 特殊金属エクセル TOKKIN(C7701·C5210) · DOWAメタルテック(C1990상당)
- [x] CDA copper.org C75200·C77000·C52100·C19900 확보
- [x] §604 — 인쇄 탄성계수를 물리 경계(Cu-Ni-Zn 110~130 GPa)와 대조
- [x] §606·§671 — `pdftotext -bbox-layout` x좌표로 JCBA 표 열 배정 확정
- [x] 산출 JSON 작성(`out_zb/*.json`)
- [x] 스냅샷 `VACUUM INTO` (§647) → 사본에 `--apply` 먼저
- [x] 라이브 드라이런 → `--apply`
- [x] `integrity_check.py` 신규 위반 0 · `verdicts_check.py` 이상 0 · `pytest -q`
- [x] `out_zb/BRIEF_DRAFT.md` 교훈 초안(번호 비움)
- [x] §504 경로 제한 커밋 · §656 메시지 파일 이름에 `zb`
