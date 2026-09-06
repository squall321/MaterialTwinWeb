#!/usr/bin/env python3
# JCBA 표 1.2(bjr001006) 의 **C1720(ベリリウム銅2種)** 조질×방향 실측을 재료 179 에 세운다(65차 AD).
# 64차 ZB 는 같은 표의 C1990 만 넣고 C1720 은 **규약이 갈려 있다는 이유로** 보류했다 — 그 규약을 이 배치가 정했다.
# 열 배정·조건 어휘·notes 골격은 ZB 가 같은 표에서 세운 계보를 글자 그대로 따른다(§612).
from __future__ import annotations

import json
import os

SRC = {
    "kind": "database",
    "title": ("一般社団法人日本伸銅協会 伸銅品板条材料特性データベース — 表1.2 機械的性質 C1720·C1990 一覧表 "
              "(試験方法 2.4 は method/bjm001.pdf·bjm002.pdf)"),
    "publisher": "一般社団法人日本伸銅協会 (Japan Copper and Brass Association, JCBA)",
    "url": "https://www.copper-brass.gr.jp/data/file/banjou/result/bjr001006.pdf",
    "local_path": ("/data/paper_patent_corpus/standards_appnotes/mech/"
                   "JCBA_banjou_bjr001006_Table1-2_MechProps_C1720_C1990.pdf"),
}
TS = "JIS Z 2241 / JIS Z 2201 (JIS 5号)"
DIRS = [("L.D.", "MD (rolling direction)", "L.D. (圧延方向に平行)"),
        ("45", "45 deg to rolling direction", "45° (圧延方向に45度)"),
        ("T.D.", "TD (transverse to rolling)", "T.D. (圧延方向に直角)")]

# 조질 → (두께 mm, HV, 結晶粒度 mm, {방향: (引張, 耐力, 伸び%, n値, 縦弾性 kN/mm2, ばね限界値, たわみ係数, 3본원값)})
DATA = {
    "1/4HM": (0.30, 271, 0.015, {
        "L.D.": (851, 647, 16.3, 0.16, 133, 593, 100,
                 "引張 852/849/852 · 耐力 649/647/644 · 伸び 16.0/16.8/16.2"),
        "45":   (828, 632, 17.5, 0.14, 121, 604, 99,
                 "引張 826/832/826 · 耐力 636/636/624 · 伸び 17.7/17.5/17.4"),
        "T.D.": (839, 646, 16.7, 0.12, 136, 638, 111,
                 "引張 841/837/839 · 耐力 648/644/647 · 伸び 16.7/16.4/17.0"),
    }),
    "HM": (0.32, 334, 0.020, {
        "L.D.": (1015, 861, 11.1, 0.09, 118, 806, 104,
                 "引張 1023/1027/996 · 耐力 867/861/853 · 伸び 11.4/10.8/11.1"),
        "45":   (974, 857, 13.2, 0.08, 115, 829, 101,
                 "引張 975/979/969 · 耐力 857/862/853 · 伸び 13.0/13.2/13.5"),
        "T.D.": (1018, 815, 12.1, 0.10, 134, 882, 115,
                 "引張 1017/1018/1019 · 耐力 822/821/803 · 伸び 12.0/12.0/12.3"),
    }),
}

COLS = ("열 배정은 `pdftotext -bbox-layout` x좌표로 확정했다(브리프 606·671) — 引張強さ 195-226 · 耐力 240-266 · "
        "伸び 272-293 · 硬さHV 299-320 · 結晶粒度 331-349 · n値 362-378 · ばね限界値 389-421 · "
        "縦弾性係数 430-461 · たわみ係数 472-503. 64차 ZB 가 **같은 표의 C1990 행**을 같은 배정으로 읽었고 "
        "그 값(EHM 1012/1020/1038 · 1/4HM 897/876/855)이 이 배치의 재판독과 글자까지 일치한다 — 열 배정이 "
        "두 배치에서 재현됐다(브리프 600 형제 검산).")
