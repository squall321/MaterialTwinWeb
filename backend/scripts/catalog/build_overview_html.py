# 물성 카탈로그 전체 현황·수집 방법·출처·역산 경계를 발표용 HTML 한 장으로 묶는다.
# 수치는 전부 라이브 DB에서 계산한다 — 하드코딩하면 파동마다 페이지가 낡는다.
# 사용: .venv/bin/python scripts/catalog/build_overview_html.py
from __future__ import annotations

import os
import html
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import coverage_report as CR  # noqa: E402

# `integrity_check.py`·`coverage_report.py` 와 같은 이유로 환경변수를 본다 —
# 박아 두면 스냅샷으로 검증할 수 없다(53차 OB, 브리프 572).
DB = os.path.join(
    os.environ.get("MATERIALTWIN_DATA_DIR",
                   "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
    "materialtwin.db")
OUT = Path("/home/koopark/claude/MaterialTwinWeb/docs/물성카탈로그_현황.html")

# 역산을 잡아낸 실제 사건 — DB에서 셀 수 없는 역사라 여기 적는다.
# 값이 지워졌으므로 카탈로그를 조회해도 나오지 않는다. 그래서 문서가 기억한다.
BACKCALC_CAUGHT = [
    ("E = 2G(1+ν)", "VHB 점착테이프 14행",
     "수기 항등식으로 탄성률을 산출하고 출처만 Satas 핸드북 표기. "
     "핸드북 인쇄값 0.4 MPa 로 환원."),
    ("AZoM <code>Shear Modulus</code>", "폴리머·세라믹 전 행",
     "같은 표의 E·ν로 E/(2(1+ν))를 계산하면 마지막 자리까지 일치한다 "
     "(96% 알루미나: 300/(2×1.21) = 123.97 = 인쇄값 124)."),
    ("AZoM <code>Ductility</code>", "세라믹 행",
     "σts/E 유도값. 파단연신율로 이관 시 취성재에 소성 연신을 부여하게 됨."),
    ("AZoM <code>Endurance Limit</code>", "폴리머 행",
     "k × Elastic Limit이고 범위 양 끝점이 정확히 같은 배수다"
     "(PET 0.6000/0.6000 · PI 0.5500/0.5500 · LDPE 0.7000/0.7000). "
     "세라믹 행은 MgO 내구한도 하한이 동일 표의 탄성한도 하한을 초과 — 물리적 불성립."),
    ("MakeItFrom 폴리머 <code>G</code>", "전 폴리머 행",
     "LDPE 가 E=0.30 GPa · G=0.21 GPa 를 동시 인쇄, 환산 시 ν=−0.29. "
     "동일 사이트의 금속 값은 정합 — 폴리머 계열만 오염."),
    ("α = β/3", "액체 전해질",
     "인쇄분은 체적팽창계수 단독. 3 으로 나누면 역산에 해당하므로 칸을 비움."),
]

# 허용되는 계산 — 경계가 어디인지가 이 표의 요지다.
COMPUTED_OK = [
    ("단위 환산", "psi→Pa, cal/(cm·s·°C)→W/(m·K), Barrer→SI, N/25mm→N/m",
     "같은 양을 다른 눈금으로 옮기는 것에 한정. 원문 값과 배율을 notes 에 병기."),
    ("원문이 인쇄한 피팅", "Prony 급수, Ogden·Mooney-Rivlin 계수, Johnson-Cook, Basquin 회귀식",
     "저자가 자기 데이터에 맞춰 발표한 상수. 우리가 곡선에서 추출한 값이 아님."),
    ("공표된 상관식", "Okabe 적층재 S-N, Maekawa 세라믹 피로, Ishiyama 흑연",
     "관계식의 보증 주체가 판별 기준. 논문 보증분은 인용, 자체 작성분은 배제."),
    ("무차원비 이전", "공여재 정적강도로 나눠 수용재 강도를 곱한다",
     "입력 2개가 모두 원문 인쇄값일 것. 계보를 notes 에 명기."),
    ("클래스 중앙값", "카탈로그 내 같은 클래스 실측값의 중앙값",
     "출처 제목에 산출 방식 명시. tier4 · assumption 표지 부착."),
]

RULES = [
    ("지어내지 않는다", "빈칸이 틀린 값보다 우선. 문서에 실제 인쇄된 숫자만 등재."),
    ("역산 금지", "타 물성 유도값 저장 금지. 원문이 수행한 계산만 인용."),
    ("그래프에서 읽지 않는다", "축 눈금과 스캔 해상도가 유효숫자를 결정 — 판독 자릿수는 우리가 만든 값."),
    ("재인쇄본·2차 인용 불가", "인용값은 1차 출처까지 추적해 확인."),
    ("조건 없는 값은 값이 아니다", "온도·주파수·방향·습도 미기재 시 해석 입력 불가."),
    ("자릿수 대조", "동일 재료의 상위 tier 값과 자릿수 불일치 시 등재 보류."),
    ("인접 열 오독 주의", "표는 한 열이 통째로 밀릴 수 있음. 대조군 행과 본문 서술로 검산."),
]

# 검사 항목 수는 **적는 순간 늙는다**(§601) — 오래 "37항목" 이라 적혀 있었는데
# 실제로는 SQL 45 · 파이썬 6 이었다. 검사기 소스에서 직접 센다.
def _count_checks() -> int:
    import pathlib
    src = (pathlib.Path(__file__).with_name("integrity_check.py")).read_text(encoding="utf-8")
    return sum(1 for ln in src.splitlines()
               if ln.startswith('    ("') or "bad += 1" in ln)


_N_CHECKS = _count_checks()

CYCLE = [
    ("빈칸 탐지", "커버리지 격자 재계산 후 (재료 × 물성) 공백 추출"),
    ("표적 선정", "칸 수가 아닌 <b>칸/재료</b>와 <b>1칸 부족 재료</b> 기준으로 우선순위 결정"),
    ("브리프 전달", "규칙·함정 지도·확정 부재 목록 일괄 인계"),
    ("병렬 수집", "재료군별 배치 분할 후 원문 동시 확보"),
    ("청크 저장", "10~12종마다 중간 파일 기록 — 종료 시 일괄 기록하면 중단 시 전량 소실"),
    ("값 검증", "규칙 6 자릿수 대조 · 자기 검산 · 원문 문자열 대조"),
    ("인제스트", "스키마·단위·조건·tier 규약 미통과분 거부"),
    ("반례 검증", "부재 선언에 실측 반례 1건이라도 존재 시 해당 선언 자동 은퇴"),
    ("무결성 검사", f"{_N_CHECKS}항목 전량 0 이어야 배포"),
    ("기록", "성공보다 <b>실패와 함정</b>을 기록 — 다음 파동의 동일 벽 재충돌 방지"),
]


def q(c, sql, *a):
    return c.execute(sql, a).fetchall()


def esc(s):
    return html.escape(str(s))


def bar_row(label, pct, extra="", cls="teal"):
    return (f'<div class="brow"><span class="blabel">{esc(label)}</span>'
            f'<span class="btrack"><i class="bfill {cls}" style="width:{pct:.1f}%"></i></span>'
            f'<span class="bval">{pct:.1f}%</span>'
            f'<span class="bnote">{extra}</span></div>')


def main():
    c = sqlite3.connect(DB)
    n_mat, n_val, n_src, n_def = q(c, """select
        (select count(*) from material), (select count(*) from property_value),
        (select count(*) from source), (select count(*) from property_definition)""")[0]

    tiers = dict(q(c, "select quality_tier,count(*) from property_value group by 1"))
    methods = dict(q(c, "select method,count(*) from property_value group by 1"))
    domains = q(c, """select pd.domain,count(*) from property_value pv
        join property_definition pd on pd.key=pv.property_key group by 1 order by 2 desc""")
    dom_defs = dict(q(c, "select domain,count(*) from property_definition group by 1"))
    kinds = q(c, "select kind,count(*) from source group by 1 order by 2 desc")
    cats = q(c, "select category,count(*) from material group by 1 order by 2 desc")
    top_src = q(c, """select s.title,s.kind,count(*) n from source s
        join property_value pv on pv.source_id=s.id group by s.id order by n desc limit 12""")
    n_doi = q(c, "select count(*) from source where coalesce(doi,'')<>''")[0][0]
    n_url = q(c, "select count(*) from source where coalesce(url,'')<>''")[0][0]
    # 조건 보유는 **살림살이 키를 빼고** 센다 — `verdict_*`·`correction_reason`·`corrected_by`·
    # `*_before_correction`·`moved_from_*`·`direction_verbatim` 은 우리가 적은 기록이지 조건축이 아니다
    # (브리프 557·571). 라이브 실측 40,230행 중 31행이 살림살이 키만 갖고 있다.
    n_cond = sum(1 for (raw,) in q(c, "select conditions from property_value")
                 if CR.real_conditions(raw))
    n_assum = q(c, """select count(*) from property_value where
        replace(replace(coalesce(conditions,''),' ',''),'"assumption":true','@@') like '%@@%'""")[0][0]
    comp_keys = q(c, """select property_key,count(*) from property_value
        where method='computed' group by 1 order by 2 desc limit 10""")
    comp_tier = dict(q(c, "select quality_tier,count(*) from property_value where method='computed' group by 1"))
    growth = q(c, "select date(created_at),count(*) from property_value group by 1 order by 1")

    # tier4로만 대표되는 칸 — 대체 여지의 실제 크기다.
    t4_cells = q(c, """select material_id,property_key from property_value
        group by 1,2 having min(quality_tier)>=4""")
    all_cells = q(c, "select count(*) from (select 1 from property_value group by material_id,property_key)")[0][0]
    t4_by_key = Counter(k for _, k in t4_cells)
    t4_by_mat = Counter(m for m, _ in t4_cells)
    matname = dict(q(c, "select id,name from material"))
    defname = dict(q(c, "select key,name from property_definition"))

    def meas_cov(key):
        """그 물성의 (재료 × 물성) 칸 중 실측(tier<=3)이 있는 칸의 비율."""
        tot = q(c, "select count(*) from (select 1 from property_value "
                   "where property_key=? group by material_id)", key)[0][0]
        ms = q(c, "select count(*) from (select 1 from property_value where property_key=? "
                  "group by material_id having min(quality_tier)<=3)", key)[0][0]
        return ms * 100 / max(tot, 1)

    _c2, _mat2, _own2, cov = CR.compute()
    sc = CR.subsystem_core(DB)
    tot_cells = sum(x["cells"] for x in cov)
    tot_filled = sum(x["filled"] for x in cov)
    tot_meas = sum(x["meas_filled"] for x in cov)
    tot_unfill = sum(x["unfillable"] for x in cov)
    tot_eff_filled = tot_filled - sum(x["unfill_filled"] for x in cov)
    tot_eff = tot_cells - tot_unfill
    remain = tot_eff - tot_eff_filled

    # 성장 곡선 SVG — 라이브러리 없이 폴리라인 하나로 그린다.
    cum, pts, labels = 0, [], []
    for i, (d, n) in enumerate(growth):
        cum += n
        pts.append((i, cum))
        labels.append(d)
    W, H, PAD = 880, 200, 8
    mx = max(p[1] for p in pts) or 1
    poly = " ".join(f"{PAD + p[0] * (W - 2 * PAD) / max(len(pts) - 1, 1):.1f},"
                    f"{H - PAD - p[1] * (H - 2 * PAD) / mx:.1f}" for p in pts)
    area = f"{PAD},{H - PAD} {poly} {W - PAD},{H - PAD}"
    dots = "".join(f'<circle cx="{PAD + p[0] * (W - 2 * PAD) / max(len(pts) - 1, 1):.1f}" '
                   f'cy="{H - PAD - p[1] * (H - 2 * PAD) / mx:.1f}" r="2.5"/>' for p in pts)

    T = []
    A = T.append
    A('<title>MaterialTwin 물성 카탈로그 현황</title>')
    A(CSS)

    # ── 표지
    A('<header class="hero">')
    A('<p class="eyebrow">MaterialTwin · 물성 카탈로그</p>')
    A('<h1>측정한 값과 가정한 값을<br>같은 표에 두되, 절대 섞지 않는다</h1>')
    A('<p class="lede">스마트폰 구조해석에 필요한 물성을 재료 × 물성 격자로 세고, '
      '모든 값에 출처와 등급을 붙여 <b>무엇이 근거 있는 값이고 무엇이 아직 가정인지</b>를 '
      '표 위에서 바로 읽게 만든 카탈로그다. 아래 숫자는 전부 라이브 DB에서 계산했다.</p>')
    A('<div class="kpis">')
    for v, k, s in [(f"{n_val:,}", "물성값", f"재료 {n_mat}종 · 정의 {n_def}종"),
                    (f"{n_src:,}", "출처", f"DOI {n_doi} · URL {n_url}"),
                    (f"{tot_filled * 100 / tot_cells:.1f}%", "셀 채움", f"격자 {tot_cells:,}칸"),
                    (f"{tot_meas * 100 / tot_cells:.1f}%", "실측기반", "tier4 가정을 뺀 값")]:
        A(f'<div class="kpi"><b>{v}</b><span>{k}</span><em>{s}</em></div>')
    A('</div></header>')

    A('<nav class="toc"><ol>')
    for i, t in enumerate(["경로", "기준", "해석", "계통", "등급", "출처", "주기", "규정",
                           "역산", "부재", "검증", "추이", "과제"], 1):
        A(f'<li><a href="#s{i}">{t}</a></li>')
    A('</ol></nav>')

    # ── 1. 경로 (그림이 메커니즘을 대신 말한다)
    A(sec(1, "수집 경로", "원천에서 해석 카드까지 6단계"))
    A(FLOW_SVG)
    A('</section>')

    # ── 2. 격자
    A(sec(2, "집계 기준", "해석이 요구하는 칸만 분모로 계상"))
    A(lead([
        f'재료 {n_mat}종 × 정의 {n_def}종 = 이론상 {n_mat * n_def:,}칸이나, 전량을 분모로 두지 않음',
        '세라믹의 항복강도·도체의 유전율처럼 <b>성립하지 않는 요구를 넣으면 분모 자체가 거짓</b>',
        f'해석 13종이 실제로 요구하는 <b>{tot_cells:,}칸</b>만 격자로 확정, 이 격자만 계상',
    ]))
    A('<div class="grid4">')
    for v, k in [(f"{tot_cells:,}", "해석이 실제로 요구하는 칸"),
                 (f"{tot_filled:,}", "채워진 칸"),
                 (f"{tot_unfill:,}", "구조적으로 못 채우는 칸"),
                 (f"{remain:,}", "아직 채울 수 있는 칸")]:
        A(f'<div class="cell"><b>{v}</b><span>{k}</span></div>')
    A('</div>')
    A('<p class="note"><b>택일군을 둔다.</b> 낙하해석의 소성 입력은 <code>항복강도</code> 단독 또는 '
      '<code>인장강도 + 파단연신율</code> 쌍 중 하나로 충족되므로 <b>칸 1개</b>로 계상한다. '
      '어느 쪽이 인쇄되는지는 재료가 아니라 시험규격 관행이 결정한다.</p>')
    A(dl([("셀 채움", "채워진 칸 / 전체 칸 — 수집 진척도"),
          ("실측기반", "tier4(가정·계산)를 뺀 채움 — 근거의 실제 크기"),
          ("유효채움", "구조적 부재를 분모에서 뺀 채움 — 도달 가능한 천장 대비"),
          ("적용 대비 준비율", "그 해석이 원리적으로 성립하는 재료만 분모로 둔 재료 준비율")]))
    A('</section>')

    # ── 2. 현황
    A(sec(3, "해석별 충족도", "해석 13종 · 재료 준비율"))
    A(lead([
        '해석 13종 각각에 대해 <b>대상 재료·요구 칸·채움률·재료 준비율</b>을 산출',
        '<b>셀 채움</b>과 <b>실측기반</b>을 나란히 제시 — 한쪽만 보면 가정값을 실측으로 오독',
        '준비율은 해석이 원리적으로 성립하는 재료만 분모로 계상',
    ]))
    A('<div class="tblwrap"><table class="cov">')
    A('<thead><tr><th>해석</th><th class="n">대상</th><th class="n">칸</th>'
      '<th>셀 채움</th><th class="n">실측기반 %</th><th class="n">유효채움 %</th>'
      '<th class="n">적용 대비<br>준비율</th></tr></thead><tbody>')
    for x in cov:
        rp = x["ready_app_pct"]
        cls = "ok" if rp >= 95 else ("warn" if rp >= 85 else "crit")
        A(f'<tr><td class="nm">{esc(x["name"])}</td><td class="n">{x["n_target"]}</td>'
          f'<td class="n">{x["cells"]:,}</td>'
          f'<td class="barcell"><span class="btrack sm"><i class="bfill teal" '
          f'style="width:{x["cell_pct"]:.1f}%"></i></span><span class="pct">{x["cell_pct"]:.1f}</span></td>'
          f'<td class="n mono">{x["meas_pct"]:.1f}</td><td class="n mono">{x["eff_pct"]:.1f}</td>'
          f'<td class="n"><span class="pill {cls}">{rp:.1f}%</span></td></tr>')
    A(f'<tr class="tot"><td class="nm">전체</td><td class="n">{n_mat}</td>'
      f'<td class="n">{tot_cells:,}</td>'
      f'<td class="barcell"><span class="btrack sm"><i class="bfill teal" '
      f'style="width:{tot_filled * 100 / tot_cells:.1f}%"></i></span>'
      f'<span class="pct">{tot_filled * 100 / tot_cells:.1f}</span></td>'
      f'<td class="n mono">{tot_meas * 100 / tot_cells:.1f}</td>'
      f'<td class="n mono">{tot_eff_filled * 100 / tot_eff:.1f}</td><td class="n">—</td></tr>')
    A('</tbody></table></div>')
    A(f'<p class="note"><b>셀 채움과 실측기반의 차 '
      f'{(tot_filled - tot_meas) * 100 / tot_cells:.1f}%p · {tot_filled - tot_meas:,}칸이 '
      f'가정값에 해당한다.</b> 두 지표를 함께 읽어야 한다 — '
      f'채움률 100%인 해석도 실측기반은 67% 수준일 수 있다.</p>')
    A('</section>')

    # ── 3. 계통 — 43·49차 태깅이 끝나 이제 계통별로 셀 수 있다.
    A(sec(4, "계통별 충족도", "코어 7물성 기준 · 계통 17종"))
    A(f'<p>제품 재료 {sc["total"]["n_mat"]}종을 계통으로 태깅했다. 아래는 '
      f'<b>코어 {len(sc["core"])}물성</b>(밀도·영률·포아송비·CTE·열전도율·비열·인장강도) '
      f'{sc["total"]["cells"]:,}칸의 채움률이다 — 해석 격자와 달리 <b>재료 하나가 최소한 이것은 '
      f'있어야 한다</b>는 축이다.</p>')
    A('<div class="tblwrap"><table class="cov">')
    # 갈래가 여섯이 되면서 열이 열 개가 된다 — 표가 좁아진다. 그래서 **빈칸 열을 없애지 않고
    # 채움 칸 안으로 접었다**(빈칸 = 갈래 여섯의 합이라 읽는 사람의 검산 기준점이 사라지면 안 된다).
    A('<thead><tr><th>계통</th><th class="n">재료</th><th>코어 채움 <span class="hsub">/ 빈칸</span></th>'
      '<th class="n">해당<br>없음</th><th class="n">벤더<br>부재</th>'
      '<th class="n">인쇄됐으나<br>기각</th>'
      '<th class="n">판정이<br>자유 키에</th><th class="n">등급<br>미확정</th>'
      '<th class="n">진짜<br>남은 것</th></tr></thead><tbody>')
    for r in sc["rows"]:
        cls = "ok" if r["pct"] >= 90 else ("warn" if r["pct"] >= 70 else "crit")
        A(f'<tr><td class="nm">{esc(r["subsystem"])}</td><td class="n">{r["n_mat"]}</td>'
          f'<td class="barcell"><span class="btrack sm"><i class="bfill teal" '
          f'style="width:{r["pct"]:.1f}%"></i></span>'
          f'<span class="pct">{r["pct"]:.1f}</span>'
          f'<span class="blk">/ {r["blank"]}</span></td>'
          f'<td class="n mono">{r["V1"] or "·"}</td><td class="n mono">{r["V2"] or "·"}</td>'
          f'<td class="n mono">{r["V6"] or "·"}</td>'
          f'<td class="n mono">{r["V3"] or "·"}</td><td class="n mono">{r["V4"] or "·"}</td>'
          f'<td class="n"><span class="pill {cls}">{r["V5"]}</span></td></tr>')
    t = sc["total"]
    A(f'<tr class="tot"><td class="nm">전체</td><td class="n">{t["n_mat"]}</td>'
      f'<td class="barcell"><span class="btrack sm"><i class="bfill teal" '
      f'style="width:{t["pct"]:.1f}%"></i></span><span class="pct">{t["pct"]:.1f}</span>'
      f'<span class="blk">/ {t["blank"]:,}</span></td><td class="n mono">{t["V1"]}</td>'
      f'<td class="n mono">{t["V2"]}</td><td class="n mono">{t["V6"]}</td>'
      f'<td class="n mono">{t["V3"]}</td>'
      f'<td class="n mono">{t["V4"]}</td><td class="n mono">{t["V5"]:,}</td></tr>')
    A('</tbody></table></div>')
    A('<details class="more"><summary>빈칸 갈래 정의</summary>'
      '<div class="tblwrap"><table class="unf"><tbody>'
      + "".join(f'<tr><td class="nm">{esc(lbl)}</td><td>{esc(why)}</td></tr>'
                for _, lbl, why in CR.VERDICT_LABEL) + '</tbody></table></div></details>')
    A(f'<p class="note warn"><b>빈칸 {t["blank"]:,}칸 중 수집 가능한 것은 {t["V5"]:,}칸이다.</b> '
      f'나머지 {t["blank"] - t["V5"]:,}칸은 판정 완료분이거나 원리적으로 충족 불가다. '
      f'이 중 {t["V3"]}칸은 <b>판정이 자유 키에 기록돼 집계가 읽지 못한다</b> — '
      f'집계가 읽는 자리(<code>core_not_applicable</code>·'
      f'<code>core_absent_from_vendor_sheet</code>·'
      f'<code>core_rejected_printed_value</code>)로 이관하기 전까지는 다음 파동이 중복 계상한다.</p>')
    A('</section>')

    # ── 3. 등급
    A(sec(5, "근거 등급", "tier 1~4 판정 기준과 구성비"))
    A('<div class="tiers">')
    tinfo = [(1, "그 제품에 대해 인쇄된 값", "벤더 데이터시트·논문이 이 제품을 시험한 결과"),
             (2, "핸드북·규격·인증 DB", "계열 대표값이지만 권위 있는 기관이 보증한다"),
             (3, "2차 인용·클래스 대표·등급 대체", "출처는 실재하나 이 제품의 값은 아니다"),
             (4, "계산·유도·추정·가정", "우리가 만든 값이다. 반드시 표지를 단다")]
    for t, ttl, desc in tinfo:
        n = tiers.get(t, 0)
        A(f'<div class="tier t{t}"><b>tier {t}</b><span class="tn">{n:,}</span>'
          f'<span class="tp">{n * 100 / n_val:.1f}%</span>'
          f'<p class="tt">{esc(ttl)}</p><p class="td">{esc(desc)}</p></div>')
    A('</div>')
    A(lead([
        'tier4 는 <b>허용하되 표지 필수</b> — 빈칸이면 해석 미가동, 무표지면 가정이 실측 행세',
        '요건 3종 동시 충족 — <code>method="estimated"</code> · '
        '<code>conditions.assumption=true</code> · notes 근거',
        f'현재 assumption 표지 부착 <b>{n_assum:,}건</b>, 지표는 셀 채움·실측기반 2행으로 분리 제시',
    ]))
    A('<div class="split">')
    A('<div><h4>method 구성</h4>' + "".join(
        bar_row(k, v * 100 / n_val, f"{v:,}건") for k, v in
        sorted(methods.items(), key=lambda z: -z[1])) + '</div>')
    A('<div><h4>도메인 구성</h4>' + "".join(
        bar_row(f"{k} ({dom_defs.get(k, 0)}종)", v * 100 / n_val, f"{v:,}건")
        for k, v in domains[:7]) + '</div>')
    A('</div></section>')

    # ── 4. 출처
    # 「출처가 붙어 있다」와 「그 출처를 다시 열 수 있다」는 다르다. 68차에 배치 셋이
    # 연달아 못 여는 핸드북에 막혔다(853 Polymer Handbook · 971 Rubber Technology ·
    # 972 Touloukian). 전량 출처 부착을 자랑하면서 이걸 안 적으면 과장이 된다.
    _dead = q(c, """
        select count(*), coalesce(sum(n),0) from (
          select s.id, (select count(*) from property_value where source_id=s.id) n
          from source s
          where (s.local_path is null or s.local_path='')
            and (s.url is null or s.url='') and (s.doi is null or s.doi=''))""")[0]
    n_dead_src, n_dead_val = _dead[0], _dead[1]

    A(sec(6, "출처 관리", "값 1건당 문서 1건"))
    A(lead([
        '스키마가 <b>출처 없는 값의 저장을 거부</b> — 등록 API 가 DOI·URL·제목 중 1건 요구',
        f'값 <b>{n_val:,}건 전량</b>에 출처 부착, 끊어진 참조 <b>0건</b>',
        f'조건(온도·주파수·방향 등) 부착 값 {n_cond:,}건 · {n_cond * 100 / n_val:.1f}%',
        f'단, <b>다시 열 수 없는 출처 {n_dead_src}건</b>이 값 <b>{n_dead_val:,}건</b>({n_dead_val * 100 / n_val:.1f}%)을 받침 — 재확인 경로 없음',
    ]))
    A('<div class="split">')
    A('<div><h4>출처 유형 ' + f'({n_src:,}건)</h4>' + "".join(
        bar_row(k, v * 100 / n_src, f"{v}건") for k, v in kinds) + '</div>')
    A('<div><h4>재료 분류 ' + f'({n_mat}종)</h4>' + "".join(
        bar_row(k, v * 100 / n_mat, f"{v}종", "clay") for k, v in cats) + '</div>')
    A('</div>')
    A('<h4>값 산출 상위 문서</h4><div class="tblwrap"><table class="src"><tbody>')
    for t, kd, n in top_src:
        A(f'<tr><td class="n mono">{n}</td><td class="kind">{esc(kd)}</td>'
          f'<td>{esc(clip(t, 88))}</td></tr>')
    A('</tbody></table></div>')
    A(f'<p class="note warn"><b>출처가 붙어 있다는 것과 그 출처를 열 수 있다는 것은 다르다.</b> '
      f'DOI·URL·로컬사본이 <b>셋 다 없는 출처 {n_dead_src}건</b>이 값 {n_dead_val:,}건을 받친다 — '
      '대부분 인쇄 핸드북이다(Polymer Handbook·Touloukian·ASM·CRC). '
      '이 값들은 <b>틀렸다는 뜻이 아니라 우리 손으로 재확인할 경로가 없다</b>는 뜻이다. '
      '수집 배치가 이 출처를 표적으로 지목받으면 열 대상이 없어 헛돈다 — 실제로 세 번 났다.</p>')
    A('<p class="note">단일 문서가 800건 이상을 산출하는 사례가 있다 — 패키지 워피지 논문 1편이 '
      '재료 수십 종의 물성표를 일괄 수록하기 때문이다. '
      '<b>상위 문서일수록 검증 비용이 크다</b> — 열이 1개 밀리면 수백 건이 동시에 오염된다.</p>')
    A('</section>')

    # ── 5. 사이클
    A(sec(7, "수집 주기", f"1파동 {len(CYCLE)}단계"))
    A('<ol class="steps">')
    for i, (t, d) in enumerate(CYCLE, 1):
        A(f'<li><span class="sn">{i:02d}</span><div><b>{esc(t)}</b><p>{d}</p></div></li>')
    A('</ol>')
    A('<p class="note">5단계(청크 저장)는 <b>장애 대응으로 도입</b>했다. '
      '배치 6개가 결과를 종료 시점에 일괄 기록하다 동시 중단돼 산출물 0건이 발생했다. '
      '이후 전 파동이 10~12종마다 중간 파일을 기록하며 동일 유형 손실은 재발하지 않았다.</p>')
    A('</section>')

    # ── 6. 규칙
    A(sec(8, "금지 규정", f"예외 없이 적용하는 {len(RULES)}개 항"))
    A('<ol class="rules">')
    for i, (t, d) in enumerate(RULES, 1):
        A(f'<li><b>{esc(t)}</b><p>{esc(d)}</p></li>')
    A('</ol>')
    A('<p class="note">각 규칙은 <b>실제 적발 이력</b>을 근거로 한다. '
      '규칙 4는 「3M 인쇄값 0.49」로 기재된 43건의 근거가 계열 기술자료였음을 적발했고, '
      '규칙 6은 1,000배 과대 굽힘강도 2건을 차단했다.</p>')
    A('</section>')

    # ── 7. 역산
    A(sec(9, "역산 판별", "인용 가능한 계산과 배제 대상의 경계"))
    A(lead([
        '판별 기준은 계산의 <b>수행 주체</b> — 계산 자체가 금지 대상이 아님',
        '원문이 자기 데이터에 피팅한 상수는 <b>인용</b>, 우리가 타 물성에서 유도한 값은 <b>배제</b>',
        '표상으로는 양자 구별 불가 — 근거 검증으로만 갈림',
    ]))
    A('<div class="two">')
    A('<div class="box ok"><h4>인용 대상 · 원문 산출값</h4><table class="mini"><tbody>')
    for t, ex, why in COMPUTED_OK:
        A(f'<tr><td class="nm">{t}</td><td><span class="ex">{ex}</span>{why}</td></tr>')
    A('</tbody></table></div>')
    A('<div class="box crit"><h4>배제 대상 · 자체 산출값</h4><table class="mini"><tbody>')
    for t, where, why in BACKCALC_CAUGHT:
        A(f'<tr><td class="nm">{t}<span class="where">{esc(where)}</span></td><td>{why}</td></tr>')
    A('</tbody></table></div>')
    A('</div>')
    A('<details class="more"><summary>등재 현황 및 검출 기준</summary>')
    A(f'<h4>계산값 등재 현황</h4>'
      f'<p><code>method="computed"</code>는 {methods.get("computed", 0):,}건이다. '
      f'tier 분포가 {" · ".join(f"t{t} {n}" for t, n in sorted(comp_tier.items()))}인데, '
      f'<b>tier1·2에 계산값이 있는 것이 정상</b>이다 — 그 논문이 자기 시편에 피팅해 발표한 '
      f'구성모델 상수이기 때문이다. 반대로 <code>estimated</code>는 '
      f'{methods.get("estimated", 0):,}건 전부가 tier3 이하로 내려가 있다.</p>')
    A('<div class="split">')
    A('<div><h4>계산값 상위 물성</h4>' + "".join(
        f'<div class="krow"><span>{esc(defname.get(k, k))}</span>'
        f'<b class="mono">{n}</b></div>' for k, n in comp_keys[:8]) + '</div>')
    A('<div><h4>역산 검출 5개 항</h4>'
      '<ul class="tips">'
      '<li><b>말단 자릿수 일치 여부.</b> E/(2(1+ν))를 손으로 계산해 인쇄값과 대조.</li>'
      '<li><b>범위 양 끝점의 배수 동일 여부.</b> 유도열은 하한·상한이 같은 계수로 묶임.</li>'
      '<li><b>물리적 성립 여부.</b> 내구한도 하한이 탄성한도 하한을 초과하면 유도열.</li>'
      '<li><b>ν 음수 산출 여부.</b> E·G 를 함께 인쇄하는 표는 이 검산에서 무너짐.</li>'
      '<li><b>대조군 행과 본문의 일치 여부.</b> 0 wt% 대조 행이 본문 값과 같으면 첨가물의 값.</li>'
      '</ul></div>')
    A('</div></details>')
    A('<p class="note"><b>근거를 변경하는 편집은 값을 변경하는 편집보다 적발이 늦다.</b> '
      '출처 정리 과정에서 추정 라벨 5건이 실제 벤더 문서명으로 치환되면서, '
      '값 변경 0건인 채로 하위 18개 값의 근거만 허위가 됐다. 현재는 정합성 검사가 이 패턴을 검출한다.</p>')
    A('</section>')

    # ── 8. 부재
    A(sec(10, "부재 선언", "분모 제외 대상과 반례 검증"))
    A(lead([
        '액체의 항복강도·증착 도판트의 투습도 등 <b>원리적으로 성립하지 않는 칸</b>이 대상',
        '분모 존치 시 <b>도달 불가능한 100%</b>를 목표로 삼게 됨',
        f'(재료군 × 물성) 쌍 단위 선언 <b>{len(CR.UNFILLABLE)}건</b> · 분모 제외 {tot_unfill:,}칸',
    ]))
    A(f'<details class="more"><summary>부재 선언 {len(CR.UNFILLABLE)}건 전문</summary>'
      '<div class="tblwrap"><table class="unf"><tbody>'
      + "".join(f'<tr><td class="n mono">{len(k)}키</td><td>{esc(r)}</td></tr>'
                for m, k, r in CR.UNFILLABLE) + '</tbody></table></div></details>')
    A('<p class="note"><b>부재 선언은 반례 검증을 거친다.</b> 성립 요건은 둘이다 — '
      '문서에 기록된 사유가 있을 것, 해당 군의 어느 재료도 그 물성을 <b>실측으로</b> 보유하지 않을 것. '
      '실측값이 1건이라도 등재되면 그 쌍은 선언에서 자동 제외된다. '
      '「세라믹 피로계수 미보유」 선언은 알루미나 S-N 회귀식 1건으로, '
      '「폼 박리강도 미보유」 선언은 VHB 반례 25건으로 각각 철회됐다.</p>')
    A('<p class="note warn"><b>전수 검색 결과 0건은 검색 실패와 구분되지 않는다.</b> '
      '출처를 재수집해 검색한 결과가 0건이어도 그 자체로는 부재의 근거가 아니다 — '
      '인쇄된 부재 문장 또는 물리적 논거가 있는 군만 선언 대상으로 한다.</p>')
    A('</section>')

    # ── 9. 검증
    A(sec(11, "검증 체계", "5중 필터"))
    A('<div class="verify">')
    for t, d in [
        (f"무결성 검사 {_N_CHECKS}항목", "구조 점검. 출처 없는 값·단위 불일치·쌍이 깨진 모델 상수·"
                          "조건 없는 확산계수·근거 없는 tier4 를 전량 0 으로 만들어야 배포."),
        ("반례 검증", "실측 반례 1건이라도 존재 시 해당 부재 선언 자동 은퇴. "
                  "자체 가정이 자체 선언을 지우지 못하도록 tier4 는 반례에서 제외."),
        ("자기 검산", "확보한 값으로 동일 논문의 다른 값을 예측. "
                  "Ogden 계수에서 E₀=2(μ₁+μ₂) 를 산출해 동일 논문 실측 탄성률과 대조."),
        ("원문 문자열 대조", "저장 숫자의 인용 출처 실재 여부를 전문 확보 후 grep 으로 확인. "
                       "값 0.176 이 원문에 0회 출현하는 사례를 이 경로로 적발."),
        ("규칙 6 자릿수 대조", "동일 재료의 상위 tier 값과 자릿수 불일치 시 등재 보류. "
                        "1000배 과대 굽힘강도 2건을 이 단계에서 적발."),
    ]:
        A(f'<div class="vcard"><b>{esc(t)}</b><p>{esc(d)}</p></div>')
    A('</div>')
    A('<p class="note">검사가 <b>오탐</b>을 내면 값이 아니라 <b>검사를 수정한다</b> — '
      '예외 사유는 코드 주석에 기록한다. Prony 급수 외부 항인 장기계수 E∞ 36건이 이 경로로 처리됐다.</p>')
    A('</section>')

    # ── 10. 성장
    A(sec(12, "누적 추이", f"{labels[0]} ~ {labels[-1]}"))
    A(f'<div class="chart"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" role="img" '
      f'aria-label="물성값 누적 성장 곡선">'
      f'<polygon points="{area}" class="ar"/><polyline points="{poly}" class="ln"/>'
      f'<g class="dt">{dots}</g></svg>'
      f'<div class="xax"><span>{labels[0]}</span><span>{labels[-1]}</span></div></div>')
    A(lead([
        f'{len(growth)}일간 <b>{cum:,}건</b> 누적',
        '각 파동은 직전 파동이 남긴 <b>함정 지도를 인계받아</b> 착수',
        '축적 대상은 값과 <b>오독 이력</b> 양쪽',
    ]))
    A('</section>')

    # ── 11. 남은 일
    A(sec(13, "잔여 과제", "빈칸 소진 이후의 실제 표적"))
    A('<div class="two">')
    A(f'<div class="box"><h4>미채움 잔량</h4>'
      f'<p class="big">{remain:,}<em>칸</em></p>'
      f'<p>구조적 부재 제외 시 유효채움 {tot_eff_filled * 100 / tot_eff:.1f}%. '
      f'잔여 칸은 분산돼 있고 건당 난도가 높음 — 앵커 논문에 인장강도는 있으나 '
      f'변형률이 전문에 0회인 유형.</p></div>')
    A(f'<div class="box crit"><h4>가정값 대체 대상</h4>'
      f'<p class="big">{len(t4_cells):,}<em>칸</em></p>'
      f'<p>(재료 × 물성) {all_cells:,}칸 중 <b>{len(t4_cells) * 100 / all_cells:.1f}%가 '
      f'가정값 단독 대표</b> — 약 {all_cells / len(t4_cells):.0f}칸 중 1칸이 '
      f'근거 미확보 상태.</p></div>')
    A('</div>')
    A('<div class="split">')
    A('<div><h4>대체 여지 상위 물성</h4>' + "".join(
        f'<div class="krow"><span>{esc(defname.get(k, k))}</span><b class="mono">{n}</b></div>'
        for k, n in t4_by_key.most_common(8)) + '</div>')
    A('<div><h4>가정 의존 상위 재료</h4>' + "".join(
        f'<div class="krow"><span>{esc(matname[m][:42])}</span><b class="mono">{n}칸</b></div>'
        for m, n in t4_by_mat.most_common(8)) + '</div>')
    A('</div>')
    A(f'<p class="note"><b>대체 가능성은 물성마다 다르다.</b> 실측(tier≤3) 피복률이 '
      f'열전도율 {meas_cov("thermal.conductivity"):.0f}% · '
      f'포아송비 {meas_cov("mechanical.poisson_ratio"):.0f}%다. '
      '<b>CAMPUS 스키마에 포아송비 필드가 없고</b>, Rogers 전 사이트의 '
      '<code>Poisson</code> 출현이 5건이며, MnZn 페라이트 데이터북은 E·인장·경도·파괴인성을 '
      '수록하면서 ν만 제외한다. <b>벤더 미공표 물성</b>이라 도달 가능 상한 자체가 낮다.</p>')
    A(yield_block())
    A('</section>')

    A(f'<footer><p>라이브 DB 조회 · 재료 {n_mat}종 · 물성값 {n_val:,}건 · 출처 {n_src:,}건 · '
      f'무결성 검사는 <code>integrity_check.py</code>가 매 파동 돌린다 · 최종 갱신 {labels[-1]}</p>'
      f'<p class="gen">이 페이지는 <code>build_overview_html.py</code>가 매번 다시 생성한다 — '
      f'숫자를 손으로 적지 않는다.</p></footer>')

    OUT.write_text("\n".join(T), encoding="utf-8")
    print(f"저장: {OUT}")
    print(f"  재료 {n_mat} · 값 {n_val:,} · 출처 {n_src:,} · 격자 {tot_cells:,}칸 "
          f"· 셀채움 {tot_filled * 100 / tot_cells:.1f}% · 실측기반 {tot_meas * 100 / tot_cells:.1f}%")
    print(f"  남은 칸 {remain} · tier4 단독 대표 {len(t4_cells):,}/{all_cells:,}")
    _t = sc["total"]
    print(f"  계통 {len(sc['rows'])}개 · 코어7 채움 {_t['pct']}% · 빈칸 {_t['blank']:,} "
          f"(해당없음 {_t['V1']} · 벤더부재 {_t['V2']} · 인쇄기각 {_t['V6']} · "
          f"자유키판정 {_t['V3']} · 등급미확정 {_t['V4']} · 진짜 남은 것 {_t['V5']:,})")


FLOW_SVG = """<figure class="flow">
<svg viewBox="0 0 980 268" role="img" aria-label="적재 경로 6단계와 검증 단계 2개소, DB 상단의 정합성 검사·병합 경로">
<defs>
<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" fill="var(--clay)"/></marker>
</defs>

<!-- 본류 -->
<g class="fb">
<rect x="12" y="96" width="128" height="52" rx="7"/>
<rect x="180" y="96" width="128" height="52" rx="7"/>
<rect x="348" y="96" width="128" height="52" rx="7"/>
<rect x="516" y="96" width="128" height="52" rx="7"/>
<rect x="684" y="96" width="128" height="52" rx="7"/>
<rect x="852" y="96" width="116" height="52" rx="7"/>
</g>
<g class="ft">
<text x="76" y="117">원천</text><text x="76" y="134" class="sm">문헌·시트·규격</text>
<text x="244" y="117">추출</text><text x="244" y="134" class="sm">원문 표 판독</text>
<text x="412" y="117">적재</text><text x="412" y="134" class="sm">단일 쓰기 경로</text>
<text x="580" y="117">DB</text><text x="580" y="134" class="sm">값·출처·조건</text>
<text x="748" y="117">대표값 선정</text><text x="748" y="134" class="sm">동일 물성 다중 행</text>
<text x="910" y="117">해석 입력</text><text x="910" y="134" class="sm">카드·API·화면</text>
</g>

<!-- 본류 화살표 -->
<g class="fa">
<line x1="140" y1="122" x2="176" y2="122" marker-end="url(#ah)"/>
<line x1="308" y1="122" x2="344" y2="122" marker-end="url(#ah)"/>
<line x1="476" y1="122" x2="512" y2="122" marker-end="url(#ah)"/>
<line x1="644" y1="122" x2="680" y2="122" marker-end="url(#ah)"/>
<line x1="812" y1="122" x2="848" y2="122" marker-end="url(#ah)"/>
</g>
<g class="fl">
<text x="158" y="112">선별</text>
<text x="326" y="112">JSON</text>
<text x="494" y="112">저장</text>
<text x="662" y="112">조회</text>
<text x="830" y="112">출력</text>
</g>

<!-- 거르는 곳 둘 -->
<g class="fa rj">
<line x1="244" y1="148" x2="244" y2="196" marker-end="url(#ahr)"/>
<line x1="412" y1="148" x2="412" y2="196" marker-end="url(#ahr)"/>
</g>
<g class="fb rj">
<rect x="176" y="196" width="136" height="44" rx="7"/>
<rect x="344" y="196" width="136" height="44" rx="7"/>
</g>
<g class="ft rj">
<text x="244" y="215">제외 기록</text><text x="244" y="231" class="sm">탈락 사유 보존</text>
<text x="412" y="215">검증 불합격</text><text x="412" y="231" class="sm">단위·범위·출처·조건</text>
</g>

<!-- DB 를 지키는 둘 -->
<g class="fa gd">
<line x1="580" y1="96" x2="580" y2="62" marker-end="url(#ah)"/>
<line x1="612" y1="62" x2="612" y2="92" marker-end="url(#ah)"/>
</g>
<g class="fb gd"><rect x="500" y="18" width="192" height="44" rx="7"/></g>
<g class="ft gd">
<text x="596" y="37">정합성 검사 · 병합</text>
<text x="596" y="53" class="sm">배포 판정 · 운영 반영</text>
</g>

<!-- 대표값이 갈릴 때 -->
<g class="fa alt"><line x1="748" y1="148" x2="748" y2="196" marker-end="url(#ah)"/></g>
<g class="fb alt"><rect x="672" y="196" width="152" height="44" rx="7"/></g>
<g class="ft alt">
<text x="748" y="215">비채택 후보 병기</text><text x="748" y="231" class="sm">삭제하지 않음</text>
</g>
</svg>
<figcaption>적재 경로에 <b>검증 단계 2개소</b>를 둔다. 추출 단계 탈락분은 사유와 함께 제외 기록에 보존하고,
적재 단계 불합격분은 단위·범위·출처·조건 위반으로 분류한다. DB 반영 이후에는 정합성 검사가 배포 가부를 판정하고
병합 단계가 운영 DB 반영을 담당한다. 동일 재료·동일 물성에 행이 복수인 경우
<b>대표값 1건을 선정하되 비채택 후보를 삭제하지 않고 함께 제공한다.</b></figcaption>
</figure>"""


# 66차 BC 가 코어 밖 격자를 전수로 두드려 잰 **낱말 적중률**과, 68차 DD 가 그 위에서
# 실제로 잰 **칸 마감률**. 둘을 같이 싣는 이유가 있다 — 66차에는 앞 열만 싣고 그것을
# 「수확률」이라 불렀는데, 68차 DD 가 두 갈래를 끝까지 캐 보니 마감률이 6.0% 였다.
# **낱말이 있다는 것과 그 등급의 값이 찍혀 있다는 것은 다르다**(통과율 약 30%).
# 이 숫자는 DB 질의가 아니라 그날의 측정치다 — 다시 재기 전까지 갱신되지 않는다.
YIELD_MEASURED = "낱말 적중 2026-09-07(66차 BC) · 칸 마감 2026-09-09(68차 DD)"
YIELD_ROWS = [
    # 물성, 표적 재료, 쓰는 출처, 로컬 확보, 낱말 적중, 낱말 적중률 %, 칸 마감률 % (None=미측정)
    ("접착강도",      65,  83,  37, 19, 51.4, 6.0),
    ("투습도",       142, 123,  74, 27, 36.5, 6.0),
    ("소성 상수",     290, 284, 199, 64, 32.2, None),
    ("전기 물성",     232, 195, 139, 20, 14.4, None),
    ("율속 민감도",   437, 401, 306, 38, 12.4, None),
    ("피로 계수",     312, 290, 209, 26, 12.4, None),
    ("젖음·표면에너지", 428, 395, 318, 18,  5.7, None),
    ("Prony 계열",    154, 195, 130,  6,  4.6, None),
]


def yield_block():
    """표적별 채굴 난도. 낱말이 걸리는 비율과 칸이 실제로 닫히는 비율을 갈라 싣는다."""
    rows = "".join(
        f'<tr><td class="nm">{esc(nm)}</td><td class="n">{tgt}</td>'
        f'<td class="n mono">{src}</td><td class="n mono">{loc}</td>'
        f'<td class="n mono">{hit}</td>'
        f'<td class="barcell"><span class="btrack sm"><i class="bfill teal" '
        f'style="width:{y:.1f}%"></i></span><span class="pct">{y:.1f}</span></td>'
        + (f'<td class="n"><span class="pill crit">{c:.1f}%</span></td>'
           if c is not None else '<td class="n mono">·</td>')
        + '</tr>'
        for nm, tgt, src, loc, hit, y, c in YIELD_ROWS)
    return (
        '<h4>표적별 채굴 난도 — 낱말이 걸리는 비율과 칸이 닫히는 비율</h4>'
        '<div class="tblwrap"><table class="cov">'
        '<thead><tr><th>물성</th><th class="n">표적 재료</th><th class="n">쓰는 출처</th>'
        '<th class="n">로컬 확보</th><th class="n">낱말 적중</th><th>낱말 적중률</th>'
        '<th class="n">칸 마감률</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
        '<p class="note warn"><b>두 열을 섞어 읽으면 안 된다 — 66차에 그 착오를 냈다.</b> '
        '「낱말 적중률」은 <b>표적이 이미 쓰는 문서에 그 물성 낱말이 나오는가</b>이고, '
        '「칸 마감률」은 <b>그 등급의 값이 조건까지 갖춰 실제로 등재됐는가</b>다. '
        '66차에는 앞 열만 재고 그것을 수확률이라 부르며 포아송비 7.5%(칸 마감률)와 견줬다 — '
        '<b>단위가 다른 두 수를 비교한 것이다.</b> 68차가 상위 둘을 끝까지 캐니 마감률이 '
        '둘 다 <b>6.0%</b>로, 포아송비와 같은 자리였다. <b>낱말→값 통과율이 약 30%</b>이므로 '
        '아직 안 캔 표적은 왼쪽 값에 0.3을 곱해 읽어라.</p>'
        '<p class="note">낮은 쪽의 원인은 셋으로 갈린다. '
        '<b>젖음</b>은 재료의 물성이 아니라 <b>공정의 결과</b>로 발표돼 벤더 시트에 열이 없다. '
        '<b>Prony</b>는 문서에 있으나 <b>표가 아니라 마스터커브 그림</b>이라 디지타이즈 대상이다. '
        '<b>율속·피로</b>는 적중이 「이 논문이 율속을 언급한다」이지 '
        '「이 등급의 상수를 찍는다」가 아니다 — 적중 수가 성과를 예고한다는 착각을 주는 구간이다.</p>'
        f'<p class="note"><b>이 표는 측정치다.</b> {esc(YIELD_MEASURED)}. '
        '다른 지표와 달리 DB 조회로 갱신되지 않는다.</p>')


def lead(items):
    """개조식 요약 항목. 각 항은 명사형으로 끝낸다 — 서술문을 넣지 마라."""
    return '<ul class="lead">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def clip(t, n):
    """낱말 중간에서 자르지 않는다 — 마지막 공백까지만 남기고 말줄임표를 붙인다."""
    t = t.strip()
    if len(t) <= n:
        return t
    cut = t[:n].rstrip()
    sp = cut.rfind(" ")
    if sp > n * 0.6:
        cut = cut[:sp]
    return cut.rstrip(" ,;·-") + "\u2026"


def sec(i, title, sub):
    return (f'<section id="s{i}"><div class="shead"><span class="sno">{i:02d}</span>'
            f'<h2>{title}</h2><p class="ssub">{sub}</p></div>')


def dl(items):
    out = ['<dl class="defs">']
    for t, d in items:
        out.append(f'<dt>{esc(t)}</dt><dd>{esc(d)}</dd>')
    out.append('</dl>')
    return "".join(out)


CSS = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600&display=swap">
<style>
:root{
  --ink:#14181c; --ink2:#3d474f; --ink3:#6b7780;
  --paper:#f5f6f7; --card:#ffffff; --line:#dfe3e6;
  --teal:#0d5c55; --teal2:#2f8378; --tealw:#e2efec;
  --clay:#a8674a; --clayw:#f4e9e3;
  --ok:#0d5c55; --warn:#9a6b12; --crit:#98402f;
  --mono:ui-monospace,"SF Mono","Cascadia Mono","Roboto Mono",Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Pretendard","Segoe UI","Noto Sans KR",
         "Malgun Gothic","Apple SD Gothic Neo",sans-serif;
  --serif:"Noto Serif KR","Nanum Myeongjo","Apple SD Gothic Neo",Georgia,serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ink:#e8ecee; --ink2:#aab4bb; --ink3:#7c878e;
  --paper:#12161a; --card:#1a2026; --line:#2b333a;
  --teal:#5fb3a6; --teal2:#3f8b80; --tealw:#152b28;
  --clay:#cf9375; --clayw:#2c211b;
  --ok:#5fb3a6; --warn:#d5a343; --crit:#e08a75;
}}
:root[data-theme="dark"]{
  --ink:#e8ecee; --ink2:#aab4bb; --ink3:#7c878e;
  --paper:#12161a; --card:#1a2026; --line:#2b333a;
  --teal:#5fb3a6; --teal2:#3f8b80; --tealw:#152b28;
  --clay:#cf9375; --clayw:#2c211b;
  --ok:#5fb3a6; --warn:#d5a343; --crit:#e08a75;
}
:root[data-theme="light"]{
  --ink:#14181c; --ink2:#3d474f; --ink3:#6b7780;
  --paper:#f5f6f7; --card:#ffffff; --line:#dfe3e6;
  --teal:#0d5c55; --teal2:#2f8378; --tealw:#e2efec;
  --clay:#a8674a; --clayw:#f4e9e3;
  --ok:#0d5c55; --warn:#9a6b12; --crit:#98402f;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
     font-size:16px;line-height:1.72;-webkit-font-smoothing:antialiased}
