#!/usr/bin/env python3
"""
By Design - 已读不回
出远门前的检查清单管理器
"""

import json
import time
import uuid
from pathlib import Path

DATA_DIR = Path("/root/.openclaw/workspace/data/bydesign")
CHECKLIST_FILE = DATA_DIR / "checklist.json"  # 通用检查清单（每次都要做的）
TRIPS_FILE = DATA_DIR / "trips.json"  # 出行记录（单次的）
TEMPLATES_FILE = DATA_DIR / "templates.json"  # 检查清单模板

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

class ByDesignManager:
    def __init__(self):
        self.checklist = self._load_checklist()
        self.trips = self._load_trips()
        self.templates = self._load_templates()
    
    def _load_checklist(self):
        """加载通用检查清单"""
        if CHECKLIST_FILE.exists():
            with open(CHECKLIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "items": [
                {"id": "1", "text": "关闭所有窗户", "completed": False},
                {"id": "2", "text": "关闭所有电器电源", "completed": False},
                {"id": "3", "text": "检查门锁", "completed": False},
                {"id": "4", "text": "清空垃圾", "completed": False},
                {"id": "5", "text": "检查水龙头", "completed": False}
            ]
        }
    
    def _save_checklist(self):
        """保存检查清单"""
        with open(CHECKLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.checklist, f, ensure_ascii=False, indent=2)
    
    def _load_trips(self):
        """加载出行记录"""
        if TRIPS_FILE.exists():
            with open(TRIPS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"trips": []}
    
    def _save_trips(self):
        """保存出行记录"""
        with open(TRIPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.trips, f, ensure_ascii=False, indent=2)
    
    def _load_templates(self):
        """加载检查清单模板"""
        if TEMPLATES_FILE.exists():
            with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"templates": []}
    
    def _save_templates(self):
        """保存检查清单模板"""
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)
    
    # ========== Checklist 管理 ==========
    def get_checklist(self):
        """获取检查清单"""
        return self.checklist["items"]
    
    def _normalize_text(self, text):
        """标准化文本（用于去重比较）"""
        return text.strip().lower()
    
    def _is_duplicate(self, items, text):
        """检查是否重复"""
        normalized = self._normalize_text(text)
        return any(self._normalize_text(item["text"]) == normalized for item in items)
    
    def add_checklist_item(self, text):
        """添加检查项（自动去重）"""
        if self._is_duplicate(self.checklist["items"], text):
            return None  # 重复项返回 None
        
        item = {
            "id": str(uuid.uuid4()),
            "text": text,
            "completed": False,
            "created_at": int(time.time())
        }
        self.checklist["items"].append(item)
        self._save_checklist()
        return item
    
    def add_checklist_items_batch(self, texts, skip_duplicates=True):
        """批量添加检查项（自动去重）"""
        added_items = []
        for text in texts:
            if skip_duplicates and self._is_duplicate(self.checklist["items"], text):
                continue  # 跳过重复项
            
            item = {
                "id": str(uuid.uuid4()),
                "text": text,
                "completed": False,
                "created_at": int(time.time())
            }
            self.checklist["items"].append(item)
            added_items.append(item)
        self._save_checklist()
        return added_items
    
    def update_checklist_item(self, item_id, updates):
        """更新检查项"""
        for item in self.checklist["items"]:
            if item["id"] == item_id:
                item.update(updates)
                self._save_checklist()
                return item
        return None
    
    def delete_checklist_item(self, item_id):
        """删除检查项"""
        self.checklist["items"] = [i for i in self.checklist["items"] if i["id"] != item_id]
        self._save_checklist()
        return True
    
    def reset_checklist(self):
        """重置所有检查项为未完成"""
        for item in self.checklist["items"]:
            item["completed"] = False
        self._save_checklist()
        return True
    
    # ========== Trip 管理 ==========
    def create_trip(self, name, description=""):
        """创建新的出行记录"""
        trip = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "created_at": int(time.time()),
            "status": "planning",  # planning, ongoing, completed
            "checklist_snapshot": self._snapshot_checklist(),
            "custom_items": []
        }
        self.trips["trips"].append(trip)
        self._save_trips()
        return trip
    
    def _snapshot_checklist(self):
        """创建检查清单快照"""
        return [{"id": i["id"], "text": i["text"], "completed": False} for i in self.checklist["items"]]
    
    def get_all_trips(self):
        """获取所有出行记录"""
        return sorted(self.trips["trips"], key=lambda x: x["created_at"], reverse=True)
    
    def get_trip(self, trip_id):
        """获取单个出行记录"""
        for trip in self.trips["trips"]:
            if trip["id"] == trip_id:
                return trip
        return None
    
    def add_custom_item(self, trip_id, text):
        """添加自定义物品/事项"""
        trip = self.get_trip(trip_id)
        if not trip:
            return None
        
        item = {
            "id": str(uuid.uuid4()),
            "text": text,
            "completed": False,
            "created_at": int(time.time())
        }
        trip["custom_items"].append(item)
        self._save_trips()
        return item
    
    def update_trip_item(self, trip_id, item_id, updates, is_custom=False):
        """更新出行中的项目"""
        trip = self.get_trip(trip_id)
        if not trip:
            return None
        
        items = trip["custom_items"] if is_custom else trip["checklist_snapshot"]
        for item in items:
            if item["id"] == item_id:
                item.update(updates)
                self._save_trips()
                return item
        return None
    
    def delete_trip(self, trip_id):
        """删除出行记录"""
        self.trips["trips"] = [t for t in self.trips["trips"] if t["id"] != trip_id]
        self._save_trips()
        return True
    
    def complete_trip(self, trip_id):
        """完成出行"""
        trip = self.get_trip(trip_id)
        if trip:
            trip["status"] = "completed"
            trip["completed_at"] = int(time.time())
            self._save_trips()
        return trip
    
    def get_trip_progress(self, trip_id):
        """获取出行进度"""
        trip = self.get_trip(trip_id)
        if not trip:
            return None
        
        checklist_total = len(trip["checklist_snapshot"])
        checklist_done = sum(1 for i in trip["checklist_snapshot"] if i["completed"])
        custom_total = len(trip["custom_items"])
        custom_done = sum(1 for i in trip["custom_items"] if i["completed"])
        
        total = checklist_total + custom_total
        done = checklist_done + custom_done
        
        return {
            "checklist": {"total": checklist_total, "done": checklist_done},
            "custom": {"total": custom_total, "done": custom_done},
            "overall": {"total": total, "done": done, "percent": round(done/total*100) if total > 0 else 0}
        }
    
    # ========== 模板管理 ==========
    def get_templates(self):
        """获取所有模板"""
        return self.templates.get("templates", [])
    
    def create_template(self, name, items, category=""):
        """创建检查清单模板（自动去重）"""
        # 去重处理
        unique_items = []
        seen_texts = set()
        for item in items:
            text = item["text"] if isinstance(item, dict) else item
            normalized = self._normalize_text(text)
            if normalized not in seen_texts:
                seen_texts.add(normalized)
                unique_items.append({"text": text})
        
        template = {
            "id": str(uuid.uuid4()),
            "name": name,
            "category": category,
            "items": unique_items,
            "created_at": int(time.time())
        }
        self.templates["templates"].append(template)
        self._save_templates()
        return template
    
    def delete_template(self, template_id):
        """删除模板"""
        self.templates["templates"] = [t for t in self.templates["templates"] if t["id"] != template_id]
        self._save_templates()
        return True
    
    def import_template_to_trip(self, trip_id, template_id):
        """导入模板到出行（添加到 custom_items，自动去重）"""
        trip = self.get_trip(trip_id)
        if not trip:
            return None
        
        template = None
        for t in self.templates["templates"]:
            if t["id"] == template_id:
                template = t
                break
        
        if not template:
            return None
        
        # 收集现有项的文本（用于去重）
        existing_texts = set()
        for item in trip.get("checklist_snapshot", []):
            existing_texts.add(self._normalize_text(item["text"]))
        for item in trip.get("custom_items", []):
            existing_texts.add(self._normalize_text(item["text"]))
        
        # 将模板项添加到出行的 custom_items（去重）
        imported_count = 0
        for item_text in template["items"]:
            text = item_text["text"] if isinstance(item_text, dict) else item_text
            normalized = self._normalize_text(text)
            
            # 检查是否已存在（包括通用清单和自定义项）
            if normalized in existing_texts:
                continue  # 跳过重复项
            
            existing_texts.add(normalized)
            custom_item = {
                "id": str(uuid.uuid4()),
                "text": text,
                "completed": False,
                "created_at": int(time.time()),
                "from_template": template["name"]
            }
            trip["custom_items"].append(custom_item)
            imported_count += 1
        
        self._save_trips()
        return {
            "imported": imported_count,
            "template_name": template["name"],
            "skipped": len(template["items"]) - imported_count
        }

# 全局实例
manager = ByDesignManager()
