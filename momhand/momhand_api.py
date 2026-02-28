#!/usr/bin/env python3
"""
momhand_api.py - momhand API 服务（集成到 WebViewer）
"""

import json
import sys
sys.path.insert(0, "/root/.openclaw/workspace/momhand/skills")
from item_manager import manager

def handle_api(path, query=None):
    """处理 API 请求，返回 JSON"""
    query = query or {}
    
    try:
        if path == "/momhand/api/items":
            return {"success": True, "data": manager.get_all_items()}
        
        elif path == "/momhand/api/search":
            keyword = query.get("q", [""])[0]
            return {"success": True, "data": manager.search_items(keyword)}
        
        elif path == "/momhand/api/stats":
            return {"success": True, "data": manager.get_statistics()}
        
        elif path == "/momhand/api/expiring":
            days = int(query.get("days", [7])[0])
            return {"success": True, "data": manager.get_expiring_items(days)}
        
        else:
            return {"success": False, "error": "Unknown API endpoint"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # 测试
    print(json.dumps(handle_api("/momhand/api/stats"), ensure_ascii=False, indent=2))