.mono,code,.n,.pct,.bval{font-family:var(--mono);font-variant-numeric:tabular-nums}
code{background:var(--tealw);color:var(--teal);padding:.08em .34em;border-radius:3px;font-size:.88em}
b{font-weight:650}
em{font-style:normal}

.hero{max-width:1080px;margin:0 auto;padding:76px 28px 40px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.16em;text-transform:uppercase;
         color:var(--teal);margin:0 0 22px}
.hero h1{font-family:var(--serif);font-weight:600;font-size:clamp(29px,4.4vw,47px);line-height:1.32;letter-spacing:-.014em;
         font-weight:700;margin:0 0 22px;text-wrap:pretty;max-width:26ch}
.lede{font-size:17.5px;color:var(--ink2);max-width:66ch;margin:0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:1px;
      background:var(--line);border:1px solid var(--line);border-radius:10px;
      overflow:hidden;margin-top:40px}
.kpi{background:var(--card);padding:20px 18px;display:flex;flex-direction:column;gap:2px}
.kpi b{font-family:var(--mono);font-size:29px;font-weight:600;letter-spacing:-.02em;
       color:var(--teal);line-height:1.1}
.kpi span{font-size:13px;font-weight:600;margin-top:5px}
.kpi em{font-size:12px;color:var(--ink3);font-family:var(--mono)}

