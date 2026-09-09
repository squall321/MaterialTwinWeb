# 69차 EC — Jung 2019 Fig.9 디지타이즈 결과를 KGK-200A50 저장·손실탄성률 행으로 낸다
import json, math, statistics as st

f9 = json.load(open('ec_jung2019_fig9.json'))
f10 = json.load(open('ec_jung2019_mastercurve.json'))

MAT = 'KGK-200A50 acrylic PSA transfer tape, 50 um (Kyodo Giken Chemical)'
SRC = dict(kind='journal',
           title='Determination of viscoelastic properties of thin pressure sensitive adhesive using dynamic mechanical analysis',
           doi='10.1007/s11043-019-09412-5', url='https://doi.org/10.1007/s11043-019-09412-5', year=2019,
           local_path='/data/paper_patent_corpus/structured/mech_papers/10_adhesion_mechanics/Jung - 2019 - Determination of viscoelastic properties of thin pressure sensitive adhesive using dynamic mechanical analysis/Jung - 2019 - Determination of viscoelastic properties of thin pressure sensitive adhesive using dynamic mechanical analysis.md')

NOMINAL = [0.1, 0.3, 0.5, 0.7, 1.0, 3.0, 5.0]

BASE = dict(
    mode='shear (double-shear, 시편 20 x 20 mm x 50 um, 전단변형 진폭 100 %)',
    instrument='자체 제작 double-shear tester — 정전용량 변위센서(레인지 2.5 mm / 분해능 14 nm) · 로드셀 294.3 N · 보이스코일 액추에이터 · 두랄루민 지그 · 냉매(물:에틸렌글리콜 1:1) 냉각',
    test_standard='원문 미기재 — ASTM D5992-96 의 정사각 double-shear 시편 형상만 따랐다고 적는다(2.3절 verbatim `The length-to-width ratio of the specimen is 1:1, which is the same as the ratio of square type double-shear specimen given in ASTM D5992-96`)',
    quantity_source='30번째 사이클의 이력루프 면적에서 위상차를 구해 산출한 값(원문 3.2절, 식 (7))',
    read_uncertainty_pct=0.25,
    read_uncertainty_basis=('같은 48점이 Fig. 9(원시 f·T)와 Fig. 10(이동 f′ 마스터커브) 두 그림에 각각 그려져 있다. '
                            '두 그림을 독립으로 디지타이즈해 모듈러스 값을 정렬 비교하면 상대차 중앙값 0.09 % · 최대 0.24 % 다.'))

def rows(panel9, panel10, key, sym):
    ser = f9[panel9]['series']
    out = []
    for s in ser:
        for fq, mo in s['points']:
            nom = min(NOMINAL, key=lambda v: abs(math.log10(v)-math.log10(fq)))
            c = dict(BASE)
            c.update(frequency_hz=nom,
                     frequency_hz_digitized=round(fq, 4),
                     frequency_snap_error_pct=round(abs(fq-nom)/nom*100, 3),
                     temperature_k=round(s['temperature_c']+273.15, 2),
                     temperature_c=s['temperature_c'],
                     digitized_from=panel9,
                     digitized_series_marker=f"{s['marker']} · stroke rgb({s['color']})",
                     digitized_series_legend_verbatim=f"{s['temperature_c']}℃",
                     digitized_points_in_series=s['n'],
                     axis_type='x 로그(0.1~10 Hz, 십년눈금 3개) · y 로그(10~1000 kPa, 십년눈금 3개)',
                     x_ticks='10^-1 / 10^0 / 10^1 Hz', y_ticks='10 / 100 / 1000 kPa',
                     printed_value_kPa=round(mo, 2))
            notes = (
                f"**그림에서 읽은 값이지 인쇄된 값이 아니다.** {panel9} 의 계열 범례 verbatim `{s['temperature_c']}℃` "
                f"(마커 {s['marker']}). 계열 동정은 색이 아니라 **드로잉 순서**로 했다 — PDF 가 벡터라 계열마다 "
                f"연결 폴리라인 → 그 계열 마커 윤곽 순으로 그려지고 범례도 같은 순서다(색은 보조 확인으로만 썼다). "
                f"데이터점은 마커 중심이 아니라 **연결 폴리라인의 꼭짓점**에서 읽었다 — 마커 중심과 최대 "
                f"{f9[panel9]['marker_vs_polyline_max_pt']:.2f} pt(마커 반폭 이내) 안에서 일치한다. "
                f"**양축이 로그다.** 십년눈금 3개를 최소제곱으로 맞춰 좌표계를 세웠고 "
                f"**검산 잔차는 x {f9[panel9]['x_resid_decades']:.6f} decade · y {f9[panel9]['y_resid_decades']:.6f} decade** 다. "
                f"주파수는 읽은 값 {fq:.4f} Hz 를 원문 시험주파수 {nom} Hz 로 동정했다(차 {abs(fq-nom)/nom*100:.3f} %). "
                f"**독립 검산 — 같은 48점이 Fig. 10 마스터커브에도 그려져 있어 두 그림을 따로 디지타이즈했고, "
                f"모듈러스 값의 상대차가 중앙값 0.09 % · 최대 0.24 % 였다.** "
                f"원값 {mo:.2f} kPa → {mo*1000:.1f} Pa. 기호 {sym}.")
            out.append(dict(key=key, value=round(mo*1000, 1), unit='Pa', method='digitized', tier=1,
                            conditions=c, notes=notes))
    return out

