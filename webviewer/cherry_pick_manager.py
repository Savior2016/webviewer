#!/usr/bin/env python3
"""
Cherry Pick - 一搬不丢
搬家物品追踪管理器
"""

import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/root/.openclaw/workspace/webviewer/data/cherry-pick")
DB_FILE = DATA_DIR / "moves.json"
MOMHAND_FILE = Path("/root/.openclaw/workspace/momhand/data/items.json")

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

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
        self.data["moves"] = [m for m in self.data["moves"] if m["id"] != move_id]
        self.data["items"] = [i for i in self.data["items"] if i["move_id"] != move_id]
        self._save_data()
        return True
    
    def add_item(self, move_id, name, before_location="", pack_location="", after_location=""):
        """添加物品"""
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
        
        print(f"✅ 添加物品：{item['name']}, before={item['before_location']}, pack={item['pack_location']}, after={item['after_location']}")
        
        # 检查是否需要同步到 momhand
        if after_location and after_location != "未指定" and after_location != "":
            self._sync_to_momhand(item)
        
        return item
    
    def get_items(self, move_id):
        """获取搬家活动的物品列表"""
        items = [i for i in self.data["items"] if i["move_id"] == move_id]
        return sorted(items, key=lambda x: x["created_at"], reverse=True)
    
    def update_item(self, item_id, updates):
        """更新物品"""
        print(f"📝 更新物品 {item_id}: {updates}")
        
        for item in self.data["items"]:
            if item["id"] == item_id:
                was_synced = bool(item.get("after_location") and item["after_location"] != "未指定" and item["after_location"] != "")
                
                for key, value in updates.items():
                    if key in ["name", "before_location", "pack_location", "after_location"]:
                        old_value = item.get(key, '')
                        item[key] = value if value is not None else ''
                        print(f"   {key}: '{old_value}' -> '{item[key]}'")
                
                # 检查是否需要同步到 momhand
                is_synced = bool(item.get("after_location") and item["after_location"] != "未指定" and item["after_location"] != "")
                if is_synced and not was_synced:
                    print(f"   🔄 同步到 Momhand: {item['after_location']}")
                    self._sync_to_momhand(item)
                    item["synced_to_momhand"] = True
                
                item["updated_at"] = int(time.time())
                self._save_data()
                print(f"   ✅ 保存成功")
                return item
        
        print(f"   ❌ 物品未找到")
        return None
    
    def delete_item(self, item_id):
        """删除物品"""
        self.data["items"] = [i for i in self.data["items"] if i["id"] != item_id]
        self._save_data()
        return True
    
    def _sync_to_momhand(self, item):
        """同步物品到 momhand"""
        try:
            items = []
            if MOMHAND_FILE.exists():
                with open(MOMHAND_FILE, 'r', encoding='utf-8') as f:
                    items = json.load(f)
            
            # 查找是否已存在
            existing_idx = None
            for idx, i in enumerate(items):
                if i.get("id") == item["id"]:
                    existing_idx = idx
                    break
            
            momhand_item = {
                "id": item["id"],
                "name": item["name"],
                "location": item["after_location"],
                "category": "搬家物品",
                "source": "cherry-pick",
                "moveId": item["move_id"],
                "createdAt": item["created_at"] * 1000,
                "updatedAt": int(time.time() * 1000)
            }
            
            if existing_idx is not None:
                items[existing_idx].update(momhand_item)
            else:
                items.append(momhand_item)
            
            MOMHAND_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MOMHAND_FILE, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 物品 \"{item['name']}\" 已同步到 momhand")
        except Exception as e:
            print(f"同步到 momhand 失败：{e}")

# 全局实例
manager = CherryPickManager()