.toc{position:sticky;top:0;z-index:9;background:var(--paper);border-bottom:1px solid var(--line)}
section{scroll-margin-top:96px}
.toc ol{max-width:1080px;margin:0 auto;padding:11px 28px;list-style:none;display:flex;
        flex-wrap:wrap;gap:2px 20px;counter-reset:t}
.toc li{counter-increment:t}
.toc a{font-family:var(--mono);font-size:12px;color:var(--ink3);text-decoration:none}
.toc a::before{content:counter(t,decimal-leading-zero) " ";color:var(--teal2)}
.toc a:hover{color:var(--teal)}
.toc a:focus-visible{outline:2px solid var(--teal);outline-offset:3px}

section{max-width:1080px;margin:0 auto;padding:56px 28px 8px;border-top:1px solid var(--line)}
section:first-of-type{border-top:none}
.shead{margin-bottom:26px}
.sno{font-family:var(--mono);font-size:12px;color:var(--teal2);letter-spacing:.1em}
.shead h2{font-family:var(--serif);font-weight:600;font-size:clamp(21px,2.5vw,28px);margin:6px 0 5px;letter-spacing:-.012em}
.ssub{margin:0;color:var(--ink3);font-size:14.5px}
h4{font-size:13px;font-family:var(--mono);letter-spacing:.05em;text-transform:uppercase;
   color:var(--ink3);margin:30px 0 12px;font-weight:600}
