# WebViewer 消息处理技能

处理来自 WebViewer 页面的消息请求

## 功能

1. 接收 Web 页面发送的消息
2. 根据消息内容选择对应的功能
3. 执行操作（创建出行/记录物品/查询物品）
4. 返回结果到 Web 页面和 Feishu

## 使用方法

```bash
# 处理 Web 消息
openclaw webviewer handle --message "我要出差 3 天"

# 查询结果
openclaw webviewer result --msg-id xxx
```

## 消息类型

### 出行相关
- "我要出差 3 天"
- "帮我创建出行清单"
- "去北京旅行"

### 搬家相关
- "帮我记录搬家物品：书籍，原位置书房"
- "创建搬家活动：搬到新家"

### 物品查询
- "找一下感冒药"
- "查询工具在哪里"
