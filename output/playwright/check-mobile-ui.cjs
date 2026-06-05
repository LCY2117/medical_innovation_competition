const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const outDir = path.resolve('output/playwright');
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true });
  await page.goto('https://lifereflex.mddcommunity.top/mobile?beta=patient&slot=patient&incidentId=f3445385-b48a-4dd2-9a12-3cac6b20bffc', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(1500);
  const metrics = await page.evaluate(() => {
    const health = document.querySelector('.mobile-health-line');
    const userPanel = document.querySelector('.mobile-user-panel');
    const buttons = [...document.querySelectorAll('.mobile-icon-button')].map((button) => {
      const b = button.getBoundingClientRect();
      const svg = button.querySelector('svg')?.getBoundingClientRect();
      return {
        width: b.width,
        height: b.height,
        svgCenterDx: svg ? Math.round((svg.left + svg.width / 2) - (b.left + b.width / 2)) : null,
        svgCenterDy: svg ? Math.round((svg.top + svg.height / 2) - (b.top + b.height / 2)) : null,
      };
    });
    const h = health?.getBoundingClientRect();
    const p = userPanel?.getBoundingClientRect();
    return {
      healthText: health?.textContent?.trim(),
      healthWidth: h?.width ?? null,
      panelWidth: p?.width ?? null,
      healthOverflowsPanel: Boolean(h && p && h.right > p.right + 1),
      shellScrollWidth: document.documentElement.scrollWidth,
      viewportWidth: window.innerWidth,
      hasHorizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
      buttons,
    };
  });
  const screenshot = path.join(outDir, 'mobile-ui-390.png');
  await page.screenshot({ path: screenshot, fullPage: true });
  await browser.close();
  console.log(JSON.stringify({ screenshot, metrics }, null, 2));
})();
