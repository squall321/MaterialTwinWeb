<!-- 70차 FA 수집 배치 보고서 — 69차 EB 가 "이 배치 최대의 손실"로 남긴 MGC·Sumitomo·Resonac 등급을 카드로 세운다 -->

# 70차 FA — EB 가 못 담은 표들을 담을 그릇을 만들었다

**한 줄 답: 손실은 문서가 아니라 그릇이었다. 등급 카드 32장을 세우니 이미 로컬에 있던 표 다섯 개에서 795행이 그냥 흘러들어왔다.**

69차 EB 는 이렇게 적었다 — 「풍부한 총합표를 세 개나 찾았는데 DB 에 그 등급이 없다 … 등급을 등록만 하면 문서는 이미 로컬에 있다」.
이 배치는 그 문장을 그대로 실행했다. **새로 받은 문서는 0건이다.** 값은 전부 EB 가 이미 코퍼스에 넣어 둔 원문에서 나왔다.

**수확: 재료 32장 · 물성 795행** (`out_fa/fa01_materials.json`) · 자체검증 오류 0

| 벤더 | 세운 카드 | 코어7 채움 | 원문 |
|---|---:|---|---|
| **MGC 三菱ガス化学** | **16장** | BT 11장이 **7/7** · BT 2장 6/7 · FR-4 2장 6/7 · Chip-LED 1장 3/7 | 일본어 라인업 HTML 3장 |
| **Sumitomo Bakelite 住友ベークライト** | **6장** | 전부 **4/7** (E·α·k·σu) | ELC 仕様一覧 HTML 2장 |
| **Resonac** | **10장** | 전부 **3/7** (E·α·k) | 2023-2024 총합 카탈로그 PDF 66쪽 중 2쪽 |

---

## 1. 등급 몇 장을 세웠고 각각 코어7 몇 칸을 채웠는가

코어7 = `physical.density`(ρ) · `mechanical.youngs_modulus`(E) · `mechanical.poisson_ratio`(ν) ·
`thermal.expansion_linear`(α) · `thermal.conductivity`(k) · `thermal.specific_heat`(cp) · `mechanical.tensile_strength`(σu).

| 카드 | 물성행 | 코어7 | 채운 칸 | 남은 칸 |
|---|---:|:--:|---|---|
| `MGC CCL-HL832NX type A (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL832NS (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL832NS type LC (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL832NSR (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL832NSR type LCA (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL832NSF (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL832NSF type LCA (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL832NSA type LCA (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL972LF type LD (BT resin CCL)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-HL972LFG (BT resin CCL)` | 20 | 6 | ρ E α k cp σu | **ν** |
| `MGC CCL-HL972LFG type LD (BT resin CCL)` | 20 | 6 | ρ E α k cp σu | **ν** |
| `MGC GHPL-830SR (BT resin prepreg)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC GHPL-830SR type LC (BT resin prepreg)` | 21 | **7** | ρ E ν α k cp σu | — |
| `MGC CCL-EL190T (high-performance FR-4 CCL)` | 32 | 6 | E ν α k cp σu | **ρ** |
| `MGC CCL-EL230T (high-performance FR-4 CCL)` | 32 | 6 | E ν α k cp σu | **ρ** |
| `MGC CCL-HL820WDI (Chip-LED BT resin CCL)` | 18 | 3 | E α σu | ρ ν k cp |
| `Sumitomo Bakelite Sumilite ELC-4762 / ELC-4756 (FR-4 CCL)` | 24 | 4 | E α k σu | ρ ν cp |
| `Sumitomo Bakelite Sumilite ELC-4970 (CEM-3 CCL)` | 24 | 4 | E α k σu | ρ ν cp |
| `Sumitomo Bakelite Sumilite ELC-4972R&S (CEM-3 CCL)` | 24 | 4 | E α k σu | ρ ν cp |
| `Sumitomo Bakelite Sumilite ELC-4970GS (CEM-3 CCL)` | 24 | 4 | E α k σu | ρ ν cp |
| `Sumitomo Bakelite Sumilite ELC-4765 (FR-4.0 CCL)` | 24 | 4 | E α k σu | ρ ν cp |
| `Sumitomo Bakelite Sumilite ELC-4768 (FR-4.0 CCL)` | 24 | 4 | E α k σu | ρ ν cp |
| `Resonac MCL-E-795G (glass/epoxy CCL)` | 31 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-795G (LH type) (glass/epoxy CCL)` | 31 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-705G (glass/epoxy CCL)` | 31 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-705G (L type) (glass/epoxy CCL)` | 31 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-705G (LH type) (glass/epoxy CCL)` | 31 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-700G (R type) (glass/epoxy CCL)` | 31 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-770G (R type) (glass/epoxy CCL)` | 30 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-770G (RLH type) (glass/epoxy CCL)` | 30 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-679FG (R type) (glass/epoxy CCL)` | 26 | 3 | E α k | ρ ν cp σu |
| `Resonac MCL-E-679FG (S type) (glass/epoxy CCL)` | 26 | 3 | E α k | ρ ν cp σu |