p{max-width:74ch}
ul.lead{list-style:none;margin:20px 0 26px;padding:0;display:flex;flex-direction:column;gap:10px;max-width:64ch}
ul.lead>li{position:relative;padding-left:19px;font-size:15px;line-height:1.66;color:var(--ink)}
ul.lead>li::before{content:"";position:absolute;left:1px;top:.72em;width:9px;height:1px;background:var(--teal2)}
.note{background:var(--card);border-left:3px solid var(--teal2);padding:14px 18px;
      border-radius:0 7px 7px 0;font-size:14.5px;color:var(--ink2);max-width:none}
.note.warn{border-left-color:var(--warn)}

.grid4{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;
       background:var(--line);border:1px solid var(--line);border-radius:9px;overflow:hidden;margin:22px 0}
.cell{background:var(--card);padding:16px 16px}
.cell b{display:block;font-family:var(--mono);font-size:25px;color:var(--teal);font-weight:600}
.cell span{font-size:12.5px;color:var(--ink3)}

.defs{display:grid;grid-template-columns:auto 1fr;gap:6px 20px;margin:22px 0;
      font-size:14.5px;align-items:baseline}
.defs dt{font-weight:650;color:var(--teal);white-space:nowrap}
.defs dd{margin:0;color:var(--ink2)}

