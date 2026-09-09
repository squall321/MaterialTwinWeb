# 68차 DA — SDS 형식으로 밀도 부재를 다시 판정한다

표적은 밀도만 비어 (밀도+영률+포아송비) 카드가 한 칸 남은 **제품 27종**이었다.
전부 이미 부재판정이 걸려 있었고, 그 판정문은 하나같이 **TDS·논문**을 근거로 삼고 있었다.
이 배치의 가설은 하나다 — **부재는 문서 형식마다 따로 판정해야 한다**(브리프 627).
DB 출처 3,063건 중 SDS/MSDS 는 10건이고, 밀도 판정 27건 중 SDS 를 열어 본 것은 0건이었다.

---

## 1. 핵심 수치 — SDS 를 몇 건 열었고 그중 몇 건이 밀도를 찍었는가

| | 건수 |
|---|---|
| **실제로 내려받아 9절까지 편 SDS·MSDS** | **19건** |
| 그중 **밀도·비중에 실수를 찍은 것** | **7건** (37 %) |
| 그중 `자료없음 / No data available / Not Available / Not Determined` | 12건 |
| 그 7건 중 **표적 재료에 쓸 수 있었던 것** | **3건** |
| 그 7건 중 **버린 것(형태 불일치)** | **1건** |
| 그 7건 중 **카탈로그에 대응 재료가 없거나 이미 값이 있는 것** | 3건 |

19건 전부 `/data/paper_patent_corpus/standards_appnotes/sds/` 에 `<vendor>_<grade>_SDS_<개정일>.<ext>` 로 남겼다.

| 벤더 | 연 문서 | 비중을 찍었나 |
|---|---|---|
| Doosan | 14건 (DSR-1000 · DS-7409S(N) 영/국 · DS-7409DV · DS-7409HG · DS-7409HG BS · DS-7402 · DS-7402H · DS-7409DQT2 · DS-7409DQN · DST-9000 · DST-9000HT · DSF-400G · DSflex-600 SS) | **4건** — DST-9000 · DST-9000HT · DSF-400G · DSflex-600 |
| Zeon | 3건 (ZEONEX 330R · 5000 · 360R) | **2건** — 330R 0.95 · 5000 1.01 |
| Dow | 1건 (CYCLOTENE 4022-35) | **1건** — 0.9521 (기각) |
| Isola | 1건 (FR408HR LAMINATE) | 0건 |

**가장 중요한 구조 발견 — 같은 벤더 안에서도 SDS 템플릿 판에 따라 갈린다.**
두산의 **구판** SDS 는 9절을 제품 단위로 짜고 `SPECIFIC GRAVITY : (Water=1.0) …` 에 실수를 찍는다.
**신판 GHS** SDS 는 9절을 **CAS 성분 단위 열**로 재편하면서 비중 행을 성분마다 `자료없음` 으로 비운다.
표적 두 등급(DSR-1000 · DS-7409S(N))이 하필 신판으로 갈아탄 제품이라 빈칸이 나왔다.
Zeon 도 같다 — 2015 년 판 330R SDS 는 `0.95` 를 찍는데, 2026 년 판 360R SDS 는 같은 칸이 `Not Determined` 다.
**SDS 는 최신판일수록 물성을 덜 찍는다.** 다음 파동은 옛 판을 찾아라.

---

## 2. 넣은 값 — 3종 5행, 카드 1장

| 재료 | 값 | 등급 | 근거 |
|---|---|---|---|
| **ZEONEX 330R** (2545) | **950 kg/m³** | t1 | `Zeonex 330R SDS`(Zeon Chemicals L.P., 2015-01-23, Z01391) 9절 `Relative Density (water = 1): 0.95` |
| Doosan **DST-9000** (2484) | **2500 / 3300 kg/m³** (하한·상한 2행) | t1 | `SDS MSDS-J-064`(2012-05-04) 9절 `SPECIFIC GRAVITY : (Water=1.0) 2.5 to 3.3` |
| Doosan **DST-9000HT** (2485) | **2500 / 3300 kg/m³** (하한·상한 2행) | t1 | `MSDS-DSE-J-067`(2015-12-18) 9절 같은 행 |

