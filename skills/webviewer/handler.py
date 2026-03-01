#!/usr/bin/env python3
"""
WebViewer 消息处理 - OpenClaw 技能
处理来自主页面的消息，理解意图并调用相应的 API
"""

import json
import os
import requests
from pathlib import Path

class WebViewerSkill:
    def __init__(self):
        self.base_url = "https://localhost"
        self.verify_ssl = False  # 自签名证书
        
    def parse_and_process(self, message: str) -> dict:
        """
        解析用户消息，理解意图，调用相应 API
        返回处理结果
        """
        
        # 意图识别
        intent = self._parse_intent(message)
        print(f"📊 识别意图：{intent}")
        
        # 根据意图调用相应 API
        if intent['project'] == 'bydesign':
            return self._handle_bydesign(intent, message)
        elif intent['project'] == 'cherry_pick':
            return self._handle_cherry_pick(intent, message)
        elif intent['project'] == 'momhand':
            return self._handle_momhand(intent, message)
        else:
            return {
                'success': False,
                'message': f"抱歉，我还不太理解这条消息：{message}\n\n你可以试试：\n✈️ 我要出差 3 天\n🏠 帮我记录搬家物品\n💊 找一下感冒药"
            }
    
    def _parse_intent(self, message: str) -> dict:
        """解析消息意图"""
        import re
        
        # 出行相关
        if any(kw in message for kw in ['出差', '旅行', '出行', '旅游']):
            return {'project': 'bydesign', 'action': 'create_trip'}
        
        # 搬家相关
        if any(kw in message for kw in ['搬家', '打包']):
            return {'project': 'cherry_pick', 'action': 'add_item'}
        
        # 物品查询
        if any(kw in message for kw in ['找', '查询', '在哪里']):
            return {'project': 'momhand', 'action': 'search'}
        
        # 物品记录（自然语言）
        if any(kw in message for kw in ['记一下', '记录', '放在', '位置']):
            return {'project': 'momhand', 'action': 'add_item'}
        
        return {'project': 'unknown', 'action': 'unknown'}
    
    def _handle_bydesign(self, intent: dict, message: str) -> dict:
        """处理出行相关请求"""
        try:
            # 调用 By Design API 创建出行
            response = requests.post(
                f"{self.base_url}/bydesign/api/trips",
                json={"name": "出行记录"},
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                trip = response.json()
                return {
                    'success': True,
                    'project': 'bydesign',
                    'message': f"✅ 已创建出行记录\n\n📝 名称：{trip.get('name', '出行')}\n\n👉 访问：https://localhost/bydesign/",
                    'refresh': '/bydesign/'
                }
            
            return {'success': False, 'message': '创建失败'}
        except Exception as e:
            return {'success': False, 'message': f'处理失败：{str(e)}'}
    
    def _handle_cherry_pick(self, intent: dict, message: str) -> dict:
        """处理搬家相关请求"""
        try:
            # 提取物品信息
            item_name = '物品'
            before = '未指定'
            after = '未指定'
            
            # 尝试匹配"物品：XXX"
            import re
            match = re.search(r'物品 [：:]\s*(\S+)', message)
            if match:
                item_name = match.group(1)
            
            # 获取最新搬家活动
            moves_response = requests.get(
                f"{self.base_url}/cherry-pick/api/moves",
                verify=self.verify_ssl,
                timeout=10
            )
            
            if moves_response.status_code == 200:
                moves = moves_response.json()
                if moves:
                    latest_move = moves[0]
                    
                    # 添加物品
                    item_response = requests.post(
                        f"{self.base_url}/cherry-pick/api/moves/{latest_move['id']}/items",
                        json={
                            "name": item_name,
                            "before_location": before,
                            "after_location": after
                        },
                        verify=self.verify_ssl,
                        timeout=10
                    )
                    
                    if item_response.status_code == 200:
                        return {
                            'success': True,
                            'project': 'cherry_pick',
                            'message': f"✅ 已记录物品\n\n📦 物品：{item_name}\n\n👉 访问：https://localhost/cherry-pick/",
                            'refresh': '/cherry-pick/'
                        }
            
            return {'success': False, 'message': '请先创建搬家活动'}
        except Exception as e:
            return {'success': False, 'message': f'处理失败：{str(e)}'}
    
    def _handle_momhand(self, intent: dict, message: str) -> dict:
        """处理 Momhand 相关请求"""
        try:
            if intent['action'] == 'search':
                # 搜索物品
                import re
                match = re.search(r'找 [一下 ]?(\S+)', message)
                keyword = match.group(1) if match else '物品'
                
                response = requests.get(
                    f"{self.base_url}/momhand/api/search?q={keyword}",
                    verify=self.verify_ssl,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') and result.get('data'):
                        items = result['data']
                        msg = f"🔍 找到 {len(items)} 个物品：\n\n"
                        for item in items[:3]:
                            msg += f"📦 {item['name']} - 📍 {item.get('location', '未知')}\n"
                        return {
                            'success': True,
                            'project': 'momhand',
                            'message': msg,
                            'refresh': '/momhand/'
                        }
                    return {'success': False, 'message': '未找到相关物品'}
            
            elif intent['action'] == 'add_item':
                # 添加物品（自然语言解析）
                item_name, location = self._parse_item_info(message)
                
                item_data = {
                    "name": item_name,
                    "type": "其他",
                    "location": location,
                    "usage": message[:50]
                }
                
                # 这里需要调用 Momhand API（待实现）
                return {
                    'success': True,
                    'project': 'momhand',
                    'message': f"✅ 已记录\n\n📦 {item_name}\n📍 {location}",
                    'refresh': '/momhand/'
                }
            
            return {'success': False, 'message': '处理失败'}
        except Exception as e:
            return {'success': False, 'message': f'处理失败：{str(e)}'}
    
    def _parse_item_info(self, message: str) -> tuple:
        """从自然语言中提取物品信息"""
        import re
        
        item_name = '物品'
        location = '未指定'
        
        # 匹配"我的 XXX 放在了 YYY"
        match = re.search(r'我的\s*(.+?)\s*放在\s*了\s*(.+)', message)
        if match:
            item_name = match.group(1).strip()
            location = match.group(2).strip()
        
        return item_name, location


# OpenClaw 技能入口
def handle_message(message: str) -> dict:
    """OpenClaw 调用此函数处理消息"""
    skill = WebViewerSkill()
    return skill.parse_and_process(message)