**코어7 칸 합계 32×7 = 224칸 중 145칸을 채웠다(64.7 %).**
분포는 7칸 11장 · 6칸 4장 · 4칸 6장 · 3칸 11장.

### 카드가 몇 장 섰는가 — **11장**

「선 카드」 = 밀도 + 영률 + 포아송비를 모두 가진 카드. **MGC BT 계열 11장이 섰다**
(HL832NX·HL832NS·HL832NS LC·HL832NSR·HL832NSR LCA·HL832NSF·HL832NSF LCA·HL832NSA LCA·HL972LF LD·GHPL-830SR·GHPL-830SR LC).

- **못 선 두 장은 MGC BT 안에 있다** — `HL972LFG` 와 `HL972LFG type LD` 는 원문 `ポアッソン比` 칸이 **`-`** 다.
  형제 11등급은 0.15~0.21 로 다 인쇄돼 있는데 이 둘만 비었다. **클래스 중앙값을 채우지 않았다.**
- **MGC FR-4 두 장은 밀도 하나 때문에 못 섰다.** 표에 있는 것은 `樹脂比重 1.44 / 1.42` — **수지만의 무차원 비중**이지 적층판 밀도가 아니다.
  ×1000 해서 적층판 밀도로 쓰는 것은 역산이라 하지 않았다. 사유를 `attributes.density_absent_reason` 에 적었다.

### 라이브 DB 와 겹치지 않는다 — 먼저 확인했다

`HL832`·`HL972`·`HL820`·`GHPL`·`EL190`·`EL230`·`ELC-4`·`LAZ-`·`E-795`·`E-705`·`E-700`·`E-770`·`679F`·`HS200`·`HS100`·`Sumilite`·`スミライト`·`GEA-` 18개 토큰으로 `name`·`description` 을 훑었다. **적중 0.** 걸린 것은 `MCL-` 두 건뿐이다.

- **재료 97 `BT Resin`** (role=product, 출처 306 = MGC 영문 `hfbt.html`) — **클래스 카드다.** 실제로 담긴 값이
  밀도 `2100`·`2000`, 영률 `28e9`·`32e9`, 인장강도 `270e6`·`290e6` 인데 이건 **HL832NX 와 HL832NSF 두 등급의 값을 등급 표시 없이 섞은 것**이다.
  새 13장은 그 표의 **한 등급씩**을 가리킨다. 각 카드 `description` 에 이 관계를 적었고 `attributes.related_material_ids` 에 97 을 넣었다.
- **재료 1276** (MGC 수지 BT 라미네이트, Ehrler 2002, role=evidence) — 무명 시료다. 관계만 적었다.
- **재료 1227·1228 `Hitachi MCL-679`** (Hsiung 2003, role=evidence) — 논문이 잰 **표면 상태** 카드이고 등급 접미가 `MCL-679` vs `MCL-E-679FG` 로 다르다.
  Resonac 679FG 두 장의 `description`·`related_material_ids` 에 이 차이를 적었다.

`role` 은 32장 전부 `product` 다(스마트폰·반도체 패키지 기판의 실부품 적층재이고 전부 벤더가 등급명으로 인쇄한 제품이다). `aliases` 는 하이픈 유무·공백 유무·`CCL-`/`MCL-` 접두 유무·구 사명(`Showa Denko`·`Hitachi Chemical`)까지 넣었다. 이름은 최장 57자로 200자 제한에 여유가 있다.

---

## 2. MGC 의 `Young's Modulus` = `Flexural Modulus` 동일값 문제를 어떻게 처리했는가