**카드는 1장 섰다 — ZEONEX 330R.** 이 재료는 영률·포아송비를 이미 갖고 있었고 밀도 한 칸만 비어 있었다.
DST-9000·DST-9000HT 는 **표적 27종 밖**이다(밀도 말고 영률도 없다). 카드는 아직 안 선다.
그래도 등재했다 — SDS 경로로 얻은 벤더 인쇄값을 버릴 이유가 없고, 이 두 건이 **브리프 627 의 실증**이다.
두 재료의 기존 판정문은 *"전제품 TDS v9 [Mechanical Properties] p.3 의 Density 칸이 비어 있다"* 였다.
그 진술은 지금도 맞는다. **틀린 것은 그 진술을 '밀도가 없다' 로 읽은 쪽이었다.**

### ZEONEX 330R 이 특히 값진 이유
기존 판정(57차 SB)은 **⚠ 굴절률이 같은 360R 의 0.95 를 옮기지 마라** 고 못 박아 두었다(브리프 586).
이번 값은 **옮긴 값이 아니다** — 8쪽 전 페이지 꼬리말이 `Zeonex 330R` 하나이고
3절 조성이 `Polycycloolefin Resin ~100 wt%` 인 **이 등급 전용 SDS** 가 스스로 찍은 값이다.
게다가 값이 우연히 360R 과 같다는 것이 오히려 두 등급이 같은 저굴절 계열임을 지지한다.

**검산 — Zeon 의 SDS 9절은 TDS 의 비중을 그대로 옮긴 열이다.**
ZEONEX 5000 은 SDS(2017-02-24)가 `Relative Density (water = 1): 1.01`,
현행 TDS(V2026.06.03)가 `Density 1.01 ASTM D792` 로 **글자 그대로 같다.**
즉 이 SDS 열은 임의값이 아니라 TDS 물성표의 복제다. 사본 둘 다 남겼다.

**환산 규약** — 비중은 무차원이라 물밀도를 곱해야 kg/m³ 가 된다.
세 문서 모두 **기준온도를 인쇄하지 않았다.** 규율대로 1000 kg/m³ 를 곱했고 그 사실을 각 행 notes 에 밝혔다.
(20 °C 998.2 를 쓰면 330R 이 948.3 으로 0.18 % 차이라 유효숫자 2자리 안에서 같다.)
카탈로그의 ZEONEX 형제 여섯(2540·2541·2542·2543·2544·2555)이 이미 같은 ×1000 규약으로 들어가 있다.

---

## 3. 경화판이 아니라 액상이라 버린 것 — **1건**

**Photo-BCB (1360) · Dow CYCLOTENE 4022-35 MSDS(2006-04-12).**
9절이 **값을 찍었다** — `Specific Gravity (H2O = 1) 0.9521 Literature` · `Liquid Density 0.9521 g/cm3 ASTM B311`.
**넣지 않았다.** 같은 절이 스스로 형태를 못 박기 때문이다 —
`Physical State  Liquid` · `Color  Yellow` · `Flash Point - Closed Cup  44 °C` · `Kinematic Viscosity  192 mm2/s @ 25 °C`.
이것은 메시틸렌에 녹인 **B-stage 액상 바니시**의 밀도다.
우리가 원하는 것은 스핀코팅 후 250 °C 로 경화해 용매를 날린 **repassivation 유전막**의 밀도다.
**이 배치가 미리 경계하라고 한 함정에 실제로 걸렸고, 걸린 자리에서 멈췄다.**
판정문에 값·형태·기각 사유를 그대로 적어 두었다(다음 파동이 같은 값을 다시 주워 오지 않도록).

곁가지로 두 건이 더 있으나 표적이 아니라 버린 것과 성격이 다르다.
DSF-400G(RCC) `1.30 +/-0.25` 는 카탈로그에 대응 재료가 없고,
DSflex-600 Single Side `1.45/0.92 (film/adhesive)` 는 대응 재료(2487)가 이미 밀도를 갖고 있다.

---

## 4. 못 넣은 26종 — 셋으로 갈라 적는다

