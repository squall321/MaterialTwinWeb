# 장비 카탈로그 읽기 — 함정 기록

물성 수집의 `COLLECTION_BRIEF_CORPUS.md` 와 같은 역할. 배치가 실제로 부딪힌 것만 적는다.

---

## 1. **`_spec` 짝이 같은 모델이 아닐 수 있다**

24차 Q. `Bruker_VERTEX70_flyer` 는 **VERTEX 70**(비진공), `Bruker_VERTEXseries` 는 **70v/80/80v** 다.
파수범위·분해능이 전부 달라 **합치면 사양이 섞인다.**
반면 `Bruker_DektakXT` + `_spec` 은 진짜 같은 모델이라 합치는 게 맞다.

**파일명이 아니라 표지의 모델명으로 판정해라.**

## 2. **파일명이 모델명이 아니다**

`KRUSS_DSA100_contactangle.pdf` 의 내용은 고압형 **DSA100HP**(40/690/1750 세 기종) 사양서다.
파일명을 그대로 `model` 에 넣으면 없는 장비가 생긴다.

## 3. **온도계의 측정범위 ≠ 시편 온도범위**

KRÜSS 는 두 값을 **나란히** 인쇄한다 —
`온도측정 범위 −50~400 °C`(PT100 센서)와 `온도제어 20~200/250 °C`(시편 스테이지).
**앞쪽을 `temperature_*` 에 쓰면 틀린다.** 시편이 실제로 놓이는 온도는 뒤쪽이다.

## 4. **매뉴얼의 `Technical specifications` 는 전자계 사양일 수 있다**

Metrohm 851 Titrando 는 10장이 **전극 입력·온도센서·전원**뿐이고
정작 **수분 측정범위가 없다.** 절 제목만 보고 사양표로 읽으면 안 된다.

## 5. **이미지 PDF 는 OCR 이 필요하고, OCR 은 숫자를 뭉갠다**

Hitachi SU3800 은 24쪽 전부 이미지라 `pdftotext` 로 표지만 나온다.
Q 가 `pdftoppm -r 200 -gray` + `tesseract --psm 6` 으로 사양표를 읽었다.
**`1.5 nm` 가 `15.0 nm` 로 보이는 식의 오독이 생기므로 값은 보수적으로 취해라.**

## 6. **벤더의 minimum/maximum 이 뒤집혀 있을 수 있다**

Rigaku SmartLab 의 `SAXS ... grain size (minimum 100 nm)` 와
`USAXS ... minimum grain size of 1000 nm` 는 **SAXS 물리와 어긋나** 하한/상한 판별이 안 된다.
→ **안 넣는 것이 답이다.**

## 7. **응용 그림의 스케일은 사양이 아니다**

HORIBA GD-Profiler 2 의 `1-100 nm / 10-1000 nm / 100 nm-100 µm` 는
**시료 유형 예시**이지 장비 사양이 아니다.

## 8. **프로파일러의 Z축 범위는 조도(Ra)의 상한이 아니다**

Q 의 판단이 옳다. Z축은 **프로파일 높이 축**이지 Ra 상한이 아니다 —
"검출한계는 범위의 하한이 아니다" 와 같은 종류의 오류다.
Z 범위·분해능은 `notes` 에 원문으로 남기고 `range_*` 는 비운다.

**다만 단차(step height) → `structure.layer_thickness` 행에는 Z 범위가 정식 측정범위다** —
그쪽은 측정 대상 물성의 축이 맞다.

## 9. **`insert or replace` 가 규격만 다른 행을 조용히 지운다**

유니크 키가 `(장비, 물성, 기법)` 이라 **규격만 다른 능력행이 서로를 덮어쓴다.**
Q 가 짚었다 — Mitutoyo SJ-410 은 JIS 3종 + ISO + ANSI + VDA 를 지원한다.

**규격이 여럿이면 한 행에 모아 적어라.** 정말 다른 측정이면 **기법 문자열을 달리해라.**
적재기가 이제 덮어쓸 때 경고한다.

## 10. **`resolution` 은 FLOAT 이고 단위는 `range_unit` 을 따른다**

`1 Å @ 6.55 µm range` 같은 조건부 분해능은 **숫자만 환산해 넣고 조건은 `notes` 로** 보낸다.

---

## 물성 매핑을 포기한 항목 — **taxonomy 공백 후보**

24차 Q(surface·chemical 27편)가 남긴 것. 중요한 순.

| # | 공백 | 어느 장비가 재나 | 기존 키로 안 되는 이유 |
|---|---|---|---|
| 1 | **수분함량** | 칼피셔 적정(Metrohm 851) | `water_absorption_24h` 계열은 전부 **흡수 조건**이 붙은 키다 |
| 2 | **상분율(정량상분석)** | XRD(D8·SmartLab) | `chemical.composition` 은 **원소**조성이라 축이 다르다 |
| 3 | **박막 잔류응력** | KLA P-7 (Stoney), XRD sin²ψ | `surface_compressive_stress` 는 이온교환 유리 CS(DOL 짝)다 |
| 4 | **Ra 이외의 조도** | SJ-410 이 Rq·Rz·Rsk·Rku·Rk 등 40여 종 | `surface` 도메인에 **Ra 한 줄뿐**이다. 웨이비니스·평탄도·곡률반경도 없다 |
| 5 | **결정자 크기** | XRD Scherrer | `structure.grain_size`(결정립)와 **같은 양이 아니다** |
| 6 | **기공 크기 분포** | SAXS·수은압입 | `physical.porosity`(기공률)와 다른 축 |
| 7 | **텍스처·배향도** | 극점도/ODF, 편광 UATR | 키 없음 |
| 8 | **격자상수** | XRD 기본 출력 | 키 없음 |
| 9 | **분자구조·결합상태** | NMR 전체 · XPS 결합에너지 · FTIR · Raman | 키 없음. **NMR 이 능력행 0 인 이유가 이것이다** |
| 10 | **분자량(m/z)** | GC-MS `0.6~1091 u` | `structure.molecular_weight` 는 고분자 Mw 라 축이 다르다 |
| 11 | **일함수** | XPS 바이어스 모듈·UPS | 키 없음 |

**재검토 대상** — KRÜSS 펜던트드롭의 액체 표면장력(0.01~2000 mN/m)을
`physical.surface_energy` 에 `medium` 으로 걸었다. 차원은 같지만(mN/m = mJ/m²)
우리 키는 통상 **고체** SFE 다.
