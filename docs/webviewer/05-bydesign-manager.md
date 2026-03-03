# 05 - By Design 管理器 (bydesign_manager.py)

## 功能概述

出行检查清单模块，核心功能：
- 通用检查清单（每次出行都要做）
- 出行记录（单次出行）
- 检查清单模板（可复用）
- 进度追踪

**文件**: `/root/.openclaw/workspace/bydesign_manager.py`
**行数**: 320 行
**数据存储**: JSON 文件

---

## 数据模型

### 1. 通用检查清单 (checklist.json)
```json
{
  "items": [
    {
      "id": "uuid",
      "text": "关闭所有窗户",
      "completed": false,
      "created_at": 1234567890
    }
  ]
}
```

### 2. 出行记录 (trips.json)
```json
{
  "trips": [
    {
      "id": "uuid",
      "name": "上海出差 3 天",
      "description": "业务会议",
      "created_at": 1234567890,
      "status": "planning",  // planning, ongoing, completed
      "checklist_snapshot": [...],  // 创建时的检查清单快照
      "custom_items": [...],        // 自定义物品/事项
      "completed_at": 1234567890
    }
  ]
}
```

### 3. 检查清单模板 (templates.json)
```json
{
  "templates": [
    {
      "id": "uuid",
      "name": "出差模板",
      "category": "商务",
      "items": [{"text": "带笔记本电脑"}, ...],
      "created_at": 1234567890
    }
  ]
}
```

---

## 数据存储

### 文件路径
```
/root/.openclaw/workspace/webviewer/data/bydesign/
├── checklist.json    # 通用检查清单
├── trips.json        # 出行记录
└── templates.json    # 模板
```

---

## API 接口

### ByDesignManager 类

#### Checklist 管理

| 方法 | 说明 |
|------|------|
| `get_checklist()` | 获取检查清单 |
| `add_checklist_item(text)` | 添加检查项（自动去重） |
| `add_checklist_items_batch(texts, skip_duplicates)` | 批量添加 |
| `update_checklist_item(item_id, updates)` | 更新检查项 |
| `delete_checklist_item(item_id)` | 删除检查项 |
| `reset_checklist()` | 重置所有项为未完成 |

#### Trip 管理

| 方法 | 说明 |
|------|------|
| `create_trip(name, description)` | 创建出行记录 |
| `get_all_trips()` | 获取所有出行 |
| `get_trip(trip_id)` | 获取单个出行 |
| `add_custom_item(trip_id, text)` | 添加自定义物品 |
| `update_trip_item(trip_id, item_id, updates, is_custom)` | 更新项目 |
| `delete_trip(trip_id)` | 删除出行记录 |
| `complete_trip(trip_id)` | 标记出行为完成 |
| `get_trip_progress(trip_id)` | 获取进度 |

#### 模板管理

| 方法 | 说明 |
|------|------|
| `get_templates()` | 获取所有模板 |
| `create_template(name, items, category)` | 创建模板（自动去重） |
| `delete_template(template_id)` | 删除模板 |
| `import_template_to_trip(trip_id, template_id)` | 导入模板到出行 |

---

## 核心功能

### 1. 通用检查清单

每次创建出行时，自动复制通用检查清单到出行的 `checklist_snapshot`：

```python
def _snapshot_checklist(self):
    """创建检查清单快照"""
    return [
        {"id": i["id"], "text": i["text"], "completed": False}
        for i in self.checklist["items"]
    ]
```

**默认检查项**:
- 关闭所有窗户
- 关闭所有电器电源
- 检查门锁
- 清空垃圾
- 检查水龙头

### 2. 自动去重

添加检查项时自动检测重复：

```python
def _normalize_text(self, text):
    """标准化文本（用于去重比较）"""
    return text.strip().lower()

def _is_duplicate(self, items, text):
    """检查是否重复"""
    normalized = self._normalize_text(text)
    return any(self._normalize_text(item["text"]) == normalized for item in items)
```

### 3. 进度追踪

```python
def get_trip_progress(self, trip_id):
    """获取出行进度"""
    checklist_total = len(trip["checklist_snapshot"])
    checklist_done = sum(1 for i in trip["checklist_snapshot"] if i["completed"])
    custom_total = len(trip["custom_items"])
    custom_done = sum(1 for i in trip["custom_items"] if i["completed"])
    
    return {
        "checklist": {"total": checklist_total, "done": checklist_done},
        "custom": {"total": custom_total, "done": custom_done},
        "overall": {
            "total": total,
            "done": done,
            "percent": round(done/total*100) if total > 0 else 0
        }
    }
```