COND = ("JCBA 시험조건(bjm001.pdf 2.4.1) — 引張試験 JIS Z 2241/Z 2201 준거, 100 kN 유압만능시험기, JIS 5호 시험편, "
        "인장속도 25 mm/min, 신율 계측은 차동트랜스식 신율계(크로스헤드 변위가 아니다 — 브리프 604 의 "
        "컴플라이언스 편향이 없다), 耐力은 0.2% 오프셋. 硬さ JIS Z 2244 HV0.3(시험하중 2.942 N). "
        "시험편은 L.D./45°/T.D. 각 n=3 이고 표가 3본의 平均値을 인쇄한다 — 우리가 만든 평균이 아니다. "
        "bjm001 표 1.1 이 C1720 을 `ベリリウム銅2種` 로 적고 대상 조질을 1/4HM·HM 둘로 규정한다.")
IDENT = ("**등급 동정** — 재료 179 는 이름에 UNS 가 없지만 `attributes.material_class` 가 `CuBe C17200 spring alloy` 로 "
         "스스로 등급을 적고 있고, 179 에 붙은 출처 일곱(IBC C17200 밀시트·CDA C17200·Smiths Alloy 25(C17200)·"
         "MakeItFrom UNS C17200·matmake C17200·Lai 2023 C17200·Zhang 2022 QBe2.0 대 C17200)이 **전부 C17200 문서**다"
         "(§645 — 세어서 확인했다). 그리고 JIS C1720 ↔ UNS C17200 대응은 우리가 지은 것이 아니라 문서가 인쇄한다 — "
         "特殊金属エクセル(TOKKIN) C1720 제품페이지의 `規格` 블록이 `JIS C1720 (H3130)` 과 `UNS/CDA C17200` 을 한 표에 찍고, "
         "일본신동협회 「伸銅品データブック(第2版)」 물리물성표가 `JIS C1720 | 関連ASTM C17200` 행을 찍는다(§632·663). "
         "조성도 같다 — TOKKIN `主要成分 CuBe1.9`, UNS C17200 Be 1.80~2.00. "
         "그리고 179 의 기존 導電率 22 %IACS · 引張 1140~1380 MPa 는 저Be 고도전 등급(C17410/C17510 = 45~60 %IACS · "
         "690~830 MPa)과 **두세 배 갈린다** — 도전율 열 하나가 그 후보를 배제한다(§621).")
TIER = ("**tier 규약** — 이 배치가 정했다. 등급 동정이 닫혔으므로 tier 는 재료 이름이 아니라 **문서 종류**가 정한다 "
        "(§2.1) — 생산자 밀시트/제품페이지 t1 · 핸드북·규격·공인DB·협회 편찬 데이터북 t2 · 유통사 재인쇄·집계사이트·"
        "2차 인용 t3 · 계산·가정 t4. JCBA 材料特性DB 는 협회가 **자기 시편을 직접 잰 시험결과**(조질×방향 n=3, "
        "시험조건 문서 공개)라 t1 이다 — 64차 ZB 가 같은 표의 C5210·C1990·C7701 을 t1 로 세운 계보를 그대로 따른다(§612).")


