# WebViewer 监控程序使用指南

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `monitor.sh` | 监控脚本主程序 |
| `diagnose.sh` | 快速诊断脚本 |
| `server.log` | 服务运行日志 |
| `monitor.log` | 监控程序日志 |
| `crash_history.log` | 崩溃历史记录 |
| `server.pid` | 服务进程 ID |
| `monitor.pid` | 监控进程 ID |

## 🚀 启动监控

```bash
# 方式 1：后台运行（推荐）
cd /root/.openclaw/workspace/webviewer
nohup bash monitor.sh > monitor.log 2>&1 &
echo $! > monitor.pid

# 方式 2：使用 systemd（需要 root 权限）
cp webviewer-monitor.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable webviewer-monitor
systemctl start webviewer-monitor
```

## 📊 查看状态

```bash
# 查看监控程序状态
ps aux | grep monitor

# 查看监控日志
tail -f monitor.log

# 运行诊断
bash diagnose.sh
```

## 🔧 停止监控

```bash
# 停止监控程序
kill $(cat monitor.pid)

# 如果使用 systemd
systemctl stop webviewer-monitor
systemctl disable webviewer-monitor
```

## 📈 监控功能

### 自动检测
- 每 30 秒检查一次服务状态
- 检测 PID 文件和进程是否存在
- 记录服务运行时长

### 崩溃处理
1. **记录崩溃信息**
   - 崩溃时间
   - 运行时长
   - 最后 50 行日志
   - 系统内存状态
   - 磁盘空间
   - OOM 检查

2. **自动重启**
   - 检测到崩溃后自动重启
   - 5 分钟内最多重启 5 次（防止无限重启）
   - 超过限制后停止并告警

3. **日志收集**
   - 所有崩溃记录保存到 `crash_history.log`
   - 监控日志保存到 `monitor.log`

## 🔍 诊断命令

```bash
# 快速诊断
bash diagnose.sh

# 查看崩溃历史
cat crash_history.log

# 查看服务日志
tail -100 server.log

# 检查端口占用
netstat -tlnp | grep 443

# 检查内存
free -h

# 检查磁盘
df -h
```

## ⚠️ 常见问题

### 服务频繁崩溃
1. 查看 `crash_history.log` 分析原因
2. 检查系统内存是否充足
3. 检查是否有 OOM 记录
4. 运行 `diagnose.sh` 获取详细报告

### 监控程序不工作
1. 检查 `monitor.log` 查看错误
2. 确保脚本有执行权限：`chmod +x monitor.sh`
3. 手动运行测试：`bash monitor.sh`

### 无法重启服务
1. 检查端口是否被占用：`netstat -tlnp | grep 443`
2. 清理旧 PID 文件：`rm server.pid`
3. 手动启动测试：`python3 server_enhanced.py`

## 📞 技术支持

如果问题持续，请提供以下信息：
1. `crash_history.log` 完整内容
2. `server.log` 最后 200 行
3. `diagnose.sh` 输出结果
4. 系统内存和磁盘信息