브리프가 지목한 함정이 **정확히 그대로 있었다.** MGC BT 표 13등급 전부에서 두 행의 숫자가 같다:

```
曲げ弾性率 |  |  | GPa | 28 | 27 | 30 | 30 | 33 | 32 | 34 | 31 | 25 | 23 | 21 | 21 | 22
ヤング率   |  |  | GPa | 28 | 27 | 30 | 30 | 33 | 32 | 34 | 31 | 25 | 23 | 21 | 21 | 22
```

그리고 **이 페이지에는 시험규격이 하나도 없다** — HTML 전문에서 `JIS` 0회 · `ASTM` 0회 · `IPC` 0회. `測定条件` 칸은 이 두 행에서 `&nbsp;` 다.
브리프의 규칙대로 처리했다.

- **BT 13등급의 `mechanical.youngs_modulus` 13행은 t3 로 낮췄다.** `conditions.test_mode = "unconfirmed"`, `conditions.grade_scope` 에 사유를 적었다 — 「값 자체는 이 등급에 인쇄된 것이고 등급 범위 문제는 없다. t3 로 내린 이유는 시험모드 미확정이다」. notes 에 13등급 동일값 목록과 규격 부재를 verbatim 으로 남겼다.
- **`mechanical.flexural_modulus` 13행은 t1 로 넣었다.** `曲げ弾性率` 는 행 이름 자체가 굽힘이라 모호함이 없다. 동일값 문제는 굽힘 쪽 해석에 영향을 주지 않는다.
- **굽힘값으로 영률 칸을 채운 건 0건이다.**

### 다만 — 같은 벤더의 다른 두 표가 반례를 준다. 값을 옮기기 전에 찾았다

**`lineup/led.html` (CCL-HL820WDI) 이 결정적이다.** 완전히 같은 MGC 서식인데 두 행이 **다른 숫자**다:

```
曲げ弾性率 | 縦方向 | A | GPa | 23        ヤング率 | 縦方向 | A | GPa | 25
           | 横方向 | A | GPa | 22                 | 横方向 | A | GPa | 24
```

**`lineup/fr4.html` (CCL-EL190T) 도 갈린다** — 曲げ弾性率 縦27/横27 vs ヤング率 縦27/横**26**.
게다가 세 표 모두 `引張強さ` 와 `曲げ強さ` 가 크게 다르다(HL832NX 270 vs 450 MPa, EL190T 330 vs 580 MPa) — **MGC 는 인장시험을 실제로 별도로 돌린다.** 그리고 세 표 모두 행 순서가 `曲げ強さ → 曲げ弾性率 → 引張強さ → ヤング率` 로, `ヤング率` 는 인장 블록에 놓인다.

그래서 이렇게 갈랐다.

| 표 | 두 행이 갈리나 | `youngs_modulus` 등급 | 근거 |
|---|---|:--:|---|
| `hfbt.html` BT 13등급 | **13/13 동일** | **t3** | 이 문서만으로는 확정 불가 — 브리프 규칙 적용 |
| `fr4.html` EL190T/EL230T | EL190T 에서 갈린다(27 vs 26) | **t1**, `test_mode: tensile` | 같은 표가 두 행을 가르는 것을 보여 준다 |
| `led.html` HL820WDI | **갈린다**(23/22 vs 25/24) | **t1**, `test_mode: tensile` | 이 표가 반례의 증거 자체다 |

세 표 전부 `conditions.test_standard` 는 **비웠다** — MGC 는 어느 페이지에도 규격 번호를 안 찍는다. 그 사실도 notes 에 박았다.

**다음 배치가 판단할 일** — 위 반례는 「MGC 템플릿에서 `ヤング率` 행은 인장 행이다」를 상당히 강하게 뒷받침한다. BT 13행의 동일값은 두 물성이 실제로 가깝고 유효숫자 2자리에서 붙어 버린 결과일 수 있다. 그 근거를 각 t3 행 notes 안에 그대로 적어 뒀으니 **t1 승격은 다음 배치가 결정하면 된다.** 이 배치는 낮은 쪽을 골랐다.

### Sumitomo·Resonac 은 이 문제가 없다 — 벤더가 이름으로 갈라 준다

