#!/usr/bin/env python3
# JCBA 応力緩和特性 그림 다섯 장을 적재기 JSON 으로 바꾼다(65차 AD).
#
# 값의 성격 — 그림에서 읽었으므로 `method="digitized"` 다(브리프 447·448).
#   다만 래스터 디지타이즈가 아니라 **벡터 경로의 마커 좌표**라 판독 오차가 축 눈금 양자화(0.24 pt)뿐이다.
# 저장하는 양 — 원문이 찍는 것은 `応力緩和率(%) = δt/δ0 x 100`(bjm004 식 4-3) 이고
#   카탈로그 키 `mechanical.property_retention` 은 **유지율**이라 `1 - 応力緩和率/100` 을 넣는다.
#   재료 92 가 같은 키에 같은 변환(원문이 열화율만 인쇄)을 이미 해 두었다 — 그 계보를 따른다(§612).
#   인쇄값은 `conditions.printed_value_pct` 에 그대로 남긴다(§598).
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ad_jcba_relax_extract import extract          # noqa: E402

CORPUS = "/data/paper_patent_corpus/standards_appnotes/mech"
BASE = "https://www.copper-brass.gr.jp/data/file/banjou/result/"

# pdf id → (재료명, 조질, 그림번호 범위, 코퍼스 파일명)
JOBS = [
    ("bjr004006", "C5210 Spring Phosphor Bronze (JIS H 3130 / UNS C52100 / CuSn8)", "H",
     "JCBA_banjou_bjr004006_StressRelaxation_C5210-H.pdf"),
    ("bjr004007", "C5210 Spring Phosphor Bronze (JIS H 3130 / UNS C52100 / CuSn8)", "EH",
     "JCBA_banjou_bjr004007_StressRelaxation_C5210-EH.pdf"),
    ("bjr004008", "Beryllium Copper (spring/contact)", "HM",
     "JCBA_banjou_bjr004008_StressRelaxation_C1720-HM.pdf"),
    ("bjr004009", "C1990 Spring Titanium Copper (JIS H 3130 / UNS C19900)", "EHM",
     "JCBA_banjou_bjr004009_StressRelaxation_C1990-EHM.pdf"),
    ("bjr004010", "C7701 Spring Nickel Silver (JIS H 3130 / UNS C77000 / CuNi18Zn27)", "H",
     "JCBA_banjou_bjr004010_StressRelaxation_C7701-H.pdf"),
]
DIRN = {"L.D.": ("MD (rolling direction)", "L.D. (圧延方向に平行)"),
        "T.D.": ("TD (transverse to rolling)", "T.D. (圧延方向に直角)")}
STRESS = {"耐力値×0.8": "耐力値×0.8 (0.2% 내력의 80%)",
          "250N/m㎡": "250 N/mm2", "500N/m㎡": "500 N/mm2"}
METHOD = ("JCBA T309:2001(仮) 銅および銅合金薄板条の曲げによる応力緩和試験方法 準拠 · 片持ち梁ねじ式 · "
          "試験片 幅10mm×長さ60mm · スパン長さ 30mm 一定 · n=3 (bjm004.pdf 2.4.4.1)")


def sig3(x: float) -> float:
    if x == 0:
        return 0.0
    from math import floor, log10
    return round(x, -int(floor(log10(abs(x)))) + 2)


def main() -> int:
    out = []
    for pid, matname, temper, fname in JOBS:
        charts = extract(os.path.join(CORPUS, fname))
        props = []
        for ch in charts:
            title = ch["title"]
            tc = int(title.split("(")[-1].split("℃")[0])
            # 시간축: 여섯 계열이 같은 x 를 공유한다 — 평균해 판독잡음을 줄이고 유효숫자 3자리로 적는다.
            hrs = [sig3(sum(s["points"][i]["hours"] for s in ch["series"]) / len(ch["series"]))
                   for i in range(8)]
            for s in ch["series"]:
                lab = s["series"]
                stress = next(v for k, v in STRESS.items() if lab.startswith(k))
                d = DIRN["L.D." if lab.endswith("L.D.") else "T.D."]
                for i, p in enumerate(s["points"]):
                    pct = p["relaxation_pct"]
                    props.append({
                        "key": "mechanical.property_retention",
                        "value": round(1.0 - pct / 100.0, 5), "unit": "1",
                        "method": "digitized", "tier": 1,
                        "conditions": {
                            "property": "mechanical.residual_stress (굽힘으로 부하한 초기 응력의 잔존율)",
                            "aging_hours": hrs[i],
                            "temperature_k": round(tc + 273.15, 2),
                            "temper": temper,
                            "direction": d[0],
                            "direction_verbatim": d[1],
                            "applied_stress": stress,
                            "test_standard": METHOD,
                            "printed_quantity": "応力緩和率(%) = δt/δ0 × 100 (bjm004.pdf 식 4-3)",
                            "printed_value_pct": pct,
                            "figure": title,
                            "readout": ("벡터 그림의 마커 좌표에서 읽었다(래스터 디지타이즈 아님). "
                                        "축 격자 0.24 pt 양자화 = 세로 ±0.14 %p · 가로 ±0.5 %"),
                        },
                        "notes": (
                            f"{title} 의 계열 `{lab}`. **원문이 찍는 것은 応力緩和率 {pct:.2f} %** 이고 "
                            f"이 행의 값은 그 여집합인 잔존율 {1.0 - pct / 100.0:.5f} 다 — "
                            "키 `mechanical.property_retention` 이 유지율이라 그렇다(재료 92 의 같은 변환 계보). "
                            "그림은 벡터라 마커 중심 좌표가 스트림에 그대로 있고, 축은 격자선 10개(0~100 %)와 "
                            "십년눈금 3개(1·10·100·1000 h)로 잡았다. 여섯 계열의 x 가 같은 시각을 가리키므로 "
                            "평균해 유효숫자 3자리로 적었다 — 눈금 스냅(5·20·72·100·200·336·500·1000 h 로 "
                            "반올림)은 하지 않았다. 시험조건은 bjm004.pdf 2.4.4 이고 응력 산출식은 "
                            "σ = 3·E·h·δ0/(2·ls²)(식 4-1) 다."),
                    })
        figs = " / ".join(c["title"] for c in charts)
        out.append({
            "match_name": matname,
            "source": {
                "kind": "database",
                "title": ("一般社団法人日本伸銅協会 伸銅品板条材料特性データベース — 2.4.4 応力緩和特性 "
                          f"{figs} (試験方法は method/bjm004.pdf)"),
                "publisher": "一般社団法人日本伸銅協会 (Japan Copper and Brass Association, JCBA)",
                "url": BASE + pid + ".pdf",
                "local_path": os.path.join(CORPUS, fname),
            },
            "properties": props,
        })
    doc = {"materials": out}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ad02_jcba_stress_relaxation.json")
    json.dump(doc, open(p, "w"), ensure_ascii=False, indent=1)
    print(p, sum(len(m["properties"]) for m in out), "행")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
