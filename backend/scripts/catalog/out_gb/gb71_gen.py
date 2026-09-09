# 71차 GB — MGC BT 13등급 영률 t3 승격 판정을 정정 JSON 으로 굳힌다 (라이브 DB 는 읽기 전용)
#
# 사용: python3 backend/scripts/catalog/out_gb/gb71_gen.py
#   라이브 DB 에서 13행의 현재 conditions·notes 를 읽어 판정문을 덧붙인 정정 문서를 만든다.
#   등급은 **바꾸지 않는다**(t3 유지). 바꾸는 것은 conditions.verdict_71gb 와 notes 뿐이다.
import json
import sqlite3
from pathlib import Path

DB = "file:/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db?mode=ro"
OUT = Path(__file__).resolve().parent

VERDICT_COND = (
    "71차 GB 판정 — **유지(t3). 승격하지 않는다.** 70차 FA 가 넘긴 t1 승격 근거"
    "(같은 MGC 서식의 led.html·fr4.html 이 두 행을 가른다)를 검증했더니 반대 방향을 가리켰다. "
    "① MGC 가 실제로 가르는 폭은 led.html 이 23/22 vs 25/24 = 8.3~9.1 % 다. "
    "이 표의 인쇄 자릿수는 정수 GPa(유효숫자 2자리)이고 BT 13등급 값은 21~34 GPa 라 "
    "8.3 % 는 1.74~2.82 GPa — **정수 두세 칸**이다. 그런 차이가 13등급 전부에서 같은 정수로 "
    "떨어질 확률은 0 이다. ② fr4.html EL190T 의 27 vs 26 은 3.8 % 로 반올림 반폭(0.5 GPa)의 "
    "두 배를 겨우 넘는 한 칸 차이라 '가른다'의 증거로는 약하다 — 그 폭을 BT 에 적용해도 "
    "13등급 전부 동일할 확률이 1e-9 미만이다. ③ 라이브 DB 의 벤더 확정쌍 52건(Panasonic 14 · "
    "Sumitomo 12 · Resonac 20 · AGC Taconic 2 · MGC FR4/LED 는 별도)에서 굽힘/인장 비 중앙값은 "
    "1.286 이고 동일값은 5.8 %(3/52, 전부 Sumitomo)뿐이다. **따라서 이 표의 동일값은 "
    "'두 물성이 실제로 같다'가 아니라 '한 값을 두 칸에 인쇄했다'로 읽는 것이 옳다.** "
    "시험모드는 여전히 미확정이므로 test_mode 는 unconfirmed 를 유지한다."
)

