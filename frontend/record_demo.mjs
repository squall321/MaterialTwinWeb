// MaterialTwin 시연 녹화 v2 — 카테고리 필터·brush 드래그 회귀·피팅·단위계·편집·점탄성 워크스루.
import { createRequire } from "module";
const require = createRequire("/home/koopark/claude/koofinance/frontend/");
const { chromium } = require("playwright");

const BASE = process.env.MTW_BASE || "http://127.0.0.1:17777";
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

// 1) 인사이트 — KPI·Ashby·재료군 박스플롯(비강도 전환)·연신 히스토그램
await goto("/insights");
await sleep(2600);
await scroll(520, 1500);
await scroll(1080, 1300);
await clickIf(/비강도/, 1600);
await clickIf(/비강성/, 1400);
await scroll(1900, 1400);          // 물성 분포(연신 히스토그램 포함)
await sleep(900);

// 2) 라이브러리 — 카테고리 필터 칩 + 검색
await goto("/materials");
await sleep(1600);
await clickIf(/^metal$/, 1400);    // metal 칩 → 41건
await clickIf(/^polymer$/, 1400);  // polymer 칩
await clickIf(/^전체$/, 1000);
await search("SUS");               // 스테인리스 군
await sleep(1400);

// 3) 고강도강 상세 — brush 드래그 회귀 + 진응력 + 피팅 + 단위계
await goto("/materials/10");       // 17-4PH
await sleep(2400);
await scroll(200, 1200);
// brush 드래그: 차트 탄성 구간을 가로 드래그 → 회귀 구간 선택(신기능)
try {
  const canvas = page.locator("canvas").first();
  const box = await canvas.boundingBox();
  const y = box.y + box.height * 0.55;
  await page.mouse.move(box.x + box.width * 0.08, y);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.16, y, { steps: 14 });
  await page.mouse.up();
  await sleep(1800);
} catch {}
await clickIf("진응력", 2000);     // 넥킹 마커
await clickIf("공칭", 1100);
await scroll(950, 1300);
await clickIf(/피팅 계산/, 2200);  // 구성방정식 4모델
await scroll(1300, 1500);
await sleep(900);

// 4) 재료 편집 다이얼로그(신기능) — 열고 닫기
await scroll(0, 900);
await clickIf(/^편집$/, 1600);
await page.keyboard.press("Escape");
await sleep(800);

// 5) 점탄성 — 완화곡선·Prony·MAT_VISCOELASTIC
await goto("/materials/67");       // EAR Isodamp
await sleep(2400);
await scroll(420, 1400);
await scroll(780, 1600);
await sleep(1000);

// 6) 라이브러리로 마무리(카운트·칩 노출)
await goto("/materials");
await sleep(1800);

await ctx.close();
await browser.close();
console.log("녹화 완료 →", OUT);
