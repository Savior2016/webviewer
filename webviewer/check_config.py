#!/usr/bin/env python3
"""
WebViewer 配置检查工具
"""

import os
import sys
import socket
from pathlib import Path

def check_config():
    print("🔍 WebViewer 配置检查")
    print("=" * 50)
    
    issues = []
    warnings = []
    
    # 检查 SSL 证书
    cert_file = Path('/root/.openclaw/workspace/webviewer/data/server.crt')
    key_file = Path('/root/.openclaw/workspace/webviewer/data/server.key')
    
    if cert_file.exists() and key_file.exists():
        print("✅ SSL 证书已生成")
    else:
        issues.append("SSL 证书未找到，运行 ./generate_ssl_cert.sh 生成")
    
    # 检查飞书配置
    feishu_vars = {
        'FEISHU_APP_ID': os.getenv('FEISHU_APP_ID'),
        'FEISHU_APP_SECRET': os.getenv('FEISHU_APP_SECRET'),
        'FEISHU_USER_OPEN_ID': os.getenv('FEISHU_USER_OPEN_ID')
    }
    
    for var, value in feishu_vars.items():
        if value:
            masked = value[:10] + '...' if len(value) > 10 else value
            print(f"✅ {var} = {masked}")
        else:
            issues.append(f"{var} 未设置")
    
    # 检查端口占用
    port = 8443
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            print(f"✅ 端口 {port} 可用")
    except OSError:
        warnings.append(f"端口 {port} 可能被占用")
    
    # 检查数据目录
    data_dir = Path('/root/.openclaw/workspace/webviewer/data')
    if data_dir.exists():
        print(f"✅ 数据目录存在：{data_dir}")
        files = list(data_dir.glob('*'))
        print(f"   文件数：{len(files)}")
    else:
        warnings.append("数据目录不存在，将在首次运行时创建")
    
    # 检查 Python 版本
    print(f"✅ Python 版本：{sys.version.split()[0]}")
    
    print("")
    print("=" * 50)
    
    if issues:
        print("❌ 需要修复的问题:")
        for issue in issues:
            print(f"   • {issue}")
        print("")
        return False
    
    if warnings:
        print("⚠️  警告:")
        for warning in warnings:
            print(f"   • {warning}")
        print("")
    
    print("✅ 配置检查通过！可以启动服务")
    print("")
    print("启动命令：./start-with-approval.sh")
    
    return True

if __name__ == '__main__':
    success = check_config()
    sys.exit(0 if success else 1)