### (가) SDS 를 열었는데 9절에 밀도가 없었다 — 2종
| 재료 | 문서 | 9절 verbatim |
|---|---|---|
| Doosan **DSR-1000** (2483) | `GHS-MSDS DSR-1000 BS_231220_Ver.2`(2023-12-20) | `N. Specific gravity  No data available ×5` (CAS 5열 전부) |
| Doosan **DS-7409S (N)** (2509) | `General_..._SDS_240404_Ver.7`(영, 2024-04-04) + `..._MSDS_210520`(국, 2021-05-20) | `N. Specific gravity  No data available ×3` · `하. 비중  자료없음 ×3` |

**국·영 두 판을 다 열었다.** 판정문을 이 문장으로 갱신했다.

### (나) SDS 자체를 못 찾았다 — 12종
| 갈래 | 재료 | 확인 방법 |
|---|---|---|
| Doosan 4종 (2461 DS-7409DYN · 2462 DYN2 · 2463 DYQ · 2480 DS-9000) | 공개 MSDS 목록 **전수 120건**에 없음 | `POST /rest/product/msds/list` 를 language en·ko·kr·zh·jp·빈값 **여섯**으로 던져 응답이 모두 같은 120건임을 확인 |
| Ajinomoto ABF 6종 (978~983) | 벤더가 SDS 를 **아예 공개하지 않음** | 제품 페이지 `aft-website.com/products/insulating_film-abf/` 전문을 폈고 SDS·安全データシート 링크 0건, 다운로드 구역 자체가 없음(문의폼만) |
| Isola **FR408** (1273) | 이 등급 SDS 없음 | 제품 페이지 다운로드가 `FR408-Laminate-RoHS-Declaration.pdf` 하나뿐. 형제 **FR408HR** SDS 는 열었고 9절이 `SPECIFIC GRAVITY (@25 oC): Not Available for product` — 2절이 이유도 적는다(`Product is an Article that is not subject to SDS requirements`) |
| **Permabond ESP110** (1658) | 공개 SDS 색인 **두 곳**에 없음 | `permabond.com/safety-data-sheets/` · `/sds-americas-asia/` 둘 다 열었고 ESP 계열 0건, 두 번째 쪽이 요청제임을 명시. 유통사(Ellsworth·Chemical Concepts) 호스팅분에도 없음 |

### (다) 등급 이름이 없어 SDS 를 찾을 대상 자체가 없다 — 6종
617(언더필, 원문이 '상용 언더필'로만 부름) · 641(CFRP 프리프레그, 벤더 미인쇄) · 739(EMC, 벤더·상품명 미인쇄) ·
1291(Hitachi Chemical 초저손실 빌드업 필름, 등급 미인쇄) · 1368(FOPLP 드라이필름 EMC, `trade name not printed`) ·
1369(플립칩 언더필, `trade name not printed`).
**이 여섯은 SDS 경로가 원리상 닫혀 있다.** 판정을 건드리지 않았다.

### (라) 등급 이름은 있으나 이번에 벤더 SDS 색인까지 열지 못했다 — 5종
737(Zymet X6-82-5LV50 — 회사 폐업) · 1352(Lamics U-8437-3) · 1430(Hitachi Chemical 에폭시 수지 E-67) ·
1652·1653(Hexcel AS7J / HexPly M12).
**검색만 했고 색인을 열지 못했으므로 판정을 갱신하지 않았다** — 문서를 못 연 것은 판정이 아니다(§규율).
다음 파동이 이 다섯을 이어받아라. 다만 1652·1653 은 **프리프레그 SDS 를 찾아도 값이 안 맞는다** —
SDS 는 미경화 프리프레그를 기술하고 우리 재료는 오토클레이브 경화 UD 라미나다(Photo-BCB 와 같은 함정).

---

## 5. SDS 경로가 다른 물성에도 통하는가 — 다음 파동으로 넘긴다

**통한다. 다만 9절이 무엇을 찍는지는 벤더·판마다 갈린다.**

