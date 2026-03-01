#!/usr/bin/env python3
"""
Siri 的梦 - 消息管理器
接收外部消息，转发给 Agent Dummy 处理，保存历史记录
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
import uuid

DATA_DIR = Path("/root/.openclaw/workspace/data/siri-dream")
MESSAGES_FILE = DATA_DIR / "messages.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# 确保数据目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 默认提示词
DEFAULT_SYSTEM_PROMPT = """你是 WebViewer 的助手 Dummy，负责处理用户的各种请求。

用户消息："{message}"

请：
1. 理解用户的意图
2. 提供有帮助的回复
3. 只返回纯文本回复，不要返回 JSON

示例回复：
- "收到你的消息了"
- "我已经理解了你的需求"
- "这是一个测试消息"

注意：不要返回 JSON 格式，只返回简单的中文回复。"""


def load_messages():
    """加载历史消息"""
    if MESSAGES_FILE.exists():
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_messages(messages):
    """保存历史消息"""
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def add_message(message_text, source='api', metadata=None):
    """添加新消息"""
    messages = load_messages()
    
    new_message = {
        'id': str(uuid.uuid4()),
        'text': message_text,
        'source': source,  # 'api' 或 'web'
        'timestamp': int(time.time()),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending',  # pending, processing, completed, failed
        'result': None,
        'metadata': metadata or {}
    }
    
    messages.insert(0, new_message)  # 新消息在最前面
    
    # 只保留最近 100 条
    if len(messages) > 100:
        messages = messages[:100]
    
    save_messages(messages)
    return new_message


def update_message_status(message_id, status, result=None):
    """更新消息处理状态"""
    messages = load_messages()
    
    for msg in messages:
        if msg['id'] == message_id:
            msg['status'] = status
            if result:
                msg['result'] = result
            break
    
    save_messages(messages)


def get_messages(limit=50, offset=0):
    """获取消息列表"""
    messages = load_messages()
    return messages[offset:offset+limit]


def get_message(message_id):
    """获取单条消息"""
    messages = load_messages()
    for msg in messages:
        if msg['id'] == message_id:
            return msg
    return None


def delete_message(message_id):
    """删除消息"""
    messages = load_messages()
    messages = [m for m in messages if m['id'] != message_id]
    save_messages(messages)
    return True


def clear_messages():
    """清空所有消息"""
    save_messages([])
    return True


def get_statistics():
    """获取统计信息"""
    messages = load_messages()
    total = len(messages)
    pending = len([m for m in messages if m['status'] == 'pending'])
    completed = len([m for m in messages if m['status'] == 'completed'])
    failed = len([m for m in messages if m['status'] == 'failed'])
    
    return {
        'total': total,
        'pending': pending,
        'completed': completed,
        'failed': failed,
        'today': len([m for m in messages if datetime.fromtimestamp(m['timestamp']).date() == datetime.now().date()])
    }


# 设置管理
def load_settings():
    """加载设置"""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'system_prompt': DEFAULT_SYSTEM_PROMPT}


def save_settings(settings):
    """保存设置"""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    return True


def get_system_prompt():
    """获取系统提示词"""
    settings = load_settings()
    return settings.get('system_prompt', DEFAULT_SYSTEM_PROMPT)


def save_system_prompt(prompt):
    """保存系统提示词"""
    settings = load_settings()
    settings['system_prompt'] = prompt
    return save_settings(settings)


# 全局实例
manager = {
    'load_messages': load_messages,
    'save_messages': save_messages,
    'add_message': add_message,
    'update_message_status': update_message_status,
    'get_messages': get_messages,
    'get_message': get_message,
    'delete_message': delete_message,
    'clear_messages': clear_messages,
    'get_statistics': get_statistics,
    'load_settings': load_settings,
    'save_settings': save_settings,
    'get_system_prompt': get_system_prompt,
    'save_system_prompt': save_system_prompt,
    'DEFAULT_SYSTEM_PROMPT': DEFAULT_SYSTEM_PROMPT
}
