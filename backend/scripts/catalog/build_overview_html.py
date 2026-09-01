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
     "손으로 만든 항등식으로 탄성률을 만들고 출처는 Satas 핸드북을 달았다. "
     "핸드북이 실제로 인쇄한 0.4 MPa로 되돌렸다."),
    ("AZoM <code>Shear Modulus</code>", "폴리머·세라믹 전 행",
     "같은 표의 E·ν로 E/(2(1+ν))를 계산하면 마지막 자리까지 일치한다 "
     "(96% 알루미나: 300/(2×1.21) = 123.97 = 인쇄값 124)."),
    ("AZoM <code>Ductility</code>", "세라믹 행",
     "σts/E 유도값이다. 파단연신율로 옮기면 취성재에 소성 연신을 부여하게 된다."),
    ("AZoM <code>Endurance Limit</code>", "폴리머 행",
     "k × Elastic Limit이고 범위 양 끝점이 정확히 같은 배수다"
     "(PET 0.6000/0.6000 · PI 0.5500/0.5500 · LDPE 0.7000/0.7000). "
     "세라믹 행은 MgO의 내구한도 하한이 같은 표의 탄성한도 하한을 넘는다 — 물리적으로 불가능하다."),
    ("MakeItFrom 폴리머 <code>G</code>", "전 폴리머 행",
     "LDPE가 E=0.30 GPa, G=0.21 GPa를 동시에 인쇄하는데 이러면 ν=−0.29가 된다. "
     "같은 사이트의 금속 값은 정합한다 — 폴리머만 오염됐다."),
    ("α = β/3", "액체 전해질",
     "인쇄된 것은 체적팽창계수뿐이었다. 3으로 나누면 역산이라 칸을 비웠다."),
]

# 허용되는 계산 — 경계가 어디인지가 이 표의 요지다.
COMPUTED_OK = [
    ("단위 환산", "psi→Pa, cal/(cm·s·°C)→W/(m·K), Barrer→SI, N/25mm→N/m",
     "같은 양을 다른 눈금으로 옮기는 것뿐이다. 원문 값과 배율을 notes에 남긴다."),
    ("원문이 인쇄한 피팅", "Prony 급수, Ogden·Mooney-Rivlin 계수, Johnson-Cook, Basquin 회귀식",
     "저자가 자기 데이터에 맞춰 발표한 상수다. 우리가 곡선에서 뽑은 것이 아니다."),
    ("공표된 상관식", "Okabe 적층재 S-N, Maekawa 세라믹 피로, Ishiyama 흑연",
     "누가 그 관계를 보증하느냐가 갈림길이다. 논문이 보증하면 쓰고, 우리가 만들면 안 쓴다."),
    ("무차원비 이전", "공여재 정적강도로 나눠 수용재 강도를 곱한다",
     "입력 두 숫자가 모두 원문 인쇄값이어야 한다. 계보를 notes에 적는다."),
    ("클래스 중앙값", "카탈로그 내 같은 클래스 실측값의 중앙값",
     "출처 제목이 그 사실을 그대로 말한다. tier4이고 assumption 표지를 단다."),
]

