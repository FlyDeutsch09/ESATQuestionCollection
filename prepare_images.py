import os, re, json, shutil

INPUT_JSON  = r"D:\Downloads\questions.json"     # 题库 JSON
IMAGE_SRC   = r"D:\Downloads\raw_images"        # 你原始存放题目图片的目录
OUTPUT_DIR  = r"D:\Downloads\output"            # 输出目录
IMAGE_DST   = os.path.join(OUTPUT_DIR, "images")

def main():
    os.makedirs(IMAGE_DST, exist_ok=True)

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data if isinstance(data, list) else data.get("questions", [])
    updated = []

    for qi, q in enumerate(questions, start=1):
        stem = str(q.get("stem", ""))
        # 找到占位符 [IMAGE:0], [IMAGE:1]...
        matches = re.findall(r"\[IMAGE:(\d+)\]", stem)
        local_images = []
        for mi, midx in enumerate(matches):
            img_name = f"q_{qi:04d}_img{mi}.png"
            src_path = os.path.join(IMAGE_SRC, f"{midx}.png")   # 假设原图以编号命名
            dst_path = os.path.join(IMAGE_DST, img_name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                local_images.append(f"images/{img_name}")
            else:
                print(f"[WARN] 图片缺失 {src_path}")
                local_images.append("")  # 占位
        q["_local_images"] = local_images
        updated.append(q)

    # 保存新的 JSON
    new_json = os.path.join(OUTPUT_DIR, "questions_with_images.json")
    with open(new_json, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

    print(f"[DONE] 新 JSON 保存到 {new_json}")
    print(f"[INFO] 图片复制到 {IMAGE_DST}")

if __name__ == "__main__":
    main()