- **Sumitomo**: `曲げ弾性率` vs `引っ張り弾性率` 를 행 이름부터 가르고 값도 다르다(ELC-4970 굽힘 タテ18/ヨコ16 vs 인장 タテ14/ヨコ12). **굽힘이 인장보다 높게** 나오는 것까지 그대로 보인다.
- **Resonac**: `弾性率(引張モード)` vs `弾性率(曲げモード)` — **행 이름에 시험모드를 박아 놓는다.** 전 등급에서 값이 다르다(795G 인장 26-28 vs 굽힘 35-37).

둘 다 `test_mode` 확정이므로 **t1** 로 넣었다. 다만 **Sumitomo 도 시험규격 번호는 안 찍는다**(`JIS`·`ASTM`·`IPC` 0회, 있는 건 처리조건 코드 `A` 뿐) — 그 사실도 notes 에 적었다.

---

## 3. 열 밀림을 어떻게 확인했는가

**HTML 5장 (MGC 3 · Sumitomo 2) — 렌더 대신 `<tr>`/`<td>` 직접 파싱.**
`html.parser` 로 `colspan`/`rowspan` 까지 읽어 셀 경계를 확정했다. 레이아웃 추측이 끼어들 자리가 없으므로 열 밀림 위험이 원천적으로 없다.
그 위에서 **CJK 라벨을 원문 그대로 확인**했다 — 예컨대 CTE 두 행이 정말 둘 다 `X,Y` 인지 원본 태그로 검증했다:
```
<th rowspan="2" scope="row">熱膨張係数</th><th class="st002" scope="row">X,Y</th><td>&alpha;1</td> …
<th class="st002 bdrL" scope="row">X,Y</th><td>&alpha;2</td> …
```
→ **두 번째 행도 Z 축이 아니라 X,Y 다.** (유리포가 지배하는 면내라 Tg 위에서 CTE 가 내려가는 것이 물리적으로도 맞는다.) 이 사실을 α2 행 notes 에 verbatim 으로 남겼다.

**PDF (Resonac 66쪽) — `pdftotext -layout` + 350 dpi 렌더 대조를 값을 옮긴 두 쪽 전부에 적용했다.**

| 쪽 | 렌더 | 대조 결과 |
|---|---|---|
| PDF 5쪽(印刷 6) | 350 dpi | **일치.** 8개 열 머리가 자리까지 같다 — `MCL-E-795G / (LH) / MCL-E-705G / (L) / (LH) / MCL-E-700G(R) / MCL-E-770G(R) / (RLH)`. `弾性率(引張モード) X` 26-28 … 와 `熱伝導率` 의 6번째 열만 `0.60-0.80` 인 것까지 그림에서 확인 |
| PDF 6쪽(印刷 7) | 350 dpi | **불일치를 잡았다 — 아래 참조** |

### 렌더가 실제로 잡아낸 오독 — 이 배치의 핵심

PDF 6쪽의 `pdftotext -layout` 출력은 **오른쪽 세로 탭**(`ＭＣＬ用途別推奨品種一覧`·`半導体パッケージ用材料` …)을 본문 줄 사이에 끼워 넣으면서 열 머리 두 줄을 이렇게 쪼갠다:

```
                     MCL-E-679FG     MCL-E-679FG      MCL-HS200        MCL-HS200       MCL-HS100
   GEA-705G        GEA-770G        (R タイプ)          (S タイプ)                          (D タイプ)
```

**이 텍스트를 그대로 읽으면 `GEA-705G` 에 `(R タイプ)` 가 붙는다** — 열이 두 칸 밀린 채로 679FG 의 값 전부가 GEA 프리프레그로 들어갈 뻔했다.
350 dpi 렌더로 실제 열 순서가 **`GEA-705G | GEA-770G | MCL-E-679FG(R) | MCL-E-679FG(S) | MCL-HS200 | MCL-HS200(D) | MCL-HS100`** 임을 눈으로 확정하고, 그 순서로만 값을 옮겼다. 사유를 이 쪽에서 나온 **모든 행의 notes 에** 박아 뒀다.

### 각주도 쪽 단위로 다시 읽었다 (EB 가 남긴 경고)

