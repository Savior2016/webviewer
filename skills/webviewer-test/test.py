#!/usr/bin/env python3
"""
WebViewer 项目自动化测试与优化脚本
每次代码修改后自动执行全面测试
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# 配置
BASE_DIR = Path("/root/.openclaw/workspace")
WWW_DIR = BASE_DIR / "www"
DATA_DIR = BASE_DIR / "data"
SERVER_URL = "https://localhost"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "PASS": Colors.GREEN,
        "FAIL": Colors.RED,
        "WARN": Colors.YELLOW,
        "INFO": Colors.BLUE,
        "TEST": Colors.BOLD
    }
    color = colors.get(level, "")
    print(f"{color}[{timestamp}] [{level}] {message}{Colors.END}")

def test_module_pages():
    """1. 测试模块页面层级"""
    log("开始测试模块页面层级...", "TEST")
    
    pages = {
        "主页": WWW_DIR / "index.html",
        "By Design": WWW_DIR / "bydesign" / "index.html",
        "Cherry Pick": WWW_DIR / "cherry-pick" / "index.html",
        "Momhand": WWW_DIR / "momhand" / "index.html",
        "Siri Dream": WWW_DIR / "siri-dream" / "index.html"
    }
    
    results = []
    for name, path in pages.items():
        if path.exists():
            # 检查文件结构
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查必要元素
            checks = {
                "DOCTYPE": "<!DOCTYPE html>" in content,
                "HTML 标签": "<html" in content,
                "HEAD 标签": "<head>" in content,
                "BODY 标签": "<body" in content,
                "Tailwind CSS": "tailwindcss" in content,
                "标题": "<title>" in content
            }
            
            failed = [k for k, v in checks.items() if not v]
            if failed:
                log(f"{name}: 缺少 {', '.join(failed)}", "FAIL")
                results.append((name, False, failed))
            else:
                log(f"{name}: ✅ 页面结构完整", "PASS")
                results.append((name, True, []))
        else:
            log(f"{name}: ❌ 文件不存在", "FAIL")
            results.append((name, False, ["文件不存在"]))
    
    return results

def test_data_storage():
    """2. 测试数据存储"""
    log("开始测试数据存储...", "TEST")
    
    storage_files = {
        "By Design - Checklist": DATA_DIR / "bydesign" / "checklist.json",
        "By Design - Trips": DATA_DIR / "bydesign" / "trips.json",
        "By Design - Templates": DATA_DIR / "bydesign" / "templates.json",
        "Cherry Pick - Moves": DATA_DIR / "cherry-pick" / "moves.json",
        "Siri Dream - Messages": DATA_DIR / "siri-dream" / "messages.json",
        "Siri Dream - Settings": DATA_DIR / "siri-dream" / "settings.json"
    }
    
    results = []
    for name, path in storage_files.items():
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                log(f"{name}: ✅ JSON 格式有效", "PASS")
                results.append((name, True, None))
            except json.JSONDecodeError as e:
                log(f"{name}: ❌ JSON 格式错误 - {e}", "FAIL")
                results.append((name, False, str(e)))
        else:
            log(f"{name}: ⚠️ 文件不存在（可能首次使用）", "WARN")
            results.append((name, None, "文件不存在"))
    
    # 检查 Momhand SQLite 数据库
    momhand_db = BASE_DIR / "webviewer" / "data" / "momhand.db"
    if momhand_db.exists():
        log(f"Momhand - Database: ✅ 数据库存在", "PASS")
        results.append(("Momhand - Database", True, None))
    else:
        log(f"Momhand - Database: ⚠️ 数据库不存在（可能首次使用）", "WARN")
        results.append(("Momhand - Database", None, "数据库不存在"))
    
    return results

def test_module_prompts():
    """3. 测试模块提示词存储"""
    log("开始测试模块提示词存储...", "TEST")
    
    # 检查每个模块是否有独立的提示词配置
    modules = {
        "By Design": BASE_DIR / "www" / "bydesign",
        "Cherry Pick": BASE_DIR / "www" / "cherry-pick",
        "Momhand": BASE_DIR / "www" / "momhand",
        "Siri Dream": BASE_DIR / "www" / "siri-dream"
    }
    
    results = []
    for name, path in modules.items():
        # 检查模块目录中的设置
        settings_file = path / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'system_prompt' in data:
                    log(f"{name}: ✅ 提示词独立存储", "PASS")
                    results.append((name, True, None))
                else:
                    log(f"{name}: ⚠️ 设置文件存在但无提示词", "WARN")
                    results.append((name, None, "无提示词字段"))
            except:
                log(f"{name}: ❌ 设置文件读取失败", "FAIL")
                results.append((name, False, "读取失败"))
        else:
            log(f"{name}: ⚠️ 使用全局提示词配置", "WARN")
            results.append((name, None, "使用全局配置"))
    
    # Siri Dream 提示词（已实现独立存储）
    siri_settings = DATA_DIR / "siri-dream" / "settings.json"
    if siri_settings.exists():
        with open(siri_settings, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'system_prompt' in data:
            log(f"Siri Dream (全局): ✅ 提示词已配置", "PASS")
            results.append(("Siri Dream (全局)", True, None))
    
    return results

def test_api_endpoints():
    """7. 测试 API 接口"""
    log("开始测试 API 接口...", "TEST")
    
    endpoints = {
        "GET /api/settings": ("GET", f"{SERVER_URL}/api/settings"),
        "GET /api/logs": ("GET", f"{SERVER_URL}/api/logs?lines=5"),
        "GET /momhand/api/items": ("GET", f"{SERVER_URL}/momhand/api/items"),
        "GET /momhand/api/stats": ("GET", f"{SERVER_URL}/momhand/api/stats"),
        "GET /cherry-pick/api/moves": ("GET", f"{SERVER_URL}/cherry-pick/api/moves"),
        "GET /bydesign/api/checklist": ("GET", f"{SERVER_URL}/bydesign/api/checklist"),
        "GET /bydesign/api/trips": ("GET", f"{SERVER_URL}/bydesign/api/trips"),
        "GET /siri-dream/api/messages": ("GET", f"{SERVER_URL}/siri-dream/api/messages?limit=10"),
        "GET /siri-dream/api/stats": ("GET", f"{SERVER_URL}/siri-dream/api/stats"),
    }
    
    results = []
    for name, (method, url) in endpoints.items():
        try:
            if method == "GET":
                response = requests.get(url, verify=False, timeout=5)
            
            if response.status_code == 200:
                log(f"{name}: ✅ {response.status_code}", "PASS")
                results.append((name, True, response.status_code))
            else:
                log(f"{name}: ❌ {response.status_code}", "FAIL")
                results.append((name, False, response.status_code))
        except Exception as e:
            log(f"{name}: ❌ {str(e)}", "FAIL")
            results.append((name, False, str(e)))
    
    return results

def test_server_status():
    """测试服务器状态"""
    log("测试服务器状态...", "TEST")
    
    try:
        response = requests.get(SERVER_URL, verify=False, timeout=5)
        if response.status_code == 200:
            log(f"服务器：✅ 正常运行 ({response.status_code})", "PASS")
            return True
        else:
            log(f"服务器：❌ 异常状态 ({response.status_code})", "FAIL")
            return False
    except Exception as e:
        log(f"服务器：❌ 无法连接 - {e}", "FAIL")
        return False

def generate_report(results_dict):
    """生成测试报告"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}WebViewer 测试报告{Colors.END}")
    print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_warnings = 0
    
    for category, results in results_dict.items():
        print(f"\n{Colors.BOLD}{category}{Colors.END}")
        print("-" * 40)
        
        passed = sum(1 for _, status, _ in results if status is True)
        failed = sum(1 for _, status, _ in results if status is False)
        warnings = sum(1 for _, status, _ in results if status is None)
        
        total_tests += len(results)
        total_passed += passed
        total_failed += failed
        total_warnings += warnings
        
        for name, status, detail in results:
            icon = "✅" if status is True else "❌" if status is False else "⚠️"
            print(f"  {icon} {name}")
            if detail and status is False:
                print(f"     └─ {detail}")
        
        print(f"\n小计：{Colors.GREEN}{passed} 通过{Colors.END} / {Colors.RED}{failed} 失败{Colors.END} / {Colors.YELLOW}{warnings} 警告{Colors.END}")
    
    print("\n" + "="*60)
    print(f"{Colors.BOLD}总计{Colors.END}: {total_tests} 测试 / {Colors.GREEN}{total_passed} 通过{Colors.END} / {Colors.RED}{total_failed} 失败{Colors.END} / {Colors.YELLOW}{total_warnings} 警告{Colors.END}")
    
    if total_failed == 0:
        print(f"\n{Colors.GREEN}🎉 所有测试通过！{Colors.END}")
    else:
        print(f"\n{Colors.RED}⚠️  有 {total_failed} 项测试失败，请检查修复{Colors.END}")
    
    print("="*60)

def main():
    """主测试流程"""
    print(f"\n{Colors.BOLD}🚀 WebViewer 自动化测试{Colors.END}")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # 1. 测试服务器状态
    server_ok = test_server_status()
    
    # 2. 测试模块页面
    results["1. 模块页面"] = test_module_pages()
    
    # 3. 测试数据存储
    results["2. 数据存储"] = test_data_storage()
    
    # 4. 测试模块提示词
    results["3. 模块提示词"] = test_module_prompts()
    
    # 5. 测试 API 接口（如果服务器运行）
    if server_ok:
        results["4. API 接口"] = test_api_endpoints()
    else:
        log("服务器未运行，跳过 API 测试", "WARN")
        results["4. API 接口"] = [("API 测试", None, "服务器未运行")]
    
    # 生成报告
    generate_report(results)
    
    # 返回退出码
    failed_count = sum(
        sum(1 for _, status, _ in results if status is False)
        for results in results.values()
    )
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
