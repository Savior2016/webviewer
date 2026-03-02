# 提示词更新记录 - 2026-03-02

## 修改内容

### 1. 更新系统提示词

**文件**: `/root/.openclaw/workspace/data/settings.json`

**新提示词**:
```
你是 WebViewer 的专业助手 Dummy。你擅长：理解用户的出行、搬家、物品管理需求

用户消息:"{message}"

请根据以上提示词和用户消息进行处理：
1. 选取 webviewer 中合适的模块处理消息
2. 进行实际的保存操作，不要只返回 JSON

可用项目：
1. 出行相关（出差、旅行、出行）→ By Design (/bydesign/)
   - API: POST /bydesign/api/trips
   - 数据：{name, description}

2. 搬家相关（搬家、打包、物品记录）→ Cherry Pick (/cherry-pick/)
   - API: POST /cherry-pick/api/moves/{moveId}/items
   - 数据：{name, before_location, after_location}

3. 物品相关（找、查询、记录位置）→ Momhand (/momhand/)
   - API: POST /momhand/api/items 或 GET /momhand/api/search?q=xxx
   - 数据：{name, type, location, usage}

返回 JSON 格式：
{
  "success": true/false,
  "project": "bydesign 或 cherry_pick 或 momhand 或 null",
  "action": "操作类型或 null",
  "message": "回复消息",
  "refresh": "/页面路径/ 或 null",
  "data": {保存的数据} 或 null
}
```

### 2. 同步页面默认提示词

**文件**: `/root/.openclaw/workspace/www/index.html`

更新了 `DEFAULT_SYSTEM_PROMPT` 常量，确保点击"恢复默认"时使用新提示词。

### 3. 修复设置 API 绑定

**文件**: `/root/.openclaw/workspace/server.py`

**问题**: `handle_get_settings` 和 `handle_save_settings` 错误地使用了 Siri Dream 的设置文件 (`SIRI_DREAM_SETTINGS_FILE`)，而不是 WebViewer 主设置文件 (`SETTINGS_FILE`)。

**修复**: 
- `handle_get_settings`: 改为从 `SETTINGS_FILE` (`/root/.openclaw/workspace/data/settings.json`) 读取
- `handle_save_settings`: 改为保存到 `SETTINGS_FILE`

现在页面设置模态框与 `data/settings.json` 完全绑定，页面修改时直接修改该文件。

## 验证

### API 测试
```bash
# 获取提示词
curl -sk https://43.153.153.62/api/settings

# 保存提示词
curl -sk -X PUT https://43.153.153.62/api/settings \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "新提示词"}'
```

### 页面测试
1. 访问 https://43.153.153.62/
2. 点击右上角 ⚙️ 设置按钮
3. 查看提示词是否正确显示
4. 修改提示词并保存
5. 刷新页面，确认修改已持久化
6. 点击"恢复默认"，确认恢复为新默认提示词

## 影响范围

- ✅ WebViewer 首页聊天功能
- ✅ 页面设置模态框
- ✅ 提示词持久化存储
- ❌ Siri Dream 模块（使用独立的设置文件，不受影响）

## 服务重启

修改后已重启服务：
```bash
pkill -9 -f "python3 server.py"
cd /root/.openclaw/workspace
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

## 相关文件

- `/root/.openclaw/workspace/data/settings.json` - 提示词存储
- `/root/.openclaw/workspace/www/index.html` - 页面默认提示词
- `/root/.openclaw/workspace/server.py` - API 处理逻辑
