import os
import json
import re
import requests
from urllib.parse import urlparse

# === 配置 ===
INPUT_JSON = r"D:\Downloads\questions.json"
IMAGE_DIR  = r"D:\Downloads\downloaded_images"

os.makedirs(IMAGE_DIR, exist_ok=True)

def download_missing_images(json_file, image_dir):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data if isinstance(data, list) else data.get("questions", [])
    total = 0
    downloaded = 0

    for q in questions:
        for field in ["question_raw", "explanation_raw"]:
            html = str(q.get(field, ""))
            matches = re.findall(r'<img[^>]+src="([^"]+)"', html)
            for url in matches:
                fname = os.path.basename(urlparse(url).path)
                save_path = os.path.join(image_dir, fname)
                total += 1
                if not os.path.exists(save_path):
                    try:
                        r = requests.get(url, timeout=10)
                        if r.status_code == 200:
                            with open(save_path, "wb") as f:
                                f.write(r.content)
                            downloaded += 1
                            print(f"[DOWNLOADED] {fname}")
                        else:
                            print(f"[ERROR] {fname} {r.status_code}")
                    except Exception as e:
                        print(f"[FAIL] {fname} {e}")
                else:
                    print(f"[SKIP] 已存在 {fname}")

    print(f"\n[SUMMARY] 需要 {total} 张，下载 {downloaded} 张，已有 {total-downloaded} 张")

if __name__ == "__main__":
    download_missing_images(INPUT_JSON, IMAGE_DIR)
