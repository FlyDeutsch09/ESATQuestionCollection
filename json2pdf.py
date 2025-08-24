#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
json2pdf.py - Convert a structured JSON with questions into a PDF (via LaTeX).
修复内容：
- ✅ 修复 invalid escape warnings
- ✅ 修复图片路径和复制问题
- ✅ 替换 XITS Math 为 Latin Modern Math
- ✅ 改善 LaTeX 结构和兼容性
"""

import os
import json
import shutil
import argparse
from pathlib import Path
import subprocess
import re

# --------------------------
# 配置项
# --------------------------

LATEX_TEMPLATE = r"""
\documentclass[12pt]{article}
\usepackage{xeCJK}
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{caption}

\setCJKmainfont{SimSun}
\setmainfont{Times New Roman}
\setmathfont{Latin Modern Math}

\geometry{margin=1in}
\graphicspath{{images/}}

\title{{\Huge %(title)s}}
\date{}

\begin{document}
\maketitle
\setlength{\parskip}{0.5em}

%(body)s

\end{document}
"""

QUESTION_BLOCK = r"""
\noindent
\textbf{Q%(id)d.} %(question)s

%(image_block)s

\textbf{A.} %(A)s \\
\textbf{B.} %(B)s \\
\textbf{C.} %(C)s \\
\textbf{D.} %(D)s \\

\textbf{Answer:} %(answer)s \\
\textbf{Explanation:} %(explanation)s

\hrule
\vspace{1em}
"""

IMAGE_BLOCK = r"""
\begin{center}
\includegraphics[width=0.8\linewidth]{%(filename)s}
\end{center}
"""

# --------------------------
# 核心逻辑
# --------------------------


def escape_latex_math(text: str) -> str:
    """把 JSON 中的数学符号替换为 LaTeX 语法"""
    if not text:
        return ""

    replacements = {
        "⋅": r"\cdot ",
        "∙": r"\cdot ",
        "·": r"\cdot ",
        "√": r"\sqrt{}",
        "∣": r"|",
        "∘": r"\circ ",
        "≤": r"\leq ",
        "≥": r"\geq ",
        "≠": r"\neq ",
        "⟹": r"\implies ",
        "→": r"\to ",
        "∞": r"\infty ",
    }

    # 替换特殊符号
    for k, v in replacements.items():
        text = text.replace(k, v)

    # 替换 Unicode 数学斜体字母 (𝑎..𝑧, 𝐴..𝑍)
    text = re.sub(r"[𝑎-𝑧𝐴-𝑍]", lambda m: f"${m.group(0)}$", text)

    # 确保 a^2, m_0 这种公式被包裹
    text = re.sub(r"([A-Za-z0-9]+[\^_][A-Za-z0-9]+)", r"$\1$", text)

    return text


def json_to_latex(input_path: Path, outdir: Path, title: str) -> Path:
    """读取 JSON 文件并生成 LaTeX 文件"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        questions = data
    else:
        questions = data.get("questions", [])

    body_parts = []
    image_dir = outdir / "images"
    image_dir.mkdir(exist_ok=True)

    for idx, item in enumerate(questions, start=1):
        image_block = ""
        if "image" in item and item["image"]:
            src = Path(item["image"])
            if src.exists():
                dst = image_dir / src.name
                shutil.copy(src, dst)
                image_block = IMAGE_BLOCK % {"filename": src.name}
            else:
                print(f"[WARN] Image not found: {src}")

        body_parts.append(QUESTION_BLOCK % {
            "id": idx,
            "question": escape_latex_math(item.get("question", "")),
            "A": escape_latex_math(item.get("options", {}).get("A", "")),
            "B": escape_latex_math(item.get("options", {}).get("B", "")),
            "C": escape_latex_math(item.get("options", {}).get("C", "")),
            "D": escape_latex_math(item.get("options", {}).get("D", "")),
            "answer": escape_latex_math(item.get("answer", "")),
            "explanation": escape_latex_math(item.get("explanation", "")),

            "image_block": image_block
        })

    latex_code = LATEX_TEMPLATE % {
        "title": title or "Questions",
        "body": "\n".join(body_parts)
    }

    tex_path = outdir / "questions.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    print(f"[OK] LaTeX file written to: {tex_path}")
    return tex_path


def compile_latex(tex_path: Path):
    """调用 XeLaTeX 编译 LaTeX 文件"""
    try:
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-output-directory", str(tex_path.parent), str(tex_path)],
            check=True
        )
        print(f"[OK] PDF generated at: {tex_path.with_suffix('.pdf')}")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] XeLaTeX compilation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert JSON questions to PDF via LaTeX")
    parser.add_argument("-i", "--input", required=True, help="Path to JSON input file")
    parser.add_argument("-o", "--outdir", default="output", help="Output directory")
    parser.add_argument("-t", "--title", default="Questions", help="Title of the PDF")
    parser.add_argument("--no-compile", action="store_true", help="Only generate .tex, do not compile PDF")

    args = parser.parse_args()
    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    tex_path = json_to_latex(input_path, outdir, args.title)

    if not args.no_compile:
        compile_latex(tex_path)


if __name__ == "__main__":
    main()
