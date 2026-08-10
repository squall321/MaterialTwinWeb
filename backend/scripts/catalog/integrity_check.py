# 카탈로그 정합성 32항목 + 주의 1항목 일괄 점검 — 0이 아니면 결함이다. 배포 전 반드시 통과시킬 것.
import sqlite3
import sys

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
OPT = "('optical.refractive_index','optical.reflectance','optical.extinction_coefficient','optical.birefringence')"
# 값 자체가 온도인 물성 — 여기에 temperature_C 조건이 붙으면 대표값 선택이 무너진다(문서 19장).
TEMP_VALUED = ("('thermal.melting_point','thermal.glass_transition','thermal.max_service_temp',"
               "'thermal.min_service_temp','thermal.decomposition_temp','thermal.heat_deflection_temp',"
               "'thermal.vicat_softening')")

CHECKS = [
    ("출처 없는 값", "select count(*) from property_value where source_id is null"),
    ("끊어진 출처 참조", """select count(*) from property_value pv left join source s on s.id=pv.source_id
        where pv.source_id is not null and s.id is null"""),
    ("정의 없는 물성키", """select count(*) from property_value pv
        left join property_definition pd on pd.key=pv.property_key where pd.key is null"""),
    ("고아 시편", "select count(*) from specimen sp left join material m on m.id=sp.material_id where m.id is null"),
    ("값·텍스트 모두 없음", "select count(*) from property_value where value_num is null and coalesce(value_text,'')=''"),
    # 곱 순서만 다른 표기(m^2*K/W vs K*m^2/W)는 같은 단위다 — 문자·숫자만 뽑아 정렬해 비교한다.
    ("단위가 정의와 다름", """select count(*) from property_value pv join property_definition pd on pd.key=pv.property_key
        where pv.value_num is not null and pd.si_unit is not null
        and replace(replace(replace(coalesce(pv.unit,''),'(',''),')',''),' ','')
         <> replace(replace(replace(pd.si_unit,'(',''),')',''),' ','')"""),
    ("tier 범위 밖", "select count(*) from property_value where quality_tier not between 1 and 5"),
    ("method 어휘 밖", "select count(*) from property_value where method not in ('measured','handbook','computed','estimated')"),
    ("출처 kind 어휘 밖", """select count(*) from source where kind not in
        ('journal','book','database','datasheet','computed','standard','web','other')"""),
    ("category 어휘 밖", """select count(*) from material where category not in
        ('metal','polymer','rubber','composite','ceramic','foam')"""),
    ("물성값 0인 재료", "select count(*) from material m where not exists(select 1 from property_value where material_id=m.id)"),
    ("추정만 있는 재료", """select count(*) from (select m.id from material m join property_value pv on pv.material_id=m.id
        group by m.id having min(pv.quality_tier)>=4)"""),
    ("제목 없는 출처", "select count(*) from source where coalesce(title,'')=''"),
    ("journal인데 DOI 없음", "select count(*) from source where kind='journal' and coalesce(doi,'')=''"),
    ("조건이 dict 아님", "select count(*) from property_value where conditions is not null and conditions not like '{%'"),
    ("초탄성인데 model 조건 없음", """select count(*) from property_value where property_key like 'mechanical.hyperelastic%'
        and (conditions is null or conditions not like '%model%')"""),
    ("파장 없는 광학값(tier<4)", f"""select count(*) from property_value where property_key in {OPT}
        and quality_tier<4 and (conditions is null or (conditions not like '%wavelength%' and conditions not like '%line%'))"""),
    ("온도가 값인데 온도 조건", f"select count(*) from property_value where property_key in {TEMP_VALUED} and conditions like '%temperature_C%'"),
    # 장기계수(E∞)는 **Prony 항이 아니라 평형값**이라 항번호가 없는 것이 맞다.
    # 급수는 E(t) = E∞ + Σ Ei·exp(-t/τi) 이고 E∞는 급수 밖에 있다.
    # 9차 파동이 장기계수 36건을 넣자 이 검사가 전부 오탐했다.
    ("Prony 항에 항번호 없음", """select count(*) from property_value where property_key like 'mechanical.prony_%'
        and property_key <> 'mechanical.prony_long_term_modulus'
        and (conditions is null or conditions not like '%term%')"""),
    # 계수·지수는 쌍이 맞아야 곡선이 성립한다. 하나만 있으면 수명 계산이 안 된다.
    #
    # 다만 **의도한 반쪽**이 있다. 원문이 sigma_f'를 sigma_f'/E(무차원)로만 인쇄하면 E를 곱하는
    # 순간 역산이라, 지수만 넣는 것이 옳다(VACOFLUX 50이 그랬다). 그런 행은
    # conditions.pair_incomplete 에 사유를 적어 두고 검사에서 뺀다 — 사유 없는 반쪽만 잡는다.
    ("Basquin 계수·지수 쌍 불일치", """select count(*) from (
        select material_id from property_value
        where property_key in ('mechanical.fatigue_strength_coefficient','mechanical.fatigue_strength_exponent')
        and instr(coalesce(conditions,''),'pair_incomplete')=0
        group by material_id
        having count(distinct property_key)=1)"""),
    ("Coffin-Manson 계수·지수 쌍 불일치", """select count(*) from (
        select material_id from property_value
        where property_key in ('mechanical.fatigue_ductility_coefficient','mechanical.fatigue_ductility_exponent')
        group by material_id
        having count(distinct property_key)=1)"""),
    # Mooney-Rivlin 2항의 초기 전단탄성률 G0 = 2(C10+C01)이 음수면 Drucker 안정조건 위반이라
    # 해석이 발산한다. 수집 중 실제로 2건이 들어왔다(변형률 0~10.4·0~16.4 전구간 피팅).
    ("Mooney-Rivlin G0 음수(Drucker 불안정)", """select count(*) from (
        select pv.material_id, json_extract(pv.conditions,'$.fit_strain_range') r,
               sum(pv.value_num) s, count(*) n
        from property_value pv
        where pv.property_key='mechanical.hyperelastic_coefficient'
          and pv.conditions like '%mooney_rivlin_2%'
          and json_extract(pv.conditions,'$.term') in ('C10','C01')
        group by pv.material_id, r having n=2 and s<=0)"""),
    # Stromeyer는 (계수, 지수, 점근응력) **셋이 한 세트**다. 하나만 있으면 곡선이 안 선다.
    ("Stromeyer 3종 세트 불완전", """select count(*) from (
        select material_id from property_value
        where property_key in ('mechanical.fatigue_stromeyer_coefficient',
                               'mechanical.fatigue_stromeyer_exponent',
                               'mechanical.fatigue_stromeyer_asymptote')
        group by material_id
        having count(distinct property_key) <> 3)"""),
    ("Morrow 계수·지수 쌍 불일치", """select count(*) from (
        select material_id from property_value
        where property_key in ('mechanical.morrow_energy_coefficient','mechanical.morrow_energy_exponent')
        group by material_id
        having count(distinct property_key)=1)"""),
    # Darveaux는 두 쌍으로 갈린다 — (K1,K2)는 균열 개시, (K3,K4)는 균열 성장 dA/dN이다.
    # 넷을 다 요구하면 성장만 발표한 문헌을 결함으로 잡는다(NREL 소결은이 실제로 그랬다:
    # dA/dN = 0.76·ΔW^0.431 로 K3·K4만 인쇄). 쌍이 깨진 것만 잡는다 —
    # 지수 없는 계수, 계수 없는 지수는 어느 쪽도 쓸 수 없다.
    ("Darveaux 쌍 깨짐(홀수 개)", """select count(*) from (
        select material_id from property_value where property_key='mechanical.darveaux_constant'
        group by material_id having count(*) % 2 <> 0)"""),
    # 항번호 없는 상수는 세트로 복원되지 않는다 — Prony와 같은 규율.
    ("항번호 없는 다항 상수", """select count(*) from property_value
        where property_key in ('mechanical.darveaux_constant','mechanical.anand_constant',
                               'mechanical.johnson_cook_damage')
        and (conditions is null or conditions not like '%term%')"""),
    # 노화 유지율은 조건 넷이 다 있어야 해석 입력이 된다.
    ("노화 유지율 조건 불완전", """select count(*) from property_value
        where property_key='mechanical.property_retention'
        and (conditions is null or conditions not like '%aging_hours%'
             or conditions not like '%temperature%' or conditions not like '%property%')"""),
    # 확산계수는 온도에 지수적으로 의존한다. 85 C와 상온이 10배 넘게 다르다.
    # 조건에 '미상'이라고 밝힌 경우는 통과 — 값을 지우기보다 한계를 드러내는 편이 낫다.
    # 온도를 모른다고 **밝힌** 경우는 통과시킨다. 한계를 드러낸 값을 지우는 것보다 낫다.
    # 다만 '미상' 한 단어만 보면 같은 뜻의 다른 표기('미기재', 'not stated')가 걸린다 —
    # 검사는 선언의 존재를 봐야지 특정 어휘를 봐선 안 된다.
    ("확산계수에 온도 조건 없음", """select count(*) from property_value
        where property_key='physical.diffusion_coefficient'
        and (conditions is null or conditions not like '%temperature%')
        and coalesce(conditions,'') not like '%미상%'
        and coalesce(conditions,'') not like '%미기재%'
        and coalesce(conditions,'') not like '%미표기%'
        and lower(coalesce(conditions,'')) not like '%not stated%'
        and lower(coalesce(conditions,'')) not like '%unknown%'"""),
    # 가정값은 반드시 tier4·estimated여야 한다. 그래야 대표값 선택에서 실측에 밀리고,
    # 나중에 실측이 들어오면 자동으로 대체된다(fill_assumed_poisson.py 참조).
    # 표지는 **구조화된 키** `"assumption": true`다. 부분문자열 'assumption'을 찾으면
    # 방법 서술 안의 낱말에 걸린다 — `direction: "bulk effective (isotropic assumption)"`는
    # 초음파 실측의 등방 근사 서술이지 값이 가정이라는 뜻이 아니다(SmCo 3건이 실제로 걸렸다).
    # 근거 문구를 복원하고 conditions가 풍부해지자 이 오탐이 나타났다 —
    # **검사는 산문이 아니라 구조를 봐야 한다.**
    # method='estimated'는 **우리가 세운 가정**을 뜻한다. 그 값이 tier1~2에 앉으면
    # "추정값은 실측에 밀린다"는 규약이 무력화된다 — 실측이 들어와도 대표값이 안 바뀐다.
    # 10차 점검에서 8건이 발견됐고 전부 라벨 오류였다(논문이 동정한 모델 상수였다).
    # tier3은 허용한다 — 계열 대체값·경계값이 여기 앉고, 이미 tier1·2에 밀린다.
    ("estimated인데 tier1·2", "select count(*) from property_value "
                              "where method='estimated' and quality_tier<3"),
    ("가정값인데 tier4·estimated 아님", """select count(*) from property_value
        where (instr(replace(coalesce(conditions,''),' ',''),'"assumption":true')>0
               or instr(replace(coalesce(conditions,''),' ',''),'"assumption":True')>0)
        and (quality_tier<>4 or method<>'estimated')"""),
    ("가정값인데 근거 출처 없음", """select count(*) from property_value
        where (instr(replace(coalesce(conditions,''),' ',''),'"assumption":true')>0
               or instr(replace(coalesce(conditions,''),' ',''),'"assumption":True')>0)
        and source_id is null"""),
    # 비금속 고체의 비열은 대개 400~2500 J/(kg*K)다. 그보다 낮으면 금속(Ag 235, Pb 130)의
    # 값이 잘못 옮겨왔을 가능성이 크다 — 실제로 EMC 236 J/(kg*K)가 이 방식으로 걸렸다.
    ("비금속인데 비열이 금속급으로 낮음", """select count(*) from property_value pv
        join material m on m.id=pv.material_id
        where pv.property_key='thermal.specific_heat' and pv.value_num < 380
        and m.category in ('polymer','rubber','foam','composite')
        -- 값의 근거가 금속임을 조건에 밝힌 경우(예: AgNW의 'bulk silver')는 정상이다
        and coalesce(pv.conditions,'') not like '%silver%'
        and coalesce(pv.conditions,'') not like '%metal%'"""),
    ("파장 조건이 가시광 밖(오타 의심)", f"""select count(*) from property_value where property_key in {OPT}
        and conditions like '%wavelength_nm%' and (
            cast(replace(substr(conditions, instr(conditions,'wavelength_nm')+15), '}}', '') as real) <= 0)"""),
]

