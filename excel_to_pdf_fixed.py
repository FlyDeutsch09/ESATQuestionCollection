# excel_to_pdf_fixed.py
import os
import re
import json
import subprocess
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

# ========== 配置 ==========
INPUT_XLSX = r"D:\Downloads\PracticeQuestions.xlsx"  # 改成你的路径
SHEET_NAME = "导出结果"   # 若失败脚本会回退到第一个 sheet
OUT_DIR = r"D:\Downloads\output"  # 改成你想要的输出目录
IMG_DIR = os.path.join(OUT_DIR, "images")
JSON_FILE = os.path.join(OUT_DIR, "questions.json")
TEX_PRACTICE = os.path.join(OUT_DIR, "questions_practice.tex")
TEX_ANS = os.path.join(OUT_DIR, "questions_answers.tex")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# ========== 工具函数 ==========
def clean_html_to_text(html):
    """把 HTML 字段转成纯文本，保留 <img> 的 src 列表"""
    if pd.isna(html) or html is None:
        return "", []
    soup = BeautifulSoup(html, "lxml")
    imgs = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            imgs.append(src)
        # 用占位符替代 img 元素，便于后续替换
        img.replace_with(f"[IMAGE:{len(imgs)-1}]")
    text = soup.get_text(separator="\n", strip=True)
    return text, imgs

def download_img(src, dst_dir, idx_prefix="img"):
    """下载图片 src（支持 http(s) 与 data URI），返回本地路径或 None"""
    if not src:
        return None
    # data URI
    if src.startswith("data:"):
        try:
            header, b64 = src.split(",", 1)
            ext = "png"
            m = re.search(r"data:(image/[^;]+);base64", header)
            if m:
                ext = m.group(1).split("/")[1]
            filename = f"{idx_prefix}_{len(os.listdir(dst_dir))+1}.{ext}"
            path = os.path.join(dst_dir, filename)
            import base64
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64))
            return path
        except Exception:
            return None
    # http/https
    try:
        resp = requests.get(src, timeout=15)
        resp.raise_for_status()
        up = urlparse(src)
        fn = os.path.basename(unquote(up.path)) or f"{idx_prefix}_{len(os.listdir(dst_dir))+1}.png"
        fn = re.sub(r"[^0-9A-Za-z._-]", "_", fn)
        path = os.path.join(dst_dir, fn)
        with open(path, "wb") as f:
            f.write(resp.content)
        return path
    except Exception:
        return None

def latex_escape(s):
    """对常见 LaTeX 特殊字符做转义，保留换行处理"""
    if not s:
        return ""
    replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&', '%': r'\%', '$': r'\$',
        '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
        '~': r'\textasciitilde{}', '^': r'\^{}'
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\n\n", "\n\\medskip\n")
    s = s.replace("\n", "\\\\\n")
    return s

# ========== 读取 Excel ==========
def read_excel_safe(path, sheet_name):
    try:
        df = pd.read_excel(path, sheet_name=sheet_name)
        return df
    except Exception as e:
        print(f"[WARN] 无法按 sheet 名 `{sheet_name}` 读取：{e}，尝试读取第一个 sheet。")
        try:
            df = pd.read_excel(path, sheet_name=0)
            return df
        except Exception as e2:
            raise RuntimeError(f"读取 Excel 失败：{e2}")

print("开始读取 Excel...")
df = read_excel_safe(INPUT_XLSX, SHEET_NAME)
print(f"读取表 {SHEET_NAME if SHEET_NAME in df.keys() else '第一个 sheet'}，共 {len(df)} 行")