.tblwrap{overflow-x:auto;border:1px solid var(--line);border-radius:9px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{padding:9px 13px;text-align:left;border-bottom:1px solid var(--line);vertical-align:middle}
thead th{font-size:11.5px;font-family:var(--mono);text-transform:uppercase;letter-spacing:.05em;
         color:var(--ink3);font-weight:600;background:var(--paper);white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
td.n,th.n{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}
td.nm{font-weight:600;white-space:nowrap}
tr.tot td{background:var(--paper);font-weight:650;border-top:2px solid var(--line)}
.barcell{min-width:150px}
.pct{font-size:12px;color:var(--ink3);margin-left:8px}
.blk{font-size:11px;color:var(--ink3);opacity:.7;margin-left:5px}
.hsub{font-weight:400;color:var(--ink3);opacity:.8}
.src td.kind{font-family:var(--mono);font-size:11.5px;color:var(--ink3);white-space:nowrap}
.unf td:first-child{color:var(--teal2);white-space:nowrap}

.btrack{display:inline-block;width:110px;height:7px;background:var(--line);
        border-radius:4px;overflow:hidden;vertical-align:middle}
.btrack.sm{width:96px;height:6px}
.bfill{display:block;height:100%;border-radius:4px;background:var(--teal)}
.bfill.clay{background:var(--clay)}
.brow{display:flex;align-items:center;gap:10px;padding:5px 0;font-size:13.5px}
.blabel{flex:0 0 150px;color:var(--ink2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bval{flex:0 0 48px;text-align:right;font-size:12.5px}
.bnote{color:var(--ink3);font-size:12px;font-family:var(--mono)}

.pill{display:inline-block;padding:2px 9px;border-radius:11px;font-family:var(--mono);
      font-size:12px;font-weight:600}
.pill.ok{background:var(--tealw);color:var(--ok)}
.pill.warn{background:#f7edd7;color:var(--warn)}
.pill.crit{background:var(--clayw);color:var(--crit)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .pill.warn{background:#2e2513}}
:root[data-theme="dark"] .pill.warn{background:#2e2513}

.tiers{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:22px 0}
.tier{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:15px 16px;
      border-top:3px solid var(--teal)}
.tier.t2{border-top-color:var(--teal2)}
.tier.t3{border-top-color:#9bb0ab}
.tier.t4{border-top-color:var(--clay)}
.tier b{font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--ink3)}
.tn{display:block;font-family:var(--mono);font-size:26px;font-weight:600;color:var(--teal);line-height:1.2}
.tier.t4 .tn{color:var(--clay)}
.tp{font-family:var(--mono);font-size:12px;color:var(--ink3)}
.tt{margin:9px 0 3px;font-size:14px;font-weight:600;max-width:none}
.td{margin:0;font-size:13px;color:var(--ink3);max-width:none}

.split{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px 40px}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin:22px 0}
.box{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:16px 18px}
.box.ok{border-left:3px solid var(--teal)}
.box.crit{border-left:3px solid var(--clay)}
.box h4{margin-top:0}
.box .big{font-family:var(--mono);font-size:38px;font-weight:600;color:var(--teal);
          margin:0 0 6px;line-height:1}
.box.crit .big{color:var(--clay)}
.box .big em{font-size:15px;color:var(--ink3);margin-left:5px}
.box p{font-size:14px;color:var(--ink2);max-width:none}
.mini td{font-size:13.5px;padding:9px 0;vertical-align:top;border-bottom:1px solid var(--line)}
.mini td.nm{padding-right:16px;color:var(--ink);width:36%;white-space:normal}
.mini .where{display:block;font-family:var(--mono);font-size:11.5px;color:var(--ink3);font-weight:400}
.mini .ex{display:block;font-family:var(--mono);font-size:11.5px;color:var(--teal2);margin-bottom:3px}
.mini tr:last-child td{border-bottom:none}

.steps{list-style:none;counter-reset:s;padding:0;margin:22px 0;
       display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:1px;
       background:var(--line);border:1px solid var(--line);border-radius:9px;overflow:hidden}
.steps li{background:var(--card);padding:14px 16px;display:flex;gap:13px;align-items:flex-start}
.sn{font-family:var(--mono);font-size:12px;color:var(--teal2);padding-top:3px}
.steps b{font-size:14.5px}
.steps p{margin:2px 0 0;font-size:13px;color:var(--ink3);max-width:none}
.rules{padding-left:0;list-style:none;counter-reset:r;margin:22px 0;display:grid;gap:10px}
.rules li{counter-increment:r;background:var(--card);border:1px solid var(--line);
          border-radius:8px;padding:13px 16px 13px 52px;position:relative}
.rules li::before{content:counter(r);position:absolute;left:16px;top:13px;font-family:var(--mono);
                  font-size:12px;color:var(--teal);font-weight:600}
.rules b{font-size:14.5px}
.rules p{margin:2px 0 0;font-size:13.5px;color:var(--ink2);max-width:none}

.krow{display:flex;justify-content:space-between;gap:14px;padding:7px 0;
      border-bottom:1px solid var(--line);font-size:13.5px}
.krow span{color:var(--ink2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.krow b{color:var(--teal);font-weight:600}
.tips{margin:0;padding-left:18px;font-size:13.5px;color:var(--ink2)}
.tips li{margin-bottom:7px}

.verify{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin:22px 0}
.vcard{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:15px 17px}
.vcard b{display:block;font-size:14.5px;margin-bottom:5px;color:var(--teal)}
.vcard p{margin:0;font-size:13.5px;color:var(--ink2);max-width:none}

.chart{margin:22px 0;background:var(--card);border:1px solid var(--line);
       border-radius:9px;padding:16px 16px 10px}
.chart svg{width:100%;height:180px;display:block}
.chart .ar{fill:var(--tealw)}
.chart .ln{fill:none;stroke:var(--teal);stroke-width:2;vector-effect:non-scaling-stroke;
           stroke-linejoin:round}
.chart .dt circle{fill:var(--teal)}
.xax{display:flex;justify-content:space-between;font-family:var(--mono);
     font-size:11.5px;color:var(--ink3);margin-top:6px}

footer{max-width:1080px;margin:44px auto 0;padding:22px 28px 60px;border-top:1px solid var(--line)}
footer p{font-family:var(--mono);font-size:12px;color:var(--ink3);margin:0 0 5px}
footer .gen{color:var(--ink3);opacity:.8}
@media (max-width:640px){
  .hero{padding:48px 20px 30px} section{padding:40px 20px 6px} footer{padding:20px 20px 44px}
  .toc ol{padding:9px 20px} .blabel{flex-basis:110px}
}

.flow{margin:26px 0 8px}
.flow svg{width:100%;height:auto;display:block;color:var(--ink2)}
.flow .fb rect{fill:var(--card);stroke:var(--teal2);stroke-width:1.2}
.flow .fb.rj rect{stroke:var(--clay);stroke-dasharray:4 3}
.flow .fb.gd rect{stroke:var(--teal);stroke-width:1.6}
.flow .fb.alt rect{stroke:var(--teal2);stroke-dasharray:4 3}
.flow .ft text{text-anchor:middle;font-size:13px;font-weight:650;fill:var(--ink)}
.flow .ft text.sm{font-size:10.5px;font-weight:400;fill:var(--ink3)}
.flow .ft.rj text{fill:var(--clay)}
.flow .ft.rj text.sm{fill:var(--ink3)}
.flow .fa line{stroke:currentColor;stroke-width:1.4}
.flow .fa.rj line{stroke:var(--clay);stroke-dasharray:4 3}
.flow .fa.alt line{stroke:var(--teal2);stroke-dasharray:4 3}
.flow .fl text{text-anchor:middle;font-family:var(--mono);font-size:10.5px;fill:var(--ink3)}
.flow figcaption{margin-top:12px;font-size:13.5px;color:var(--ink2);max-width:none}
details.more{margin:18px 0;border:1px solid var(--line);border-radius:9px;background:var(--card)}
details.more>summary{cursor:pointer;padding:12px 16px;font-size:13.5px;color:var(--teal);
                     font-weight:600;list-style:none}
details.more>summary::-webkit-details-marker{display:none}
details.more>summary::before{content:"▸ ";color:var(--teal2)}
details.more[open]>summary::before{content:"▾ "}
details.more>summary:focus-visible{outline:2px solid var(--teal);outline-offset:2px}
details.more .tblwrap{border:none;border-top:1px solid var(--line);border-radius:0}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>"""


if __name__ == "__main__":
    main()
