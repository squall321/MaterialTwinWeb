#!/usr/bin/env python3
# 65차 AD — 코어 빈칸 판정 갱신과 재료 179 의 등급·tier 규약 판정을 낸다.
# 기존 사유문을 **덮지 않고 이어붙인다**(§627③·648 — 사유문은 다음 파동의 검색어다).
from __future__ import annotations

import json
import os
import sqlite3

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
                                 "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
                  "materialtwin.db")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ad06_verdicts.json")

APPEND = {
    (2694, "mechanical.youngs_modulus"): (
        "\n\n[65차 AD — **그 한 장은 존재하지 않는다.** V5(아직 못 연 층)를 닫고 구조적 부재로 바꾼다] "
        "ZA 가 표적으로 남긴 `LEXAN(TM) FR RESINS 3413R REGION EUROPE` TDS 는 **발행된 적이 없다.** "
        "SABIC 자사 등급 카탈로그(sabic.com/en/products/polymers/polycarbonate-pc/lexan-fr-resins, LEXAN FR 57등급, "
        "REVISION 21/08/2024)가 등급마다 판매지역을 찍는데 verbatim 으로 `3413R :: ASIAAMERICAS` 다 — "
        "**지역 탭이 ASIA·AMERICAS 둘뿐이고 EUROPE 탭이 없다.** 두 탭을 다 펴서 세면 `ISO 527`·`ISO 178`·"
        "`Tensile Modulus` 가 **0건**이고 전부 ASTM 서식이다. "
        "**같은 페이지·같은 세션에서 형제 둘이 양성 대조로 재현됐다** — `3412R :: EUROPEAMERICAS` 의 EUROPE 탭이 "
        "`Tensile Modulus, 1 mm/min 6000 MPa ISO 527`, `500R :: EUROPEAMERICAS` 가 `… 3300 MPa ISO 527` 을 찍는다. "
        "그 6000·3300 이 우리 DB 의 재료 313·302 값과 글자까지 같다 — **탐침이 Europe 층을 검출할 수 있음이 증명됐고 "
        "3413R 에는 그 층이 없다.** 곁증거 — plastore.it 의 file818 전량(Wayback CDX 2,741 URL)에 3413R 이 0건인데 "
        "3412R·143R·500 계열의 Europe 시트는 있다. "
        "**부재의 주어가 갈렸다** — `아직 못 연 층`이 아니라 `이 등급은 유럽에서 팔지 않아 ISO 서식 문서가 발행되지 않았다` 다"
        "(§628·676 의 지리 갈래 — 64차 ZD 가 Al 7003 에서 만난 것과 같은 모양이다). "
        "**다음 파동은 이 문을 다시 두드리지 마라.** 남은 갈래는 셋뿐이다 — ① 굴곡탄성률 6610 MPa 에서 만들지 않는다(§43) "
        "② PC-GF30 계열 대입(형제 3412R 은 GF20 6000 MPa 라 충전량이 다르다) ③ 실측. "
        "새로 확인한 것 — Asia 판 최신 리비전(honcere 배포 2019-09-20 · SABIC 라이브 2024-08-21)도 값이 같고 여전히 ASTM 이다."),
    (2559, "mechanical.poisson_ratio"): (
        "\n\n[65차 AD — **일본 창구를 열었다. 등급 행이 거기에도 없다**] ZD 가 넘긴 `日本アルミニウム協会 물성표` 를 열었다 — "
        "`aluminum.or.jp/use/materialdb/c/`(3. 物理的性質, 更新日 2023/04/01). **전권에 `7003` 이 0건이다.** "
        "협회가 등급별로 주는 표2(アルミニウム合金の物理的性質)는 열이 密度·溶解温度範囲·導電率·熱伝導度 넷뿐이고 "
        "실린 합금은 1070·1060·1050·2024·3003·4032·5182·6063·7075 아홉 종이라 7003 이 없다. "
        "표3~표6·図1 도 마찬가지다. **대신 협회가 머리표에서 전합금 공통값을 선언한다** — verbatim "
        "`アルミニウムの物理的性質は通常の場合、合金の種類や質別に関わらず、以下の値が用いられます。` 아래 "
        "密度 2.7 Mg/m³(20℃) · 縦弾性係数 70 kN/mm² · 横(せん断)弾性係数 26 kN/mm² · **ポアソン比 0.33** · "
        "線膨張係数 24×10⁻⁶/℃ 다섯 행. **65차 AD 는 이 0.33 을 t3 로 넣었다** — 선언된 범위가 알루미늄 전 합금이라 "
        "클래스값이고, 위 선언(벤더 서식에 등급별 ν 행이 없다)은 **지금도 참이다**(§639 — 벤더 부재 선언의 반증은 "
        "벤더 문서에서 온 t1 뿐이다). 닫은 근거는 값 쪽 `conditions.grade_scope` 에 있다(§676). "
        "**JIS 창구도 닫혔다** — kikakurui 미러의 JIS H 4100:2015 는 목차만이고 `7003`·`比熱` 0건, "
        "협회의 합금물성DB 호스트 `metal.matdb.jp` 는 NXDOMAIN 이다. 남은 일본 문은 유료 「アルミニウムハンドブック第8版」 제4장뿐이다."),
    (2559, "thermal.specific_heat"): (
        "\n\n[65차 AD — 일본 창구에도 등급 행이 없다. 값은 논문에서 t3 로 왔다] 위 ν 판정의 같은 조사다 — "
        "日本アルミニウム協会 공개 물성표에 `7003` 0건이고 **비열 열 자체가 표7(각종 순금속, アルミニウム Al 917 J/kg·℃)에만 있다.** "
        "일본 편찬표 둘은 7003 행을 갖고 있으나 비열 열이 없다 — 機械要素ザ・バイブル "
        "`Al-Zn-Mg 7003 T5 … 比重 2.80 · 溶融温度範囲 615~65[5] · 導電率 37 %IACS · 縦弾性係数 7.3×1000 kgf/mm²`(比熱·ポアソン比 열 없음) · "
        "toishi.info A7003-T5(縦弾性係数 73 kN/mm² 까지, 比熱 없음). "
        "**65차 AD 는 Materials 2024, 17, 4219(doi:10.3390/ma17174219)의 인쇄값 875 J/(kg·K)를 t3 로 넣었다** — "
        "저자가 `the studied 7003 aluminum alloy` 라고 지목하지만 문헌 인용값이고 같은 문장의 밀도가 2.7e3 kg/m³(7003 은 2.77~2.80)이라 "
        "**알루미늄 일반 상수로 보인다**는 사실을 그 행 notes 에 적었다. 위 선언은 지금도 참이다 — 벤더 서식에는 여전히 없다."),
    (2560, "thermal.expansion_linear"): (
        "\n\n[65차 AD — 유료벽을 확인하고, 개방 문서 하나로 CTE·열전도율만 닫았다] ZD 가 지목한 Alcoa 계보 둘을 확인했다. "
        "① **ASM Alloy Digest Al-282 는 실재하고 번호가 맞다** — `ALCOA ALUMINUM ALLOY 6013: High Strength Aluminum Alloy`, "
        "Alloy Digest 37(7), 1988-07-01, DOI 10.31399/asm.ad.al0282, PDF 경로 `dl.asminternational.org/alloy-digest/"
        "article-pdf/37/7/Al-282/367525/ad_v37_07_al-282.pdf`. 초록 verbatim — `This datasheet provides information on "
        "composition, physical properties, elasticity, and tensile properties as well as fracture toughness.` "
        "② **ASM Vol.2B 6013 장**도 실재한다 — `6013: High-Strength Al-Mg-Si-Cu Alloy`, DOI 10.31399/asm.hb.v02b.a0006711, pp.379-381. "
        "**둘 다 하드 유료벽 + Cloudflare 봇벽이다** — UA 유무 무관 403(5.6~5.9 KB `Just a moment…`), Playwright 도 통과 못 한다. "
        "`ad_v37_07_al-282`·`asm.ad.al0282` 로 검색해도 공개 미러가 0건이다. **가격 표시가 없는 구독벽이라 개별 구매도 안 된다.** "
        "③ Alcoa 계보 문서를 하나 더 찾았다 — `6013 Power Plate™`(Alcoa Global Rolled Products, 2012-10, Wayback 305,975 B). "
        "**그 시트에도 물리물성 블록이 없다**(`physical|thermal|conductiv|expansion|specific heat|density` 적중 1건이고 그것은 "
        "`Electrical conductivity … certifications are also available, on request` 라는 문장이다). "
        "**65차 AD 는 AZoM 6013-T8 페이지(2013-04-25)에서 CTE 23.4 µm/m°C 와 열전도율 164 W/mK 를 t3 로 넣었다** — "
        "쓴 근거는 열 단위 검산이다(§650): 같은 표의 밀도 2.71 g/cm³ 가 우리가 이미 가진 MIL-HDBK-5J 의 0.098 lb/in³ 와 0.1% 안이고, "
        "세 행이 전부 단위 병기로 자기검산된다. **비열은 여전히 못 닫았다** — 개방 문서 어디에도 6013 의 비열 행이 없다."),
    (2560, "thermal.conductivity"): (
        "\n\n[65차 AD] 위 `thermal.expansion_linear` 판정과 같은 조사다. AZoM 6013-**T8** 열전도율 164 W/mK 를 t3 로 넣었다. "
        "**조질축은 안 닫혔다** — 알루미늄 열전도율은 조질에 15~19% 갈리므로(ZD: Hydro 6082 T4 150 / T6 172 · "
        "Kaiser 7075 T6 130 / T73 155) 이 값을 T6 값으로 읽으면 안 된다. 그 경고를 값 쪽 `conditions.grade_scope` 에 박았다."),
    (2560, "thermal.specific_heat"): (
        "\n\n[65차 AD — **이 칸만 못 닫았다.** 개방 문서에 6013 비열 행이 존재하지 않는다] 위 두 판정의 같은 조사에서 "
        "6013 의 비열을 찍는 개방 문서를 하나도 못 찾았다. 연 문을 이름으로 적는다 — AZoM 6013-T8(물리·열 블록에 C 행 자체가 없다) · "
        "Alcoa 6013 Power Plate 2012(물리물성 블록 없음) · Alcoa Tech Fact Sheet rev.5/07(58차 TD 가 확인) · "
        "Wikipedia 6013(물성표 없음) · AmesWeb 알루미늄 비열표(`6013` 0건) · MMPDS-12 목차(3.6.1 6013 장은 있으나 본문 비공개) · "
        "NIST materialsdata `Properties of Wrought Aluminum and Aluminum Alloys`(항목 404, 저장소에서 사라졌다). "
        "**안 쓴 것을 이름으로 적는다** — MakeItFrom 6013 은 T4·T6·T651 세 페이지가 바이트까지 같고(Cp 900 · k 150 · α 23 · ν 0.33) "
        "metalzenith 는 비열 `~900 J/kg·K` 옆에 스스로 `Typical value for aluminum alloys at room temperature` 라고 적는다 — "
        "둘 다 조질 의존이 없는 파생값이라 넣지 않았다(§616). **다음 문은 하나뿐이다 — ASM Alloy Digest Al-282 유료 PDF.**"),
}

