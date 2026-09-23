from pathlib import Path
from tkinter import Tk, filedialog

import fitz  # PyMuPDF: 渲染 PDF 页为图片

from rapidocr_onnxruntime import RapidOCR


def pdf_to_txt(pdf_path: str, txt_path: str | None = None):
    """纯 OCR: 每一页都渲染成图片交给 RapidOCR 识别, 再写入 TXT。

    与 pdf_to_txt.py(纯文字层提取) 区分用途:
      - pdf_to_txt.py: 处理有文字层的电子版 PDF
      - 本脚本: 处理扫描件/图片型 PDF, 强制走 OCR, 不做任何文字层判断

    运行接口保持一致:
      - txt_path 为 None 时, 输出到同名 .txt
      - 每页以 "--- Page {i} ---" 分隔
      - UTF-8 编码写入
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"找不到文件: {pdf_file}")

    if txt_path is None:
        txt_file = pdf_file.with_suffix(".txt")
    else:
        txt_file = Path(txt_path)

    doc = fitz.open(str(pdf_file))
    engine = RapidOCR()  # 纯 OCR, 每页都走识别

    pages_text = []
    for i, page in enumerate(doc, start=1):
        ocr_text = _ocr_page(page, engine)
        pages_text.append(f"--- Page {i} ---\n{ocr_text}\n")
        print(f"  第{i}页: 已 OCR 识别")

    txt_file.write_text("\n".join(pages_text), encoding="utf-8")
    print(f"已生成: {txt_file}")
    return str(txt_file)


def _ocr_page(page, engine, dpi: int = 200) -> str:
    """把 PDF 页面渲染成图片, 交给 RapidOCR, 返回按行排序的文本"""
    zoom = dpi / 72
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    result, _ = engine(pix.tobytes("png"))
    if not result:
        return ""
    lines = sorted(result, key=lambda x: x[0][0][1])  # 按纵坐标从上到下
    return "\n".join(line[1] for line in lines)


def select_and_convert_pdfs():
    root = Tk()
    root.withdraw()

    selected_files = filedialog.askopenfilenames(
        title='请选择要转换的 PDF 文件',
        filetypes=[('PDF 文件', '*.pdf'), ('All Files', '*.*')]
    )

    if not selected_files:
        print('未选择任何文件，退出。')
        return []

    converted = []
    for pdf_path in selected_files:
        output = pdf_to_txt(pdf_path)
        converted.append(output)

    print(f'转换完成，共处理 {len(converted)} 个文件。')
    return converted


if __name__ == "__main__":
    select_and_convert_pdfs()
