#!/usr/bin/env python3
"""
AI Agent 领域搜索与总结工具
搜索最新发展、论文、科普文章，并生成总结报告
"""

import sys
import json
import subprocess
from datetime import datetime

def run_search(query, num_results=15):
    """执行搜索"""
    cmd = [
        "python3",
        "/root/.openclaw/workspace/tools/search.py",
        query,
        "-n", str(num_results),
        "-f", "json",
        "-e", "duckduckgo,baidu"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        print(f"搜索错误：{result.stderr}", file=sys.stderr)
        return []
    
    try:
        return json.loads(result.stdout)
    except:
        return []

def generate_summary(results):
    """生成总结报告（原始数据格式，供 AI 进一步处理）"""
    if not results:
        return json.dumps({"error": "未搜索到相关内容", "results": []}, ensure_ascii=False)
    
    # 输出原始搜索结果，供 AI 总结
    output = {
        "search_time": datetime.now().isoformat(),
        "total_results": len(results),
        "results": results
    }
    
    return json.dumps(output, ensure_ascii=False, indent=2)

def main():
    # 默认搜索词
    queries = [
        "AI agent 2026 最新发展 趋势",
        "autonomous agent research paper 2026",
        "AI agent framework tools 2026",
        "multi-agent system breakthrough",
        "AI agent 科普 教程"
    ]
    
    all_results = []
    
    print("[开始搜索 AI Agent 最新信息...]", file=sys.stderr)
    
    for query in queries:
        print(f"[搜索] {query}", file=sys.stderr)
        results = run_search(query, num_results=8)
        all_results.extend(results)
    
    # 去重
    seen = set()
    unique = []
    for r in all_results:
        key = r.get('url', '')
        if key and key not in seen:
            seen.add(key)
            unique.append(r)
    
    # 生成总结
    summary = generate_summary(unique)
    print(summary)

if __name__ == '__main__':
    main()
