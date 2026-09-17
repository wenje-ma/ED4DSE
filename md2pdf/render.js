// render.js —— 将合并后的 Markdown 渲染为自包含 HTML（MPE 风格：markdown-it + KaTeX）
// 用法: node render.js <input.md> <output.html>
// 特性:
//   1. 行内 $...$ 与行间 $$...$$ 数学公式 -> KaTeX 服务端渲染（静态，Chrome 打印零等待）
//   2. pandoc 风格图片宽度 ![alt](figures/1.4.png){width=67%} -> <img style="width:67%">
//   3. 图片相对路径 -> 绝对 file:// URL（HTML 放在任意目录都能找到图）
//   4. 内联 KaTeX 字体 CSS（从 node_modules 复制 fonts 到本目录），HTML 完全自包含
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const MarkdownIt = require('markdown-it');
const texmath = require('markdown-it-texmath');
const katex = require('katex');

const [,, mdArg, htmlArg] = process.argv;
if (!mdArg || !htmlArg) {
  console.error('用法: node render.js <input.md> <output.html>');
  process.exit(1);
}

const mdPath = path.resolve(mdArg);
const htmlPath = path.resolve(htmlArg);
const toolDir = __dirname;

// ---------- 1. 确保 KaTeX 字体目录可用（一次复制，之后复用） ----------
const katexFontsDst = path.join(toolDir, 'katex_fonts');
const katexFontsSrc = path.join(toolDir, 'node_modules', 'katex', 'dist', 'fonts');
try {
  if (!fs.existsSync(katexFontsDst)) {
    fs.cpSync(katexFontsSrc, katexFontsDst, { recursive: true });
    console.log('  已复制 KaTeX 字体到', katexFontsDst);
  }
} catch (e) {
  console.error('⚠️ 复制 KaTeX 字体失败:', e.message);
  process.exit(1);
}

// ---------- 2. 读取 Markdown 并预处理 ----------
let src = fs.readFileSync(mdPath, 'utf8');
const baseDir = path.dirname(mdPath);

// 2a. 兼容行内公式结束 $ 前误加空格、且紧跟中文的情况:
//     $D=\{...x_n\} $开展  ->  $D=\{...x_n\}$开展
//     （texmath 的规则要求结束 $ 前不能有空格，否则会把后面内容一起吞进公式）
src = src.replace(/\$([^$\n]+?)\s+\$(?=[\u4e00-\u9fff])/g, '$$$1$$');
// 2a. 图片宽度属性: ![alt](src){width=67%} -> <img src="abs" alt="alt" style="width:67%">
src = src.replace(/!\[([^\]]*)\]\(([^)]+)\)\{([^}]*)\}/g, (m, alt, imgSrc, attrs) => {
  const widthMatch = attrs.match(/width\s*=\s*([^\s,]+)/);
  let style = '';
  if (widthMatch) style = ` style="width:${widthMatch[1]}"`;
  const abs = pathToFileURL(path.resolve(baseDir, imgSrc)).href;
  return `<img src="${abs}" alt="${alt || ''}"${style}>`;
});
// 2b. 兜底: 无属性图片也转绝对路径
src = src.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (m, alt, imgSrc) => {
  if (/^(https?:|file:)/.test(imgSrc)) return m;
  const abs = pathToFileURL(path.resolve(baseDir, imgSrc)).href;
  return `<img src="${abs}" alt="${alt || ''}">`;
});

// ---------- 3. markdown-it + texmath(KaTeX) 渲染 ----------
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: false,
  breaks: false
}).use(texmath, {
  engine: katex,
  delimiters: 'dollars',
  katexOptions: {
    throwOnError: false,
    strict: false,
    trust: true,
    output: 'html'
  }
});

const bodyHtml = md.render(src);

// ---------- 4. KaTeX CSS（内联，字体路径改写为绝对 file://） ----------
let katexCss = fs.readFileSync(path.join(toolDir, 'node_modules', 'katex', 'dist', 'katex.min.css'), 'utf8');
katexCss = katexCss.replace(/url\(fonts\//g, `url(${pathToFileURL(katexFontsDst).href}/`);

// ---------- 5. 页面样式（GitHub 风格正文 + 打印规则） ----------
const pageCss = `
@page { size: A4; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: -apple-system, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
  font-size: 14.5px; line-height: 1.7; color: #24292f;
  max-width: 920px; margin: 0 auto; padding: 8px 24px 40px;
  word-wrap: break-word;
}
h1, h2, h3, h4, h5, h6 { margin: 1.4em 0 0.6em; font-weight: 600; line-height: 1.3; color: #1f2328; }
h1 { font-size: 1.9em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }
h2 { font-size: 1.55em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }
h3 { font-size: 1.28em; }
h4 { font-size: 1.1em; }
h5 { font-size: 1em; }
h6 { font-size: 0.9em; color: #57606a; }
p { margin: 0 0 0.85em; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
img { max-width: 100%; height: auto; }
strong { font-weight: 600; }
hr { height: 1px; border: 0; background: #d0d7de; margin: 1.6em 0; }
blockquote {
  margin: 0 0 0.85em; padding: 0.2em 1em; color: #57606a;
  border-left: 4px solid #d0d7de; background: #f6f8fa;
}
blockquote p { margin: 0.4em 0; }
ul, ol { padding-left: 2em; margin: 0 0 0.85em; }
li { margin: 0.2em 0; }
li > ul, li > ol { margin-bottom: 0; }
code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.88em; background: rgba(175,184,193,0.18);
  padding: 0.15em 0.4em; border-radius: 6px;
}
pre {
  background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px;
  padding: 12px 14px; overflow-x: auto; margin: 0 0 0.85em;
}
pre code { background: none; padding: 0; font-size: 0.86em; }
table {
  border-collapse: collapse; width: 100%; margin: 0 0 0.85em; display: table;
}
th, td { border: 1px solid #d0d7de; padding: 6px 12px; }
th { background: #f6f8fa; font-weight: 600; }
tr:nth-child(2n) { background: #f6f8fa; }
/* KaTeX */
.katex { font-size: 1.02em; }
.math.block { display: block; margin: 0.9em 0; text-align: center; }
/* 打印规则 */
@media print {
  body { max-width: none; padding: 0; font-size: 13.5px; }
  h1, h2, h3, h4 { page-break-after: avoid; break-after: avoid; }
  img, pre, table, .math.block { page-break-inside: avoid; break-inside: avoid; }
  blockquote { page-break-inside: avoid; }
}
`;

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>${path.basename(mdPath, path.extname(mdPath))}</title>
<style>${katexCss}</style>
<style>${pageCss}</style>
</head>
<body>
${bodyHtml}
</body>
</html>`;

fs.writeFileSync(htmlPath, html, 'utf8');
console.log(`  已生成 HTML: ${htmlPath} (${(Buffer.byteLength(html) / 1024 / 1024).toFixed(2)} MB)`);