| SDS 9절이 찍은 것 | 문서 | 우리 물성키 |
|---|---|---|
| `Flash Point - Closed Cup 44 °C` · `Autoignition 550 °C` · `Boiling Point 162 °C` · `Vapor Pressure 3.3 hPa @25 °C` · `Kinematic Viscosity 192 mm2/s @25 °C` · `Solubility in Water 0.1 %` | Dow CYCLOTENE 4022-35 | 액상 수지·바니시 개체가 있으면 **전부 t1** |
| `Melting Point >500 °C` · `Boiling Point >1000 °C at 1013 hPa` | 두산 신판 GHS SDS 전건 | ⚠ **제품값이 아니라 CAS 65997-17-3(E-glass) 성분값**이다. 제품 행으로 옮기지 마라 |
| `Relative Density` · `Volatiles (minus H2O) w/w% <0.0001` · `Water Solubility` | Zeon 구판 SDS | 밀도·휘발분 |
| `SPECIFIC GRAVITY` (구판 템플릿) | 두산 DST-9000 계열 · DSF-400G · DSflex-600 | 밀도 |

**열전도율·비열은 9절 항목이 아니다** — 19건 어디에도 없었다. 이 둘은 SDS 경로로 안 열린다.

### 다음 파동 표적 셋
1. **두산 공개 MSDS 목록 120건 전수 스캔.** 이번엔 표적 관련 14건만 폈다. 구판 템플릿을 쓰는 제품이 몇 건인지,
   그중 카탈로그 재료와 겹치는 것이 몇 건인지 아직 모른다. 목록 JSON 은 이미 뽑는 법을 알아냈다 —
   `POST https://www.doosanelectronics.com/rest/product/msds/list` (`language=en`), 파일은
   `GET /file/productAttachment/download/<productAttachmentId>`. 인증 없이 열린다.
2. **벤더 SDS 색인을 REST 로 통째로 받는 기법 자체가 자산이다.** 페이지를 사람처럼 훑는 대신
   그 페이지가 쓰는 엔드포인트를 찾아 전수를 받으면 "목록에 없다" 가 **검색 0건이 아니라 열람 결과**가 된다.
   이번 두산 4종 판정이 그렇게 섰다.
3. **옛 판 SDS 를 노려라.** 최신판은 물성 칸을 비우는 방향으로 간다(두산 신판 · Zeon 2026 판 둘 다).
   단종 등급의 옛 SDS 가 벤더 서버에 그대로 남아 있는 경우가 있다 —
   ZEONEX 330R 은 현행 다운로드 목록에 없는데 `zeonex.com/downloads/MSDS/ZEONEX-330R-SDS.pdf` 가 아직 살아 있었다.

---

## 6. 산출물

| 파일 | 내용 |
|---|---|
| `da01_materials.json` | 값 3종 5행 (ZEONEX 330R 1행 · DST-9000 2행 · DST-9000HT 2행) |
| `da02_verdicts.json` | 판정 갱신 **19종** — 기존 판정문을 보존하고 `**[68차 DA …]**` 문단을 덧붙인 전문 |
| `/data/paper_patent_corpus/standards_appnotes/sds/*.pdf` | 내려받은 SDS·MSDS **19건** |

판정 갱신 19종 = 표적 16종(2483·2509·2461·2462·2463·2480·978~983·1273·1360·1658·2545)
+ 표적 밖 3종(2484·2485·2486 — DST-9000 계열).

`gen_da02_verdicts.py` — 라이브 DB 의 기존 판정문을 읽어 68차 문단을 덧붙여 `da02_verdicts.json` 을 만드는 생성기.
`apply_core_verdicts.py` 는 판정 키를 **덮어쓰므로**(옛 값은 `_before_correction` 으로 보존) 전문을 다시 만들어야 한다.

**DB 에는 아무것도 쓰지 않았다.** 두 도구를 예행으로만 돌려 형식을 검증했다.

```
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  .venv/bin/python scripts/catalog/ingest_agent_json.py   scripts/catalog/out_da/da01_materials.json   # [DRY-RUN] ok 5
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  .venv/bin/python scripts/catalog/apply_core_verdicts.py scripts/catalog/out_da/da02_verdicts.json    # [예행] 병합 19 · 재료 19
```

(참고 — `/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web` 는 `/data/appdata/materialtwin_web` 로 가는 심링크다.
두 경로가 같은 파일이라 이번 예행에서 낡은 개발 DB 를 친 것이 아니다.)
