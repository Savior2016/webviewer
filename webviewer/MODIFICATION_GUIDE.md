# WebViewer 修改快速指南

> ⚠️ **修改前必读** - 避免重蹈覆辙

---

## 🚨 血泪教训 (2026-02-28)

**问题**: `server.py` 中有两个 `do_PUT` 方法定义，导致 Cherry Pick 位置更新失败。

**症状**: 在"一搬不丢"页面填写"打包前位置"时显示更新失败。

**原因**: Python 类中后定义的方法会覆盖前面的，导致 Cherry Pick 的 PUT 路由丢失。

**修复**: 合并所有 PUT 路由到一个 `do_PUT` 方法。

**验证**:
```bash
# 检查方法定义数量 - 应该只输出一行！
grep -n "def do_PUT" /root/.openclaw/workspace/webviewer/server.py
```

---

## 📋 修改前检查清单

### 1. 读文档
```bash
# 必须首先读取完整架构文档
read /root/.openclaw/workspace/webviewer/WEBVIEWER_COMPLETE_ARCHITECTURE.md
```

### 2. 查方法
```bash
# 确保没有重复定义
grep -n "def do_PUT" server.py     # 应该只有 1 行
grep -n "def do_POST" server.py    # 应该只有 1 行
grep -n "def do_DELETE" server.py  # 应该只有 1 行
```

### 3. 备份数据
```bash
# 备份所有数据文件
cp -r /root/.openclaw/workspace/webviewer/data \
      /root/.openclaw/workspace/webviewer/data.backup.$(date +%Y%m%d)
```

### 4. 测试现有功能
```bash
# Cherry Pick (关键！)
curl -k -X PUT https://localhost/cherry-pick/api/items/test123 \
  -H "Content-Type: application/json" \
  -d '{"before_location":"test"}'
# 预期：{"error": "物品不存在"} (而不是 404)

# Momhand
curl -k https://localhost/momhand/api/stats

# By Design
curl -k https://localhost/bydesign/api/checklist
```

---

## 🔧 常见修改

### 添加新的 API 端点

**步骤**:
1. 在 `server.py` 的对应 HTTP 方法中添加路由
2. 创建 handler 方法
3. 在管理器中添加业务逻辑
4. 测试

**示例**:
```python
def do_GET(self):
    # ... 现有路由 ...
    
    # 新增路由
    elif path.startswith("/new-api/"):
        self.handle_new_api(path)
```

---

### 修改数据结构

**⚠️ 警告**: 务必备份！

**步骤**:
1. 备份数据文件
2. 修改管理器
3. 添加迁移逻辑（如需要）
4. 更新前端
5. 测试

---

## 🧪 测试命令

### Cherry Pick 完整测试
```bash
# 1. 获取搬家活动列表
curl -k https://localhost/cherry-pick/api/moves

# 2. 创建搬家活动
curl -k -X POST https://localhost/cherry-pick/api/moves \
  -H "Content-Type: application/json" \
  -d '{"name":"测试搬家"}'

# 3. 添加物品
curl -k -X POST https://localhost/cherry-pick/api/moves/{moveId}/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试物品"}'

# 4. 更新打包前位置 (关键测试！)
curl -k -X PUT https://localhost/cherry-pick/api/items/{itemId} \
  -H "Content-Type: application/json" \
  -d '{"before_location":"书房"}'

# 5. 更新打包后位置
curl -k -X PUT https://localhost/cherry-pick/api/items/{itemId} \
  -H "Content-Type: application/json" \
  -d '{"pack_location":"纸箱 1"}'

# 6. 更新拆封后位置 (会同步到 Momhand)
curl -k -X PUT https://localhost/cherry-pick/api/items/{itemId} \
  -H "Content-Type: application/json" \
  -d '{"after_location":"新家书房"}'
```

### Momhand 测试
```bash
# 添加物品
curl -k -X POST https://localhost/momhand/api/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","type":"测试","location":"测试位置"}'

# 搜索
curl -k "https://localhost/momhand/api/search?q=测试"

# 统计
curl -k https://localhost/momhand/api/stats
```

### By Design 测试
```bash
# 创建出行
curl -k -X POST https://localhost/bydesign/api/trips \
  -H "Content-Type: application/json" \
  -d '{"name":"测试出行"}'

# 获取清单
curl -k https://localhost/bydesign/api/checklist
```

---

## 📁 关键文件

| 文件 | 用途 | 修改风险 |
|------|------|----------|
| `server.py` | 主服务器 | ⚠️⚠️⚠️ 高 - 曾出问题 |
| `cherry_pick_manager.py` | 搬家管理器 | ⚠️ 中 |
| `momhand_manager_db.py` | 物品管理器 (SQLite) | ⚠️ 中 |
| `bydesign_manager.py` | 出行管理器 | ⚠️ 中 |
| `openclaw_agent_processor.py` | AI 处理器 | ⚠️ 低 |
| `www/*/index.html` | 前端页面 | ⚠️ 低 |

---

## 🆘 故障排除

### PUT 请求 404
```bash
# 检查路由
grep -A 15 "def do_PUT" server.py

# 确保包含 Cherry Pick 路由
if path.startswith("/cherry-pick/api/items/"):
    self.handle_cherry_pick_put(path, data)
```

### 数据保存失败
```bash
# 检查权限
ls -la data/

# 检查 JSON 格式
python3 -m json.tool data/cherry-pick/moves.json
```

### 服务异常
```bash
# 重启服务
pkill -f "python3 server.py"
cd /root/.openclaw/workspace/webviewer && python3 server.py &

# 查看日志
tail -f /tmp/webviewer.log
```

---

## 📚 相关文档

- **完整架构**: `WEBVIEWER_COMPLETE_ARCHITECTURE.md`
- **技能文档**: `../skills/webviewer/SKILL.md`
- **项目总结**: `PROJECTS.md`

---

*最后更新：2026-02-28*