props  = rows('Fig. 9(a) storage modulus G′', 'Fig. 10(a) storage modulus G′', 'mechanical.storage_modulus', "G'")
props += rows('Fig. 9(b) loss modulus G″',   'Fig. 10(b) loss modulus G″',   'mechanical.loss_modulus', 'G"')

WLF_NOTE = (
 "원문 4.2절이 인쇄한 값이다(디지타이즈 아님) — `Constants of the WLF model, C1 and C2 were found to be "
 "C1 = 10.84 and C2 = 58.17, respectively` · `The R-square value of the WLF regression equation was 0.99996`. "
 "**로그 밑과 부호 규약은 원문 식 (9) verbatim 이다 — `ln(aT) = − C1(T−T0)/(C2+(T−T0))`. 상용로그가 아니라 자연로그다.** "
 "원문 자신은 바로 다음 문단에서 `the product of C1 and C2 is generally of the order of 400 to 900 for an amorphous "
 "polymer (Ferry 1980)` 라며 곱 631 을 근거로 쓰는데, Ferry 의 그 범위는 **상용로그 규약**의 것이라 원문 안에 규약 "
 "불일치가 있다. **우리는 고르지 않고 수치로 가렸다** — Fig. 9 의 원시 주파수와 Fig. 10 의 이동 주파수를 모듈러스 "
 "값으로 짝지어 이동인자 a_T 를 되뽑았고(계열마다 7점이 같은 비를 주며 산포 0.001~0.002 decade), "
 "그 log10(a_T) = 0 / 0.397 / 0.777 / 1.601 / 1.874 / 2.300 / 2.601 을 두 규약의 예측과 비교하면 "
 "**자연로그 규약의 잔차노름이 0.41, 상용로그 규약이 5.91 로 자연로그가 14배 낫다.** 식 (9) 대로 읽는 것이 맞다. "
 "다만 되뽑은 a_T 는 3.8 °C 에서 WLF 예측(1.302)보다 0.30 decade 높아(1.601) 원문이 주장하는 R²=0.99996 과는 맞지 않는다 — "
 "우리는 원문 값을 그대로 옮기고 이 어긋남을 기록만 한다.")
WLF_COND = dict(reference_temperature_k=289.55, reference_temperature_c=16.4,
                equation_verbatim='ln(aT) = − C1(T−T0)/(C2+(T−T0))   [원문 식 (9)]',
                log_base='ln (자연로그) — 원문 식 (9) 가 그렇게 쓴다',
                sign_convention='T > T0 에서 aT < 1 (원문 식 (9) 의 음부호)',
                convention_verified_by=('우리가 Fig. 9 · Fig. 10 에서 되뽑은 이동인자와 대조해 자연로그 규약을 확인했다 '
                                        '(잔차노름 ln 0.41 vs log10 5.91)'),
                fit_r2=0.99996,
                valid_temperature_range_c=[-5.5, 16.4],
                model='WLF (Williams-Landel-Ferry)')
props.append(dict(key='mechanical.wlf_c1', value=10.84, unit='1', method='computed', tier=1,
                  conditions=dict(WLF_COND), notes=WLF_NOTE))
props.append(dict(key='mechanical.wlf_c2', value=58.17, unit='K', method='computed', tier=1,
                  conditions=dict(WLF_COND, unit_note='원문은 단위를 안 적지만 식 (9) 의 C2+(T−T0) 가 온도차와 더해지므로 K(=°C 차) 다'),
                  notes=WLF_NOTE))

json.dump(dict(batch='69차 EC', materials=[dict(match_name=MAT, source=SRC, properties=props)]),
          open('ec02_kgk200a50_dma.json','w'), ensure_ascii=False, indent=2)
import collections
print("행", len(props), collections.Counter(p['key'] for p in props))
