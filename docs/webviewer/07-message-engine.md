# 07 - 消息引擎 (message_engine.py)

## 功能概述

本地消息处理引擎（不依赖 AI），核心功能：
- 基于规则解析用户意图
- 智能路由到三个项目（By Design/Cherry Pick/Momhand）
- 直接执行操作并返回结果

**文件**: `/root/.openclaw/workspace/message_engine.py`
**行数**: 315 行
**类型**: 规则引擎（无 AI）

---

## 与 OpenClaw 处理器的区别

| 特性 | message_engine.py | openclaw_agent_processor.py |
|------|-------------------|----------------------------|
| 处理方式 | 规则匹配 | AI 理解 |
| 响应速度 | 快（毫秒级） | 慢（秒级，需调用 AI） |
| 灵活性 | 低（固定规则） | 高（AI 理解） |
| 超时风险 | 无 | 有（30 秒超时） |
| 使用场景 | 简单明确指令 | 复杂/模糊指令 |

---

## 核心类：MessageProcessor

### 初始化
```python
class MessageProcessor:
    def __init__(self):
        self.bydesign_manager = None
        self.cherry_pick_manager = None
        self.momhand_manager = None
```

### 加载管理器
```python
def load_managers(self):
    """延迟加载各个项目的管理器"""
    from bydesign_manager import manager as bydesign_mgr
    from cherry_pick_manager import manager as cherry_mgr
    from item_manager import manager as momhand_mgr
```

---

## 意图识别规则

### 1. By Design - 出行相关

**关键词**: `出差`, `旅行`, `出行`, `旅游`, `出门`, `远门`

**触发条件**: 包含关键词 + (`创建` OR `清单` OR `帮我` OR `记`)

**提取逻辑**:
```python
# 提取天数
match = re.search(r'出差 (\d+) 天', message)
days = match.group(1) if match else '3'

# 提取目的地
match = re.search(r'(?:去 | 到 | 出差 | 旅行)([\u4e00-\u9fa5]+)', message)
destination = match.group(1) if match else '出差'

# 返回
('bydesign', 'create_trip', {
    'name': f'{destination}{days}天',
    'days': days
})
```

**示例**:
- "我要出差 3 天" → `create_trip(name="出差 3 天")`
- "去上海旅行" → `create_trip(name="上海旅行")`

---

### 2. Cherry Pick - 搬家相关

#### 2.1 记录物品

**关键词**: `搬家`, `打包`, `物品记录`, `新位置`, `原位置`

**触发条件**: 包含关键词 + (`记录` OR `添加` OR `帮我` OR `记`)

**提取逻辑**:
```python
# 提取物品名称
match = re.search(r'物品 [：:]\s*(\S+)', message)
item_name = match.group(1) if match else '物品'

# 提取原位置
match = re.search(r'原位置 [：:]\s*(\S+)', message)
before = match.group(1) if match else '未指定'

# 提取新位置
match = re.search(r'新位置 [：:]\s*(\S+)', message)
after = match.group(1) if match else '未指定'

# 返回
('cherry_pick', 'add_item', {
    'item_name': item_name,
    'before_location': before,
    'after_location': after
})
```

#### 2.2 创建搬家活动

**触发条件**: `创建` + `搬家活动`

**提取逻辑**:
```python
match = re.search(r'创建.*?搬家 [：:]\s*(\S+)', message)
move_name = match.group(1) if match else '新搬家'

# 返回
('cherry_pick', 'create_move', {'name': move_name})
```

---

### 3. Momhand - 物品查询

**关键词**: `找`, `查询`, `在哪里`, `放哪`

**触发条件**: 包含关键词

**提取逻辑**:
```python
match = re.search(r'找 [一下 ]?(\S+)', message)
keyword = match.group(1) if match else message

# 返回
('momhand', 'search_item', {'keyword': keyword})
```

**示例**:
- "找一下感冒药" → `search_item(keyword="感冒药")`
- "我的钥匙在哪里" → `search_item(keyword="我的钥匙在哪里")`

---

### 4. Momhand - 记录物品位置

**关键词**: `记一下`, `记录`, `放在`, `位置`, `存放`

**匹配模式**（优先级从高到低）:

#### 模式 1: "我的 XXX 放在了 YYY"
```python
match = re.search(r'我的\s*(.+?)\s*放在\s*了\s*(.+)', message)
# 示例："我的相机放在了电视柜上"
# → item_name="相机", location="电视柜上"
```

#### 模式 2: "XXX 放在了 YYY"
```python
match = re.search(r'(.+?)\s*放在\s*了\s*(.+)', message)
# 示例："action4 放在了透明箱子里"
# → item_name="action4", location="透明箱子里"
```

#### 模式 3: "XXX 在 YYY"
```python
match = re.search(r'(.+?)\s*在\s*(.+)', message)
# 示例："药在抽屉里"
# → item_name="药", location="抽屉里"
```

**清理逻辑**:
```python
# 移除前缀
item_name = re.sub(r'^我的\s*', '', item_name)
item_name = re.sub(r'^(帮我 | 帮我记一下 | 记录 | 记一下)[，,]?\s*', '', item_name)
```

---

### 5. 通用 - 添加物品

**触发条件**: `帮我` + (`记` OR `添加` OR `记录` OR `放`)

**返回**:
```python
('momhand', 'add_item', {
    'item_name': '物品',
    'location': '未指定',
    'original_message': original_message
})
```

---

## 处理函数

### 1. process_bydesign

```python
def process_bydesign(self, action, params):
    if action == 'create_trip':
        trip = self.bydesign_manager.create_trip(
            name=params['name'],
            description=f"{params['days']}天出行"
        )
        
        return (True, f"""✅ 已创建出行记录

📝 名称：{params['name']}
📅 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

📋 已自动加载通用检查清单...""")
```

