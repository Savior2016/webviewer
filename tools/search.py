#!/usr/bin/env python3
"""
多搜索引擎搜索工具
支持：DuckDuckGo、Google（HTML）、百度（HTML）
无需 API Key，直接返回搜索结果
"""

import sys
import json
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote
import re
import time
import random

# User-Agent 池，模拟不同浏览器
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

def get_random_ua():
    return random.choice(USER_AGENTS)

def search_duckduckgo(query, num_results=10):
    """
    DuckDuckGo 搜索（无需 API Key）
    使用 HTML 接口
    """
    results = []
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        data = {"q": query, "kl": "zh-cn"}
        
        response = requests.post(url, headers=headers, data=data, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for result in soup.select('div.results_links')[:num_results]:
            title_elem = result.select_one('a.result__a')
            snippet_elem = result.select_one('div.snippet')
            url_elem = result.select_one('a.result__url')
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                # DuckDuckGo 的链接需要解码
                if url.startswith('/l/?kh=-1&uddg='):
                    from urllib.parse import unquote
                    url = unquote(url.replace('/l/?kh=-1&uddg=', ''))
                
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source": "DuckDuckGo"
                })
        
        time.sleep(1)  # 礼貌延迟
    except Exception as e:
        print(f"[DuckDuckGo 错误] {e}", file=sys.stderr)
    
    return results

def search_google(query, num_results=10):
    """
    Google 搜索（HTML 解析）
    注意：可能需要处理反爬
    """
    results = []
    try:
        url = f"https://www.google.com/search?q={quote(query)}&num={num_results}&hl=zh-CN"
        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Google 的搜索结果选择器（可能会变化）
        for result in soup.select('div.g')[:num_results]:
            title_elem = result.select_one('h3')
            snippet_elem = result.select_one('div.VwiC3b, div[data-sncf="1"], span.aCOpRe')
            url_elem = result.select_one('a')
            
            if title_elem and url_elem:
                title = title_elem.get_text(strip=True)
                url = url_elem.get('href', '')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                # 过滤掉非结果链接
                if url.startswith('/search?') or url.startswith('https://www.google.'):
                    continue
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source": "Google"
                })
        
        time.sleep(1)
    except Exception as e:
        print(f"[Google 错误] {e}", file=sys.stderr)
    
    return results

def search_baidu(query, num_results=10):
    """
    百度搜索（HTML 解析）
    """
    results = []
    try:
        url = f"https://www.baidu.com/s?wd={quote(query)}&rn={num_results}"
        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": "BAIDUID=1234567890:FG=1"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 百度搜索结果选择器
        for result in soup.select('div.result, div.c-container')[:num_results]:
            title_elem = result.select_one('h3 a, a.c-title')
            snippet_elem = result.select_one('div.c-abstract, span.c-abstract, div.abstract')
            url_elem = title_elem
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = url_elem.get('href', '') if url_elem else ""
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                # 过滤广告和非结果
                if 'baijiahao' in url or url.startswith('/'):
                    continue
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source": "Baidu"
                })
        
        time.sleep(1)
    except Exception as e:
        print(f"[Baidu 错误] {e}", file=sys.stderr)
    
    return results

def search(query, engines=None, num_results=10):
    """
    多引擎搜索
    
    Args:
        query: 搜索关键词
        engines: 引擎列表 ['duckduckgo', 'google', 'baidu']，默认全部
        num_results: 每个引擎的结果数
    
    Returns:
        搜索结果列表
    """
    if engines is None:
        engines = ['duckduckgo', 'google', 'baidu']
    
    all_results = []
    
    engine_map = {
        'duckduckgo': search_duckduckgo,
        'google': search_google,
        'baidu': search_baidu,
    }
    
    for engine in engines:
        if engine in engine_map:
            print(f"[搜索] {engine}: {query}", file=sys.stderr)
            results = engine_map[engine](query, num_results)
            all_results.extend(results)
    
    # 去重（按 URL）
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r['url'] not in seen_urls:
            seen_urls.add(r['url'])
            unique_results.append(r)
    
    return unique_results

def format_results(results, output_format='json'):
    """格式化输出"""
    if output_format == 'json':
        return json.dumps(results, ensure_ascii=False, indent=2)
    elif output_format == 'text':
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. [{r['source']}] {r['title']}")
            lines.append(f"   {r['url']}")
            lines.append(f"   {r['snippet'][:200]}...")
            lines.append("")
        return "\n".join(lines)
    elif output_format == 'markdown':
        lines = ["## 搜索结果\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"### {i}. {r['title']}")
            lines.append(f"- 来源：{r['source']}")
            lines.append(f"- 链接：<{r['url']}>")
            lines.append(f"- 摘要：{r['snippet'][:300]}")
            lines.append("")
        return "\n".join(lines)
    return json.dumps(results, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description='多搜索引擎搜索工具')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('-n', '--num', type=int, default=10, help='每个引擎的结果数')
    parser.add_argument('-e', '--engines', type=str, default='all', 
                        help='引擎列表，逗号分隔 (duckduckgo,google,baidu)，默认全部')
    parser.add_argument('-f', '--format', choices=['json', 'text', 'markdown'], 
                        default='json', help='输出格式')
    
    args = parser.parse_args()
    
    if args.engines == 'all':
        engines = None
    else:
        engines = [e.strip() for e in args.engines.split(',')]
    
    results = search(args.query, engines=engines, num_results=args.num)
    print(format_results(results, args.format))

if __name__ == '__main__':
    main()
