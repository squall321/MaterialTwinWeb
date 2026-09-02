# 62차 XB — `optical.emissivity_total` 진짜 대체 대상 체크리스트

- [x] 61차 WB `AUDIT_emissivity_total.md` 정독 → W-A 43 · W-B 35 · W-C 123 갈래 확인
- [x] 라이브 DB 에서 t4 단독 대표 재수 → 186. W-A·W-B 를 빼니 **W-C 잔여 110종**
- [x] §635 세 줄 검사 — notes 전문검색 · 출처 전수 · 코퍼스 ls|grep
- [x] 표적 110종이 쓰는 출처 872건 전수 → URL 756건 내려받기(740 파일) + 재시도 65건
- [x] `emissiv|emittanc|방사율|放射率` grep → 적중 6건
- [x] §649 재개봉 — Sandia SAND2018-13271 · Mikron 편찬표 · NASA RP-1121 전권
- [x] Sandia 부록 C 가 가리킨 논문 조달 → BNL-52579(Inconel 718) 획득
- [x] 값 적재 JSON 작성 → `xb01_emissivity_surface_state.json`
- [x] 모순 여섯 조건·notes 못박기 → `xb02_contradiction_notes.json`
- [x] 문서축 부재 판정 → `xb03_verdicts.json`
- [x] `integrity_check.py` · `verdicts_check.py` · `pytest -q`
- [x] 교훈 초안 `BRIEF_DRAFT.md`