RULES = [
    ("지어내지 않는다", "빈 칸이 틀린 값보다 낫다. 문서에 실제로 인쇄된 숫자만 넣는다."),
    ("역산 금지", "다른 물성에서 계산한 값을 저장하지 않는다. 계산은 원문이 했을 때만 옮긴다."),
    ("그래프에서 읽지 않는다", "축 눈금과 스캔 해상도가 유효숫자를 정한다 — 읽으면 그 자릿수는 우리가 만든 것이다."),
    ("재인쇄본·2차 인용 불가", "인용된 값은 1차 출처까지 따라가서 확인한다."),
    ("조건 없는 값은 값이 아니다", "온도·주파수·방향·습도가 없으면 해석 입력이 되지 않는다."),
    ("자릿수 대조", "그 재료의 상위 tier 값과 자릿수가 어긋나면 넣지 않는다."),
    ("인접 열 오독 주의", "표는 한 열이 통째로 밀려 있을 수 있다. 대조군 행과 본문 서술로 검산한다."),
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
    ("빈칸 탐지", "커버리지 격자를 재계산해 (재료 × 물성) 공백을 뽑는다"),
    ("표적 선정", "칸 수가 아니라 <b>칸/재료</b>와 <b>1칸 부족 재료</b>로 우선순위를 정한다"),
    ("브리프 전달", "규칙·함정 지도·확정 부재 목록을 그대로 넘긴다"),
    ("병렬 수집", "재료군별로 배치를 나눠 동시에 원문을 받는다"),
    ("청크 저장", "10~12종마다 중간 파일을 쓴다 — 끝에 몰아 쓰면 중단 시 전부 잃는다"),
    ("값 검증", "규칙 6 자릿수 대조 · 자기 검산 · 원문 문자열 대조"),
    ("인제스트", "스키마·단위·조건·tier 규약을 거치지 못하면 거부한다"),
    ("반례 검증", "부재 선언에 실측 반례가 하나라도 있으면 선언을 자동 은퇴시킨다"),
    ("무결성 검사", f"{_N_CHECKS}항목이 전부 0이어야 배포한다"),
    ("기록", "성공보다 <b>실패와 함정</b>을 남긴다 — 다음 파동이 같은 벽에 부딪히지 않도록"),
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
    for i, t in enumerate(["경로", "격자", "현황", "계통", "등급", "출처", "사이클", "규칙",
                           "역산 경계", "부재", "검증", "성장", "남은 일"], 1):
        A(f'<li><a href="#s{i}">{t}</a></li>')
    A('</ol></nav>')

    # ── 1. 경로 (그림이 메커니즘을 대신 말한다)
    A(sec(1, "경로", "값이 어디서 와서 어디로 가는가"))
    A(FLOW_SVG)
    A('</section>')

    # ── 2. 격자
    A(sec(2, "격자", "무엇을 세고 있는가"))
    A(f'<p>재료 {n_mat}종 × 물성 정의 {n_def}종은 {n_mat * n_def:,}칸이지만 이것을 다 세지 않는다. '
      f'<b>세라믹에 항복강도를 요구하고 도체에 유전율을 요구하면 분모가 거짓이 된다.</b> '
      f'그래서 실제 해석 13종이 각각 요구하는 물성만 골라 <b>{tot_cells:,}칸</b>의 격자를 만들고, '
      f'그 격자만 센다.</p>')
    A('<div class="grid4">')
    for v, k in [(f"{tot_cells:,}", "해석이 실제로 요구하는 칸"),
                 (f"{tot_filled:,}", "채워진 칸"),
                 (f"{tot_unfill:,}", "구조적으로 못 채우는 칸"),
                 (f"{remain:,}", "아직 채울 수 있는 칸")]:
        A(f'<div class="cell"><b>{v}</b><span>{k}</span></div>')
    A('</div>')
    A('<p class="note">택일군이 있다. 낙하해석의 소성 입력은 <code>항복강도</code> 하나든 '
      '<code>인장강도+파단연신율</code> 쌍이든 역할이 채워지므로 <b>칸 하나</b>로 센다. '
      '어느 쪽이 인쇄되는지는 시험규격 관행이 정하지, 재료가 정하지 않는다.</p>')
    A(dl([("셀 채움", "채워진 칸 / 전체 칸 — 수집 진척도"),
          ("실측기반", "tier4(가정·계산)를 뺀 채움 — 근거의 실제 크기"),
          ("유효채움", "구조적 부재를 분모에서 뺀 채움 — 도달 가능한 천장 대비"),
          ("적용 대비 준비율", "그 해석이 원리적으로 성립하는 재료만 분모로 둔 재료 준비율")]))
    A('</section>')

    # ── 2. 현황
    A(sec(3, "현황", "해석 13종이 지금 돌아가는가"))
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
    A(f'<p class="note"><b>셀 채움과 실측기반의 차이 {(tot_filled - tot_meas) * 100 / tot_cells:.1f}%p'
      f'({tot_filled - tot_meas:,}칸)가 가정값이 만든 착시다.</b> 표를 하나만 보면 속는다 — '
      f'채움률이 100%인 해석도 실측기반은 67%일 수 있다.</p>')
    A('</section>')

    # ── 3. 계통 — 43·49차 태깅이 끝나 이제 계통별로 셀 수 있다.
    A(sec(4, "계통", "어느 계통이 비었고, 그 빈칸이 무엇인가"))
    A(f'<p>제품 재료 {sc["total"]["n_mat"]}종을 계통으로 태깅했다. 아래는 '
      f'<b>코어 {len(sc["core"])}물성</b>(밀도·영률·포아송비·CTE·열전도율·비열·인장강도) '
      f'{sc["total"]["cells"]:,}칸의 채움률이다 — 해석 격자와 달리 <b>재료 하나가 최소한 이것은 '
      f'있어야 한다</b>는 축이다.</p>')
    A('<div class="tblwrap"><table class="cov">')
    A('<thead><tr><th>계통</th><th class="n">재료</th><th>코어 채움</th><th class="n">빈칸</th>'
      '<th class="n">해당<br>없음</th><th class="n">벤더<br>부재</th>'
      '<th class="n">판정이<br>자유 키에</th><th class="n">등급<br>미확정</th>'
      '<th class="n">진짜<br>남은 것</th></tr></thead><tbody>')
    for r in sc["rows"]:
        cls = "ok" if r["pct"] >= 90 else ("warn" if r["pct"] >= 70 else "crit")
        A(f'<tr><td class="nm">{esc(r["subsystem"])}</td><td class="n">{r["n_mat"]}</td>'
          f'<td class="barcell"><span class="btrack sm"><i class="bfill teal" '
          f'style="width:{r["pct"]:.1f}%"></i></span>'
          f'<span class="pct">{r["pct"]:.1f}</span></td>'
          f'<td class="n mono">{r["blank"]}</td>'
          f'<td class="n mono">{r["V1"] or "·"}</td><td class="n mono">{r["V2"] or "·"}</td>'
          f'<td class="n mono">{r["V3"] or "·"}</td><td class="n mono">{r["V4"] or "·"}</td>'
          f'<td class="n"><span class="pill {cls}">{r["V5"]}</span></td></tr>')
    t = sc["total"]
    A(f'<tr class="tot"><td class="nm">전체</td><td class="n">{t["n_mat"]}</td>'
      f'<td class="barcell"><span class="btrack sm"><i class="bfill teal" '
      f'style="width:{t["pct"]:.1f}%"></i></span><span class="pct">{t["pct"]:.1f}</span></td>'
      f'<td class="n mono">{t["blank"]:,}</td><td class="n mono">{t["V1"]}</td>'
      f'<td class="n mono">{t["V2"]}</td><td class="n mono">{t["V3"]}</td>'
      f'<td class="n mono">{t["V4"]}</td><td class="n mono">{t["V5"]:,}</td></tr>')
    A('</tbody></table></div>')
    A('<details class="more"><summary>다섯 갈래가 각각 무슨 뜻인가</summary>'
      '<div class="tblwrap"><table class="unf"><tbody>'
      + "".join(f'<tr><td class="nm">{esc(lbl)}</td><td>{esc(why)}</td></tr>'
                for _, lbl, why in CR.VERDICT_LABEL) + '</tbody></table></div></details>')
    A(f'<p class="note warn"><b>빈칸 {t["blank"]:,}칸 중 실제로 캘 수 있는 것은 {t["V5"]:,}칸이다.</b> '
      f'나머지 {t["blank"] - t["V5"]}칸은 판정이 끝났거나 원리적으로 못 닫는다. '
      f'그리고 그중 {t["V3"]}칸은 <b>판정이 자유 키에 적혀 있어 이 표가 스스로 읽지 못한다</b> — '
      f'집계가 읽는 자리(<code>core_not_applicable</code>·'
      f'<code>core_absent_from_vendor_sheet</code>)로 옮기기 전까지는 다음 파동이 또 센다.</p>')
    A('</section>')

    # ── 3. 등급
    A(sec(5, "등급", "tier가 무엇을 뜻하고 왜 가정을 허용하는가"))
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
    A(f'<p>tier4를 <b>허용하되 반드시 표시한다.</b> 빈 칸으로 두면 해석이 아예 안 돌고, '
      f'표시 없이 채우면 가정이 실측 행세를 한다. 그래서 tier4는 '
      f'<code>method="estimated"</code> · <code>conditions.assumption=true</code> · '
      f'notes에 근거를 함께 요구하고, 지표를 <b>셀 채움과 실측기반 두 줄로 나란히</b> 낸다. '
      f'현재 assumption 표지를 단 값이 {n_assum:,}건이다.</p>')
    A('<div class="split">')
    A('<div><h4>method 분포</h4>' + "".join(
        bar_row(k, v * 100 / n_val, f"{v:,}건") for k, v in
        sorted(methods.items(), key=lambda z: -z[1])) + '</div>')
    A('<div><h4>도메인 분포</h4>' + "".join(
        bar_row(f"{k} ({dom_defs.get(k, 0)}종)", v * 100 / n_val, f"{v:,}건")
        for k, v in domains[:7]) + '</div>')
    A('</div></section>')

    # ── 4. 출처
    A(sec(6, "출처", "값 하나에 문서 하나"))
    A(f'<p>스키마가 <b>출처 없는 값의 저장 자체를 거부한다</b> — 등록 API가 DOI·URL·제목 중 하나를 '
      f'요구한다. 덕분에 {n_val:,}건 전부에 출처가 붙어 있고 끊어진 참조가 0건이다. '
      f'조건(온도·주파수·방향 등)이 붙은 값은 {n_cond:,}건({n_cond * 100 / n_val:.1f}%)이다.</p>')
    A('<div class="split">')
    A('<div><h4>출처 종류 ' + f'({n_src:,}건)</h4>' + "".join(
        bar_row(k, v * 100 / n_src, f"{v}건") for k, v in kinds) + '</div>')
    A('<div><h4>재료 분류 ' + f'({n_mat}종)</h4>' + "".join(
        bar_row(k, v * 100 / n_mat, f"{v}종", "clay") for k, v in cats) + '</div>')
    A('</div>')
    A('<h4>값을 가장 많이 낸 문서</h4><div class="tblwrap"><table class="src"><tbody>')
    for t, kd, n in top_src:
        A(f'<tr><td class="n mono">{n}</td><td class="kind">{esc(kd)}</td>'
          f'<td>{esc(t[:88])}</td></tr>')
    A('</tbody></table></div>')
    A('<p class="note">한 문서가 800건 넘게 내는 경우가 있다 — 패키지 워피지 논문 하나가 '
      '재료 수십 종의 물성표를 통째로 싣기 때문이다. '
      '<b>그래서 상위 문서일수록 검증 비용이 크다</b> — 한 열이 밀려 있으면 수백 건이 함께 틀린다.</p>')
    A('</section>')

    # ── 5. 사이클
    A(sec(7, "사이클", "한 파동에 무엇을 하는가"))
    A('<ol class="steps">')
    for i, (t, d) in enumerate(CYCLE, 1):
        A(f'<li><span class="sn">{i:02d}</span><div><b>{esc(t)}</b><p>{d}</p></div></li>')
    A('</ol>')
    A('<p class="note">5단계(청크 저장)는 <b>사고에서 나온 규칙</b>이다. '
      '배치 6개가 결과를 끝에 몰아 쓰다가 동시에 죽어 산출물이 0이었다. '
      '이후 모든 파동이 10~12종마다 중간 파일을 쓰고, 다시는 잃지 않았다.</p>')
    A('</section>')

    # ── 6. 규칙
    A(sec(8, "규칙", "절대 넘지 않는 선"))
    A('<ol class="rules">')
    for i, (t, d) in enumerate(RULES, 1):
        A(f'<li><b>{esc(t)}</b><p>{esc(d)}</p></li>')
    A('</ol>')
    A('<p class="note">이 규칙들은 이상론이 아니라 <b>실제로 사고를 막은 기록</b>이다. '
      '규칙 4는 "3M이 인쇄한 0.49"라던 43건의 근거 문장이 사실은 계열 기술자료였음을 잡아냈고, '
      '규칙 6은 1000배 큰 굽힘강도 두 건을 걸러냈다.</p>')
    A('</section>')

    # ── 7. 역산
    A(sec(9, "역산 경계", "무엇이 계산이고 무엇이 조작인가"))
    A('<p><b>계산이 금지된 것이 아니라, 계산을 <em>누가</em> 했느냐가 갈림길이다.</b> '
      '원문이 자기 데이터에 피팅한 상수는 옮기고, 우리가 다른 물성에서 만들어낸 값은 넣지 않는다. '
      '표 위에서 둘은 똑같이 생겼다.</p>')
    A('<div class="two">')
    A('<div class="box ok"><h4>옮긴다 — 원문이 계산한 것</h4><table class="mini"><tbody>')
    for t, ex, why in COMPUTED_OK:
        A(f'<tr><td class="nm">{t}</td><td><span class="ex">{ex}</span>{why}</td></tr>')
    A('</tbody></table></div>')
    A('<div class="box crit"><h4>넣지 않는다 — 우리가 계산한 것</h4><table class="mini"><tbody>')
    for t, where, why in BACKCALC_CAUGHT:
        A(f'<tr><td class="nm">{t}<span class="where">{esc(where)}</span></td><td>{why}</td></tr>')
    A('</tbody></table></div>')
    A('</div>')
    A('<details class="more"><summary>계산값은 지금 얼마나 있고, 역산은 어떻게 잡아내는가</summary>')
    A(f'<h4>지금 계산값으로 들어와 있는 것</h4>'
      f'<p><code>method="computed"</code>는 {methods.get("computed", 0):,}건이다. '
      f'tier 분포가 {" · ".join(f"t{t} {n}" for t, n in sorted(comp_tier.items()))}인데, '
      f'<b>tier1·2에 계산값이 있는 것이 정상</b>이다 — 그 논문이 자기 시편에 피팅해 발표한 '
      f'구성모델 상수이기 때문이다. 반대로 <code>estimated</code>는 '
      f'{methods.get("estimated", 0):,}건 전부가 tier3 이하로 내려가 있다.</p>')
    A('<div class="split">')
    A('<div><h4>계산값이 많은 물성</h4>' + "".join(
        f'<div class="krow"><span>{esc(defname.get(k, k))}</span>'
        f'<b class="mono">{n}</b></div>' for k, n in comp_keys[:8]) + '</div>')
    A('<div><h4>역산을 어떻게 잡아내는가</h4>'
      '<ul class="tips">'
      '<li><b>마지막 자리까지 일치하는가.</b> E/(2(1+ν))를 손으로 계산해 인쇄값과 대조한다.</li>'
      '<li><b>범위 양 끝점이 같은 배수인가.</b> 유도열은 하한·상한이 정확히 같은 계수로 묶인다.</li>'
      '<li><b>물리적으로 가능한가.</b> 내구한도 하한이 탄성한도 하한을 넘으면 그 열은 유도값이다.</li>'
      '<li><b>ν가 음수로 나오는가.</b> E와 G를 함께 인쇄하는 표는 이 검산으로 무너진다.</li>'
      '<li><b>대조군 행이 본문과 같은가.</b> 0 wt% 대조 행이 본문 값과 같으면 그 값은 첨가물의 것이다.</li>'
      '</ul></div>')
    A('</div></details>')
    A('<p class="note"><b>근거를 바꾸는 편집이 값을 바꾸는 편집보다 늦게 발각된다.</b> '
      '추정 라벨 5건이 출처 정리 중 실제 벤더 문서 이름으로 바뀌면서, '
      '값은 하나도 안 바뀐 채 그 아래 18개 값의 근거만 거짓이 됐다. 지금은 검사가 이 패턴을 잡는다.</p>')
    A('</section>')

    # ── 8. 부재
    A(sec(10, "부재", "채울 수 없는 칸을 분모에서 뺀다"))
    A(f'<p>액체에 항복강도를, 증착 도판트에 투습도를 요구하면 그 칸은 영원히 비어 있다. '
      f'분모에 남겨 두면 <b>도달할 수 없는 100%를 좇게 된다.</b> '
      f'그래서 (재료군 × 물성) 쌍 단위로 부재를 선언하고 {tot_unfill:,}칸을 분모에서 뺐다. '
      f'현재 선언 {len(CR.UNFILLABLE)}건이다.</p>')
    A(f'<details class="more"><summary>선언 {len(CR.UNFILLABLE)}건 전부 보기</summary>'
      '<div class="tblwrap"><table class="unf"><tbody>'
      + "".join(f'<tr><td class="n mono">{len(k)}키</td><td>{esc(r)}</td></tr>'
                for m, k, r in CR.UNFILLABLE) + '</tbody></table></div></details>')
    A('<p class="note"><b>선언은 주장이 아니라 반례로 검증된다.</b> 문서에 기록된 사유가 있고, '
      '그 군의 어느 재료도 그 물성을 <b>실측으로</b> 갖고 있지 않아야 부재로 친다 — '
      '값이 하나라도 들어오면 그 쌍은 자동으로 빠진다. '
      '"세라믹은 피로계수가 없다"가 알루미나 S-N 회귀식 하나에, '
      '"폼엔 박리강도가 없다"가 VHB 반례 25건에 무너졌다.</p>')
    A('<p class="note warn"><b>전수 검색이 비었다는 것은 검색 실패와 구분되지 않는다.</b> '
      '출처를 재다운로드해 grep한 결과가 0건이어도 그것만으로는 부재가 아니다 — '
      '인쇄된 부재 문장이나 기전(機轉) 논거가 있는 군만 선언에 넣는다.</p>')
    A('</section>')

    # ── 9. 검증
    A(sec(11, "검증", "다섯 겹으로 거른다"))
    A('<div class="verify">')
    for t, d in [
        (f"무결성 검사 {_N_CHECKS}항목", "구조를 본다. 출처 없는 값·단위 불일치·쌍이 깨진 모델 상수·"
                          "조건 없는 확산계수·근거 없는 tier4를 전부 0으로 만들어야 배포한다."),
        ("반례 검증", "부재 선언에 실측 반례가 하나라도 있으면 선언을 자동 은퇴시킨다. "
                  "우리가 만든 가정이 우리의 선언을 지우지는 못하게 tier4는 반례로 치지 않는다."),
        ("자기 검산", "얻은 값으로 그 논문의 다른 값을 예측해 본다. "
                  "Ogden 계수에서 E₀=2(μ₁+μ₂)를 계산해 같은 논문 실측 탄성률과 맞는지 본다."),
        ("원문 문자열 대조", "저장한 숫자가 인용 출처에 실제로 있는지 전문을 받아 grep한다. "
                       "0.176이라는 값이 원문에 0회 나오는 것을 이 방법으로 잡았다."),
        ("규칙 6 자릿수 대조", "같은 재료의 상위 tier 값과 자릿수가 어긋나면 넣지 않는다. "
                        "1000배 큰 굽힘강도 두 건이 여기 걸렸다."),
    ]:
        A(f'<div class="vcard"><b>{esc(t)}</b><p>{esc(d)}</p></div>')
    A('</div>')
    A('<p class="note">검사가 <b>오탐</b>을 냈을 때는 값이 아니라 <b>검사를 고친다</b> — '
      '왜 예외인지를 코드 주석에 남긴다. Prony 급수 밖에 있는 장기계수 E∞ 36건이 그렇게 걸렸다.</p>')
    A('</section>')

    # ── 10. 성장
    A(sec(12, "성장", f"{labels[0]} → {labels[-1]}"))
    A(f'<div class="chart"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" role="img" '
      f'aria-label="물성값 누적 성장 곡선">'
      f'<polygon points="{area}" class="ar"/><polyline points="{poly}" class="ln"/>'
      f'<g class="dt">{dots}</g></svg>'
      f'<div class="xax"><span>{labels[0]}</span><span>{labels[-1]}</span></div></div>')
    A(f'<p>{len(growth)}일 동안 {cum:,}건이 쌓였다. 파동을 계속 돌았고, '
      f'각 파동은 <b>이전 파동이 남긴 함정 지도를 읽고 시작한다.</b> '
      f'축적되는 것은 값만이 아니라 <b>어디서 속았는지의 목록</b>이다.</p>')
    A('</section>')

    # ── 11. 남은 일
    A(sec(13, "남은 일", "무엇이 실제로 남았는가"))
    A('<div class="two">')
    A(f'<div class="box"><h4>빈칸 — 거의 소진됐다</h4>'
      f'<p class="big">{remain}<em>칸</em></p>'
      f'<p>구조적 부재를 뺀 유효채움이 {tot_eff_filled * 100 / tot_eff:.1f}%다. '
      f'남은 칸은 흩어져 있고 하나씩 난이도가 높다 — 앵커 논문에 인장강도는 있는데 '
      f'변형률이 전문에 0회인 식이다.</p></div>')
    A(f'<div class="box crit"><h4>가정 대체 — 이것이 진짜 남은 일</h4>'
      f'<p class="big">{len(t4_cells):,}<em>칸</em></p>'
      f'<p>(재료 × 물성) {all_cells:,}칸 중 <b>{len(t4_cells) * 100 / all_cells:.1f}%가 '
      f'가정값으로만 대표된다.</b> 셋 중 하나는 아직 근거가 없다는 뜻이다.</p></div>')
    A('</div>')
    A('<div class="split">')
    A('<div><h4>대체 여지가 큰 물성</h4>' + "".join(
        f'<div class="krow"><span>{esc(defname.get(k, k))}</span><b class="mono">{n}</b></div>'
        for k, n in t4_by_key.most_common(8)) + '</div>')
    A('<div><h4>가정 의존이 큰 재료</h4>' + "".join(
        f'<div class="krow"><span>{esc(matname[m][:42])}</span><b class="mono">{n}칸</b></div>'
        for m, n in t4_by_mat.most_common(8)) + '</div>')
    A('</div>')
    A(f'<p class="note"><b>다만 대체 가능성은 물성마다 다르다.</b> 실측(tier≤3)으로 덮인 칸의 '
      f'비율이 열전도율은 {meas_cov("thermal.conductivity"):.0f}%인데 '
      f'포아송비는 {meas_cov("mechanical.poisson_ratio"):.0f}%다. '
      '<b>CAMPUS 스키마에 포아송비 필드가 없고</b>, Rogers 전 사이트에 '
      '<code>Poisson</code>이 5건이며, MnZn 페라이트 데이터북은 E·인장·경도·파괴인성까지 싣고 ν만 뺀다. '
      '<b>벤더가 아예 발표하지 않는 물성</b>이라 여기는 천장이 낮다.</p>')
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
          f"(해당없음 {_t['V1']} · 벤더부재 {_t['V2']} · 자유키판정 {_t['V3']} · "
          f"등급미확정 {_t['V4']} · 진짜 남은 것 {_t['V5']:,})")


