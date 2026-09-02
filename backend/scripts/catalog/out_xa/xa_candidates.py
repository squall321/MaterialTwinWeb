# 62차 XA — t4 단독 대표 칸 중 같은 재료의 다른 행 notes 가 그 물성의 낱말+숫자+단위를 담은 후보를 뽑는다(경로는 인자로 준다)
# 후보를 좁힌다 — 낱말과 '숫자+단위 붙은 토큰'이 같은 문장에 있을 때만
import sqlite3, re, json, sys
from collections import defaultdict
DB='/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
NUMU = {
 'physical.density': r'\d[\d.,]*\s*(?:g\s*/\s*cm3?|g/cc|kg\s*/\s*m3|Mg/m3|g\s*cm-?3)',
 'mechanical.youngs_modulus': r'\d[\d.,]*\s*(?:GPa|MPa|ksi|psi|N/mm2|kgf/mm2)',
 'mechanical.poisson_ratio': r'0\.[0-9]{2,3}',
 'mechanical.tensile_strength': r'\d[\d.,]*\s*(?:MPa|GPa|ksi|psi|N/mm2|kgf/mm2)',
 'thermal.conductivity': r'\d[\d.,]*\s*(?:W\s*/\s*\(?\s*m|W/mK|W\s*m-?1)',
 'thermal.specific_heat': r'\d[\d.,]*\s*(?:J\s*/\s*\(?\s*kg|J/gK|J\s*kg-?1|J\s*/\s*g)',
 'thermal.expansion_linear': r'\d[\d.,]*\s*(?:ppm|[eE]-0?6|x?\s*10-?6|µm/m|um/m)',
 'mechanical.elongation_at_break': r'\d[\d.,]*\s*%',
 'mechanical.yield_strength': r'\d[\d.,]*\s*(?:MPa|GPa|ksi|psi|N/mm2)',
 'electrical.dielectric_constant': r'\d\.\d+',
 'optical.emissivity_total': r'0\.\d+',
 'optical.refractive_index': r'1\.\d{2,}',
 'physical.contact_angle_water': r'\d[\d.]*\s*(?:°|deg)',
 'physical.surface_energy': r'\d[\d.]*\s*(?:mN/m|mJ/m2|dyn)',
 'chemical.water_absorption_24h': r'\d[\d.]*\s*%',
 'chemical.water_absorption_saturation': r'\d[\d.]*\s*%',
 'mechanical.flexural_strength': r'\d[\d.,]*\s*(?:MPa|ksi|psi)',
 'mechanical.flexural_modulus': r'\d[\d.,]*\s*(?:GPa|MPa|ksi|psi)',
 'thermal.melting_point': r'\d[\d.,]*\s*(?:°\s*C|K\b)',
 'thermal.glass_transition': r'\d[\d.,]*\s*(?:°\s*C|K\b)',
}
W = {
 'physical.density': r"\bdensit|비중|밀도|密度|specific gravity",
 'mechanical.youngs_modulus': r"young'?s? modulus|elastic modulus|tensile modulus|모듈러스|탄성률|탄성계수|modulus of elasticity",
 'mechanical.poisson_ratio': r"poisson'?s? ratio|포아송",
 'mechanical.tensile_strength': r'tensile strength|인장강도|\bUTS\b|ultimate tensile',
 'thermal.conductivity': r'thermal conductivit|heat conductivit|열전도|熱伝導',
 'thermal.specific_heat': r'specific heat|heat capacit|비열|比熱|\bCp\b',
 'thermal.expansion_linear': r'thermal expansion|\bCTE\b|열팽창|線膨張|coefficient of (linear|thermal)',
 'mechanical.elongation_at_break': r'elongation|연신|伸び|strain at break',
 'mechanical.yield_strength': r'yield strength|yield stress|항복강도|降伏',
 'electrical.dielectric_constant': r'dielectric constant|permittivity|\bDk\b|유전율|誘電率',
 'optical.emissivity_total': r'emissivit|방사율',
 'optical.refractive_index': r'refractive index|굴절률',
 'physical.contact_angle_water': r'contact angle|접촉각',
 'physical.surface_energy': r'surface energy|surface tension|표면에너지|표면장력',
 'chemical.water_absorption_24h': r'water absorption|흡수율|吸水',
 'chemical.water_absorption_saturation': r'water absorption|흡수율|吸水',
 'mechanical.flexural_strength': r'flexural strength|bending strength|굽힘강도',
 'mechanical.flexural_modulus': r'flexural modulus|굽힘탄성',
 'thermal.melting_point': r'melting (point|temperature)|융점|용융점',
 'thermal.glass_transition': r'glass transition|\bTg\b',
}
c=sqlite3.connect('file:%s?mode=ro'%DB,uri=True)
cells=defaultdict(list); rows=defaultdict(list)
for pid,mid,k,t,notes,sid,vn,un in c.execute('select id,material_id,property_key,quality_tier,notes,source_id,value_num,unit from property_value'):
    cells[(mid,k)].append(t); rows[mid].append((pid,k,notes or '',t,sid,vn,un))
sole=sorted([(m,k) for (m,k),ts in cells.items() if all(t==4 for t in ts)])
names=dict(c.execute('select id,name from material'))
t4val={}
for (mid,k) in sole:
    for pid,k2,n,t,sid,vn,un in rows[mid]:
        if k2==k: t4val[(mid,k)]=(vn,un); break
def sents(t): return [s for s in re.split(r'(?<=[.;])\s+|\n|(?<=\S)\s\|\s', t) if s.strip()]
out=[]
for mid,key in sole:
    if key not in W: continue
    wre=re.compile(W[key],re.I); nre=re.compile(NUMU[key],re.I)
    hits=[]
    for pid,k2,notes,t2,sid,vn,un in rows[mid]:
        if k2==key or not notes: continue
        for s in sents(notes):
            if wre.search(s) and nre.search(s):
                hits.append({'pv':pid,'from_key':k2,'src':sid,'sent':s.strip()[:500]}); break
    if hits:
        out.append({'mid':mid,'name':names.get(mid),'key':key,'t4':t4val.get((mid,key)),'hits':hits[:3]})
print('candidates:',len(out))
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