def main() -> int:
    props = []
    for temper, (th, hv, gs, dirs) in DATA.items():
        for tag, dnorm, dverb in DIRS:
            uts, ys, el, n, e, kb, tw, raw = dirs[tag]
            row = (f"C1720 {temper} 材 {tag} 방향, 원문 표 1.2 의 平均値 행. 같은 행이 함께 인쇄하는 값 — "
                   f"引張強さ {uts} · 耐力 {ys} · 伸び {el}% · HV {hv} · 結晶粒度 {gs} mm · n値 {n} · "
                   f"ばね限界値 {kb} N/mm2 · 縦弾性係数 {e} kN/mm2 · たわみ係数 {tw} kN/mm2. "
                   f"3본 원값 — {raw}. ")
            base = {"temper": temper, "direction": dnorm, "direction_verbatim": dverb,
                    "thickness_mm": th, "grain_size_mm": gs, "test_standard": TS,
                    "temperature_c": "미인쇄(실온 시험)"}
            note = row + COLS + " " + COND + " " + IDENT + " " + TIER
            props += [
                {"key": "mechanical.tensile_strength", "value": uts * 1e6, "unit": "Pa",
                 "method": "measured", "tier": 1,
                 "conditions": {**base, "statistic": "3본 평균(平均値)", "printed_as": f"{uts} N/mm2"},
                 "notes": note},
                {"key": "mechanical.yield_strength", "value": ys * 1e6, "unit": "Pa",
                 "method": "measured", "tier": 1,
                 "conditions": {**base, "statistic": "3본 평균(平均値)", "printed_as": f"{ys} N/mm2",
                                "offset_pct": 0.2},
                 "notes": note},
                {"key": "mechanical.elongation_at_break", "value": round(el / 100.0, 5), "unit": "1",
                 "method": "measured", "tier": 1,
                 "conditions": {**base, "statistic": "3본 평균(平均値)", "printed_as": f"{el} %",
                                "gauge_length": "JIS 5号 시험편(표점거리 50 mm)"},
                 "notes": note},
                {"key": "mechanical.monotonic_strain_hardening_exponent", "value": n, "unit": "1",
                 "method": "measured", "tier": 1,
                 "conditions": {**base, "statistic": "방향별 단일 인쇄값", "printed_as": f"n値 {n}"},
                 "notes": note},
                {"key": "mechanical.youngs_modulus", "value": e * 1e9, "unit": "Pa",
                 "method": "measured", "tier": 1,
                 "conditions": {**base, "statistic": "방향별 단일 인쇄값",
                                "printed_as": f"縦弾性係数 {e} kN/mm2",
                                "modulus_type": "인장 縦弾性係数(방향별 1개 값, 시편별 아님)"},
                 "notes": note + (" 브리프 604 검산 — CuBe C17200 의 E 통용대역은 125~131 GPa 이고 이 표의 방향별 값이 "
                                  "115~136 kN/mm2 다. 같은 재료의 등방값 셋(IBC 밀시트 131 · 伸銅品データブック 127 · "
                                  "MakeItFrom 120)이 전부 그 안이라 대역은 옳고 방향값이 그것을 감싼다. "
                                  "이방성 순서가 두 조질에서 같다 — T.D.(136·134) > L.D.(133·118) > 45°(121·115) 로 "
                                  "45° 가 항상 최소다. C7701·C5210·C1990 에서 본 것과 같은 압연 집합조직 패턴이다(§642).")},
            ]
        props.append(
            {"key": "mechanical.hardness_vickers", "value": hv, "unit": "HV",
             "method": "measured", "tier": 1,
             "conditions": {"temper": temper, "thickness_mm": th,
                            "direction": "미인쇄(조질 단위로 한 값만 인쇄된다)",
                            "test_standard": "JIS Z 2244, HV0.3, 시험하중 2.942 N",
                            "grain_size_mm": gs, "printed_as": f"{hv} HV(0.5)"},
             "notes": (f"C1720 {temper} 材, 원문 표 1.2 의 硬さ 열. 이 값은 방향별로 나뉘지 않고 조질·두께 단위로 "
                       "한 번만 인쇄된다(세 방향 블록의 세로 중앙에 놓여 있다). " + COLS + " " + COND + " " + IDENT + " " + TIER)})
    doc = {"materials": [{"match_name": "Beryllium Copper (spring/contact)",
                          "source": SRC, "properties": props}]}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ad03_179_c1720_jcba_table12.json")
    json.dump(doc, open(p, "w"), ensure_ascii=False, indent=1)
    print(p, len(props), "행")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
