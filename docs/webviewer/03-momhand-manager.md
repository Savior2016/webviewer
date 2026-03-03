# 03 - Momhand 管理器 (momhand_manager_db.py)

## 功能概述

物品管理模块 - SQLite 数据库版本，支持：
- 物品 CRUD 操作
- 搜索（名称、类型、用途、位置）
- 统计（总数、即将过期、已过期、按位置）
- 过期提醒

**文件**: `/root/.openclaw/workspace/momhand_manager_db.py`
**行数**: 237 行
**数据库**: `/root/.openclaw/workspace/webviewer/data/momhand.db`

---

## 数据库设计

### 表结构：`items`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER | 主键，自增 |
| `name` | TEXT | 物品名称 |
| `type` | TEXT | 类型（默认：其他） |
| `photo` | TEXT | 照片路径 |
| `usage` | TEXT | 用途说明 |
| `purchase_date` | TEXT | 购买日期 |
| `price` | REAL | 价格 |
| `production_date` | TEXT | 生产日期 |
| `expiry_date` | TEXT | 过期日期 |
| `location` | TEXT | 存放位置 |
| `created_at` | TEXT | 创建时间 |
| `updated_at` | TEXT | 更新时间 |

### 索引
```sql
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_location ON items(location);
CREATE INDEX idx_items_expiry ON items(expiry_date);
```

---

## API 接口

### MomhandManager 类

#### 1. 获取所有物品
```python
def get_all_items(self) -> List[dict]
# 返回：按创建时间倒序的所有物品
```

#### 2. 添加物品
```python
def add_item(self, item_data: dict) -> dict
# 参数：{"name", "type", "location", "usage", ...}
# 返回：新添加的物品（含 ID）
```

#### 3. 根据 ID 获取物品
```python
def get_item_by_id(self, item_id: int) -> dict | None
```

#### 4. 删除物品
```python
def delete_item(self, item_id: int) -> dict
# 返回：{"success": True, "deleted": {...}}
```

#### 5. 搜索物品
```python
def search_items(self, keyword: str) -> List[dict]
# 搜索范围：name, type, usage, location (LIKE 模糊匹配)
```

#### 6. 获取统计信息
```python
def get_statistics(self) -> dict
# 返回：
{
    "total": 总数，
    "expiring_soon": 7 天内过期数量，
    "expired": 已过期数量，
    "by_location": {"位置 A": 数量， "位置 B": 数量}
}
```

#### 7. 更新物品位置
```python
def update_location(self, item_id: int, new_location: str) -> dict
```

#### 8. 更新物品信息
```python
def update_item(self, item_id: int, updates: dict) -> dict
# 参数：{"name": "新名称", "location": "新位置", ...}
```

---

## 使用示例

### 初始化
```python
from momhand_manager_db import manager

# manager 是全局实例，自动初始化数据库
items = manager.get_all_items()
```

### 添加物品
```python
item = manager.add_item({
    "name": "感冒药",
    "type": "药品",
    "location": "卧室抽屉",
    "usage": "治疗感冒",
    "expiry_date": "2026-12-31"
})
print(f"添加成功，ID: {item['id']}")
```

### 搜索物品
```python
results = manager.search_items("感冒")
for item in results:
    print(f"{item['name']} - {item['location']}")
```

### 获取统计
```python
stats = manager.get_statistics()
print(f"总物品数：{stats['total']}")
print(f"即将过期：{stats['expiring_soon']}")
print(f"已过期：{stats['expired']}")
print(f"按位置：{stats['by_location']}")
```

### 更新位置
```python
updated = manager.update_location(item_id=5, new_location="客厅药箱")
```

---

## 与 Cherry Pick 集成

Cherry Pick 管理器在物品添加后自动同步到 Momhand：

```python
# cherry_pick_manager.py 中的 _sync_to_momhand 方法
def _sync_to_momhand(self, item):
    # 1. 读取 momhand/data/items.json
    # 2. 查找是否已存在（按 ID）
    # 3. 更新或添加
    # 4. 保存
```

**同步条件**: `after_location` 不为空且不为 "未指定"

---

## 数据文件

### 旧版本（JSON）
- 路径：`/root/.openclaw/workspace/momhand/data/items.json`
- 格式：数组
- 状态：已弃用（保留向后兼容）

### 新版本（SQLite）
- 路径：`/root/.openclaw/workspace/webviewer/data/momhand.db`
- 格式：SQLite 数据库
- 状态：当前使用

---

## 过期检测逻辑

```python
# 即将过期（7 天内）
SELECT COUNT(*) FROM items 
WHERE expiry_date IS NOT NULL 
AND date(expiry_date) BETWEEN date('now') AND date('now', '+7 days')

# 已过期
SELECT COUNT(*) FROM items 
WHERE expiry_date IS NOT NULL 
AND date(expiry_date) < date('now')
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `momhand_manager_db.py` | 管理器主文件 |
| `www/momhand/index.html` | Web 界面 |
| `webviewer/data/momhand.db` | SQLite 数据库 |
| `momhand/data/items.json` | 旧版 JSON 数据（兼容） |

---

## 与服务器集成

### API 端点
```python
# server.py 中的路由
GET  /momhand/api/items       # 获取所有物品
GET  /momhand/api/search?q=x  # 搜索物品
GET  /momhand/api/stats       # 获取统计
GET  /momhand/api/items/{id}  # 获取单个物品
POST /momhand/api/items       # 添加物品
```

### 处理函数
```python
def handle_momhand_api(self, path, query):
    manager = get_momhand_manager()
    # 根据路径调用不同方法
```

---

## 常见问题

### Q: 数据库在哪里？
A: `/root/.openclaw/workspace/webviewer/data/momhand.db`

### Q: 如何备份数据？
A: 
```bash
cp /root/.openclaw/workspace/webviewer/data/momhand.db backup.db
```

### Q: 搜索支持哪些字段？
A: name, type, usage, location（使用 LIKE 模糊匹配）

### Q: 过期检测基于什么时区？
A: SQLite 的 `date('now')` 使用服务器本地时间（UTC+8）

---

*最后更新：2026-03-02*
