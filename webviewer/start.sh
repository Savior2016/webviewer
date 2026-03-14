#!/bin/bash
# WebViewer 启动脚本 - systemd 管理

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 直接启动，由 systemd 管理生命周期
exec python3 server_enhanced.py