### 2. process_cherry_pick

```python
def process_cherry_pick(self, action, params):
    if action == 'create_move':
        move = self.cherry_pick_manager.create_move(name=params['name'])
        return (True, f"✅ 已创建搬家活动\n\n📦 名称：{params['name']}")
    
    elif action == 'add_item':
        # 获取最新搬家活动
        moves = self.cherry_pick_manager.get_all_moves()
        latest_move = moves[0]
        
        item = self.cherry_pick_manager.add_item(
            move_id=latest_move['id'],
            name=params.get('item_name', '物品'),
            before_location=params.get('before_location', '未指定'),
            after_location=params.get('after_location', '未指定')
        )
        return (True, f"✅ 已记录物品\n\n📦 物品：{item_name}...")
```

### 3. process_momhand

```python
def process_momhand(self, action, params):
    if action == 'search_item':
        items = self.momhand_manager.search_items(params['keyword'])
        
        if not items:
            return (False, f'😕 没有找到与 "{params["keyword"]}" 相关的物品')
        
        result = f"🔍 找到 {len(items)} 个相关物品：\n\n"
        for item in items[:5]:
            result += f"📦 {item['name']}\n"
            result += f"   📍 位置：{item.get('location', '未知')}\n"
        return (True, result)
    
    elif action == 'add_item':
        # 智能识别物品类型
        item_type = '其他'
        if any(kw in item_name.lower() for kw in ['相机', 'action', '摄影']):
            item_type = '电子产品'
        elif any(kw in item_name for kw in ['书', '籍']):
            item_type = '书籍'
        elif any(kw in item_name for kw in ['药', '药品']):
            item_type = '药品'
        
        item = self.momhand_manager.add_item({
            "name": item_name,
            "type": item_type,
            "location": location,
            "usage": f"用户记录：{original_message[:50]}"
        })
        return (True, f"✅ 已记录物品位置\n\n📦 物品：{item_name}\n📍 位置：{location}")
```

---

## 使用示例

### 完整流程
```python
from message_engine import processor

# 1. 解析意图
project, action, params = processor.parse_intent("我要出差 3 天")
# → ('bydesign', 'create_trip', {'name': '出差 3 天', 'days': '3'})

# 2. 执行处理
success, message = processor.process(project, action, params)

# 3. 输出结果
if success:
    print(message)
else:
    print(f"失败：{message}")
```

### 测试用例

| 输入 | 识别结果 |
|------|----------|
| "我要出差 3 天" | bydesign/create_trip |
| "帮我记一下，相机放在电视柜上" | momhand/add_item |
| "找一下感冒药" | momhand/search_item |
| "记录搬家物品：电脑，原位置书房，新位置卧室" | cherry_pick/add_item |
| "创建搬家活动：春节搬家" | cherry_pick/create_move |

---

## 智能类型识别

```python
def process_momhand(self, action, params):
    item_type = '其他'
    
    # 电子产品
    if any(kw in item_name.lower() for kw in ['相机', 'action', '摄影', '摄像', 'dji']):
        item_type = '电子产品'
    
    # 书籍
    elif any(kw in item_name for kw in ['书', '籍', '杂志']):
        item_type = '书籍'
    
    # 药品
    elif any(kw in item_name for kw in ['药', '药品']):
        item_type = '药品'
    
    # 工具
    elif any(kw in item_name for kw in ['工具']):
        item_type = '工具'
    
    # 证件
    elif any(kw in item_name for kw in ['证件']):
        item_type = '证件'
```

---

## 错误处理

### 无法识别意图
```python
return ('unknown', 'unknown', {'message': original_message})

# process 函数返回
(False, "抱歉，我还不太理解这条消息：{message}\n\n你可以试试：\n✈️ 我要出差 3 天\n🏠 帮我记录搬家物品\n💊 找一下感冒药")
```

### 管理器未加载
```python
if not self.bydesign_manager:
    return (False, "By Design 服务暂时不可用")
```

### 异常捕获
```python
try:
    # 处理逻辑
except Exception as e:
    return (False, f"处理失败：{str(e)}")
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `message_engine.py` | 消息引擎主文件 |
| `bydesign_manager.py` | By Design 管理器 |
| `cherry_pick_manager.py` | Cherry Pick 管理器 |
| `momhand_manager_db.py` | Momhand 管理器 |

---

## 性能对比

| 指标 | message_engine | openclaw_agent |
|------|----------------|----------------|
| 响应时间 | <100ms | 5-30 秒 |
| 准确率 | ~80% (固定规则) | ~95% (AI 理解) |
| 资源消耗 | 低 | 高（需调用 AI） |
| 可维护性 | 中（需手动更新规则） | 高（AI 自适应） |

---

## 优缺点

### 优点
- ✅ 响应速度快
- ✅ 无超时风险
- ✅ 不依赖外部服务
- ✅ 可预测性强

### 缺点
- ❌ 规则固定，灵活性低
- ❌ 无法处理复杂/模糊指令
- ❌ 需要手动维护规则
- ❌ 不支持自然语言理解

---

## 常见问题

### Q: 什么时候使用 message_engine？
A: 适用于简单明确的指令，如"出差 3 天"、"找感冒药"。

### Q: 如何提高识别准确率？
A: 在 `parse_intent` 方法中添加更多关键词和正则匹配规则。

### Q: 支持自定义规则吗？
A: 需要手动修改 `message_engine.py` 文件。

### Q: 与 AI 处理器如何选择？
A: 优先使用 AI 处理器（更智能），超时或失败时降级到规则引擎。

---

*最后更新：2026-03-02*
