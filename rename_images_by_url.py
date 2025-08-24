import os
import json
import shutil
import re
from urllib.parse import urlparse

# === 配置 ===
INPUT_JSON = r"D:\Downloads\questions.json"       # 题库 JSON 文件
IMAGE_DIR   = r"D:\Downloads\downloaded_images"   # 你原始保存的图片目录
OUTPUT_DIR  = r"D:\Downloads\raw_images"          # 目标文件夹（重命名后的）

def extract_image_filenames_from_json(json_file):
    """提取 JSON 中所有 <img src="..."> 的文件名，并和 [IMAGE:x] 建立对应关系"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data if isinstance(data, list) else data.get("questions", [])
    mapping = {}  # {原始文件名: 新编号}

    counter = 0
    for q in questions:
        # 从 explanation_raw 和 question_raw 中提取 <img src="...">
        for field in ["question_raw", "explanation_raw"]:
            html = str(q.get(field, ""))
            matches = re.findall(r'<img[^>]+src="([^"]+)"', html)
            for url in matches:
                fname = os.path.basename(urlparse(url).path)  # 提取文件名
                if fname not in mapping:
                    mapping[fname] = counter
                    counter += 1
    return mapping

def rename_images(json_file, image_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    mapping = extract_image_filenames_from_json(json_file)

    if not mapping:
        print("[WARN] JSON 中未找到任何 <img src=...> 标签")
        return

    # 遍历映射表，把文件复制并重命名
    for orig_name, new_idx in mapping.items():
        src = os.path.join(image_dir, orig_name)
        dst = os.path.join(output_dir, f"{new_idx}.png")
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"[OK] {orig_name} -> {new_idx}.png")
        else:
            print(f"[MISSING] 找不到 {orig_name} (JSON 需要但本地没有)")

    print(f"\n[FINISHED] 共处理 {len(mapping)} 张图片，已保存到 {output_dir}")

if __name__ == "__main__":
    rename_images(INPUT_JSON, IMAGE_DIR, OUTPUT_DIR)
