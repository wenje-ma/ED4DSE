// print.js —— 用本机 Chrome (puppeteer-core) 将 HTML 打印为 A4 PDF（带页码页脚）
// 用法: node print.js <input.html> <output.pdf> <chrome.exe路径>
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const puppeteer = require('puppeteer-core');

const [,, htmlArg, pdfArg, chromePath] = process.argv;
if (!htmlArg || !pdfArg || !chromePath) {
  console.error('用法: node print.js <input.html> <output.pdf> <chrome.exe路径>');
  process.exit(1);
}
const htmlPath = path.resolve(htmlArg);
const pdfPath = path.resolve(pdfArg);
if (!fs.existsSync(htmlPath)) {
  console.error(`找不到 HTML: ${htmlPath}`);
  process.exit(1);
}
if (!fs.existsSync(chromePath)) {
  console.error(`找不到 Chrome: ${chromePath}`);
  process.exit(1);
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ['--disable-gpu', '--hide-scrollbars', '--no-first-run']
  });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 1600 });
    await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle0', timeout: 120000 });
    await page.pdf({
      path: pdfPath,
      preferCSSPageSize: true,
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate: '<span></span>',
      footerTemplate: `<div style="width:100%; font-size:9px; color:#888; text-align:center; padding:0 15mm;">
        <span class="pageNumber"></span> / <span class="totalPages"></span>
      </div>`,
      margin: { top: '20mm', bottom: '18mm', left: '16mm', right: '16mm' }
    });
    console.log(`  已生成 PDF: ${pdfPath}`);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error('打印失败:', e.message);
  process.exit(1);
});