FLOW_SVG = """<figure class="flow">
<svg viewBox="0 0 980 268" role="img" aria-label="원천에서 해석 카드까지 — 관문 둘이 값을 거르고, 검사기와 병합기가 DB 를 지킨다">
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
<text x="76" y="117">원천</text><text x="76" y="134" class="sm">논문·시트·규격</text>
<text x="244" y="117">채굴</text><text x="244" y="134" class="sm">배치가 표를 읽는다</text>
<text x="412" y="117">적재기</text><text x="412" y="134" class="sm">유일한 쓰기 문</text>
<text x="580" y="117">DB</text><text x="580" y="134" class="sm">값·출처·조건</text>
<text x="748" y="117">대표값 선택</text><text x="748" y="134" class="sm">행 여럿 중 하나</text>
<text x="910" y="117">카드·화면</text><text x="910" y="134" class="sm">해석 입력</text>
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
<text x="244" y="215">폐기 대장</text><text x="244" y="231" class="sm">왜 안 쓰는지 남긴다</text>
<text x="412" y="215">거부</text><text x="412" y="231" class="sm">단위·범위·출처·조건</text>
</g>

<!-- DB 를 지키는 둘 -->
<g class="fa gd">
<line x1="580" y1="96" x2="580" y2="62" marker-end="url(#ah)"/>
<line x1="612" y1="62" x2="612" y2="92" marker-end="url(#ah)"/>
</g>
<g class="fb gd"><rect x="500" y="18" width="192" height="44" rx="7"/></g>
<g class="ft gd">
<text x="596" y="37">검사기 · 병합기</text>
<text x="596" y="53" class="sm">배포 전 관문 · 운영 전파</text>
</g>

<!-- 대표값이 갈릴 때 -->
<g class="fa alt"><line x1="748" y1="148" x2="748" y2="196" marker-end="url(#ah)"/></g>
<g class="fb alt"><rect x="672" y="196" width="152" height="44" rx="7"/></g>
<g class="ft alt">
<text x="748" y="215">대안 후보 노출</text><text x="748" y="231" class="sm">진 값도 쓸 수 있다</text>
</g>
</svg>
<figcaption>값은 두 관문을 지나야 DB 에 들어간다 — <b>채굴이 버린 것은 대장에</b>, <b>적재기가 거부한 것은 반려로</b> 남는다.
DB 위에서는 검사기가 배포를 막고 병합기가 운영 전파를 책임진다. 한 재료·한 물성에 행이 여럿이면
선택기가 하나를 고르되 <b>진 후보를 지우지 않고 함께 낸다.</b></figcaption>
</figure>"""