- Resonac `*4: 0.8 mmt` 는 **`弾性率(曲げモード)` 와 `CTE z` 행에만** 붙는다. `弾性率(引張モード)` 에는 각주 번호가 없다 → 인장탄성률의 시편 두께는 표 맨 위 `厚み 0.2 mm` 다. 두 값을 `conditions.specimen_thickness_mm` 에 다르게(0.2 vs 0.8) 박았다.
- Resonac `*5: 引張` 는 **CTE 측정모드**를 뜻한다. p5 의 여덟 열과 p6 의 679FG 열에는 `*5` 가 **없고** 대신 `(圧縮)` 라고 인쇄돼 있다 → `conditions.test_mode: "compression (圧縮)"`. (같은 p6 의 GEA/HS 열에는 `*5` 가 붙는다 — 그래서 이 배치는 그 열들을 안 건드렸다.)
- Sumitomo 다층 페이지의 `引っ張り強さ※`·`引っ張り弾性率※` 의 `※` 는 **`※0.1mmtで測定`** 이다 → ELC-4765·4768 의 인장 4행에만 `specimen_thickness_mm: 0.1` 을 박았다. 굽힘 행에는 안 붙는다.
- MGC BT 표의 `*2: 45umプリプレグの特性値を記載しております` 는 **표 안에 앵커가 없다.** HTML 의 `<sup>` 를 전수로 확인했고 전부 지수 표기(`10^15-16`·`g/cm3`·`W/m*K`)뿐이다. GHPL-830SR 두 열이 프리프레그 전용이라 여기 걸릴 가능성이 가장 높지만 **문서가 확정하지 않으므로** 조건에 넣지 않고 `attributes.vendor_table_footnote` 에 사실만 적었다.

### 그 밖의 규율 점검

- **인쇄된 구간은 두 행.** Resonac 은 값이 전부 구간(`26 - 28`)이라 `conditions.bound: "lower"/"upper"` 두 행으로 갈랐다 — **평균 0건.** 10장에서 이 방식으로 나온 행이 대부분이다.
- **경사/위사는 두 행.** MGC FR-4·Chip-LED 의 `縦/横`, Sumitomo 의 `タテ/ヨコ` 를 전부 갈랐다. MGC FR-4 의 포아송비 `縦0.17/横0.16` 도 평균 내지 않았다.
- **같은 물성의 다른 측정법도 두 행.** Tg 는 DMA/TMA/DSC 를 갈랐고, Resonac 의 Z축 CTE 는 `圧縮` 과 `DIC` 를 갈랐다(795G: 10-15 vs 8.5).
- **부등호는 하한 한 행.** HL832NSA typeLCA 의 `ガラス転移温度 DMA >350℃` 와 MGC FR-4 의 `T-260 ＞60 min` 은 `bound: "lower"` 한 행으로만 넣었다.
- **비중과 밀도를 구별했다.** MGC BT 표의 행 이름은 `密度` 이고 단위가 `g/cm3` 다(무차원 比重 이 아니다) → **곱한 수는 1000 하나뿐**이고 그 사실을 13행 notes 에 전부 적었다. 반대로 MGC FR-4 의 `樹脂比重`(무차원)은 쓰지 않았다.
- **환산 검산**을 모든 행 notes 에 넣었다. 예: `20.7 GPa × 1e9 = 2.07e10 Pa; 되돌리면 2.07e10/1e9 = 20.7`, `0.95 J/(g·K) × 1000 g/kg = 950 J/(kg·K)`, `14 ppm/℃ × 1e-6 = 1.4e-05 1/K`, `230 + 273.15 = 503.15 K`.
- **원문 오식도 지우지 않고 남겼다.** Sumitomo 다층 페이지는 Z축 CTE 두 행 이름을 `CTE Z (α1)` 로 **두 번** 인쇄한다. 형제 페이지(양면 CCL)가 같은 자리를 `α1`/`α2` 로 찍고 값 크기(65→270)도 같은 꼴이라 두 번째를 α2 로 읽었고, **원문 표기가 α1 이라는 사실을 해당 행 notes 에 적었다.**
- **t4 는 0건이다.** 추정·계산으로 만든 값이 하나도 없다. 등급 분포는 **t1 782행 · t3 13행**.

---

## 4. 못 넣은 것 — 셋으로 갈라 적는다

### (가) 표에 열이 없었다 (문서를 열었고 열 부재를 확인)

