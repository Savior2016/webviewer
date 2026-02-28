# WebViewer - Web 服务

## 服务信息
- **端口**: 443 (HTTPS)
- **根目录**: `/root/.openclaw/workspace/webviewer/www`
- **首页**: `https://<IP>/` - Dummy的小弟（工具索引）

## 集成的应用

### 🏠 首页 - Dummy的小弟
**访问地址**: `https://<IP>/`

三个生活管理工具的统一入口，精美卡片式设计。

---

### ✈️ By Design - 已读不回
**访问地址**: `https://<IP>/bydesign/`

出远门前的检查清单管理器，读了就不需要单独返回。

**功能**:
- **通用检查清单**: 每次出行都要做的待办事项（关窗、断电、锁门等）
- **单次出行记录**: 特别携带的物品和单次事项
- **进度追踪**: 实时显示完成进度
- **易于核对**: 逐个勾选，完成出行

**API**:
- `GET /bydesign/api/checklist` - 获取检查清单
- `POST /bydesign/api/checklist` - 添加检查项
- `PUT /bydesign/api/checklist/:id` - 更新检查项
- `DELETE /bydesign/api/checklist/:id` - 删除检查项
- `GET /bydesign/api/trips` - 获取所有出行记录
- `POST /bydesign/api/trips` - 创建出行
- `GET /bydesign/api/trips/:id` - 获取出行详情
- `POST /bydesign/api/trips/:id/items` - 添加自定义物品
- `PUT /bydesign/api/trips/:id/items/:id` - 更新物品状态
- `POST /bydesign/api/trips/:id/complete` - 完成出行
- `GET /bydesign/api/trips/:id/progress` - 获取进度

**数据存储**: `/root/.openclaw/workspace/webviewer/data/bydesign/`

---

### 🏠 Cherry Pick - 一搬不丢
**访问地址**: `https://<IP>/cherry-pick/`

搬家物品追踪系统，记录每次搬家的物品信息。

**功能**:
- 创建搬家活动
- 记录物品名称、原位置、新位置
- 标记物品是否已放置
- 已放置物品自动同步到 momhand

**API**:
- `GET /cherry-pick/api/moves` - 获取所有搬家活动
- `POST /cherry-pick/api/moves` - 创建搬家活动
- `GET /cherry-pick/api/moves/:id/items` - 获取物品列表
- `POST /cherry-pick/api/moves/:id/items` - 添加物品
- `PUT /cherry-pick/api/items/:id` - 更新物品
- `DELETE /cherry-pick/api/moves/:id` - 删除搬家活动
- `DELETE /cherry-pick/api/items/:id` - 删除物品

**数据存储**: `/root/.openclaw/workspace/webviewer/data/cherry-pick/moves.json`

---

### 📦 Momhand - 物品管理
**访问地址**: `https://<IP>/momhand/`

个人物品管理系统，支持分类、搜索、过期提醒。

**API**:
- `GET /momhand/api/items` - 获取所有物品
- `GET /momhand/api/search?q=关键词` - 搜索物品
- `GET /momhand/api/stats` - 统计信息
- `GET /momhand/api/expiring?days=7` - 即将过期物品

---

## 启动服务
```bash
cd /root/.openclaw/workspace/webviewer
python3 server.py
```

## 证书
使用自签名证书，浏览器访问时需要信任。
证书文件：`selfsigned.crt` / `selfsigned.key`

## 项目结构
```
webviewer/
├── server.py                  # HTTPS 服务器
├── bydesign_manager.py        # By Design 管理器
├── cherry_pick_manager.py     # Cherry Pick 管理器
├── www/
│   ├── index.html             # Dummy的小弟（首页）
│   ├── bydesign/
│   │   └── index.html         # By Design 页面
│   ├── cherry-pick/
│   │   └── index.html         # Cherry Pick 页面
│   └── momhand/
│       └── index.html         # Momhand 页面
└── data/
    ├── bydesign/              # By Design 数据
    └── cherry-pick/           # Cherry Pick 数据
```