def sec(i, title, sub):
    return (f'<section id="s{i}"><div class="shead"><span class="sno">{i:02d}</span>'
            f'<h2>{title}</h2><p class="ssub">{sub}</p></div>')


def dl(items):
    out = ['<dl class="defs">']
    for t, d in items:
        out.append(f'<dt>{esc(t)}</dt><dd>{esc(d)}</dd>')
    out.append('</dl>')
    return "".join(out)


CSS = """<style>
:root{
  --ink:#14181c; --ink2:#3d474f; --ink3:#6b7780;
  --paper:#f5f6f7; --card:#ffffff; --line:#dfe3e6;
  --teal:#0d5c55; --teal2:#2f8378; --tealw:#e2efec;
  --clay:#a8674a; --clayw:#f4e9e3;
  --ok:#0d5c55; --warn:#9a6b12; --crit:#98402f;
  --mono:ui-monospace,"SF Mono","Cascadia Mono","Roboto Mono",Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Pretendard","Segoe UI","Noto Sans KR",
         "Malgun Gothic","Apple SD Gothic Neo",sans-serif;
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
.hero h1{font-size:clamp(30px,4.6vw,50px);line-height:1.24;letter-spacing:-.022em;
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
.shead h2{font-size:clamp(22px,2.7vw,31px);margin:4px 0 4px;letter-spacing:-.018em;font-weight:700}
.ssub{margin:0;color:var(--ink3);font-size:14.5px}
h4{font-size:13px;font-family:var(--mono);letter-spacing:.05em;text-transform:uppercase;
   color:var(--ink3);margin:30px 0 12px;font-weight:600}
p{max-width:74ch}
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