VERDICT_NOTE = (
    "\n\n[71차 GB 판정 — 유지, 승격하지 않는다] 70차 FA 가 넘긴 물음('led.html·fr4.html 이 "
    "두 행을 가르므로 BT 13행도 t1 로 올릴 수 있는가')에 대한 답은 **아니오**다. "
    "새 문서 셋을 더 열었다 — MGC 영문판 `eng/products/sc/btprint/lineup/hfbt.html`(행 이름이 "
    "`Flexural Modulus`/`Young's Modulus` 이고 값은 일문판과 같은 13/13 동일, 조건열 이름이 "
    "`Measurement Method` 인데 두 기계행 모두 **비어 있다**), 영문 `led.html`, 그리고 배포본 PDF "
    "`pcbapeak.com/.../CCL-HL832NX.pdf`(영문 페이지의 인쇄 캡처라 새 정보 0). "
    "`btprint` 섹션 네 쪽 전수에서 `JIS`·`ASTM`·`IPC`·`試験方法`·`測定方法` 적중은 **0 회**다. "
    "즉 MGC 는 어느 판에도 이 행의 시험규격을 밝히지 않는다. "
    "반올림 자릿수 분석: 인쇄값은 정수 GPa(유효숫자 2자리, 반올림 반폭 0.5 GPa)이고 BT 값은 "
    "21~34 GPa 다. MGC 자신이 led.html 에서 보여 준 두 행의 차이 8.3~9.1 % 를 여기 대면 "
    "1.74~2.82 GPa 로 **정수 두세 칸**이라 13등급 전부가 같은 정수로 떨어지는 일은 일어날 수 없다. "
    "fr4.html EL190T 의 3.8 %(27 vs 26) 를 대도 등급마다 같은 정수일 확률이 0~0.20 이라 "
    "13등급 전부는 1e-9 미만이다. 다른 벤더 실측(라이브 DB 확정쌍 52건): 굽힘/인장 비 중앙값 "
    "1.286, 최소 1.000, 최대 1.912, 동일값 3건(5.8 %, 전부 Sumitomo ELC-4762 ヨコ·ELC-4765 タテ/ヨコ), "
    "**인장이 굽힘보다 큰 사례 0건**. 대표 실측 — Panasonic R-1766 굽힘 23/21 vs 인장 17.8/16.5, "
    "Resonac MCL-E-705G 굽힘 32-34 vs 인장 20-22, Sumitomo ELC-4970 굽힘 18/16 vs 인장 14/12. "
    "결론: 이 표의 `ヤング率` 는 독립 측정으로 보기 어렵고 `曲げ弾性率` 를 복사한 칸일 가능성이 크다. "
    "그러나 **문서가 그것을 말하지 않으므로 값을 지우지도 굽힘으로 옮기지도 않았다** — t3 와 "
    "`test_mode: unconfirmed` 를 유지한다. 이 13행은 삭제 후보로 보고서에 적었고 판단은 사람 몫이다"
    "(같은 수가 `mechanical.flexural_modulus` t1 로 이미 들어 있어 지워도 잃는 정보가 없다). "
    "다음 파동은 이 물음을 다시 묻지 마라 — 새 결정 증거는 **MGC 가 시험규격이나 시편 형상을 "
    "밝힌 판**뿐이고, 2026-09-09 현재 그런 판은 공개 웹에 없다."
)

REASON = ("71차 GB 판정 — 70차 FA 가 넘긴 t3→t1 승격 물음의 결론(유지)과 그 근거를 값과 함께 남긴다. "
          "등급·값·단위는 건드리지 않고 conditions.verdict_71gb 와 notes 만 고친다.")

def main() -> int:
    c = sqlite3.connect(DB, uri=True)
    rows = list(c.execute(
        "select pv.id, pv.material_id, m.name, pv.value_num, pv.quality_tier, pv.conditions, pv.notes "
        "from property_value pv join material m on m.id = pv.material_id "
        "where pv.property_key = 'mechanical.youngs_modulus' and pv.quality_tier = 3 "
        "  and m.name like 'MGC %' order by pv.material_id"))
    corrections = []
    for pid, mid, name, val, tier, cond, note in rows:
        assert tier == 3, (pid, tier)
        d = json.loads(cond) if cond else {}
        assert d.get("test_mode") == "unconfirmed", (pid, d)
        assert "verdict_71gb" not in d, f"pv{pid} 이미 판정이 들어 있다"
        d["verdict_71gb"] = VERDICT_COND
        corrections.append({
            "target": {"property_value_id": pid},
            "by": "71차 GB",
            "reason": REASON,
            "set": {"conditions": d, "notes": (note or "") + VERDICT_NOTE},
            "_grade": name, "_value_gpa": val / 1e9,
        })
    doc = {
        "batch": "71차 GB",
        "note": ("MGC BT 13등급 `mechanical.youngs_modulus` 판정 — **유지(t3)**. 등급을 바꾸지 않는다. "
                 "conditions.verdict_71gb 와 notes 에 판정과 근거만 남긴다."),
        "corrections": corrections,
    }
    (OUT / "gb71_01_corrections.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"정정 {len(corrections)}건 — 등급 변경 0건")
    for cc in corrections:
        print(f"  pv{cc['target']['property_value_id']:6d} {cc['_grade'][:52]:52} {cc['_value_gpa']:.0f} GPa  t3 유지")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
