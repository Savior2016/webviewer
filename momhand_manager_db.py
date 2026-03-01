#!/usr/bin/env python3
"""
Momhand 物品管理器 - SQLite 数据库版本
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_FILE = Path("/root/.openclaw/workspace/webviewer/data/momhand.db")

def get_db():
    """获取数据库连接"""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT DEFAULT '其他',
            photo TEXT,
            usage TEXT,
            purchase_date TEXT,
            price REAL,
            production_date TEXT,
            expiry_date TEXT,
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_name ON items(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_type ON items(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_location ON items(location)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_expiry ON items(expiry_date)')
    
    conn.commit()
    conn.close()
    print("✅ Momhand 数据库初始化完成")

class MomhandManager:
    def __init__(self):
        init_db()
    
    def get_all_items(self):
        """获取所有物品"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items ORDER BY created_at DESC')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def add_item(self, item_data):
        """添加物品"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO items (name, type, photo, usage, purchase_date, price, 
                             production_date, expiry_date, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_data.get('name', '未知'),
            item_data.get('type', '其他'),
            item_data.get('photo'),
            item_data.get('usage', ''),
            item_data.get('purchase_date'),
            item_data.get('price'),
            item_data.get('production_date'),
            item_data.get('expiry_date'),
            item_data.get('location', '')
        ))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return self.get_item_by_id(item_id)
    
    def get_item_by_id(self, item_id):
        """根据 ID 获取物品"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def delete_item(self, item_id):
        """删除物品"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        deleted = cursor.fetchone()
        
        if deleted:
            cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
            conn.commit()
            conn.close()
            return {"success": True, "deleted": dict(deleted)}
        
        conn.close()
        return {"success": False, "error": "物品不存在"}
    
    def search_items(self, keyword):
        """搜索物品"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM items 
            WHERE name LIKE ? OR type LIKE ? OR usage LIKE ? OR location LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def get_statistics(self):
        """获取统计信息"""
        conn = get_db()
        cursor = conn.cursor()
        
        # 总数
        cursor.execute('SELECT COUNT(*) as count FROM items')
        total = cursor.fetchone()['count']
        
        # 即将过期（7 天内）
        cursor.execute('''
            SELECT COUNT(*) as count FROM items 
            WHERE expiry_date IS NOT NULL 
            AND date(expiry_date) BETWEEN date('now') AND date('now', '+7 days')
        ''')
        expiring_soon = cursor.fetchone()['count']
        
        # 已过期
        cursor.execute('''
            SELECT COUNT(*) as count FROM items 
            WHERE expiry_date IS NOT NULL 
            AND date(expiry_date) < date('now')
        ''')
        expired = cursor.fetchone()['count']
        
        # 按位置统计
        cursor.execute('SELECT location, COUNT(*) as count FROM items GROUP BY location')
        by_location = {row['location']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total": total,
            "expiring_soon": expiring_soon,
            "expired": expired,
            "by_location": by_location
        }
    
    def update_location(self, item_id, new_location):
        """更新物品位置"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE items 
            SET location = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_location, item_id))
        
        conn.commit()
        conn.close()
        return self.get_item_by_id(item_id)
    
    def update_item(self, item_id, updates):
        """更新物品信息"""
        conn = get_db()
        cursor = conn.cursor()
        
        # 构建动态更新语句
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key in ['name', 'type', 'photo', 'usage', 'purchase_date', 'price', 'production_date', 'expiry_date', 'location']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            conn.close()
            return None
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        
        sql = f'''
            UPDATE items 
            SET {', '.join(set_clauses)}
            WHERE id = ?
        '''
        values.append(item_id)
        
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
        
        return self.get_item_by_id(item_id)

# 全局实例
manager = MomhandManager()

if __name__ == "__main__":
    # 测试
    init_db()
    print("数据库已初始化")
    
    # 添加测试物品
    test_item = {
        "name": "测试物品",
        "type": "测试",
        "location": "测试位置",
        "usage": "用于测试"
    }
    result = manager.add_item(test_item)
    print(f"添加物品：{result}")
    
    # 获取所有物品
    items = manager.get_all_items()
    print(f"物品总数：{len(items)}")