| 표적 | 연 문서 | 확인한 부재 |
|---|---|---|
| **Resonac 10등급 — 밀도·포아송비·비열·인장강도 (40칸)** | 총합 카탈로그 **66쪽 전수** | `比重`·`密度`·`ポアソン`·`ポアッソン`·`比熱` 를 66쪽에 걸쳐 grep 해 적중 3쪽(15·19·42)뿐이고 **그 셋 다 산문**이다(`高密度ガラスクロス`·`高密度電子機器`). **물성값으로서의 밀도·포아송비·비열 행이 이 카탈로그에 아예 없다.** 인장강도도 없다 — Resonac 의 기계축은 `弾性率(引張/曲げモード)` 두 행뿐이다 |
| **Sumitomo ELC 6등급 — 밀도·포아송비·비열 (18칸)** | ELC 사양표 2장 전수 | 두 페이지 어디에도 밀도·포아송비·비열 행이 없다. Sumitomo 의 열축은 `熱伝導率`(레이저플래시)와 `ガラス転移温度`(TMA/DMA/DSC) 다 |
| **MGC EL190T·EL230T — 밀도 (2칸)** | `fr4.html` 36행 전수 | 적층판 밀도 행이 없다. 있는 건 `樹脂比重 1.44/1.42`(무차원 수지 비중) |
| **MGC HL820WDI — 밀도·포아송비·비열·열전도율 (4칸)** | `led.html` 23행 전수 | 네 행 모두 표에 없다. 같은 벤더 BT 표(`hfbt.html`)에는 있는데 이 Chip-LED 페이지에는 안 싣는다 |
| **MGC HL972LFG·HL972LFG typeLD — 포아송비 (2칸)** | `hfbt.html` 25행 | 행은 있는데 이 **두 열만 `-`** 다. 형제 11등급은 0.15~0.21 로 인쇄돼 있다 |
| **Resonac MCL-E-770G(R)·(RLH) — CTE z (DIC)** | PDF 5쪽 | 두 열만 `－` 다(형제 여섯은 8.5·5.5·9.6·7.0·6.9·13.1) |
| **Resonac MCL-E-679FG 두 등급 — Dk/Df 10 GHz** | PDF 6쪽 | 1 GHz 칸만 있고 10 GHz 칸이 `－` 다 |

### (나) 문서를 못 열었다

**이 배치는 0건이다.** 네트워크를 한 번도 쓰지 않았다 — 값의 출처가 된 원문 5개가 전부 로컬에 있었고 전부 열렸다.
다만 **URL 을 확정하지 못한 문서가 3개** 있고, **지어내지 않고 `url: null` + `url_note` 로 남겼다**(EB 의 선례를 따랐다):

- `SumitomoBakelite_Sumilite_ELC_DoubleSided_CCL_Spec_ja_*.html` · `_Multilayer_PWB_Spec_ja_*.html` — 저장본에 절대 URL 이 없다(`og:url`·canonical 없음, `href` 는 `/common/css/…`·`/index.html` 뿐).
- `Resonac_MCL_CopperCladLaminates_Catalog_ja_2023-2024.pdf` — PDF 메타가 `CubePDF`/`iTextSharp` 뿐이라 원 URL 이 남아 있지 않다.

(MGC 3장은 `og:url` 이 살아 있어 `https://www.mgc.co.jp/products/sc/btprint/lineup/{hfbt,fr4,led}.html` 를 그대로 실었다.)

### (다) 등급이 안 맞았다

**EB 가 이 칸에 적었던 것을 이 배치가 비웠다.** 남은 것은 이 배치가 스스로 만든 다음 표적뿐이다.