questions = []
for idx, row in df.iterrows():
    # 解析题目 HTML -> 文本 + 图片 list
    q_raw = row.get("题目", "") if "题目" in row else row.get("question", "")
    q_text, q_imgs = clean_html_to_text(q_raw)

    # 解析选项字段（可能是 HTML 或纯文本）
    opts_raw = row.get("选项", "")
    opt_text, opt_imgs = ("", [])
    if isinstance(opts_raw, str):
        opt_text, opt_imgs = clean_html_to_text(opts_raw)

    # --- 选项解析（稳健版） ---
    options = {}
    if opt_text:
        # 方法1：按块匹配 A) / A. / A、 ... 到下一个字母或文本结尾
        pattern = re.compile(r'([A-F])[、\.\)]\s*(.*?)(?=(?:\n+[A-F][、\.\)]|\Z))', re.S | re.M)
        matches = pattern.findall(opt_text)
        if matches:
            for k, v in matches:
                options[k.strip()] = v.strip()
        else:
            # 方法2：按行匹配
            lines = [line.strip() for line in opt_text.splitlines() if line.strip()]
            for line in lines:
                m = re.match(r'^([A-F])[、\.\)]\s*(.*)$', line)
                if m:
                    options[m.group(1)] = m.group(2).strip()
            # 方法3：回退 — 如果仍为空且行数合理，按行序号分配 A,B,C...
            if not options and 0 < len(lines) <= 8:
                for i, line in enumerate(lines):
                    options[chr(65 + i)] = line

    # 合并图片来源（题干+选项）
    imgs = (q_imgs or []) + (opt_imgs or [])
    local_imgs = []
    for s in imgs:
        p = download_img(s, IMG_DIR)
        if p:
            local_imgs.append(p)

    questions.append({
        "id": f"Q{idx+1:04d}",
        "type": row.get("题目类型", ""),
        "paper_type": row.get("试卷类型", ""),
        "difficulty": row.get("难度", ""),
        "year": row.get("年份", ""),
        "question_raw": q_raw,
        "question": q_text,
        "options": options,
        "answer": str(row.get("答案", "")).strip(),
        "explanation_raw": row.get("解题思路", ""),
        "explanation": (clean_html_to_text(row.get("解题思路", ""))[0] if isinstance(row.get("解题思路", ""), str) else ""),
        "images": local_imgs
    })

# 保存标准 JSON
with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print(f"[DONE] 已写出标准 JSON: {JSON_FILE} （共 {len(questions)} 道题）")

# ========== 生成 LaTeX（练习册 + 答案册） ==========
def build_tex(questions, tex_path, include_answers=False):
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(r"""\documentclass[12pt]{article}
\usepackage{xeCJK}
\setCJKmainfont{SimSun} % 根据你系统替换字体
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{geometry}
\geometry{a4paper,margin=1in}
\begin{document}
""")
        f.write("\n")
        from collections import defaultdict
        groups = defaultdict(list)
        for q in questions:
            key = q.get("paper_type") or "General"
            groups[key].append(q)

        for group_name, qlist in groups.items():
            f.write(r"\section*{" + latex_escape(str(group_name)) + "}\n")
            for q in qlist:
                f.write(r"\subsection*{" + latex_escape(q["id"]) + "}\n")
                f.write(latex_escape(q["question"]) + "\n\n")
                if q.get("images"):
                    for imgpath in q["images"]:
                        rel = os.path.relpath(imgpath, os.path.dirname(tex_path))
                        f.write(r"\begin{center}" + "\n")
                        f.write(r"\includegraphics[width=0.7\linewidth]{" + rel.replace("\\","/") + "}\n")
                        f.write(r"\end{center}" + "\n\n")
                if q.get("options"):
                    f.write(r"\begin{enumerate}[label=\Alph*.]" + "\n")
                    for k in sorted(q["options"].keys()):
                        f.write(r"\item " + latex_escape(q["options"][k]) + "\n")
                    f.write(r"\end{enumerate}" + "\n\n")
                if include_answers and q.get("answer"):
                    f.write(r"\textbf{Answer:} " + latex_escape(q["answer"]) + "\n\n")
                if include_answers and q.get("explanation"):
                    f.write(r"\textit{Explanation:} " + latex_escape(q["explanation"]) + "\n\n")
                f.write("\n\\bigskip\n")
        f.write(r"\end{document}")
    print(f"[DONE] LaTeX 文件已生成: {tex_path}")

build_tex(questions, TEX_PRACTICE, include_answers=False)
build_tex(questions, TEX_ANS, include_answers=True)

# ========== 可选：自动调用 xelatex（若系统配置了 xelatex） ==========
def compile_tex(texfile, outdir=OUT_DIR):
    try:
        subprocess.run(["xelatex", "-interaction=nonstopmode", "-output-directory", outdir, texfile], check=True)
        return True
    except Exception as e:
        print("编译失败：", e)
        return False

# 若你希望脚本自动编译，把下面注释取消
# compile_tex(TEX_PRACTICE)
# compile_tex(TEX_ANS)

print("完成。请到 output 目录查看生成的 .tex、.json 与 images 文件夹。")