def k_missing_direction() -> int:
    """열적 이방성이 입증됐는데 열전도율에 방향이 없는 값의 수.

    같은 재료의 CTE가 두 방향 이상으로 갈려 있으면 그 재료는 열적으로 이방성이다.
    그런데 열전도율만 스칼라 하나면 **서식 문제가 아니라 실제 공백이다** — CCL 배치가
    "같은 표가 CTE는 방향을 갈라 놓고 열전도율은 안 갈랐다"고 짚은 그대로다.
    FR-4는 면내가 두께방향의 약 3배라(0.81~1.06 vs 0.29~0.34) 등방으로 쓰면 크게 틀린다.

    금속은 제외한다. 압연재는 인장에 방향이 있어도 열전도는 등방이다 —
    처음엔 "어떤 물성이든 방향이 붙은 재료"로 셌더니 텅스텐·SUS304까지 걸렸다.
    """
    import json as _json
    con = sqlite3.connect(DB)

    def _dir(cond):
        if not cond:
            return None
        try:
            d = _json.loads(cond)
        except Exception:
            return None
        x = d.get("direction") or d.get("orientation")
        if not x or "not stated" in str(x).lower() or "unspecified" in str(x).lower():
            return None
        return str(x)

    aniso: dict = {}
    for mid, cond in con.execute(
            "select p.material_id,p.conditions from property_value p "
            "join material m on m.id=p.material_id "
            "where p.property_key='thermal.expansion_linear' "
            "and m.category in ('composite','polymer','ceramic')"):
        d = _dir(cond)
        if d:
            aniso.setdefault(mid, set()).add(d)
    proven = {m for m, s in aniso.items() if len(s) >= 2}
    n = 0
    for mid, cond in con.execute(
            "select material_id,conditions from property_value "
            "where property_key='thermal.conductivity'"):
        if mid in proven and not _dir(cond):
            n += 1
    return n