### 4. 模板导入

导入模板时自动去重（不添加已存在的项）：

```python
def import_template_to_trip(self, trip_id, template_id):
    # 1. 收集现有项的文本
    existing_texts = set()
    for item in trip["checklist_snapshot"]:
        existing_texts.add(self._normalize_text(item["text"]))
    
    # 2. 导入模板项（跳过重复）
    for item_text in template["items"]:
        if normalized not in existing_texts:
            # 添加到 custom_items
            existing_texts.add(normalized)
```

---

## 使用示例

### 创建出行
```python
from bydesign_manager import manager

trip = manager.create_trip("上海出差 3 天", "业务会议")
print(f"创建成功，ID: {trip['id']}")
# 自动包含通用检查清单
```

### 添加自定义物品
```python
item = manager.add_custom_item(trip['id'], "带名片")
```

### 完成检查项
```python
manager.update_trip_item(
    trip_id=trip['id'],
    item_id=item['id'],
    updates={"completed": True},
    is_custom=True
)
```

### 查看进度
```python
progress = manager.get_trip_progress(trip['id'])
print(f"总体进度：{progress['overall']['percent']}%")
print(f"检查清单：{progress['checklist']['done']}/{progress['checklist']['total']}")
print(f"自定义：{progress['custom']['done']}/{progress['custom']['total']}")
```

### 创建模板
```python
template = manager.create_template(
    name="出差模板",
    category="商务",
    items=[
        {"text": "带笔记本电脑"},
        {"text": "带充电器"},
        {"text": "带名片"}
    ]
)
```

### 导入模板到出行
```python
result = manager.import_template_to_trip(trip['id'], template['id'])
print(f"导入了 {result['imported']} 项，跳过了 {result['skipped']} 项重复")
```

---

## 与服务器集成

### API 端点
```python
# server.py 中的路由
GET  /bydesign/api/checklist         # 获取检查清单
GET  /bydesign/api/trips             # 获取所有出行
GET  /bydesign/api/trips/{id}        # 获取单个出行
GET  /bydesign/api/stats             # 获取统计
POST /bydesign/api/trips             # 创建出行
POST /bydesign/api/checklist/items   # 添加检查项
PUT  /bydesign/api/checklist/items/{id}  # 更新检查项
DELETE /bydesign/api/checklist/items/{id}  # 删除检查项
```

---

## 数据流

### 创建出行流程
```
用户创建出行
    ↓
ByDesignManager.create_trip()
    ↓
生成 UUID
    ↓
创建 trip 对象
    ↓
_snapshot_checklist() - 复制通用清单
    ↓
保存到 trips.json
    ↓
返回 trip 对象
```

### 导入模板流程
```
用户导入模板
    ↓
ByDesignManager.import_template_to_trip()
    ↓
查找模板
    ↓
收集现有项文本（去重）
    ↓
遍历模板项
    ↓
如果未重复 → 添加到 custom_items
    ↓
保存到 trips.json
    ↓
返回导入结果
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `bydesign_manager.py` | 管理器主文件 |
| `www/bydesign/index.html` | Web 界面 |
| `webviewer/data/bydesign/checklist.json` | 通用检查清单 |
| `webviewer/data/bydesign/trips.json` | 出行记录 |
| `webviewer/data/bydesign/templates.json` | 模板 |

---

## 设计亮点

### 1. 快照机制
每次创建出行时复制检查清单快照，后续修改通用清单不影响已创建的出行。

### 2. 智能去重
所有添加操作都支持自动去重（基于文本内容，忽略大小写和空格）。

### 3. 进度可视化
提供检查清单、自定义项、总体三个维度的进度统计。

### 4. 模板复用
支持创建和导入模板，提高重复出行的效率。

---

## 常见问题

### Q: 如何重置检查清单？
A: 使用 `reset_checklist()` 方法，将所有项标记为未完成。

### Q: 删除出行会删除什么？
A: 只删除 trips.json 中的出行记录，不影响通用检查清单和模板。

### Q: 模板导入后还能修改吗？
A: 导入的项成为 custom_items，可以独立修改，不影响原模板。

### Q: 如何备份数据？
A: 备份 `webviewer/data/bydesign/` 目录下的三个 JSON 文件。

---

*最后更新：2026-03-02*
