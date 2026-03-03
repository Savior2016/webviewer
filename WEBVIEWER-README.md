# WebViewer 服务说明

## 版本
v1.5.3 - 日志增强版

## 新增功能

### 📜 运行日志
- 服务运行日志自动记录到 `server.log`
- 主页底部新增「运行日志」按钮，可在线查看
- 支持实时刷新和下载日志文件
- 日志按级别着色显示（错误红色、警告黄色、信息绿色）

### 🛡️ 稳定性增强
- 所有日志输出使用 Python logging 模块
- 日志文件自动轮转（最多保留 500 行）
- 新增启动/停止脚本

## 使用方法

### 启动服务
```bash
./start-webviewer.sh
```

### 停止服务
```bash
./stop-webviewer.sh
```

### 查看日志
1. 打开主页 `https://<服务器 IP>`
2. 点击底部「运行日志」按钮
3. 可刷新或下载日志

### 日志文件位置
- `/root/.openclaw/workspace/server.log`

### API 端点
- `GET /api/logs?lines=100` - 获取最新 N 行日志

## 文件说明
- `server.py` - 主服务程序
- `server.log` - 运行日志
- `server.pid` - 进程 ID 文件
- `start-webviewer.sh` - 启动脚本
- `stop-webviewer.sh` - 停止脚本

## 端口
- **443** (HTTPS)