def bad_lcsr_curves() -> int:
    """LCSR 곡선의 가로축이 단조증가하지 않는 재료 수.

    SQL로는 못 잡는다 — 계열을 어떻게 묶느냐가 곡선을 정하기 때문에, 실제 생성기를 돌려
    결과를 봐야 한다. 온도 표기(C/K)가 섞이거나 방향·열처리를 안 보면 가로축이 중복되고
    배율이 거꾸로 가는 *DEFINE_CURVE가 나간다(문서 59장, Kapton HN에서 실제로 발생).
    """
    import os
    os.environ.setdefault("MATERIALTWIN_DATABASE_URL", f"sqlite:///{DB}")
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
    from app.db import SessionLocal
    from app.dyna_export import K_SIGY_RATE, rate_scale_points
    from app.models import PropertyValue
    n = 0
    with SessionLocal() as s:
        ids = {m for (m,) in s.query(PropertyValue.material_id)
               .filter(PropertyValue.property_key == K_SIGY_RATE).distinct()}
        for mid in ids:
            xs = [r for r, _ in rate_scale_points(s, mid)[0]]
            if xs and any(b <= a for a, b in zip(xs, xs[1:])):
                n += 1
    return n


c = sqlite3.connect(DB)
bad = 0
for label, sql in CHECKS:
    v = c.execute(sql).fetchone()[0]
    if v:
        bad += 1
    print(f"  {label:28s} {v}{'  ←' if v else ''}")
