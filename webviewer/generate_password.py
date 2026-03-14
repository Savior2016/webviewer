#!/usr/bin/env python3
"""
密码哈希生成工具
用于生成 config.json 中使用的密码哈希
"""

import hashlib
import json
import sys

def generate_hash(password):
    """生成 SHA-256 密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def update_config(username, password_hash):
    """更新 config.json 中的管理员配置"""
    config_file = '/root/.openclaw/workspace/webviewer/config.json'
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        config = {}
    
    config['admin'] = {
        'username': username,
        'password_hash': password_hash
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {config_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法：python3 generate_password.py <用户名> <密码>")
        print("示例：python3 generate_password.py yangjiukui mypassword123")
        print()
        print("或者直接生成哈希：")
        print("python3 generate_password.py --hash mypassword123")
        sys.exit(1)
    
    if sys.argv[1] == '--hash':
        password = sys.argv[2]
        hash_value = generate_hash(password)
        print(f"密码哈希：{hash_value}")
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        hash_value = generate_hash(password)
        print(f"用户名：{username}")
        print(f"密码哈希：{hash_value}")
        
        confirm = input("\n是否更新 config.json？(y/n): ")
        if confirm.lower() == 'y':
            update_config(username, hash_value)
            print("✅ 配置已更新，请重启服务生效")
        else:
            print("❌ 已取消")