- **Sumitomo LAZ 계열 — 이번에 안 세웠다.** 브리프 표적이 ELC 6등급이라 범위를 지켰다. 그런데 로컬 `LAZ-4785`(패키지 코어 **7종**: TH-G/GH-G/TH-B/GS-BA/GS-BE/GH-T/GS-W)와 `LAZ-6785`+`LAZ-2002`(프리프레그 **5종**)가 **`弾性率` 를 30 ℃ 와 260 ℃ 두 온도에서** 찍는다(4785: 32/31/32/29/18/18/18 GPa @30 ℃, 21/20/21/18/10/10/10 @260 ℃). **온도별 영률은 이 카탈로그에 흔치 않다.** 다만 이 표는 `弾性率` 에 시험모드를 안 붙이므로(CTE 행만 `TMA(引張モード)`) MGC BT 와 같은 판정 문제가 생긴다 — 다음 배치가 t3 로 담을지 정해야 한다. 12등급분.
- **Resonac 나머지 등급 — 이번에 안 세웠다.** 카탈로그 p7·p8·p9 에 `MCL-HS200`·`MCL-HS100`·`GH-200`·`GH-100`·`MCL-HD60`·`MCL-HD90`·`MCF-200HS`·`MCF-770G`·`MCL-LW-990`·`MCL-LW-910G`·`MCL-LW-900G`·`MCL-HE-679G`·`AS-400HS`·`MCL-I-671`·`TD-002` 등이 같은 서식으로 `弾性率(引張モード)` 를 찍는다. **쪽마다 렌더 대조를 다시 해야 하므로**(p6 에서 실제로 밀렸다) 이 배치에서는 렌더로 확정한 두 쪽만 담았다. 20등급분 이상.
- **Resonac GEA-705G·GEA-770G 프리프레그** — 값은 p6 에 있지만 `弾性率(曲げモード)` 가 `－` 이고 CTE 에 `*5`(引張)가 붙어 p5 계열과 조건이 다르다. 조건 축이 달라 같은 배치에 섞지 않았다.
- **MGC EL190T·EL230T 의 밀도** — 등급은 이제 DB 에 있는데 **문서에 열이 없다.** 다른 MGC 문서(영문 TDS·설계가이드)를 열어야 닫힌다.

---

## 5. 다음 배치에 넘길 것

### 5-1. **MGC BT 13등급 영률 t3 → t1 승격 판정**

이 배치가 브리프 규칙대로 t3 로 내렸지만, **승격 근거를 이미 다 모아서 각 행 notes 안에 넣어 뒀다** — `led.html` HL820WDI(굽힘 23/22 vs 영률 25/24)와 `fr4.html` EL190T(27/27 vs 27/26)가 같은 MGC 서식에서 두 행을 가르고, 세 표 모두 `引張強さ`≠`曲げ強さ` 이며 `ヤング率` 는 `引張強さ` 바로 아래 인장 블록에 놓인다. **판정만 하면 13칸이 t3 에서 t1 로 올라간다.** 새 문서는 필요 없다.

### 5-2. **밀도 34칸이 이 배치가 만든 가장 큰 단일 빈칸이다**

Sumitomo 6 + Resonac 10 + MGC FR-4 2 + MGC Chip-LED 1 = **19장이 밀도가 없다.** 세 벤더 다 자기 총합표에 밀도를 안 찍는다.
**IPC-4101 슬래시시트가 문일 수 있다** — Resonac 카드에 `attributes.ipc_4101_slash_sheet`(42 · 128,130 · 44 · N/A(S-glass))를, Sumitomo 카드에 `ipc_sheet_class`(FR-4 · CEM-3 · FR-4.0)를 넣어 뒀다. IPC-4101 규격서 본문이 시트별 밀도를 규정하면 **t2 로 19칸이 한 번에 닫힌다.** (규격서를 안 열고 「없다」고 선언하지 않는다 — 이 배치는 IPC-4101 본문을 열지 않았다.)

### 5-3. Sumitomo LAZ 12등급 — 문서는 이미 로컬에 있다

`SumitomoBakelite_LAZ-4785_PackageCore_Spec_ja_2026-09-09.html`(7종) · `LAZ-6785_Prepreg_Spec_ja_*.html`(5종). **온도별 영률(30 ℃/260 ℃)**이 있는 흔치 않은 표다. 등록만 하면 된다. 단 `弾性率` 에 시험모드 표기가 없어 MGC BT 와 같은 t3 판정이 필요하다.

### 5-4. Resonac 카탈로그의 남은 쪽

`弾性率` 가 있는 쪽이 p9~p16·p19~p22·p24·p28~p30·p32·p34·p36~p37·p39~p41 로 **아직 20쪽 넘게 남았다.** 20등급 이상이 같은 서식으로 대기 중이다.
**반드시 쪽마다 350 dpi 렌더 대조를 다시 해라** — 이 카탈로그는 오른쪽 세로 탭이 `pdftotext -layout` 출력에 끼어들어 **p6 에서 실제로 열 머리를 두 칸 밀었다.** 텍스트만 믿으면 679FG 의 값이 GEA 프리프레그로 들어간다.

