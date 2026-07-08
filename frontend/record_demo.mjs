// MaterialTwin 풍성 시연 녹화 — 군별 검색 조회·그래프·진응력·피팅·점탄성 워크스루.
import { createRequire } from "module";
const require = createRequire("/home/koopark/claude/koofinance/frontend/");
const { chromium } = require("playwright");

const BASE = "http://127.0.0.1:17777";
const OUT = "/tmp/mtw_video";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await chromium.launch({
  headless: true,
  executablePath: "/home/koopark/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome",
});
const ctx = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  recordVideo: { dir: OUT, size: { width: 1440, height: 900 } },
  deviceScaleFactor: 1,
});
const page = await ctx.newPage();
let _n = 0;
async function goto(hash) {
  await page.goto(`${BASE}/?n=${++_n}#${hash}`, { waitUntil: "networkidle" });
}
async function scroll(y, ms = 1300) {
  await page.evaluate((t) => window.scrollTo({ top: t, behavior: "smooth" }), y);
  await sleep(ms);
}
async function search(term) {
  const box = page.getByPlaceholder("재료명·코드 검색");
  await box.click();
  await box.fill("");
  for (const ch of term) { await box.type(ch, { delay: 90 }); }
  await sleep(1400);
}
async function clickIf(name, ms = 1800) {
  try { await page.getByRole("button", { name }).first().click({ timeout: 2200 }); await sleep(ms); } catch {}
}

// 1) 인사이트 — Ashby + 재료군 비교(비강도 전환)
await goto("/insights");
await sleep(2600);
await scroll(520, 1500);          // 인사이트 카드
await scroll(1080, 1300);
await clickIf(/비강도/, 1600);    // 박스플롯 지표 전환
await clickIf(/비강성/, 1500);
await scroll(2400, 1400);
await sleep(900);

// 2) 라이브러리 — 스틸 군 검색
await goto("/materials");
await sleep(1600);
await search("SUS");              // 스테인리스 군
await sleep(1600);
await search("");
await search("Al");              // 알루미늄 군
await sleep(1500);

// 3) 고강도강 상세 — 응력-변형률·진응력·피팅
await goto("/materials/10");     // 17-4PH
await sleep(2400);
await scroll(340, 1300);
await clickIf("진응력", 2200);   // 진응력·넥킹
await clickIf("공칭", 1200);
await scroll(920, 1300);
await clickIf(/피팅 계산/, 2400); // 구성방정식 피팅
await scroll(1250, 1500);
await sleep(1000);

// 4) 알루미늄 상세 — 다른 곡선
await goto("/materials/23");     // Al7075-T6
await sleep(2200);
await scroll(340, 1200);
await clickIf("진응력", 1800);
await clickIf("공칭", 1000);
await sleep(1000);

// 5) 점탄성 — 완화곡선·Prony
await goto("/materials/67");     // EAR Isodamp
await sleep(2400);
await scroll(420, 1400);
await scroll(760, 1600);
await sleep(1200);

// 6) 라이브러리로 마무리
await goto("/materials");
await sleep(1600);

await ctx.close();
await browser.close();
console.log("녹화 완료 →", OUT);
