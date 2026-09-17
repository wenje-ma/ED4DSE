# -*- coding: utf-8 -*-
"""
md_to_pdf.py —— 将多个 md 合并为一个，并像 MPE 预览那样渲染后通过 Chrome 转 PDF。

用法：
    1. 直接运行: python md_to_pdf.py         （弹出对话框多选 md，顺序即合并顺序）
    2. 命令行:    python md_to_pdf.py a.md b.md c.md [--out out.pdf]

工作流程：
    多个 md -> 合并为一个 document.md -> render.js(markdown-it+KaTeX) 渲染为 HTML
            -> print.js(puppeteer-core) 驱动本机 Chrome 打印 A4 PDF（带页码）

依赖：
    - Python 3.10+（标准库 + tkinter）
    - Node.js（自动探测）
    - 本机 Chrome 或 Edge（自动探测，可用 CHROME_PATH 环境变量指定）
    - 首次运行会自动在 md2pdf/ 下执行 npm install（需联网一次）
"""
import os
from pathlib import Path
import re
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

SOURCE_COMMENT_PAT = re.compile(r"\s*<!-- source file: .*? -->\r?\n?")


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


def merge_markdown_files(md_paths: list[Path], output_md: Path) -> Path:
    """按给定顺序合并多个 md，删除 <!-- source file: --> 注释行。"""
    with open(output_md, "w", encoding="utf-8") as out_f:
        for p in md_paths:
            if not p.exists():
                print(f"  ⚠️ 跳过不存在文件: {p.name}")
                continue
            try:
                content = p.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  ⚠️ 读取失败跳过 {p.name}: {e}")
                continue
            content = SOURCE_COMMENT_PAT.sub("", content)
            out_f.write("\n\n")
            out_f.write(content)
    print(f"  合并完成: {output_md}")
    return output_md


def run_node(script_name: str, *args: str) -> None:
    node = find_node()
    script = TOOL_DIR / script_name
    r = subprocess.run([str(node), str(script), *args], capture_output=True, text=True, encoding="utf-8")
    for line in (r.stdout or "").splitlines():
        print(line)
    if r.returncode != 0:
        raise RuntimeError(f"{script_name} 失败:\n{(r.stderr or '').strip()}")


def md_to_pdf(md_paths: list[Path], output_pdf: Path | None = None) -> Path:
    """
    将若干 md 合并渲染后转 PDF。
    :param md_paths: 待处理的 md 路径（顺序即合并顺序；单个文件则直接转换）
    :param output_pdf: 输出 PDF 路径；None 时自动取名
    :return: 输出 PDF 路径
    """
    if not md_paths:
        raise ValueError("没有传入 md 文件")

    ensure_npm_deps()
    chrome = find_chrome()

    # 1. 合并（多个文件）或直接使用（单个文件）
    if len(md_paths) == 1:
        merged_md = md_paths[0]
    else:
        first_parent = md_paths[0].parent
        merged_md = first_parent / "document.md"
        print(f"正在合并 {len(md_paths)} 个文件…")
        merge_markdown_files(md_paths, merged_md)

    # 2. 确定输出路径
    if output_pdf is None:
        if len(md_paths) == 1:
            output_pdf = merged_md.with_suffix(".pdf")
        else:
            output_pdf = merged_md.with_suffix(".pdf")  # document.pdf，与 document.md 同名
    output_pdf = Path(output_pdf)
    output_html = output_pdf.with_suffix(".html")

    # 3. 渲染 HTML（markdown-it + KaTeX，MPE 风格）
    print(f"正在渲染: {merged_md.name}")
    run_node("render.js", str(merged_md), str(output_html))

    # 4. Chrome 打印 PDF
    print(f"正在通过 Chrome 打印 PDF: {output_pdf.name}")
    run_node("print.js", str(output_html), str(output_pdf), str(chrome))

    print(f"\n✅ 完成，输出文件: {output_pdf.resolve()}")
    return str(output_pdf)


def select_and_convert_md():
    """弹出对话框多选 md，合并后转 PDF（与 pdf_to_txt.py 交互一致）。"""
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askopenfilenames(
        title="请选择 Markdown 文件（按住 Ctrl 多选，顺序就是合并顺序）",
        filetypes=[("Markdown 文件", "*.md"), ("All Files", "*.*")]
    )
    if not selected:
        print("未选择任何文件，程序退出。")
        return []

    paths = [Path(p) for p in selected]
    output = md_to_pdf(paths)
    return [output]


if __name__ == "__main__":
    # 简单命令行解析：python md_to_pdf.py a.md b.md [--out out.pdf]
    args = sys.argv[1:]
    out_flag = "--out"
    if out_flag in args:
        i = args.index(out_flag)
        out_path = Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    else:
        out_path = None

    if args:
        md_to_pdf([Path(a) for a in args], out_path)
    else:
        select_and_convert_md()
