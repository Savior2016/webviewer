#!/usr/bin/env python3
"""
Cherry Pick - 一搬不丢
搬家物品追踪管理器
"""

import json
import logging
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path("/root/.openclaw/workspace/data/cherry-pick")
DB_FILE = DATA_DIR / "moves.json"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 线程安全锁
_lock = threading.Lock()

class CherryPickManager:
    def __init__(self):
        self.data = self._load_data()

    def _load_data(self):
        """加载数据"""
        if DB_FILE.exists():
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"moves": [], "items": []}

    def _save_data(self):
        """保存数据"""
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def create_move(self, name, description=""):
        """创建搬家活动"""
        with _lock:
            move_id = str(uuid.uuid4())
            move = {
                "id": move_id,
                "name": name,
                "description": description,
                "created_at": int(time.time()),
                "status": "active"
            }
            self.data["moves"].append(move)
            self._save_data()
            return move

    def get_all_moves(self):
        """获取所有搬家活动"""
        return sorted(self.data["moves"], key=lambda x: x["created_at"], reverse=True)

    def get_move(self, move_id):
        """获取单个搬家活动"""
        for move in self.data["moves"]:
            if move["id"] == move_id:
                return move
        return None

    def delete_move(self, move_id):
        """删除搬家活动及其物品"""
        with _lock:
            self.data["moves"] = [m for m in self.data["moves"] if m["id"] != move_id]
            self.data["items"] = [i for i in self.data["items"] if i["move_id"] != move_id]
            self._save_data()
            return True

    def add_item(self, move_id, name, before_location="", pack_location="", after_location=""):
        """添加物品"""
        with _lock:
            move = self.get_move(move_id)
            if not move:
                return None

            item_id = str(uuid.uuid4())
            item = {
                "id": item_id,
                "move_id": move_id,
                "name": name,
                "before_location": before_location or "",
                "pack_location": pack_location or "",
                "after_location": after_location or "",
                "synced_to_momhand": False,
                "created_at": int(time.time()),
                "updated_at": int(time.time())
            }
            self.data["items"].append(item)
            self._save_data()

            logger.info(f"添加物品：{item['name']}, before={item['before_location']}, pack={item['pack_location']}, after={item['after_location']}")

            # 检查是否需要同步到 momhand
            if after_location and after_location != "未指定" and after_location != "":
                self._sync_to_momhand(item)
                self._save_data()

            return item

    def get_items(self, move_id):
        """获取搬家活动的物品列表"""
        items = [i for i in self.data["items"] if i["move_id"] == move_id]
        return sorted(items, key=lambda x: x["created_at"], reverse=True)

    def update_item(self, item_id, updates):
        """更新物品"""
        with _lock:
            logger.debug(f"更新物品 {item_id}: {updates}")

            for item in self.data["items"]:
                if item["id"] == item_id:
                    was_synced = bool(item.get("after_location") and item["after_location"] != "未指定" and item["after_location"] != "")

                    for key, value in updates.items():
                        if key in ["name", "before_location", "pack_location", "after_location"]:
                            item[key] = value if value is not None else ''

                    # 检查是否需要同步到 momhand
                    is_synced = bool(item.get("after_location") and item["after_location"] != "未指定" and item["after_location"] != "")
                    if is_synced and not was_synced:
                        logger.info(f"同步到 Momhand: {item['after_location']}")
                        self._sync_to_momhand(item)
                        item["synced_to_momhand"] = True

                    item["updated_at"] = int(time.time())
                    self._save_data()
                    return item

            logger.debug(f"物品未找到: {item_id}")
            return None

    def delete_item(self, item_id):
        """删除物品"""
        with _lock:
            self.data["items"] = [i for i in self.data["items"] if i["id"] != item_id]
            self._save_data()
            return True

    def _sync_to_momhand(self, item):
        """同步物品到 momhand (通过 SQLite API)"""
        try:
            from momhand_manager_db import manager as momhand_mgr
            momhand_data = {
                'name': item['name'],
                'location': item['after_location'],
                'type': '搬家物品',
                'usage': f"来源: cherry-pick, 搬家活动: {item['move_id']}"
            }

            if item.get('momhand_item_id'):
                momhand_mgr.update_item(item['momhand_item_id'], momhand_data)
            else:
                created = momhand_mgr.add_item(momhand_data)
                if created:
                    item['momhand_item_id'] = created['id']
                    item['synced_to_momhand'] = True

            logger.info(f"物品 \"{item['name']}\" 已同步到 momhand")
        except Exception as e:
            logger.warning(f"同步到 momhand 失败：{e}")

# 全局实例
manager = CherryPickManager()