NEW = {
    (2700, "thermal.specific_heat"): (
        "[65차 AD] **C1990(ばね용 チタン銅)의 비열을 찍는 서식이 존재하지 않는다.** 64차 ZB 가 문 셋(DOWA YCuT-M · "
        "CDA C19900 · TOKKIN)에서 부재를 확인하고 `JX金属·古河電工·三菱伸銅·JIS 정본` 을 안 연 문으로 인계했다. "
        "65차 AD 가 그 넷을 포함해 **물리물성 블록 열둘을 열었고 전부 比熱 행이 없다.** 서식 이름과 행 수를 적는다(§676) — "
        "① JX金属 표2「C1990の物理的性質」 6행(電気伝導度 12 %IACS · 固有抵抗 144 nΩ·m · 熱伝導度 54 W/mK · 線膨張係数 18.6e-6/K · "
        "縦弾性係数 127 GPa · 密度 8.70) ② JX C1990HC 6행 ③ JX C1990HP箔 6행 ④ JX Advanced Metals EN `Cu-Ti Physical Properties` 4행"
        "(Specific Gravity · Modulus of Elasticity · Electrical Conductivity · **Poisson's Ratio 0.33**) "
        "⑤ JX EN `Table 2. Physical properties of C1990(HP)` 6행 ⑥ JX「銅合金特性一覧表」(2025-12) 6열 "
        "⑦ DOWA YCuT-M 8행 ⑧ CDA C19900(물성 블록 자체가 없다) ⑨ toishi.info C1990(물리표 없음) ⑩ nmmjx-dc.com チタン銅(없음) "
        "⑪ Total Applied Material C1990 條(JS 렌더, 원본에 `比熱`·`比热` 0건) ⑫ 日本伸銅協会 伸銅品板条材料特性DB(기계적성질만). "
        "**JIS H 3130:2018 정본도 닫혔다** — kikakurui 미러 전문을 열어 `物理|比熱|熱的|弾性係数|ヤング` 적중 **0건**이다"
        "(조항 구성이 化学成分·機械的性質·寸法·製造方法·試験뿐이다). 즉 **규격 쪽에는 애초에 물리물성이 없다.** "
        "**결정적인 자리** — 일본신동협회 「伸銅品データブック(第2版)」 물리물성표는 **比熱 열을 갖고 있는데 C1990 행이 없다**"
        "(수록 등급 C1700·C1720·C5191·C5210·C5212·C5441·C6140·C6191·C6241·C6301·C7060·C7100·C7150·C7451·C7521·C7541·C7701). "
        "**행이 있는 서식에 이 등급 층이 없다** — 64차 ZD 가 Al 7003 에서 만난 것과 같은 모양이다(§628·676). "
        "**안 한 것** — 같은 표의 이웃 고Cu 등급(C1700·C1720) 비열 418 J/(kg·K) 을 옮기지 않았다. C1990 은 Cu-3Ti 라 다른 계열이다(§586). "
        "다음 문은 유료 「伸銅品データブック」 정본의 チタン銅 절이거나 JX金属의 비공개 기술자료다."),
}

