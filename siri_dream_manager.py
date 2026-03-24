#!/usr/bin/env python3
"""
Siri 的梦 - 消息管理器
接收外部消息，转发给 Agent Dummy 处理，保存历史记录
"""

import json
import threading
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
DEFAULT_SYSTEM_PROMPT = """你是 WebViewer 的专业助手 Dummy。你擅长：理解用户的出行、搬家、物品管理需求

用户消息：
{message}

请根据以上提示词和用户消息进行处理：
1. 选取 webviewer 中合适的模块处理消息。
2. 进行实际的保存操作，不要只返回 JSON"""

# 线程安全锁
_lock = threading.Lock()


class SiriDreamManager:
    """Siri Dream 消息管理器"""

    def load_messages(self):
        """加载历史消息"""
        if MESSAGES_FILE.exists():
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_messages(self, messages):
        """保存历史消息"""
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    def add_message(self, message_text, source='api', metadata=None):
        """添加新消息"""
        with _lock:
            messages = self.load_messages()

            new_message = {
                'id': str(uuid.uuid4()),
                'text': message_text,
                'source': source,
                'timestamp': int(time.time()),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'pending',
                'result': None,
                'metadata': metadata or {}
            }

            messages.insert(0, new_message)

            # 只保留最近 100 条
            if len(messages) > 100:
                messages = messages[:100]

            self.save_messages(messages)
            return new_message

    def update_message_status(self, message_id, status, result=None):
        """更新消息处理状态"""
        with _lock:
            messages = self.load_messages()

            for msg in messages:
                if msg['id'] == message_id:
                    msg['status'] = status
                    if result:
                        msg['result'] = result
                    break

            self.save_messages(messages)

    def get_messages(self, limit=50, offset=0):
        """获取消息列表"""
        messages = self.load_messages()
        return messages[offset:offset+limit]

    def get_message(self, message_id):
        """获取单条消息"""
        messages = self.load_messages()
        for msg in messages:
            if msg['id'] == message_id:
                return msg
        return None

    def delete_message(self, message_id):
        """删除消息"""
        with _lock:
            messages = self.load_messages()
            messages = [m for m in messages if m['id'] != message_id]
            self.save_messages(messages)
            return True

    def clear_messages(self):
        """清空所有消息"""
        with _lock:
            self.save_messages([])
            return True

    def get_statistics(self):
        """获取统计信息"""
        messages = self.load_messages()
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

    def load_settings(self):
        """加载设置"""
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'system_prompt': DEFAULT_SYSTEM_PROMPT}

    def save_settings(self, settings):
        """保存设置"""
        with _lock:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True

    def get_system_prompt(self):
        """获取系统提示词"""
        settings = self.load_settings()
        return settings.get('system_prompt', DEFAULT_SYSTEM_PROMPT)

    def save_system_prompt(self, prompt):
        """保存系统提示词"""
        with _lock:
            settings = self.load_settings()
            settings['system_prompt'] = prompt
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True


# 全局实例
_manager_instance = SiriDreamManager()

# 模块级函数 (向后兼容，测试直接调用 sdm.add_message() 等)
load_messages = _manager_instance.load_messages
save_messages = _manager_instance.save_messages
add_message = _manager_instance.add_message
update_message_status = _manager_instance.update_message_status
get_messages = _manager_instance.get_messages
get_message = _manager_instance.get_message
delete_message = _manager_instance.delete_message
clear_messages = _manager_instance.clear_messages
get_statistics = _manager_instance.get_statistics
load_settings = _manager_instance.load_settings
save_settings = _manager_instance.save_settings
get_system_prompt = _manager_instance.get_system_prompt
save_system_prompt = _manager_instance.save_system_prompt


def process_via_openclaw_agent(message: str, module: str = 'siri_dream') -> dict:
    """通过 OpenClaw Agent 处理消息"""
    from openclaw_agent_processor import process_via_openclaw_agent as agent_process
    return agent_process(message, module)


# 全局 manager (向后兼容 server.py 的 manager['method']() 调用)
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
