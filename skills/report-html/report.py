#!/usr/bin/env python3
"""
report.py - HTML 报告生成器（时尚 UI 版）
生成报告并部署到 WebViewer 服务
"""

import os
import re
from datetime import datetime
from pathlib import Path

REPORTS_DIR = "/root/.openclaw/workspace/webviewer/www/reports"
INDEX_FILE = os.path.join(REPORTS_DIR, "index.html")

def ensure_reports_dir():
    """确保 reports 目录存在"""
    Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)

def generate_report_html(title, content, author="Friday", tags=None, summary=None):
    """生成单份报告的 HTML（时尚 UI）"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.html"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    tags_html = ""
    if tags:
        tags_items = "".join([f'<span class="tag">#{tag}</span>' for tag in tags])
        tags_html = f'<div class="tags">{tags_items}</div>'
    
    summary_html = f'<div class="summary">{summary}</div>' if summary else ""
    
    date_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #ec4899;
            --accent: #06b6d4;
            --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --card-bg: rgba(255, 255, 255, 0.95);
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --border: rgba(99, 102, 241, 0.2);
            --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.7;
            color: var(--text-primary);
            background: var(--bg-gradient);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 50px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        header {{
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 2px solid var(--border);
        }}
        
        .badge {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 15px;
        }}
        
        h1 {{
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-dark), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.3;
        }}
        
        .meta {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 14px;
        }}
        
        .meta-item svg {{
            width: 18px;
            height: 18px;
            opacity: 0.7;
        }}
        
        .summary {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(236, 72, 153, 0.1));
            border-left: 4px solid var(--primary);
            padding: 20px 25px;
            border-radius: 12px;
            margin: 30px 0;
            font-size: 15px;
            color: var(--text-primary);
        }}
        
        .content {{
            font-size: 16px;
        }}
        
        .content h2 {{
            font-size: 22px;
            font-weight: 600;
            color: var(--text-primary);
            margin: 35px 0 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border);
        }}
        
        .content h3 {{
            font-size: 18px;
            font-weight: 600;
            color: var(--primary-dark);
            margin: 25px 0 12px;
        }}
        
        .content p {{
            margin: 15px 0;
            color: var(--text-secondary);
        }}
        
        .content ul, .content ol {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        
        .content li {{
            margin: 10px 0;
            color: var(--text-secondary);
        }}
        
        .content code {{
            background: rgba(99, 102, 241, 0.1);
            padding: 3px 8px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            font-size: 14px;
            color: var(--primary-dark);
        }}
        
        .content pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 12px;
            overflow-x: auto;
            margin: 25px 0;
        }}
        
        .content pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}
        
        .content blockquote {{
            border-left: 4px solid var(--primary);
            padding-left: 20px;
            margin: 25px 0;
            color: var(--text-secondary);
            font-style: italic;
            background: rgba(99, 102, 241, 0.05);
            padding: 15px 20px;
            border-radius: 8px;
        }}
        
        .tags {{
            margin-top: 35px;
            padding-top: 25px;
            border-top: 1px solid var(--border);
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .tag {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(236, 72, 153, 0.15));
            color: var(--primary-dark);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .tag:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}
        
        footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid var(--border);
            text-align: center;
        }}
        
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .footer-text {{
            color: var(--text-secondary);
            font-size: 13px;
        }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            padding: 10px 20px;
            border-radius: 10px;
            background: rgba(99, 102, 241, 0.1);
            transition: all 0.2s;
        }}
        
        .back-link:hover {{
            background: rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 30px 20px;
            }}
            h1 {{
                font-size: 24px;
            }}
            .meta {{
                flex-direction: column;
                gap: 10px;
            }}
            .footer-content {{
                flex-direction: column;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <span class="badge">Daily Report</span>
            <h1>{title}</h1>
            <div class="meta">
                <div class="meta-item">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    <span>{date_str}</span>
                </div>
                <div class="meta-item">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                    <span>{author}</span>
                </div>
            </div>
            {summary_html}
        </header>
        <main class="content">
            {content}
        </main>
        {tags_html}
        <footer>
            <div class="footer-content">
                <div class="footer-text">Generated by Friday 🤖</div>
                <a href="index.html" class="back-link">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                    返回报告列表
                </a>
            </div>
        </footer>
    </div>
</body>
</html>'''
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    return filename, filepath

def update_index():
    """更新报告索引页（时尚 UI）"""
    ensure_reports_dir()
    
    reports = []
    for f in os.listdir(REPORTS_DIR):
        if f.startswith("report_") and f.endswith(".html"):
            filepath = os.path.join(REPORTS_DIR, f)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
                    match = re.search(r'<title>(.*?)</title>', content)
                    title = match.group(1) if match else f
                    match = re.search(r'<span>{date_str}</span>'.replace('{date_str}', r'(.*?)</span>'), content)
                    time = match.group(1) if match else "未知"
                reports.append({"file": f, "title": title, "time": time})
            except:
                reports.append({"file": f, "title": f, "time": "未知"})
    
    reports.sort(key=lambda x: x["time"], reverse=True)
    
    reports_html = ""
    if reports:
        for i, r in enumerate(reports):
            reports_html += f'''
            <li class="report-item" style="animation-delay: {i * 0.1}s">
                <a href="{r['file']}">
                    <div class="report-title">{r['title']}</div>
                    <div class="report-time">📅 {r['time']}</div>
                </a>
            </li>'''
        reports_html = f'<ul class="report-list">{reports_html}</ul>'
    else:
        reports_html = '<div class="empty">暂无报告</div>'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>报告中心 | Report Hub</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #ec4899;
            --accent: #06b6d4;
            --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --card-bg: rgba(255, 255, 255, 0.95);
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-gradient);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 50px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        header {{
            text-align: center;
            margin-bottom: 50px;
        }}
        
        .badge {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
        }}
        
        h1 {{
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-dark), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: var(--text-secondary);
            font-size: 16px;
        }}
        
        .report-list {{
            list-style: none;
        }}
        
        .report-item {{
            background: rgba(255, 255, 255, 0.8);
            border-radius: 16px;
            margin-bottom: 15px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(99, 102, 241, 0.1);
            animation: slideIn 0.5s ease-out backwards;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        .report-item:hover {{
            transform: translateX(10px) scale(1.02);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
            border-color: var(--primary);
        }}
        
        .report-item a {{
            display: block;
            padding: 25px;
            text-decoration: none;
        }}
        
        .report-title {{
            color: var(--text-primary);
            font-weight: 600;
            font-size: 18px;
            margin-bottom: 8px;
        }}
        
        .report-time {{
            color: var(--text-secondary);
            font-size: 14px;
        }}
        
        .empty {{
            text-align: center;
            color: var(--text-secondary);
            padding: 60px 20px;
            font-size: 16px;
        }}
        
        footer {{
            margin-top: 50px;
            text-align: center;
            color: var(--text-secondary);
            font-size: 13px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 30px 20px;
            }}
            h1 {{
                font-size: 28px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <span class="badge">Report Hub</span>
            <h1>📊 报告中心</h1>
            <p class="subtitle">AI 前沿信息 · 每日更新</p>
        </header>
        <main>
            {reports_html}
        </main>
        <footer>
            <p>Powered by Friday 🤖</p>
        </footer>
    </div>
</body>
</html>'''
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

def create_report(title, content, tags=None, summary=None):
    """创建报告并更新索引"""
    ensure_reports_dir()
    filename, filepath = generate_report_html(title, content, tags=tags, summary=summary)
    update_index()
    return f"/reports/{filename}"

if __name__ == "__main__":
    url = create_report(
        title="测试报告",
        content="<p>这是一份测试报告的内容。</p>",
        tags=["测试", "示例"],
        summary="这是报告的摘要信息，会显示在标题下方。"
    )
    print(f"报告已生成：{url}")
