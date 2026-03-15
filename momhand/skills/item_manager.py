#!/usr/bin/env python3
"""
item_manager.py - momhand 物品管理核心技能
处理物品登记、查找、更新、删除等操作
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = "/root/.openclaw/workspace/momhand/data"
DB_FILE = os.path.join(DATA_DIR, "items.json")
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")

# 确保目录存在
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(PHOTOS_DIR).mkdir(parents=True, exist_ok=True)

class ItemManager:
    def __init__(self):
        self.items = self._load_items()
    
    def _load_items(self):
        """加载物品数据"""
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_items(self):
        """保存物品数据"""
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
    
    def add_item(self, item_data):
        """添加物品"""
        item = {
            "id": len(self.items) + 1,
            "name": item_data.get("name", "未知"),
            "type": item_data.get("type", "其他"),
            "photo": item_data.get("photo", None),
            "usage": item_data.get("usage", ""),
            "purchase_date": item_data.get("purchase_date", None),
            "price": item_data.get("price", None),
            "production_date": item_data.get("production_date", None),
            "expiry_date": item_data.get("expiry_date", None),
            "location": item_data.get("location", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.items.append(item)
        self._save_items()
        return item
    
    def search_items(self, keyword):
        """搜索物品"""
        results = []
        for item in self.items:
            if (keyword.lower() in item["name"].lower() or
                keyword.lower() in item.get("type", "其他").lower() or
                keyword.lower() in item.get("usage", "").lower()):
                results.append(item)
        return results
    
    def get_items_by_location(self, location):
        """按位置查找物品"""
        return [item for item in self.items if location.lower() in item["location"].lower()]
    
    def get_items_by_type(self, item_type):
        """按类型查找物品"""
        return [item for item in self.items if item_type.lower() in item["type"].lower()]
    
    def update_location(self, item_id, new_location):
        """更新物品位置"""
        for item in self.items:
            if item["id"] == item_id:
                item["location"] = new_location
                item["updated_at"] = datetime.now().isoformat()
                self._save_items()
                return item
        return None
    
    def delete_item(self, item_id):
        """删除物品"""
        for i, item in enumerate(self.items):
            if item["id"] == item_id:
                deleted = self.items.pop(i)
                self._save_items()
                return {"success": True, "deleted": deleted}
        return {"success": False, "error": "物品不存在"}
    
    def get_expiring_items(self, days=7):
        """获取即将过期的物品"""
        today = datetime.now()
        expiring = []
        for item in self.items:
            if item.get("expiry_date"):
                try:
                    expiry = datetime.fromisoformat(item["expiry_date"])
                    days_left = (expiry - today).days
                    if 0 <= days_left <= days:
                        item["days_left"] = days_left
                        expiring.append(item)
                except:
                    pass
        return expiring
    
    def get_expired_items(self):
        """获取已过期物品"""
        today = datetime.now()
        expired = []
        for item in self.items:
            if item.get("expiry_date"):
                try:
                    expiry = datetime.fromisoformat(item["expiry_date"])
                    if expiry < today:
                        item["days_expired"] = (today - expiry).days
                        expired.append(item)
                except:
                    pass
        return expired
    
    def recommend_items(self, need_description):
        """根据需求推荐物品"""
        # 简单关键词匹配推荐
        keywords = need_description.lower()
        recommendations = []
        for item in self.items:
            score = 0
            if item["name"].lower() in keywords or keywords in item["name"].lower():
                score += 3
            if item.get("usage", "").lower() in keywords or keywords in item.get("usage", "").lower():
                score += 2
            if item["type"].lower() in keywords:
                score += 1
            if score > 0:
                item["score"] = score
                recommendations.append(item)
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:5]
    
    def get_all_items(self):
        """获取所有物品"""
        return self.items
    
    def get_statistics(self):
        """获取统计信息"""
        total = len(self.items)
        by_type = {}
        by_location = {}
        for item in self.items:
            t = item["type"]
            l = item["location"]
            by_type[t] = by_type.get(t, 0) + 1
            by_location[l] = by_location.get(l, 0) + 1
        return {
            "total": total,
            "by_type": by_type,
            "by_location": by_location,
            "expiring_soon": len(self.get_expiring_items()),
            "expired": len(self.get_expired_items())
        }

# 全局实例
manager = ItemManager()

if __name__ == "__main__":
    # 测试
    print("物品管理器测试")
    print(f"当前物品数量：{len(manager.get_all_items())}")
    print(f"统计信息：{manager.get_statistics()}")