_v = bad_lcsr_curves()
bad += 1 if _v else 0
print(f"  {'LCSR 가로축 비단조':28s} {_v}{'  ←' if _v else ''}")

# 주의 항목 — 결함은 아니지만 쓰는 사람이 알아야 하는 것. bad에 세지 않는다.
# 방향을 지어내서 검사를 통과시키는 것도, 아는 위험을 안 알리는 것도 안 된다.
_w = k_missing_direction()
if _w:
    print(f"\n  [주의] 열적 이방성이 입증된 재료인데 열전도율에 방향이 없는 값: {_w}건")
    print("         CTE가 두 방향 이상으로 갈린 재료다. FR-4는 면내가 두께방향의 약 3배라")
    print("         (0.81~1.06 vs 0.29~0.34 W/mK) 등방으로 쓰면 크게 틀린다.")
    print("         원문에 방향이 없으면 지어내지 말고, 해석에서 이 값을 등방으로 쓰지 말 것.")
q = lambda s: c.execute(s).fetchone()[0]
print(f"\n재료 {q('select count(*) from material')} · 물성값 {q('select count(*) from property_value')}"
      f" · 출처 {q('select count(*) from source')}"
      f" · 정의 {q('select count(*) from property_definition')}/{q('select count(distinct property_key) from property_value')}")
print(f"이상 {bad}개")
sys.exit(1 if bad else 0)
