# -*- coding: utf-8 -*-
"""
ipynb 转 md 脚本
=================

功能：
    运行后会弹出文件选择对话框，可自由选择一个或多个 .ipynb 文件。
    对每个文件，只保留 markdown 单元格（正文/公式），**跳过代码单元格**，
    分别输出对应的 .md 文件，保存在与源文件相同的目录下。

用法：
    直接运行本脚本（如：python ipynb_to_md.py），然后在对话框中勾选文件即可。
"""

import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def notebook_to_markdown(nb_path):
    """读取一个 .ipynb 文件，只抽取 markdown 单元格，跳过代码单元格，返回 markdown 文本。"""
    with open(nb_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    cells = notebook.get("cells", [])
    md_parts = []

    for cell in cells:
        cell_type = cell.get("cell_type", "")
        source = cell.get("source", "")

        # source 字段可能是字符串，也可能是字符串列表，统一拼接成字符串
        if isinstance(source, list):
            source = "".join(source)

        # 只保留 markdown 单元格；code / raw 等其他类型一律跳过
        if cell_type == "markdown":
            md_parts.append(source)

    return "\n\n".join(md_parts)


def main():
    # 隐藏 tkinter 主窗口，只显示文件选择对话框
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="选择一个或多个 .ipynb 文件",
        filetypes=[("Jupyter Notebook", "*.ipynb"), ("所有文件", "*.*")],
    )

    if not file_paths:
        messagebox.showinfo("提示", "未选择任何文件，已退出。")
        root.destroy()
        return

    converted = []
    failed = []

    for nb_path in file_paths:
        try:
            markdown = notebook_to_markdown(nb_path)

            # 输出到与源文件相同的目录，文件名同源文件，仅后缀改为 .md
            base_dir = os.path.dirname(os.path.abspath(nb_path))
            base_name = os.path.splitext(os.path.basename(nb_path))[0]
            md_path = os.path.join(base_dir, base_name + ".md")

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown)

            converted.append(md_path)
        except Exception as e:
            failed.append((nb_path, str(e)))

    # 汇总结果并弹窗提示
    lines = []
    if converted:
        lines.append("成功转换 %d 个文件：" % len(converted))
        for p in converted:
            lines.append("  - " + p)
    if failed:
        lines.append("失败 %d 个文件：" % len(failed))
        for p, err in failed:
            lines.append("  - %s（%s）" % (p, err))

    messagebox.showinfo("转换完成", "\n".join(lines) if lines else "无操作")
    root.destroy()


if __name__ == "__main__":
    main()
