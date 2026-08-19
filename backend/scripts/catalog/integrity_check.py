# 카탈로그 정합성 37항목 + 주의 1항목 일괄 점검 — 0이 아니면 결함이다. 배포 전 반드시 통과시킬 것.
import sqlite3
import sys

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
OPT = "('optical.refractive_index','optical.reflectance','optical.extinction_coefficient','optical.birefringence')"
# 값 자체가 온도인 물성 — 여기에 temperature_C 조건이 붙으면 대표값 선택이 무너진다(문서 19장).
TEMP_VALUED = ("('thermal.melting_point','thermal.glass_transition','thermal.max_service_temp',"
               "'thermal.min_service_temp','thermal.decomposition_temp','thermal.heat_deflection_temp',"
               # 43차 EE 신규. 새그온도 Ts 도 **값 자체가 온도**다(브리프 199·266, 세 번째 재발).
               "'thermal.vicat_softening','thermal.dilatometric_softening_point')")

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
    # `digitized` = 그림에서 읽은 값(40차 BF). `datasheet` 는 로더가 measured 로 정규화하므로 여기 없다.
    ("method 어휘 밖", "select count(*) from property_value where method not in "
                    "('measured','handbook','computed','estimated','digitized')"),
    # **구간의 중앙값은 우리가 만든 계산값이다** — 실측·핸드북으로 표기하면 안 된다(41차 CD 가 짚었다).
    # 인쇄된 것은 구간이고 중앙값은 우리 산술이라, `assumed → estimated` 를 가른 것과 같은 부류다.
    # 실측 당시 143행이 measured/handbook 이었다. 값은 그대로 두고 method 만 computed 로 옮겼다.
    # **본래는 상·하한 두 행으로 갈라야 한다**(브리프 76) — 원문 구간이 있어야 하므로 배치 몫이다.
    ("중앙값인데 실측·핸드북 표기",
     "select count(*) from property_value where (notes like '%중간값%' or notes like '%중앙값%') "
     "and method in ('measured','handbook')"),
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
    # ── 시험장비 ──────────────────────────────────────────────────────────
    # **범위는 단위와 함께가 아니면 값이 아니다.** 적재기가 막지만 직접 INSERT 를 막지는 못한다.
    ("장비 범위에 단위 없음", """select count(*) from instrument_capability
        where (range_min is not null or range_max is not null) and coalesce(range_unit,'')=''"""),
    ("장비 범위 역전", """select count(*) from instrument_capability
        where range_min is not null and range_max is not null and range_min > range_max"""),
    ("장비 온도범위 역전", """select count(*) from instrument_capability
        where temperature_min_k is not null and temperature_max_k is not null
          and temperature_min_k > temperature_max_k"""),
    # 절대영도 아래는 환산 실수다 — °C 를 켈빈 칸에 그대로 넣으면 여기 걸린다.
    ("장비 온도가 절대영도 아래", """select count(*) from instrument_capability
        where (temperature_min_k is not null and temperature_min_k < 0)
           or (temperature_max_k is not null and temperature_max_k < 0)"""),
    ("장비인데 카탈로그 경로 없음", "select count(*) from instrument where coalesce(doc_path,'')=''"),
    # **부분일치로 보면 안 된다.** 17차에 `aging_temperature_c`(노화 조건)와 `cure_temperature_k`가
    # 41건 걸렸다 — 둘 다 시험온도가 아니라 독립 축이고, 노화 격자를 담으려면 반드시 있어야 하는 값이다.
    # 이 검사가 막으려는 것은 **값 자체가 온도인 물성에 시험온도가 붙는 것**이므로 키를 정확히 본다.
    ("온도가 값인데 시험온도 조건", f"""select count(*) from property_value
        where property_key in {TEMP_VALUED}
        and (json_extract(conditions,'$.temperature_C') is not null
             or json_extract(conditions,'$.temperature_c') is not null
             or json_extract(conditions,'$.temperature_K') is not null
             or json_extract(conditions,'$.temperature_k') is not null)"""),
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
        where property_key in ('mechanical.fatigue_strength_coefficient',
                               'mechanical.fatigue_strength_coefficient_normalized',
                               'mechanical.fatigue_strength_exponent')
        and instr(coalesce(conditions,''),'pair_incomplete')=0
        group by material_id
        having sum(property_key='mechanical.fatigue_strength_exponent')=0
            or sum(property_key<>'mechanical.fatigue_strength_exponent')=0)"""),
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
    # **Prony 급수는 가중치와 완화시간의 항수가 같아야 한다.** 짝이 없는 항은 쓸 수 없다.
    # 19차에 Chiu 2018이 17항인데 완화시간만 15항으로 들어와 있었다 —
    # 인제스트 범위검사 하한이 10^-22·10^-25 두 항을 조용히 잘랐고, 이 검사가 없어 못 봤다.
    #
    # **세 가지를 구분해야 오탐이 안 난다.**
    #  · 전단(또는 인장)과 체적은 **각각** 같은 tau 집합과 짝을 이룬다 — 합치면 2배로 보인다.
    #  · 평형항(w_inf / Inf / equilibrium)은 급수 밖이라 tau가 없는 것이 옳다.
    #  · 한 재료가 여러 급수를 가지면 set_id·model·temperature_k 로 갈린다 —
    #    19차에 같은 OCA가 같은 온도에서 generalized Maxwell 과 viscoelastic-viscoplastic
    #    두 모델을 동시에 갖고 있었다. model 을 안 보면 오탐이 난다.
    ("Prony 가중치·완화시간 항수 불일치", """select count(*) from (
        select material_id, json_extract(conditions,'$.set_id') sid,
               coalesce(json_extract(conditions,'$.series'),'-') ser,
               coalesce(json_extract(conditions,'$.model'),'-') mdl,
               coalesce(json_extract(conditions,'$.temperature_k'),'-') tk,
               sum(property_key='mechanical.prony_relaxation_time') n_tau,
               sum(property_key='mechanical.prony_relative_modulus'
                   and lower(coalesce(json_extract(conditions,'$.term'),'')) not like '%inf%'
                   and lower(coalesce(json_extract(conditions,'$.term'),'')) not like '%equil%') n_w
        from property_value
        where property_key in ('mechanical.prony_relaxation_time',
                               'mechanical.prony_relative_modulus')
        group by material_id, sid, ser, mdl, tk
        having n_tau>0 and n_w>0 and n_w<>n_tau)"""),
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
    # 브리프는 "무엇을 근거로 그 값을 골랐는지 notes에 반드시 적어라"를 요구한다.
    # 근거 없는 가정값은 나중에 무엇을 대체해야 하는지 알 수 없어 고도화가 막힌다.
    # 출처 제목이 실제 문서 이름인데 그 문서에서 읽은 값이 아닌 경우가 있었다 —
    # 생성 스크립트가 출처를 '…추정'이라는 익명 문자열로 적었고, 이후 '제목 없는 출처' 정리에서
    # 설명적 제목이 붙으면서 **추정 라벨이 문서 인용으로 바뀌었다**(13차에 18건 발견).
    # datasheet·standard로 분류된 출처는 그 문서를 실제로 가리켜야 한다 —
    # 걸린 값이 전부 tier4 estimated이고 URL·DOI·ISBN이 하나도 없으면 문서가 아니라 라벨이다.
    ("datasheet·standard인데 식별자도 실측도 없음", """select count(*) from source s
        where s.kind in ('datasheet','standard')
          and coalesce(s.url,'')='' and coalesce(s.doi,'')='' and coalesce(s.isbn,'')=''
          and exists(select 1 from property_value where source_id=s.id)
          and not exists(select 1 from property_value where source_id=s.id and quality_tier<=3)"""),
    ("tier4 가정인데 근거 notes 없음", "select count(*) from property_value "
                                 "where quality_tier=4 and method='estimated' and coalesce(notes,'')=''"),
    # **method와 tier의 진짜 불변식은 조합표가 아니라 둘이다.**
    # 문서가 못박아 둔 7개 조합표는 좁았다 — computed t1(벤더가 각주로 "calculated"라 밝힌 값),
    # computed t2(인쇄된 두 수로 우리가 환산한 값을 한 단계 낮춘 것), measured t2(다른 시료의
    # 실측을 계열값으로 쓴 것)는 전부 정당한데 표 밖이라 225건이 결함처럼 보였다.
    # 조합을 세지 말고 **뜻이 어긋나는 것만** 잡는다.
    #
    #   (1) estimated는 "우리가 만든 값"이다 → tier4가 아니면 어느 쪽이든 거짓말이다.
    #       실제로 15건이 tier3에 있었는데 전부 출처에 인쇄된 계열값이었다(method가 틀렸다).
    #   (2) tier4는 "우리가 만든 값"이다 → measured·handbook이면 등급이 틀렸다.
    # **`estimated` 가 곧 tier4 는 아니다.** tier4 는 **우리가** 만든 값이고,
    # **저자가 스스로 외삽해 인쇄한 값**은 인쇄값이라 tier1·2 이면서 방법만 estimated 다
    # (32차 AE 의 Kim 2017 초록 — `estimated to be only 6x10^-6`).
    # 우리 것인지는 `conditions.assumption` 이 가른다(브리프 265번).
    ("우리 추정인데 tier4가 아님", """select count(*) from property_value
        where method='estimated' and quality_tier<>4
          and instr(replace(coalesce(conditions,''),' ',''),'"assumption":true')>0"""),
    # 저자 추정은 정상이지만 **왜 estimated 인지 근거가 없으면** 구분이 안 된다.
    ("저자 추정인데 근거 없음", """select count(*) from property_value
        where method='estimated' and quality_tier<>4
          and instr(replace(coalesce(conditions,''),' ',''),'"assumption":true')=0
          and coalesce(notes,'') not like '%외삽%' and coalesce(notes,'') not like '%estimat%'
          and coalesce(notes,'') not like '%추정%'"""),
    ("tier4인데 실측·핸드북", "select count(*) from property_value "
                        "where quality_tier=4 and method in ('measured','handbook')"),
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

def bad_energy_product() -> list:
    """(BH)max 가 Br^2/(4*mu0) 를 넘는 값의 목록 — **물리 상한 위반은 확정이다**(브리프 431).

    최대자기에너지적은 감자곡선 위 B x H 의 최대값이다. 자화가 완전히 사각형이어도
    2상한의 직사각형 넓이는 (Br/2) x (Br/2/mu0) = Br^2/(4*mu0) 를 못 넘는다.
    실측 격자(Eclipse NdFeB 8등급 x min/typ · 하드페라이트)에서 실제 비는 0.90~0.97 이다.
    1 을 넘으면 단위 오입력이거나 표가 죽은 것이다.

    같은 재료의 Br 을 **여러 개 들고 있을 수 있으므로 최대 Br 로 상한을 잡는다** —
    가장 관대한 상한이라, 그래도 넘으면 확정이다.
    """
    import math
    con = sqlite3.connect(DB)
    mu0 = 4e-7 * math.pi
    br: dict = {}
    for mid, v in con.execute(
            "select material_id, value_num from property_value "
            "where property_key='magnetic.remanence' and value_num is not null"):
        br[mid] = max(br.get(mid, 0.0), float(v))
    out = []
    for mid, v, cond in con.execute(
            "select material_id, value_num, conditions from property_value "
            "where property_key='magnetic.energy_product_max' and value_num is not null"):
        b = br.get(mid)
        if not b:
            continue                      # Br 이 없으면 검산할 수 없다 — 위반이 아니다
        cap = b * b / (4 * mu0)
        # **인쇄 유효자릿수의 반올림 구간으로 판정한다**(브리프 339). Br 이 `400 mT` 로
        # 인쇄되면 실제는 [395,405) 이고 cap 은 Br^2 에 비례해 ±0.3% 흔들린다.
        # 실제로 Eclipse Y30H-1 행이 32.0 대 31.83(=1.005배)으로 걸린다 — 반올림 안이다.
        # 2% 는 반올림 잡음보다 훨씬 크고, 진짜 단위 오입력(x1000 · x7.96)보다 훨씬 작다.
        if float(v) > cap * 1.02:
            name = (con.execute("select name from material where id=?", (mid,)).fetchone()
                    or ["?"])[0]
            out.append((mid, name, float(v), cap, cond))
    return out


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
_bh = bad_energy_product()
bad += 1 if _bh else 0
print(f"  {'(BH)max > Br^2/(4mu0)':28s} {len(_bh)}{'  ←' if _bh else ''}")
for _mid, _nm, _v2, _cap, _ in _bh[:5]:
    print(f"      재료{_mid} {str(_nm)[:44]:46s} {_v2/1e3:.1f} > {_cap/1e3:.1f} kJ/m^3"
          f" (비 {_v2/_cap:.3f})")

# 주의 항목 — 결함은 아니지만 쓰는 사람이 알아야 하는 것. bad에 세지 않는다.
# 방향을 지어내서 검사를 통과시키는 것도, 아는 위험을 안 알리는 것도 안 된다.
_w = k_missing_direction()
if _w:
    print(f"\n  [주의] 열적 이방성이 입증된 재료인데 열전도율에 방향이 없는 값: {_w}건")
    print("         CTE가 두 방향 이상으로 갈린 재료다. FR-4는 면내가 두께방향의 약 3배라")
    print("         (0.81~1.06 vs 0.29~0.34 W/mK) 등방으로 쓰면 크게 틀린다.")
    print("         원문에 방향이 없으면 지어내지 말고, 해석에서 이 값을 등방으로 쓰지 말 것.")

# 같은 출처에 값이 완전히 같은 재료쌍 — **중복 적재일 수도, 정당한 클래스 전이일 수도 있다.**
# 30차 AB 가 이걸로 ZrB2 10종·Cr2O3 1종의 실제 중복을 찾았지만, 같은 질의가
# 등급 다른 대리값(SUS316/316L 같은 것)도 함께 잡는다. **그래서 이상이 아니라 주의다.**
from collections import defaultdict as _dd
_g = _dd(list)
for _sid, _sig, _mid, _n, _t in c.execute(
    """select v.source_id, group_concat(v.property_key||'='||coalesce(v.value_num,'')) sig,
              v.material_id, count(*) n, min(v.quality_tier) t
       from property_value v group by v.material_id, v.source_id having n >= 3"""):
    _g[(_sid, _sig)].append((_mid, _t))
_dup = [(k, v) for k, v in _g.items() if len(v) > 1 and min(t for _, t in v) <= 2]
if _dup:
    print(f"\n  [주의] 같은 출처에 **1차값(tier<=2)이 완전히 같은 재료쌍**: {len(_dup)}건")
    print("         두 배치가 같은 시편을 다른 이름으로 넣었을 수 있다(30차 AB 가 ZrB2 10종을 이렇게 찾았다).")
    print("         다만 한 논문이 조성만 다른 시료에 같은 값을 인쇄한 정당한 경우도 걸린다 —")
    print("         **이름이 같은 시편을 가리키는지 눈으로 확인해라.** 자동 삭제하지 말 것.")
    for (_sid, _), _ms in _dup[:5]:
        _t = (c.execute("select title from source where id=?", (_sid,)).fetchone() or ["?"])[0]
        print(f"           출처 {_sid} · {str(_t)[:56]} · 재료 {[m for m, _ in _ms]}")


# **Tg 위 CTE 가 물리적 상한을 넘는 값** — 고분자 고무상 CTE 는 대개 50~400 ppm/K 다.
# 35차 AL 의 Chung 2007 A계열이 2953 ppm/K(alpha2/alpha1 = 40배)로 들어왔다.
# 인쇄값이라 지우지 않되 **표식 없이 지나가면 안 된다**(TMA 프로브 침강 인공산물일 수 있다).
_cte = c.execute("""select count(*) from property_value
    where property_key='thermal.expansion_linear' and value_num > 1.0e-3
      and instr(coalesce(conditions,''),'magnitude_suspect')=0""").fetchone()[0]
if _cte:
    print(f"\n  [주의] **Tg 위 CTE 가 1000 ppm/K 를 넘는데 표식이 없는 값: {_cte}건**")


# **항복 > 인장은 물리적으로 불가능하다** — 42차 DB 가 PV 백시트에서 19배 역전을 찾았다.
# 다만 **자동 판정은 못 한다.** 조건을 안 맞추면 27종이 걸리는데 대부분 정상이다 —
# Uddeholm 강은 경도 등급별로, 21-6-9 은 4.2 K 대 상온으로 서로 다른 조건의 값이 나란히 있다.
# 온도·경도·방향을 맞추면 그중 상당수가 걸러지고, 조건축 전체를 맞추면 11종이 남는다.
# 남는 것도 **출처가 갈린 경우가 많다**(t4 추정 항복 대 t1 실측 인장) — 사람이 볼 목록이다.
_yt = c.execute("""
    select y.material_id, m.name, y.id, y.value_num, y.quality_tier, t.value_num, t.quality_tier
      from property_value y
      join property_value t on t.material_id = y.material_id
       and ifnull(json_extract(t.conditions,'$.temperature_k'),-1)
         = ifnull(json_extract(y.conditions,'$.temperature_k'),-1)
       and ifnull(json_extract(t.conditions,'$.hardness_hrc'),-1)
         = ifnull(json_extract(y.conditions,'$.hardness_hrc'),-1)
       and ifnull(json_extract(t.conditions,'$.direction'),'')
         = ifnull(json_extract(y.conditions,'$.direction'),'')
      join material m on m.id = y.material_id
     where y.property_key='mechanical.yield_strength'
       and t.property_key='mechanical.tensile_strength'
       and y.value_num > t.value_num*1.02
     group by y.material_id""").fetchall()
if _yt:
    print(f"\n  [주의] **항복강도가 인장강도보다 큰 재료: {len(_yt)}종**")
    print("         조건축(온도·경도·방향)을 맞춘 뒤에도 역전인 것이다.")
    print("         물리적으로 불가능하므로 한쪽이 틀렸다 — 대개 t4 추정 항복이 t1 실측 인장을 넘는다.")
    for _m, _n, _i, _yv, _yq, _tv, _tq in _yt[:6]:
        print(f"           재료{_m} {_n[:38]:40s} 항복 {_yv/1e6:>8.4g}(t{_yq}) > 인장 {_tv/1e6:>8.4g}(t{_tq})")
    if len(_yt) > 6:
        print(f"           … 외 {len(_yt)-6}종")
    print("         고분자 고무상 CTE 는 대개 50~400 ppm/K 다. TMA 팽창모드에서 연화된 시편이")
    print("         프로브 하중에 눌리면 겉보기 CTE 가 크게 나온다 — **인쇄값이어도 해석 입력으로")
    print("         바로 쓰면 안 된다.** conditions 에 `magnitude_suspect` 를 달아라.")

q = lambda s: c.execute(s).fetchone()[0]
print(f"\n재료 {q('select count(*) from material')} · 물성값 {q('select count(*) from property_value')}"
      f" · 출처 {q('select count(*) from source')}"
      f" · 정의 {q('select count(*) from property_definition')}/{q('select count(distinct property_key) from property_value')}")
print(f"이상 {bad}개")
sys.exit(1 if bad else 0)
