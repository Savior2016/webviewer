# 04 - Cherry Pick 管理器 (cherry_pick_manager.py)

## 功能概述

搬家物品追踪模块，核心功能：
- 创建搬家活动（Moves）
- 记录物品位置变化（原位置 → 打包位置 → 新位置）
- 自动同步到 Momhand

**文件**: `/root/.openclaw/workspace/cherry_pick_manager.py`
**行数**: 178 行
**数据存储**: JSON 文件

---

## 数据模型

### Move（搬家活动）
```json
{
  "id": "uuid",
  "name": "搬家活动名称",
  "description": "描述",
  "created_at": 1234567890,
  "status": "active"
}
```

### Item（物品）
```json
{
  "id": "uuid",
  "move_id": "所属搬家活动 ID",
  "name": "物品名称",
  "before_location": "原位置",
  "pack_location": "打包位置",
  "after_location": "新位置",
  "synced_to_momhand": false,
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

---

## 数据存储

### 文件路径
```
/root/.openclaw/workspace/webviewer/data/cherry-pick/moves.json
```

### 文件结构
```json
{
  "moves": [...],
  "items": [...]
}
```

---

## API 接口

### CherryPickManager 类

#### 1. 创建搬家活动
```python
def create_move(self, name: str, description: str = "") -> dict
```

#### 2. 获取所有搬家活动
```python
def get_all_moves(self) -> List[dict]
# 返回：按创建时间倒序
```

#### 3. 获取单个搬家活动
```python
def get_move(self, move_id: str) -> dict | None
```

#### 4. 删除搬家活动
```python
def delete_move(self, move_id: str) -> bool
# 同时删除该活动下的所有物品
```

#### 5. 添加物品
```python
def add_item(
    self,
    move_id: str,
    name: str,
    before_location: str = "",
    pack_location: str = "",
    after_location: str = ""
) -> dict
# 如果 after_location 不为空，自动同步到 Momhand
```

#### 6. 获取物品列表
```python
def get_items(self, move_id: str) -> List[dict]
```

#### 7. 更新物品
```python
def update_item(self, item_id: str, updates: dict) -> dict
# 如果 after_location 从空变为非空，触发同步到 Momhand
```

#### 8. 删除物品
```python
def delete_item(self, item_id: str) -> bool
```

---

## 核心功能

### 1. 物品位置追踪

支持三个阶段的位置记录：
- **before_location**: 搬家前的位置（如：旧家客厅）
- **pack_location**: 打包位置（如：3 号纸箱）
- **after_location**: 搬家后的位置（如：新家卧室）

### 2. 自动同步到 Momhand

当物品的 `after_location` 被设置且不为 "未指定" 时：

```python
def _sync_to_momhand(self, item):
    # 1. 读取 momhand/data/items.json
    # 2. 按 ID 查找是否已存在
    # 3. 如果存在 → 更新位置
    # 4. 如果不存在 → 添加新物品
    # 5. 标记 synced_to_momhand = True
```

**同步触发时机**:
- 添加物品时 `after_location` 不为空
- 更新物品时 `after_location` 从空变为非空

### 3. 更新日志

```python
def update_item(self, item_id, updates):
    print(f"📝 更新物品 {item_id}: {updates}")
    # 打印每个字段的变化
    print(f"   {key}: '{old_value}' -> '{item[key]}'")
    # 打印同步状态
    print(f"   🔄 同步到 Momhand: {item['after_location']}")
    print(f"   ✅ 保存成功")
```

---

## 使用示例

### 创建搬家活动
```python
from cherry_pick_manager import manager

move = manager.create_move("从北京搬到上海", "2026 年春节搬家")
print(f"创建成功，ID: {move['id']}")
```

### 添加物品
```python
item = manager.add_item(
    move_id=move['id'],
    name="相机",
    before_location="旧家客厅电视柜",
    pack_location="3 号纸箱",
    after_location="新家书房书架"
)
# 自动同步到 Momhand
```

### 更新物品位置
```python
updated = manager.update_item(item_id, {
    "after_location": "新家卧室床头柜"
})
# 如果之前 after_location 为空，会触发同步
```

### 查看搬家进度
```python
moves = manager.get_all_moves()
for move in moves:
    items = manager.get_items(move['id'])
    print(f"{move['name']}: {len(items)} 个物品")
```

---

## 与服务器集成

### API 端点
```python
# server.py 中的路由
GET  /cherry-pick/api/moves              # 获取所有搬家活动
GET  /cherry-pick/api/moves/{id}/items   # 获取物品列表
POST /cherry-pick/api/moves              # 创建搬家活动
POST /cherry-pick/api/moves/{id}/items   # 添加物品
PUT  /cherry-pick/api/items/{id}         # 更新物品
DELETE /cherry-pick/api/items/{id}       # 删除物品
```

### 处理函数
```python
def handle_cherry_pick_api(self, path, query):
    manager = get_cherry_pick_manager()
    # 根据路径调用不同方法

def handle_cherry_pick_post(self, data, path):
    # 处理 POST 请求
```

---

## 数据流

### 添加物品流程
```
用户添加物品
    ↓
CherryPickManager.add_item()
    ↓
保存到 moves.json
    ↓
检查 after_location 是否为空
    ↓
如果不为空 → _sync_to_momhand()
    ↓
读取 momhand/data/items.json
    ↓
查找/更新/添加
    ↓
保存
```

### 更新物品流程
```
用户更新物品
    ↓
CherryPickManager.update_item()
    ↓
记录旧值 → 新值
    ↓
检查 after_location 变化
    ↓
如果从空→非空 → _sync_to_momhand()
    ↓
保存到 moves.json
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `cherry_pick_manager.py` | 管理器主文件 |
| `www/cherry-pick/index.html` | Web 界面 |
| `webviewer/data/cherry-pick/moves.json` | 数据存储 |
| `momhand/data/items.json` | 同步目标 |

---

## 设计亮点

### 1. 简单数据结构
- 纯 JSON 文件，无需数据库
- 易于备份和迁移
- 手动可读可编辑

### 2. 智能同步
- 只在 `after_location` 确定后同步
- 避免同步未完成的数据
- 自动去重（按 ID）

### 3. 详细日志
- 每次更新都打印变化
- 便于调试和追踪
- 同步状态可见

---

## 常见问题

### Q: 数据文件在哪里？
A: `/root/.openclaw/workspace/webviewer/data/cherry-pick/moves.json`

### Q: 如何备份数据？
A: 
```bash
cp /root/.openclaw/workspace/webviewer/data/cherry-pick/moves.json backup.json
```

### Q: 同步失败怎么办？
A: 检查日志中的 `同步到 momhand 失败` 错误，通常是文件权限问题

### Q: 可以删除已同步的物品吗？
A: 可以，但 Momhand 中不会自动删除（需要手动清理）

---

*最后更新：2026-03-02*
