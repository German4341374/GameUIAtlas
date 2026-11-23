// Rasterize the vector layouts for viewers that block embedded SVG images.
const { chromium } = require("playwright");
const { resolve } = require("node:path");
const { pathToFileURL } = require("node:url");

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || undefined});
  try {
    const page = await browser.newPage({viewport:{width:1280,height:760},deviceScaleFactor:1});
    for (const study of ["apex", "vesper", "relay", "pollen"]) {
      const dir = resolve(__dirname, "../studies", study);
      await page.goto(pathToFileURL(resolve(dir, "detail.svg")).href);
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({path:resolve(dir,"model/inspection.png")});
    }
  } finally {await browser.close();}
})().catch(err => {console.error(err);process.exitCode=1;});
