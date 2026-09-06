#!/usr/bin/env python3
# 65차 AD — 청봉(清峰) りん青銅 제품페이지와 일본신동협회 「伸銅品データブック(第2版)」 물리물성표에서
# C5210 포아송비(표적 4a)와 그 옆 칸들을 세운다. 그리고 179·2698 의 횡탄성계수를 같은 표에서 얻는다.
from __future__ import annotations

import json
import os

CORPUS = "/data/paper_patent_corpus/standards_appnotes/mech/"

KIYO = {
    "kind": "datasheet",
    "title": "清峰金属工業 りん青銅(Phosphor Bronze) 製品ページ — りん青銅 成分・特性一覧(物理的性質・機械的性質)",
    "publisher": "清峰金属工業株式会社 (Kiyomine Metal Industry Co., Ltd.)",
    "year": 2026,
    "url": "https://www.kiyomine.co.jp/product/bronze/",
    "local_path": CORPUS + "Kiyomine_PhosphorBronze_product_page_ja_2026-09.html",
}
BOOK = {
    "kind": "book",
    "title": ("日本伸銅協会「伸銅品データブック（第２版）」 — 各種銅及び銅合金の物理的性質（JIS合金） "
              "(WITH COPPER 배포판 cad03.pdf)"),
    "publisher": "一般社団法人日本伸銅協会 (Japan Copper and Brass Association, JCBA)",
    "url": "https://withcopper.jp/pdf/cad03.pdf",
    "local_path": CORPUS + "JCBA_Shindouhin_DataBook_2ed_cad03_PhysicalProperties_JIS_CuAlloys.pdf",
}

KIYO_NOTE = (
    "清峰金属工業 りん青銅 제품페이지의 `物理的性質` 블록. 6등급(C5212·C5191·C5102·C5111·C5240·C5210)을 "
    "열로 세우고 融点·ポアソン比·比重·導電率·熱伝導率·縦弾性係数·熱膨張係数 일곱 행을 찍는다 — **비열 행은 없다**. "
    "우리 열은 맨 오른쪽 C5210 열이다. **§43 대로 역산하지 않았다** — 인쇄된 ポアソン比 행을 그대로 옮겼다. "
    "같은 열의 다른 값이 서로 검산한다 — 融点 1020 ℃ · 比重 8.8 · 導電率 13 %IACS · 熱伝導率 63 W/(m·K) · "
    "縦弾性係数 110 kN/mm² · 熱膨張係数 18.2 ppm/K(20~300 ℃). "
    "그리고 이 열은 **일본신동협회「伸銅品データブック(第2版)」의 C5210 행과 여섯 칸이 글자까지 같다** "
    "(1020 · 8.80 · 63 · 18.2 · 110 · 0.33). 두 문서가 계보를 공유하는지는 알 수 없으나 어느 쪽도 "
    "TOKKIN 의 값과는 안 맞는다.")

DIVERGE = (
    "**64차 ZB 가 남긴 벤더 갈림을 이 값이 닫는다.** ZB 는 TOKKIN C5210 제품페이지(열전도율 79.5 W/(m·K) · "
    "전기저항 9.6 µΩ·cm = 17.96 %IACS · 탄성계수 98 GPa)와 CDA C52100(62.31 · 13 %IACS · 110.3 GPa)이 "
    "세 칸에서 갈리는 것을 Wiedemann-Franz 로 재어 '둘 다 자기정합이므로 서로 다른 Sn 함량대를 찍는다' 로 두고 "
    "CDA 쪽만 적재했다. 65차 AD 가 **셋째·넷째 문서**를 열었다 — 清峰 63/13/110 과 伸銅品データブック 63/12/110 이 "
    "둘 다 CDA 쪽에 붙는다. **네 문서 중 셋이 한 값이고 TOKKIN 만 벗어난다.** ZB 의 선택이 옳았다.")


