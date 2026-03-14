#!/usr/bin/env python3
"""
生成报告列表 JSON 供 iOS App 调用
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_report_index():
    reports_dir = Path("/root/.openclaw/workspace/webviewer/www/reports")
    output_file = reports_dir / "index.json"
    
    reports = []
    
    # 扫描报告文件
    for file in sorted(reports_dir.glob("report_*.html")):
        filename = file.name
        # 从文件名解析日期 report_YYYYMMDD_HHMMSS.html
        try:
            date_str = filename.replace("report_", "").replace(".html", "")
            date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            title = f"📊 AI 前沿日报 · {date.strftime('%Y-%m-%d')}"
        except:
            date = datetime.fromtimestamp(file.stat().st_mtime)
            title = f"📊 报告 · {file.name}"
        
        # 构建 URL (需要替换为实际服务器地址)
        url = f"http://YOUR_SERVER_IP:PORT/webviewer/www/reports/{filename}"
        
        reports.append({
            "id": filename,
            "title": title,
            "filename": filename,
            "date": date.isoformat(),
            "url": url
        })
    
    # 按日期倒序排序
    reports.sort(key=lambda x: x["date"], reverse=True)
    
    # 生成 JSON
    output = {
        "reports": reports,
        "total": len(reports),
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成报告索引：{output_file}")
    print(f"   共 {len(reports)} 份报告")
    
    return output

if __name__ == "__main__":
    generate_report_index()