IDENT = (
    "[65차 AD 판정] **재료 179 는 UNS C17200 = JIS C1720(ベリリウム銅2種) 이다.** 64차 ZB 가 "
    "`같은 C17200 출처를 IBC 시트는 t1, CDA 는 t3 로 담아 한 재료 안에서 규약이 갈려 있다`(§612)고 신고하고 "
    "JCBA 실측 적재를 보류한 자리를 이 배치가 닫는다. 근거 넷. "
    "① **카탈로그가 스스로 등급을 적고 있다** — `attributes.material_class` = `CuBe C17200 spring alloy`. "
    "② **출처를 세었다(§645)** — 179 에 붙은 출처 일곱이 전부 C17200 문서다(IBC Advanced Alloys C17200 밀시트 · "
    "CDA alloy C17200 · Smiths Metal Centres `Alloy 25 (C17200)` · MakeItFrom `UNS C17200` · matmake C17200 · "
    "Lai 2023 `C17200 Beryllium Copper` · Zhang 2022 `QBe2.0 and C17200`). **경쟁 등급 문서가 0건이다.** "
    "③ **물성 열이 후보를 배제한다(§621)** — 이 레코드의 導電率은 22 %IACS 이고 인장은 1140~1380 MPa 인데, "
    "CDA 적재 배치가 걱정한 저Be 고도전 등급(C17410·C17510)은 45~60 %IACS · 690~830 MPa 다. **두세 배 갈린다.** "
    "④ **JIS↔UNS 대응을 문서가 인쇄한다(§632·663)** — 特殊金属エクセル(TOKKIN) C1720 제품페이지 `規格` 블록이 "
    "`JIS C1720 (H3130)` 과 `UNS/CDA C17200` 을 한 표에 찍고, 日本伸銅協会「伸銅品データブック(第2版)」 물리물성표가 "
    "`JIS C1720 | 関連ASTM C17200` 행을 찍는다. 조성도 같다(TOKKIN `主要成分 CuBe1.9` · UNS C17200 Be 1.80~2.00). "
    "**이름을 고치지 않았다** — `material.name` 은 병합기의 자연키라 바꾸면 dev↔운영 대응이 끊긴다(파이프라인 §5·§7.1). "
    "대신 판정을 `verdict_` 접두어 attribute 에 박아 운영까지 전파시킨다(CURATION_PREFIXES · §608 의 자리·독자·전파).")

