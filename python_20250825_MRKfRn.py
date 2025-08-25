def generate_html(data):
    html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content极速pdf="width=device-width, initial-scale=1.0">
    <title>物理题目集</title>
    <style>
        body {{
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            margin: 20px;
            background-color: #f9f9f9;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30极速pdfpx;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .question {{
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fff;
        }}
        .question-number {{
            font-size: 18px;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 15px;
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        .info-table th, .info-table td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        .info-table th {{
            background-color: #f2f2f2;
            font-weight: bold;
            width: 100px;
        }}
        .section-title {{
            font-weight: bold;
            color: #2c3e50;
            margin: 15px 0 8px 0;
        }}
        .options {{
            margin-left: 20px;
        }}
        .option {{
            margin: 5px 0;
        }}
        .answer {{
            font-weight: bold;
            color: #27ae60;
            font-size: 16px;
            margin-top: 15px;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        }}
        .divider {{
            height: 2px;
            background: linear-gradient(to right, transparent, #3498db, transparent);
            margin: 30px 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .formula {{
            display: block;
            margin: 10px 0;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>物理题目集</h1>
        {questions}
    </div>
</body>
</html>'''

    question_template = '''
        <div class="question">
            <div class="question-number">题目 {number}</div>
            
            <table class="info-table">
                <tr><th>题目类型</th><td>{q_type}</td></tr>
                <tr><th>试卷类型</th><td>{paper_type}</td></tr>
                <tr><极速pdfth>难度</th><td>{difficulty}</td></tr>
                <tr><th>年份</th><td>{year}</td></tr>
                <tr><th>标签</th><td>{tags}</td></tr>
                <tr><th>来源</th><td>{source}</td></tr>
            </table>
            
            <div class="section-title">题目:</div>
            <div>{question_content}</div>
            
            <div class="section-title">选项:</div>
            <div class="options">{options}</div>
            
            <div class="section-title">解题思路:</div>
            <div>{solution}</div>
            
            <div class="answer">答案: {answer}</div>
        </div>
        {divider}'''

    import re
    
    def clean_html_keep_images(text):
        """清理HTML标签但保留图片标签"""
        if not text:
            return ""
        
        # 先提取图片标签
        img_pattern = r'<img[^>]+>'
        images = re.findall(img_pattern, text)
        
        # 移除所有HTML标签
        clean_pattern = re.compile('<.*?>')
        clean_text = re.sub(clean_pattern, '', text)
        
        # 将图片重新插入到文本中
        result = clean_text
        for img in images:
            # 在图片位置插入标记
            result = result.replace('', f'<div class="formula">{img}</div>', 1)
        
        return result
    
    def clean_html(text):
        """完全清理HTML标签"""
        if not text:
            return ""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    questions_html = ""
    for i, item in enumerate(data):
        # 确保所有必要键都存在
        item.setdefault("答案", "")
        item.setdefault("解题思路", "")
        item.setdefault("选项", "")
        item.setdefault("题目", "")
        
        # 清理题目内容（完全清理）
        question_content = clean_html(item["题目"])
        options_content = ""
        
        # 处理选项（完全清理）
        options = item["选项"].split('、<p>')
        for opt in options:
            if opt.strip():
                clean_opt = clean_html(opt)
                options_content += f'<div class="option">{clean_opt}</div>'
        
        # 处理解题思路（保留图片）
        solution = clean_html_keep_images(item["解题思路"])
        
        questions_html += question_template.format(
            number=i+1,
            q_type=item.get("题目类型", ""),
            paper_type=item.get("试卷类型", ""),
            difficulty=item.get("难度", ""),
            year=item.get("年份", "未指定"),
            tags=item.get("标签", "无"),
            source=item.get("来源极速pdf", "未指定"),
            question_content=question_content,
            options=options_content,
            solution=solution,
            answer=item["答案"],
            divider='<div class="divider"></div>' if i < len(data)-1 else ''
        )
    
    return html_template.format(questions=questions_html)

# 使用您提供的原始数据
data = [
    {
        "题目类型": "单选",
        "试卷类型": "Mechanics",
        "难度": "适中",
        "年份": "",
        "题目": "<p class=\"MsoBodyText\"><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">A ball decelerates uniformly from +28.0m/s to +14.0m/s in 0.002s , then accelerates back to +20.0m/s in 0.003s . </span></p><p class=\"MsoBodyText\"><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">What is the total displacement during contact? </span></p>",
        "标签": "",
        "来源": "",
        "简介": "",
        "图片": "",
        "视频": "",
        "选项": "A、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">0.042m</span></p>B、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">0.056m</span></p>C、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">0.070极速pdfm</span></p>D、极速pdf<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">0.084m</span></p>E、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16极速pdfpx;\">0.093m</span></p>",
        "解题思路": "<p class=\"MsoBodyText\"><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">Stage 1: <img src=\"https://xinghuan-website.oss-cn-shanghai.aliyuncs.com/uploadfiles/web/2025/05-24/sd13eq5qcpthcwyi.png\" width=\"219\" height=\"38\">. Stage 2: <img src=\"https://xinghuan-website.oss-cn-shanghai.aliyuncs.com/uploadfiles/web/2025/05-24/61aegfcw7ayxzmj2.png\" width=\"210\" height=\"38\">. Total <img src=\"https://xinghuan-website.oss-cn-shanghai.aliyuncs.com/uploadfiles/web/2025/05-24/zpjzgamjdnpzfaur.png\" width=\"93\" height=\"25\">. </span></p>",
        "答案": "E"
    },
    {
        "题目类型": "单选",
        "试卷类型": "Mechanics",
        "难度": "较易",
        "年份": "",
        "题目": "<p class=\"MsoBodyText\"><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">A ball（v=12.0m/s) compresses a racket string by 0.02m before rebounding at 10.0m/s. </span></p><p class=\"MsoBodyText\"><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">What is the peak deceleration? </span></p>",
        "标签": "",
        "来源": "",
        "简介": "",
        "图片": "",
        "视频": "",
        "选项": "A、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">-1100m/s<sup>2</sup></span></p>B、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">-2200m/s<sup>2</sup></span></p>C、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">-3600m/s<sup>2</sup></span></p>D、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">-4400m/s<sup>2</sup></span></p>E、<p><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">-5500m/s<sup>2</sup></span></p>",
        "解题思路": "<p class=\"MsoNormal\"><span style=\"font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px;\">Energy loss implies non-constant force, but assuming average deceleration:<img src=\"https://xinghuan-website.oss-cn-shanghai.aliyuncs.com/uploadfiles/web/2025/05-24/a9g6uqlfvvjp3zyd.png\" width=\"436\" height=\"29\"></span></p>",
        "答案": "C"
    }
]

# 生成HTML并保存
html_content = generate_html(data)
with open("physics_questions.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML文件已成功生成: physics_questions.html")
print("图片现在应该能够正常显示了！")