def main() -> int:
    props_2699_k = [
        {"key": "mechanical.poisson_ratio", "value": 0.33, "unit": "1",
         "method": "measured", "tier": 1,
         "conditions": {"printed_as": "ポアソン比 0.33", "temper": "미인쇄(등급 단위로 한 값만 인쇄된다)",
                        "direction": "미인쇄(벤더가 방향을 갈라 찍지 않는다)",
                        "temperature_c": "미인쇄", "table": "物理的性質 (りん青銅 6등급 열, C5210 열)"},
         "notes": KIYO_NOTE + " **이 칸은 64차 ZB 가 `core_absent_from_vendor_sheet` 로 넘긴 자리다** — "
                  "ZB 는 TOKKIN 제품페이지 8행과 CDA C52100 에 ポアソン比 행이 없음을 확인하고 "
                  "'같은 벤더군에서 清峰은 洋白에, DOWA 는 チタン銅에 ポアソン比를 찍으므로 인청동 시트에도 있을 수 있다' "
                  "고 적어 넘겼다(§628). **그 예측이 맞았고 문은 清峰의 りん青銅 페이지였다.** "
                  "독립 확인 셋 — ① 日本伸銅協会「伸銅品データブック(第2版)」 C5210 행 ポアソン比 0.33 "
                  "② JX金属「銅合金特性一覧表」(2025-12) 각주 verbatim `いずれの合金もポアソン比は0.33。` "
                  "③ JX金属 りん青銅 제품페이지 物理的性質 ポアソン比 행 C5210 열 0.33. "
                  "네 문서가 같은 값을 찍는다. 종전 이 칸에 서 있던 t4 0.34 는 카탈로그 '구리·구리합금' 클래스 "
                  "중앙값이라 이 인쇄값이 대표값을 가져간다(§2.2 자동 대체)."},
        {"key": "mechanical.youngs_modulus", "value": 1.10e11, "unit": "Pa",
         "method": "measured", "tier": 1,
         "conditions": {"printed_as": "縦弾性係数 110 kN/mm2", "temper": "미인쇄(등급 단위로 한 값만 인쇄된다)",
                        "direction": "미인쇄(벤더가 방향을 갈라 찍지 않는다)",
                        "temperature_c": "미인쇄", "table": "物理的性質 (りん青銅 6등급 열, C5210 열)"},
         "notes": KIYO_NOTE + " " + DIVERGE + " 그리고 우리 DB 의 JCBA 실측 縦弾性係数(1/2H·H·EH 방향별 103~119 GPa)가 "
                  "110 을 감싼다 — 등방 인쇄값과 방향별 실측이 정합한다(§642)."},
        {"key": "thermal.conductivity", "value": 63.0, "unit": "W/(m*K)",
         "method": "measured", "tier": 1,
         "conditions": {"printed_as": "熱伝導率 63 W/m･K (20℃)", "temperature_c": 20,
                        "temper": "미인쇄(등급 단위로 한 값만 인쇄된다)",
                        "direction": "미인쇄(벤더가 방향을 갈라 찍지 않는다)",
                        "table": "物理的性質 (りん青銅 6등급 열, C5210 열)"},
         "notes": KIYO_NOTE + " " + DIVERGE + " 같은 열의 導電率 13 %IACS 도 CDA 와 같다 — "
                  "열전도율과 도전율이 **같은 방향으로 함께** 붙는다(§642 의 짝 검산)."},
    ]
    props_2699_b = [
        {"key": "thermal.melting_point", "value": 1153.15, "unit": "K",
         "method": "handbook", "tier": 2,
         "conditions": {"printed_as": "固 相 880 ℃", "phase_boundary": "solidus (固相)",
                        "temper": "미인쇄(합금 단위 한 값)", "direction": "미인쇄",
                        "table": "各種銅及び銅合金の物理的性質（JIS合金）, JIS C5210 / 関連ASTM C52100 행"},
         "notes": "일본신동협회 「伸銅品データブック(第2版)」 물리물성표의 C5210 행 — 融点 液相 1020 ℃ · 固相 880 ℃. "
                  "**신고 — 이 재료에 이미 서 있는 TOKKIN 인쇄값 `融点 871-982 ℃`(고상선 871 ℃, t1)는 "
                  "다른 합금의 값으로 보인다.** 근거 셋. ① TOKKIN 은 **자기 C1720(ベリリウム銅2種) 제품페이지에도 "
                  "글자까지 같은 `871-982 ℃`를 찍는다** — 두 합금의 융점이 같을 수 없다. "
                  "② 871/982 ℃ 는 1600/1800 °F 의 정확한 환산이고 그것은 CDA 가 C17200(CuBe)에 찍는 범위다 — "
                  "우리 DB 의 재료 179 가 IBC C17200 밀시트에서 받은 `Melting Temperature 870-980 C` 와 같은 자리다. "
                  "③ CDA C52100 은 `Melting Point - Liquidus 1880 °F(=1026.7 ℃) · Solidus 1620 °F(=882.2 ℃)` 를 찍고 "
                  "이 데이터북(880/1020)·清峰(1020)과 붙는다. **지우지 않았다(§565) — 옆에 세우고 신고만 한다.**"},
        {"key": "thermal.melting_point", "value": 1293.15, "unit": "K",
         "method": "handbook", "tier": 2,
         "conditions": {"printed_as": "液 相 1020 ℃", "phase_boundary": "liquidus (液相)",
                        "temper": "미인쇄(합금 단위 한 값)", "direction": "미인쇄",
                        "table": "各種銅及び銅合金の物理的性質（JIS合金）, JIS C5210 / 関連ASTM C52100 행"},
         "notes": "일본신동협회 「伸銅品データブック(第2版)」 물리물성표의 C5210 행 液相 1020 ℃. "
                  "清峰金属工業 りん青銅 페이지의 `融点 1020 ℃` 와 같고, CDA C52100 의 Liquidus 1880 °F(1026.7 ℃)와 "
                  "0.6 % 안이다. 같은 행의 고상선은 880 ℃ 다."},
        {"key": "electrical.resistivity_volume", "value": 1.44e-07, "unit": "ohm*m",
         "method": "handbook", "tier": 2,
         "conditions": {"printed_as": "体積抵抗率 144 [10⁻³μΩ・m]", "temperature_c": 20,
                        "temper": "미인쇄(합금 단위 한 값)", "direction": "미인쇄",
                        "table": "各種銅及び銅合金の物理的性質（JIS合金）, JIS C5210 / 関連ASTM C52100 행"},
         "notes": "일본신동협회 「伸銅品データブック(第2版)」 C5210 행 — 体積抵抗率 144×10⁻³ µΩ·m = 1.44e-7 Ω·m. "
                  "같은 행의 導電率 12 %IACS 와 자기검산이 선다 — 100 %IACS = 1.7241e-8 Ω·m 이므로 "
                  "1.7241e-8/0.12 = 1.437e-7 로 0.2 % 안이다(§628 의 단위 병기 검산과 같은 자리). "
                  "우리 DB 의 CDA 13 %IACS 와는 8 % 차이인데 두 문서가 같은 자리에서 갈리는 것이라 둘 다 남긴다(§662)."},
    ]
    props_2698 = [
        {"key": "mechanical.shear_modulus", "value": 4.70e10, "unit": "Pa",
         "method": "handbook", "tier": 2,
         "conditions": {"printed_as": "横弾性係数 47 kN/mm2", "temper": "미인쇄(합금 단위 한 값)",
                        "direction": "미인쇄", "temperature_c": "미인쇄",
                        "table": "各種銅及び銅合金の物理的性質（JIS合金）, JIS C7701 / 関連ASTM C77000 행"},
         "notes": "일본신동협회 「伸銅品データブック(第2版)」 C7701 행 — 縦弾性係数 125 · **横弾性係数 47** kN/mm² · "
                  "ポアソン比 0.32 · 比熱 377 J/(kg·K)(20℃) · 熱伝導率 29 W/(m·K)(20℃) · 導電率 5.5 %IACS · "
                  "比重 8.70 · 熱膨張性係数 16.7 ppm/K(20~300℃). **여섯 칸이 우리 DB 의 清峰·TOKKIN 값과 일치한다** — "
                  "ν 0.32 · 비열 377 · k 29 · 도전율 5.5 · 밀도 8.70 · CTE 16.7. 새로 열린 칸은 横弾性係数뿐이다. "
                  "§43 확인 — E/(2G)-1 = 125/(2×47)-1 = 0.330 이고 인쇄된 ν 0.32 와 3 % 안이지만 "
                  "**우리가 만든 값이 아니라 인쇄된 열을 옮긴 것이다**(만들지 않았다)."},
    ]
    props_179 = [
        {"key": "mechanical.shear_modulus", "value": 4.90e10, "unit": "Pa",
         "method": "handbook", "tier": 2,
         "conditions": {"printed_as": "横弾性係数 49 kN/mm2", "temper": "미인쇄(합금 단위 한 값)",
                        "direction": "미인쇄", "temperature_c": "미인쇄",
                        "table": "各種銅及び銅合金の物理的性質（JIS合金）, JIS C1720 / 関連ASTM C17200 행"},
         "notes": "일본신동협회 「伸銅品データブック(第2版)」 C1720 행 — 融点 液相 980 / 固相 865 ℃ · 比熱 418 J/(kg·K)(20℃) · "
                  "比重 8.26 · 熱伝導率 109~130 W/(m·K)(20℃) · 線膨張性係数 17.8 ppm/K(20~300℃) · 縦弾性係数 127 · "
                  "**横弾性係数 49** kN/mm² · ポアソン比 0.30 · 導電率 22 %IACS · 体積抵抗率 76.8×10⁻³ µΩ·m. "
                  "우리 DB 의 179 와 세 칸이 붙는다 — ν 0.30(ASM t2 와 같다) · 導電率 22 %IACS(IBC 밀시트와 같다) · "
                  "E 127(IBC 131·MakeItFrom 120 사이). 새로 열린 칸은 横弾性係数뿐이다. "
                  "**등급 동정** — 이 표는 행마다 `JIS | 関連ASTM` 두 열을 찍고 C1720 행의 関連ASTM 이 C17200 이다. "
                  "특殊金属エクセル(TOKKIN) C1720 제품페이지의 `規格` 블록도 `JIS C1720 (H3130)` 과 `UNS/CDA C17200` 을 "
                  "한 표에 찍는다 — 대응표를 우리가 지은 것이 아니다(§632·663). "
                  "**주의 — 이 표의 C1700 행과 C1720 행은 比重(8.41 대 8.26)만 다르고 나머지 아홉 칸이 글자까지 같다.** "
                  "그 아홉 칸은 등급이 아니라 CuBe 고Be 계열 단위의 값으로 읽어야 한다(§650 의 열 단위 판정). "
                  "横弾性係数 49 도 그 아홉 칸 중 하나다 — 계열값임을 조건이 아니라 이 문장으로 남긴다. "
                  "그래서 t1 이 아니라 t2 로 넣었다. 그리고 比熱 418 은 우리 DB 의 IBC 밀시트 440(t1)·ASM 420(t2)과 "
                  "갈리므로 넣지 않았다 — 이미 t1 이 서 있는 칸이다(§4.1 관문 8)."},
    ]
    doc = {"materials": [
        {"match_name": "C5210 Spring Phosphor Bronze (JIS H 3130 / UNS C52100 / CuSn8)",
         "source": KIYO, "properties": props_2699_k},
        {"match_name": "C5210 Spring Phosphor Bronze (JIS H 3130 / UNS C52100 / CuSn8)",
         "source": BOOK, "properties": props_2699_b},
        {"match_name": "C7701 Spring Nickel Silver (JIS H 3130 / UNS C77000 / CuNi18Zn27)",
         "source": BOOK, "properties": props_2698},
        {"match_name": "Beryllium Copper (spring/contact)",
         "source": BOOK, "properties": props_179},
    ]}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ad01_c5210_poisson_and_databook.json")
    json.dump(doc, open(p, "w"), ensure_ascii=False, indent=1)
    print(p, sum(len(m["properties"]) for m in doc["materials"]), "행")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
