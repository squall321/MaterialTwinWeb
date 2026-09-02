# 62차 XA — 위 후보를 자기참조/앵커로 자동 분류해 오탐률을 잰다
# 후보를 자기참조/앵커/딴재료로 자동 분류해 오탐률을 잰다
import json,re,sys
d=json.load(open(sys.argv[1]))
SELF=re.compile(r'tier\s*4|tier4|카탈로그|catalog|stored|이미 .{0,20}갖고|등록해|앵커|anchor|추정값',re.I)
def nums(s):
    return [float(x.replace(',','')) for x in re.findall(r'\d+(?:\.\d+)?',s.replace(' ',''))]
cnt={'self_ref':0,'value_equals_t4':0,'other':0}
rest=[]
for x in d:
    t4=x['t4'][0] if x['t4'] else None
    tag=None
    for h in x['hits']:
        s=h['sent']
        # t4 값과 같은 숫자가 문장에 있나 (단위 스케일 무시하고 유효숫자 비교)
        eq=False
        if t4:
            for n in nums(s):
                for sc in (1,1e-3,1e3,1e-6,1e6,1e-9,1e9,1e-2,1e2,1e-1,1e1):
                    if n and abs(n*sc-t4)<=abs(t4)*0.012: eq=True
        if eq: tag='value_equals_t4'; break
        if SELF.search(s): tag=tag or 'self_ref'
    if tag: cnt[tag]+=1
    else: cnt['other']+=1; rest.append(x)
print(cnt, 'total', len(d))
json.dump(rest,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
