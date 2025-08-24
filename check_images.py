import os, re, json

# === 配置 ===
INPUT_JSON = r"D:\Downloads\questions.json"   # 题库 JSON
IMAGE_DIR  = r"D:\Downloads\raw_images"       # 已重命名的图片目录

def collect_needed_indices(json_file):
    """从 JSON 中收集所有需要的图片序号"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data if isinstance(data, list) else data.get("questions", [])
    indices = set()
    for q in questions:
        # 同时检查 question 和 explanation
        for field in ["question", "explanation"]:
            text = str(q.get(field, ""))
            matches = re.findall(r"\[IMAGE:(\d+)\]", text)
            indices.update(int(m) for m in matches)
    return sorted(indices)

def check_images(json_file, image_dir):
    needed = collect_needed_indices(json_file)
    found  = [int(os.path.splitext(f)[0]) for f in os.listdir(image_dir) if f.endswith(".png")]
    found  = sorted(found)

    print(f"[INFO] JSON 需要 {len(needed)} 张图片: {needed[:20]}{'...' if len(needed)>20 else ''}")
    print(f"[INFO] 文件夹实际有 {len(found)} 张图片: {found[:20]}{'...' if len(found)>20 else ''}")

    missing = [i for i in needed if i not in found]
    extra   = [i for i in found  if i not in needed]

    if not missing and not extra:
        print("[OK] 所有图片编号完全匹配 ✅")
    else:
        if missing:
            print(f"[MISSING] 缺少 {len(missing)} 张: {missing}")
        if extra:
            print(f"[EXTRA] 多余 {len(extra)} 张: {extra}")

if __name__ == "__main__":
    check_images(INPUT_JSON, IMAGE_DIR)