### 5-5. 검색·전사 규율 (이 배치가 확인한 것)

- **HTML 표는 렌더할 필요가 없다 — `<td>` 를 직접 파싱하면 더 정확하다.** 대신 `colspan`/`rowspan` 을 반드시 읽어라(MGC 헤더가 `測定条件` 을 colspan=2 로 쓴다).
- **`pdftotext -layout` 이 밀리는 원인은 CJK 만이 아니다.** 이 카탈로그를 민 것은 **쪽 옆의 세로 탭 네비게이션**이었다. 사이드바가 있는 브로슈어형 PDF 는 언어와 무관하게 렌더 대조가 필요하다.
- **`ヤング率` 를 이름으로 믿지 말라는 규칙에 네 번째 층이 있다 — 같은 벤더 안에서도 표마다 다르다.** MGC 는 세 페이지 중 두 곳에서 두 행을 가르고 한 곳에서 붙인다. **벤더 단위가 아니라 표 단위로 판정해야 한다.**
- **밀도 행 이름을 확인해라.** `密度`(g/cm³, 밀도)와 `比重`·`樹脂比重`(무차원, 비중)은 다르고, 후자는 적층판이 아니라 **수지만**의 값일 수 있다. MGC 는 BT 표에 전자, FR-4 표에 후자를 쓴다.
- **일본어 표기 흔들림** — MGC 는 BT 쪽 `ポアッソン比`, FR-4 쪽 `ポアソン比`. Sumitomo 는 `引っ張り弾性率`(っ 있음). Resonac 은 `弾性率(引張モード)`. 셋 다 다르게 써야 잡힌다.
- **벤더 각주는 행 단위로 걸린다.** Resonac `*4`(0.8 mmt)는 굽힘·Z축 CTE 에만, `*5`(引張)는 CTE 에만, Sumitomo `※`(0.1 mmt)는 인장 행에만 걸린다. 각주를 표 전체에 일괄 적용하면 시편 두께가 통째로 틀린다.

---

## 산출물

- `out_fa/fa01_materials.json` — **재료 32장 · 물성 795행** (t1 782 · t3 13 · **t4 0**)
- `out_fa/_gen.py` — 생성기 + 자체검증(단위 대조 · 이름 200자 · `role`/`aliases` 필수 · t3 `grade_scope` 필수 · notes 필수). **오류 0.**
- **새로 받은 문서 0건.** 값의 출처는 전부 69차 EB 가 이미 코퍼스에 넣은 다섯 원문이다:
  - `pcb/MGC_CCL-HL832-HL972_BTResin_Lineup_ja_2026-09-09.html` (13등급)
  - `pcb/MGC_CCL-EL190T-EL230T_FR4_Lineup_ja_2026-09-09.html` (2등급)
  - `pcb/MGC_CCL-HL820WDI_ChipLED_BT_Lineup_ja_2026-09-09.html` (1등급)
  - `pcb/SumitomoBakelite_Sumilite_ELC_DoubleSided_CCL_Spec_ja_2026-09-09.html` (4등급) · `_Multilayer_PWB_Spec_ja_2026-09-09.html` (2등급)
  - `pcb/Resonac_MCL_CopperCladLaminates_Catalog_ja_2023-2024.pdf` PDF 5·6쪽 (10등급)
- 라이브 DB 는 **읽기 전용으로만** 썼다(중복 확인 · 물성정의 단위 대조 · 재료 97/1227/1228/1276 관계 확인). **쓰기 0건.**
- **동시 배치와 겹치지 않는다 — 확인했다.** 이 배치가 도는 동안 형제 배치 `out_fb`(유리 기판)·`out_fc`(회수)·`out_fd`(Prony/점탄성)·`out_ga`(솔더)가 돌았고 벤더 축이 다르다. `out_ed` 가 `Resonac` 을 언급하지만 그것은 **ANISOLM 이방성 도전 필름**(재료 1098) 축이고 CCL 이 아니다. 다섯 산출물 JSON 을 `HL832`·`HL972`·`ELC-4`·`MCL-E-`·`EL190T`·`EL230T`·`GHPL-830` 로 훑어 **등급 충돌 0건**을 확인했다.