TIERCONV = (
    "[65차 AD 판정] **재료 179 의 tier 는 재료 이름이 아니라 문서 종류가 정한다.** 등급 동정이 닫혔으므로(`verdict_grade_identity`) "
    "`이름에 UNS 가 없으니 C17200 문서는 등급 불일치 대체값이다` 라는 규약은 성립하지 않는다. 이 재료의 규약은 §2.1 그대로다 — "
    "**생산자 밀시트·벤더 제품페이지 t1 · 핸드북/규격/공인DB/협회 편찬 데이터북 t2 · 유통사 재인쇄·집계사이트·2차 인용 t3 · "
    "계산·가정 t4.** 조질은 tier 가 아니라 `conditions.temper` 로 가른다(§586) — 한 재료 안에 AT(TF00)·TH02·TH04·1/4HM·HM 이 "
    "공존하는 것은 정상이고, `integrity_check` 의 항복>인장 검사도 조질을 조인축에 갖고 있다. "
    "이 판정 아래 65차 AD 가 넣은 것 — JCBA 材料特性DB 표 1.2 의 C1720 조질(1/4HM·HM)×방향(L.D./45°/T.D.) 실측 32행을 **t1** 로, "
    "JCBA「伸銅品データブック(第2版)」의 横弾性係数 49 kN/mm² 를 **t2** 로, 같은 DB 의 C1720-HM 応力緩和 그림 3장 144행을 "
    "**t1 digitized** 로 세웠다. "
    "**신고(고치지 않았다 — 결함은 신고만)** — 이 규약으로 보면 기존 행 둘이 어긋나 있다. "
    "㉠ CDA alloy C17200 피로강도 3행이 t3 인데 사유가 `target name does not carry a UNS number` 다 — 그 사유는 이제 무효이고 "
    "CDA 는 §2.1 이 t2 로 명시한 공인DB다. ㉡ MakeItFrom `UNS C17200` 5행(E 120 GPa · 밀도 8250 · k 110 · HRC 43 · 인장 1380)이 "
    "**t2** 인데 집계 사이트라 t3 여야 한다(브리프가 makeitfrom 을 클래스값으로 못박은 자리다). "
    "**둘 다 이 배치가 안 고쳤다 — 값·조건·출처를 안 건드리는 tier 재판정은 다음 파동의 몫이다.**")


def main() -> int:
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    cur = {mid: json.loads(a or "{}") for mid, a in
           c.execute("select id,attributes from material where id in (179,2559,2560,2694,2699,2700)")}
    out = []
    for mid in (2559, 2560, 2694):
        v = dict(cur[mid].get("core_absent_from_vendor_sheet") or {})
        upd = {}
        for (m, k), extra in APPEND.items():
            if m == mid:
                assert k in v, (mid, k)
                upd[k] = v[k] + extra
        out.append({"material_id": mid, "name": None, "core_absent_from_vendor_sheet": upd})
    out.append({"material_id": 2700, "name": None,
                "core_absent_from_vendor_sheet": {"thermal.specific_heat": NEW[(2700, "thermal.specific_heat")]}})
    out.append({"material_id": 2699, "name": None, "core_absent_from_vendor_sheet": None})
    out.append({"material_id": 179, "name": None,
                "verdict_grade_identity": "UNS C17200 = JIS C1720 (ベリリウム銅2種), age/mill-hardened CuBe",
                "verdict_grade_identity_basis": IDENT,
                "verdict_tier_convention": TIERCONV})
    for r in out:
        r.pop("name")
    json.dump({"batch": "65차 AD", "verdicts": out}, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(OUT, len(out), "종")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
