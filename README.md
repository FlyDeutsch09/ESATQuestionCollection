# ESATQuestionCollection

*A toolchain for converting Excel-based question banks into JSON, LaTeX, and finally a printable PDF booklet.*

一个将 Excel 题库转换为 JSON、LaTeX 并最终生成可打印 PDF 练习册的工具链。

---

## 📖 Overview | 概述

This project provides a pipeline that transforms Excel files (`.xlsx`) containing practice questions into a structured JSON format, then into LaTeX (`.tex`), and finally compiles them into a **questions booklet PDF**.

本项目实现了一个处理流程：将 Excel (`.xlsx`) 格式的练习题数据转换为 JSON，再生成 LaTeX (`.tex`) 文件，最后编译为 **题册 PDF**。

**Pipeline | 转换流程**

```
Excel (.xlsx) → JSON (.json) → LaTeX (.tex) → PDF (.pdf)
```

---

## 📂 Repository Structure | 仓库结构

- `PracticeQuestions.xlsx`, `Questionbank.xlsx` → Example input Excel files  
- `excel_to_pdf_fixed.py` → Converts `.xlsx` into JSON  
- `json2pdf.py` → Converts JSON into LaTeX and PDF  
- `pictures_downloaded.py` (branch) → Downloads and renames required images  
- `your_questions.json` → JSON output containing questions, options, and explanations  
- `output/` → Contains LaTeX source code (`questions.tex`) and processed images  
- `questions.pdf` → Final generated booklet PDF  

---

## ⚙️ Prerequisites | 使用前准备

- [MiKTeX](https://miktex.org/) (or another LaTeX distribution with `pdflatex`)  
- Python 3.x  
- Python libraries:  
  - `pandas`  
  - `PyPDF2`  

---

## 🚀 Installation & Usage | 安装与使用

1. **Clone repository | 克隆仓库**
   ```bash
   git clone https://github.com/FlyDeutsch09/ESATQuestionCollection.git
   cd ESATQuestionCollection
   ```

2. **Download pictures from branch | 从分支下载图片**
   - Switch to the `pictures_downloaded.py` branch to fetch and rename images.  
   - Ensure processed images are placed under `output/` for LaTeX compilation.  

3. **Run conversion scripts | 运行转换脚本**
   ```bash
   # Step 1: Convert Excel to JSON
   python excel_to_pdf_fixed.py

   # Step 2: Convert JSON to LaTeX & PDF
   python json2pdf.py
   ```

4. **Locate output | 查看输出**
   - `questions.pdf` → located at the root of the project  
   - `output/` → contains `questions.tex` and images  

---

## 📑 Input Format | 输入格式

- **Excel input** must contain:  
  - Questions  
  - Multiple-choice options  
  - Explanations  

- **Math symbols** are inserted as images and referenced using relative positions in JSON.  

- **JSON output** (`your_questions.json`) includes:  
  ```json
  {
    "question": "Sample Question?",
    "options": ["A", "B", "C", "D"],
    "answer": "B",
    "explanation": "Explanation text here",
    "symbols": ["symbol1.png", "symbol2.png"]
  }
  ```

---

## 📘 Customization | 自定义

- The LaTeX template (`output/questions.tex`) can be modified for styling, fonts, or formatting.  
- You may edit question numbering or adjust image scaling directly in LaTeX.  

---

## 📝 Example Workflow | 示例流程

1. Edit `PracticeQuestions.xlsx` with your questions.  
2. Run conversion scripts.  
3. Open `questions.pdf` to view the formatted practice booklet.  

1. 在 `PracticeQuestions.xlsx` 中填写题目。  
2. 运行转换脚本。  
3. 打开 `questions.pdf` 查看排版好的练习册。  

---

## 📄 License | 许可

This project is distributed under the MIT License.  
本项目基于 MIT 许可协议发布。  

---
