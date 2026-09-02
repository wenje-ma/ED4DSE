import json
from pathlib import Path
from tkinter import Tk, filedialog


def ipynb_to_md(ipynb_path: str, md_path: str | None = None):
    ipynb_file = Path(ipynb_path)
    if not ipynb_file.exists():
        raise FileNotFoundError(f"找不到文件: {ipynb_file}")

    if md_path is None:
        md_file = ipynb_file.with_suffix(".md")
    else:
        md_file = Path(md_path)

    with ipynb_file.open(encoding="utf-8") as f:
        notebook = json.load(f)

    markdown_parts = []
    for cell in notebook.get("cells", []):
        # 只保留 markdown 单元格，跳过 code / raw 单元格
        if cell.get("cell_type") != "markdown":
            continue

        source = cell.get("source", "")
        if isinstance(source, list):
            text = "".join(source)
        else:
            text = str(source)

        if text.strip():
            markdown_parts.append(text.rstrip())

    md_file.write_text("\n\n".join(markdown_parts), encoding="utf-8")
    print(f"已生成: {md_file}")
    return str(md_file)


def select_and_convert_ipynbs():
    root = Tk()
    root.withdraw()

    selected_files = filedialog.askopenfilenames(
        title='请选择要转换的 ipynb 文件',
        filetypes=[('Jupyter Notebook', '*.ipynb'), ('All Files', '*.*')]
    )

    if not selected_files:
        print('未选择任何文件，退出。')
        return []

    converted = []
    for ipynb_path in selected_files:
        output = ipynb_to_md(ipynb_path)
        converted.append(output)

    print(f'转换完成，共处理 {len(converted)} 个文件。')
    return converted


if __name__ == "__main__":
    select_and_convert_ipynbs()
