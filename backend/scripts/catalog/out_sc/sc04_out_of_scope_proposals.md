<!-- 57차 SC — role='out_of_scope' 제안 목록. 값을 격자 밖으로 미는 변경이라 직접 바꾸지 않았다 -->
# `role='out_of_scope'` 제안 — 17종

§193 이 정한 셋째 부류다 — **실재 상용 제품인데 스마트폰 해석 대상이 아닌 것.**
값은 남고 격자에서만 빠진다. **직접 바꾸지 않았다.** 셋 다 이미 `verdict_subsystem: not_applicable`
이 붙어 있어 배치가 스스로 "계통이 있을 수 없다" 고 적어 둔 것들이다.

| # | 재료 | 코어 빈칸 | out_of_scope 인 근거 |
|---:|---|---:|---|
| 2381 | Uddeholm Stavax ESR | 1 | 아래 13종 공통 |
| 2390 | Uddeholm Corrax | 2 | |
| 2391 | Uddeholm Corrax for AM | 2 | |
| 2392 | Uddeholm Tyrax ESR | 1 | |
| 2393 | Uddeholm Impax Supreme | 1 | |
| 2394 | Uddeholm Orvar Supreme | 2 | |
| 2395 | Uddeholm Mirrax ESR | 1 | |
| 2396 | Uddeholm Mirrax 40 | 1 | |
| 2419 | Uddeholm Dievar | 2 | |
| 2420 | Uddeholm Vidar Superior | 2 | |
| 2421 | Uddeholm Unimax | 1 | |
| 2422 | Uddeholm Elmax SuperClean | 2 | |
| 2423 | Uddeholm Ramax HH | 1 | |

**Uddeholm 금형·공구강 13종 — 부품이 아니라 그 부품을 만드는 금형이다.** 45차 GD 가 그렇게
판정했고 49차 KA 가 `not_applicable` 로 굳혔다. 사출금형강(Stavax·Tyrax·Impax·Mirrax·Corrax·
Ramax)과 열간공구강(Orvar·Dievar·Vidar·Unimax)·PM 공구강(Elmax)이다. **스마트폰 하우징을 사출하는
금형의 강이지 스마트폰에 들어가는 강이 아니다.** 격자가 재는 것은 "스마트폰 해석 준비도" 이므로
`housing` 이 아니라 격자 밖이 옳다. 값(밀도·E·CTE·열전도율·경도·충격에너지 약 300행)은
금형 해석에 정당하므로 삭제 대상이 전혀 아니다.

| # | 재료 | 코어 빈칸 | 근거 |
|---:|---|---:|---|
| 387 | EPE EPE29 발포PE (29 kg/m³) | 0 | |
| 388 | EPE EPE36 발포PE (36 kg/m³) | 0 | |
| 389 | EPE EPE58 발포PE (58 kg/m³) | 0 | |

**포장 완충재 3종.** 제품에 남는 부재가 아니라 **출하 상자의 완충폼**이다.
`attributes` 에 *"카탈로그의 `packaging` 은 반도체 패키지를 뜻하므로 붙이면 안 된다"* 가
이미 박혀 있다(49차 KA). **다만 판단이 갈릴 수 있다 — 아래 어휘 제안 참조.**

| # | 재료 | 코어 빈칸 | 근거 |
|---:|---|---:|---|
| 364 | Intertape AC778 (0.056 mm 금속증착 BOPP 스플라이싱 테이프) | 0 | 웹 가공 라인에서 롤과 롤을 잇는 **제조 공정 소모재**다. 완제품에 남지 않는다 |

---

## 새 계통 어휘 제안 — 하지 않는다

**EPE 발포폼 3종을 위해 `shipping`(출하 포장) 같은 어휘를 새로 열 것을 검토했고, 열지 않기로 했다.**
- 낙하시험 해석에서 **상자째 떨어뜨리는** 모형은 실재하므로 완충폼은 정당한 해석 입력이다.
- 그러나 계통 어휘 하나를 늘리면 화면 패싯·집계(`subsystem_core`)·검사기를 **동시에** 고쳐야 하고
  (§466), 그 값을 채울 재료가 **3종뿐**이다. 어휘 하나에 재료 셋은 패싯을 무겁게만 한다.
- `out_of_scope` 로 빼도 값은 그대로 남는다(§193). 낙하상자 해석이 실제 표적이 되는 날
  그때 어휘를 열면 된다.

**따라서 이 파동의 어휘 제안은 없다.** 현행 어휘는 **17개가 아니라 16개**다(`pcb · packaging · display · housing · thermal ·
magnetics · camera · battery · rf · acoustics · semiconductor · wlp · passive · coating · sensor ·
emi`) — 지시서의 `17개` 는 화면의 `기타` 칸까지 센 수다. 이 16개로 충분했다 — 85종 중 **어휘가 없어서 못 붙인 것은 0종**이고, 못 붙인 이유는 전부 *근거가 없다* 였다.
