# -*- coding: utf-8 -*-
"""
md_to_pdf.py —— 将单个 md 像 MPE 预览那样渲染后，通过本机 Chrome 转为 A4 PDF（带页码）。

配合 md_merge.py 使用：先用 md_merge.py 合并章节，再对合并结果执行本脚本。

用法：
    1. 直接运行: python md_to_pdf.py          （弹出对话框选择 md，可多选批量逐个转换）
    2. 命令行:    python md_to_pdf.py a.md b.md [--out out.pdf]   （--out 仅单个文件时有效）

流程：
    md -> render.js(markdown-it+KaTeX) 渲染为 HTML
       -> print.js(puppeteer-core) 驱动本机 Chrome 打印 A4 PDF

依赖：
    - Python 3.10+（标准库 + tkinter）
    - Node.js（自动探测）
    - 本机 Chrome 或 Edge（自动探测，可用 CHROME_PATH 环境变量指定）
    - 首次运行会自动在 md2pdf/ 下执行 npm install（需联网一次）
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog

TOOL_DIR = Path(__file__).resolve().parent / "md2pdf"

CHROME_CANDIDATES = [
    Path(os.environ["CHROME_PATH"]) if os.environ.get("CHROME_PATH") else None,
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
    Path(os.environ.get("LOCALAPPDATA", "C:/Users/default/AppData/Local") + "/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]


def find_node() -> Path:
    node = shutil.which("node")
    if not node:
        raise FileNotFoundError("未找到 node.exe，请先安装 Node.js（https://nodejs.org）")
    return Path(node)


def find_chrome() -> Path:
    for cand in CHROME_CANDIDATES:
        if cand and cand.exists():
            return cand
    raise FileNotFoundError(
        "未找到 Chrome/Edge，请设置环境变量 CHROME_PATH 指向 chrome.exe 的完整路径"
    )


def ensure_npm_deps() -> None:
    """首次运行时在 md2pdf/ 下安装 node 依赖。"""
    if (TOOL_DIR / "node_modules").exists():
        return
    print("  首次运行，正在安装渲染依赖（npm install，仅需一次）…")
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise FileNotFoundError("未找到 npm，请先安装 Node.js")
    # Windows 下 npm 是 .cmd 脚本，用 shell=True 由 cmd.exe 执行最稳妥
    r = subprocess.run(f'"{npm}" install --no-audit --no-fund',
                       cwd=str(TOOL_DIR), shell=True)
    if r.returncode != 0:
        raise RuntimeError("npm install 失败，请检查网络后重试")
    print("  依赖安装完成。")


def run_node(script_name: str, *args: str) -> None:
    node = find_node()
    script = TOOL_DIR / script_name
    r = subprocess.run([str(node), str(script), *args], capture_output=True, text=True, encoding="utf-8")
    for line in (r.stdout or "").splitlines():
        print(line)
    if r.returncode != 0:
        raise RuntimeError(f"{script_name} 失败:\n{(r.stderr or '').strip()}")


def md_to_pdf(md_path: Path, output_pdf: Path | None = None) -> Path:
    """
    将单个 md 渲染为 HTML 后通过 Chrome 打印为 PDF。
    :param md_path: 待转换的 md 文件
    :param output_pdf: 输出 PDF 路径；None 时与 md 同名（同目录）
    :return: 输出 PDF 路径
    """
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(f"找不到文件: {md_path}")

    ensure_npm_deps()
    chrome = find_chrome()

    output_pdf = Path(output_pdf) if output_pdf else md_path.with_suffix(".pdf")
    output_html = output_pdf.with_suffix(".html")

    # 1. 渲染 HTML（markdown-it + KaTeX，MPE 风格）
    print(f"正在渲染: {md_path.name}")
    run_node("render.js", str(md_path), str(output_html))

    # 2. Chrome 打印 PDF
    print(f"正在通过 Chrome 打印 PDF: {output_pdf.name}")
    run_node("print.js", str(output_html), str(output_pdf), str(chrome))

    print(f"\n✅ 完成，输出文件: {output_pdf.resolve()}")
    return str(output_pdf)


def select_and_convert_md():
    """弹出对话框选择 md（可多选），逐个转换为 PDF（与 pdf_to_txt.py 交互一致）。"""
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askopenfilenames(
        title="请选择 Markdown 文件（可多选，每个文件单独转换）",
        filetypes=[("Markdown 文件", "*.md"), ("All Files", "*.*")]
    )
    if not selected:
        print("未选择任何文件，程序退出。")
        return []

    converted = []
    for p in selected:
        converted.append(md_to_pdf(Path(p)))
    print(f"转换完成，共处理 {len(converted)} 个文件。")
    return converted


if __name__ == "__main__":
    # 简单命令行解析：python md_to_pdf.py a.md b.md [--out out.pdf]
    args = sys.argv[1:]
    out_flag = "--out"
    out_path = None
    if out_flag in args:
        i = args.index(out_flag)
        out_path = Path(args[i + 1])
        args = args[:i] + args[i + 2:]

    if not args:
        select_and_convert_md()
    elif len(args) == 1:
        md_to_pdf(Path(args[0]), out_path)
    else:
        if out_path:
            print("⚠️ --out 仅支持单个文件，多个文件将各自输出同名 PDF")
        for a in args:
            md_to_pdf(Path(a))
