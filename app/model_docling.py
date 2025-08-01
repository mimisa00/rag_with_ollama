import os
import logging
from typing import Optional
from collections import defaultdict

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import  TextItem

# /backend/app
BASE_DIR = os.path.dirname(__file__)
# /backend/documents
DOC_PATH = os.path.join(os.path.dirname(BASE_DIR), "documents")
# /backend/documents/markdown
MD_PATH = os.path.join(DOC_PATH, "markdown")

config = {}
_log = logging.getLogger(__name__)

def load_config():
    global config
    try:
        from app.dao import config_dao
        config.update(config_dao.get_all_configs())
    except Exception as e:
        print(f"[ERROR] 載入配置失敗: {e}", flush=True)

def output_picture_as_markdown_table(doc, picture):
    # 設定 y 軸分群的容差
    Y_TOLERANCE = 10

    # 將文字依照 Y 軸分行
    line_map = defaultdict(list)
    for item, _ in doc.iterate_items(root=picture, traverse_pictures=True):
        if isinstance(item, TextItem):
            text = item.text
            bbox = item.prov[0].bbox
            y = bbox.t
            x = bbox.l

            matched = False
            for key_y in line_map:
                if abs(key_y - y) < Y_TOLERANCE:
                    line_map[key_y].append((x, text))
                    matched = True
                    break
            if not matched:
                line_map[y].append((x, text))

    # 排序 Y 軸（上到下）
    sorted_lines = sorted(line_map.items(), key=lambda kv: kv[0])

    print("### 📄 Markdown 表格輸出")
    pic_md_lines = []
    for _, items in sorted_lines:
        print("======= items ======", flush=True)
        print(items, flush=True)

        # 按 x 軸左到右排序每一行的文字
        row = [str(text) for x, text in sorted(items, key=lambda i: i[0])]
        print("| " + " | ".join(row) + " |")
        pic_md_lines.append("| " + " | ".join(row) + " |")
        #pic_md_lines.append(row)

    return pic_md_lines



# Docling API 文件擷取
def convert_file_via_docling(file_path: str, filename: str) -> Optional[dict]:
    try:
        load_config()
        print("========== file_path==========")
        print(file_path)
        print("========== filename==========")
        print(filename)

        # 透過原生 Docling LIB 處理
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 2
        pipeline_options.generate_page_images = True
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True
        # pipeline_options.generate_picture_images = True
        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = doc_converter.convert(file_path)
        mdtext = result.document.export_to_markdown()
        mdtext += mdtext + "\n"
        
        print("========== mdtext ==========")
        print(mdtext)

        doc = result.document

        #mdtext += picture.export_to_markdown()
        for picture in doc.pictures:
            md_lines = output_picture_as_markdown_table(doc, picture)
            mdtext += "\n".join(md_lines) + "\n\n"

        # 新增：儲存 markdown 內容到 documents/markdown/ 目錄
        markdown_dir = os.path.join(MD_PATH)
        os.makedirs(markdown_dir, exist_ok=True)
        markdown_filename = f"{filename}.md"
        markdown_path = os.path.join(markdown_dir, markdown_filename)
        with open(markdown_path, "w", encoding="utf-8") as md_file:
            md_file.write(mdtext)

        if not mdtext:
            print(f"[WARN] 無法擷取內容：{filename}", flush=True)
            return None

        # 回傳 dict 結構，包含內容與檔案資訊
        return {
            "content": mdtext ,
            "source_file": filename,
            "markdown_file": markdown_filename
        }
    except Exception as e:
        print(f"[ERROR] 處理 {filename} 時發生例外：{e}", flush=True)
        return None

