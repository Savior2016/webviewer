#!/usr/bin/env python3
"""
消息处理引擎
解析用户消息，智能路由到对应的项目进行处理
"""

import json
import re
from datetime import datetime

class MessageProcessor:
    def __init__(self):
        self.bydesign_manager = None
        self.cherry_pick_manager = None
        self.momhand_manager = None
        
    def load_managers(self):
        """加载各个项目的管理器"""
        import sys
        # 添加 workspace 根目录到路径，以便导入管理器模块
        sys.path.insert(0, "/root/.openclaw/workspace")
        
        try:
            from bydesign_manager import manager as bydesign_mgr
            self.bydesign_manager = bydesign_mgr
            print(f"✅ By Design 管理器加载成功")
        except Exception as e:
            print(f"❌ 加载 By Design 管理器失败：{e}")
        
        try:
            from cherry_pick_manager import manager as cherry_mgr
            self.cherry_pick_manager = cherry_mgr
            print(f"✅ Cherry Pick 管理器加载成功")
        except Exception as e:
            print(f"❌ 加载 Cherry Pick 管理器失败：{e}")
        
        try:
            sys.path.insert(0, "/root/.openclaw/workspace/momhand/skills")
            from item_manager import manager as momhand_mgr
            self.momhand_manager = momhand_mgr
            print(f"✅ Momhand 管理器加载成功")
        except Exception as e:
            print(f"❌ 加载 Momhand 管理器失败：{e}")
    
    def parse_intent(self, message):
        """
        解析用户意图
        返回：(project, action, params)
        """
        original_message = message
        message = message.strip()  # 不要 lower()，保持中文原样
        
        # 1. By Design - 出行相关
        if any(kw in message for kw in ['出差', '旅行', '出行', '旅游', '出门', '远门']):
            # 匹配"出差 X 天"或"旅行 X 天"格式（支持"去北京旅行 5 天"）
            match = re.search(r'(\d+)\s*天', message)
            days = match.group(1) if match else '3'
            
            # 尝试提取目的地（优先匹配"去 XX"或"到 XX"）
            dest_match = re.search(r'(?:去 | 到)([\u4e00-\u9fa5]+)', message)
            if dest_match:
                destination = dest_match.group(1)
            else:
                # 如果没有明确目的地，使用出行类型
                if '出差' in message:
                    destination = '出差'
                elif '旅行' in message:
                    destination = '旅行'
                elif '旅游' in message:
                    destination = '旅游'
                else:
                    destination = '出行'
            
            return ('bydesign', 'create_trip', {
                'name': f'{destination}{days}天',
                'days': days
            })
        
        # 2. Cherry Pick - 搬家相关
        if any(kw in message for kw in ['搬家', '打包', '物品记录', '新位置', '原位置']):
            if '记录' in message or '添加' in message or '帮我' in message or '记' in message:
                # 提取物品信息
                match = re.search(r'物品 [：:]\s*(\S+)', message)
                item_name = match.group(1) if match else '物品'
                
                before_match = re.search(r'原位置 [：:]\s*(\S+)', message)
                before = before_match.group(1) if before_match else '未指定'
                
                after_match = re.search(r'新位置 [：:]\s*(\S+)', message)
                after = after_match.group(1) if after_match else '未指定'
                
                return ('cherry_pick', 'add_item', {
                    'item_name': item_name,
                    'before_location': before,
                    'after_location': after
                })
            
            if '创建' in message or '搬家活动' in message:
                match = re.search(r'创建.*?搬家 [：:]\s*(\S+)', message)
                move_name = match.group(1) if match else '新搬家'
                
                return ('cherry_pick', 'create_move', {
                    'name': move_name
                })
        
        # 3. Momhand - 物品查询
        if any(kw in message for kw in ['找', '查询', '在哪里', '放哪']):
            if '找' in message or '哪里' in message or '哪' in message:
                # 搜索物品
                match = re.search(r'找 (?:一下)?(.+)', message) or re.search(r'找一下(.+)', message)
                keyword = match.group(1).strip() if match else message
                
                return ('momhand', 'search_item', {
                    'keyword': keyword
                })
        
        # 4. Momhand - 记录物品位置（支持自然语言）
        if any(kw in message for kw in ['记一下', '记录', '放在', '位置', '存放']):
            item_name = None
            location = None
            
            # 尝试匹配"我的 XXX 放在了 YYY"
            match = re.search(r'我的\s*(.+?)\s*放在\s*了\s*(.+)', message)
            if match:
                item_name = match.group(1).strip()
                location = match.group(2).strip()
            
            # 尝试匹配"XXX 放在了 YYY"
            if not item_name:
                match = re.search(r'(.+?)\s*放在\s*了\s*(.+)', message)
                if match:
                    item_name = match.group(1).strip()
                    location = match.group(2).strip()
                    item_name = re.sub(r'^ (帮我记一下，)?', '', item_name)
            
            # 尝试匹配"XXX 在 YYY"
            if not item_name:
                match = re.search(r'(.+?)\s*在\s*(.+)', message)
                if match:
                    item_name = match.group(1).strip()
                    location = match.group(2).strip()
            
            # 清理物品名称
            if item_name:
                item_name = re.sub(r'^我的\s*', '', item_name)
                item_name = re.sub(r'^ (帮我 | 帮我记一下 | 记录 | 记一下)[，,]?\s*', '', item_name)
                item_name = item_name.strip()
            
            if not item_name:
                item_name = '物品'
            if not location:
                location = '未指定'
            
            return ('momhand', 'add_item', {
                'item_name': item_name,
                'location': location,
                'original_message': original_message
            })
        
        # 5. 通用 - 添加物品（包含"帮我"的请求）
        if '帮我' in message and any(kw in message for kw in ['记', '添加', '记录', '放']):
            return ('momhand', 'add_item', {
                'item_name': '物品',
                'location': '未指定',
                'original_message': original_message
            })
        
        # 无法识别的意图
        return ('unknown', 'unknown', {'message': original_message})
    
    def process(self, project, action, params):
        """
        处理消息
        返回：(success, result_message)
        """
        self.load_managers()
        
        try:
            if project == 'bydesign':
                return self.process_bydesign(action, params)
            elif project == 'cherry_pick':
                return self.process_cherry_pick(action, params)
            elif project == 'momhand':
                return self.process_momhand(action, params)
            else:
                return (False, f"抱歉，我还不太理解这条消息：{params.get('message', '')}\n\n你可以试试：\n✈️ 我要出差 3 天\n🏠 帮我记录搬家物品\n💊 找一下感冒药")
        except Exception as e:
            return (False, f"处理失败：{str(e)}")
    
    def process_bydesign(self, action, params):
        """处理 By Design 相关请求"""
        if action == 'create_trip':
            if not self.bydesign_manager:
                return (False, "By Design 服务暂时不可用")
            
            trip = self.bydesign_manager.create_trip(
                name=params['name'],
                description=f"{params['days']}天出行"
            )
            
            return (True, f"""✅ 已创建出行记录

📝 名称：{params['name']}
📅 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

📋 已自动加载通用检查清单，包括：
• 关闭所有窗户
• 关闭所有电器电源
• 检查门锁
• 清空垃圾
• 检查水龙头

👉 访问：https://localhost/bydesign/ 查看详细清单""")
        
        return (False, "未知的 By Design 操作")
    
    def process_cherry_pick(self, action, params):
        """处理 Cherry Pick 相关请求"""
        if action == 'create_move':
            if not self.cherry_pick_manager:
                return (False, "Cherry Pick 服务暂时不可用")
            
            move = self.cherry_pick_manager.create_move(
                name=params['name']
            )
            
            return (True, f"""✅ 已创建搬家活动

📦 名称：{params['name']}
📅 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

👉 访问：https://localhost/cherry-pick/ 添加物品""")
        
        elif action == 'add_item':
            if not self.cherry_pick_manager:
                return (False, "Cherry Pick 服务暂时不可用")
            
            # 获取最新的搬家活动
            moves = self.cherry_pick_manager.get_all_moves()
            if not moves:
                return (False, "请先创建一个搬家活动")
            
            latest_move = moves[0]
            
            item = self.cherry_pick_manager.add_item(
                move_id=latest_move['id'],
                name=params.get('item_name', '物品'),
                before_location=params.get('before_location', '未指定'),
                after_location=params.get('after_location', '未指定')
            )
            
            return (True, f"""✅ 已记录物品

📦 物品：{params.get('item_name', '物品')}
📍 原位置：{params.get('before_location', '未指定')}
📦 新位置：{params.get('after_location', '未指定')}
📋 所属活动：{latest_move['name']}

👉 访问：https://localhost/cherry-pick/ 查看更多""")
        
        return (False, "未知的 Cherry Pick 操作")
    
    def process_momhand(self, action, params):
        """处理 Momhand 相关请求"""
        if action == 'search_item':
            if not self.momhand_manager:
                return (False, "Momhand 服务暂时不可用")
            
            try:
                items = self.momhand_manager.search_items(params['keyword'])
                
                if not items:
                    return (False, f'未找到与 "{params["keyword"]}" 相关的物品')
                
                result = f"找到 {len(items)} 个相关物品：\n\n"
                for item in items[:5]:
                    result += f"物品：{item.get('name', '未知')}\n"
                    result += f"位置：{item.get('location', '未知')}\n"
                    if item.get('usage'):
                        result += f"用途：{item['usage']}\n"
                    result += "\n"
                
                if len(items) > 5:
                    result += f"... 还有 {len(items) - 5} 个物品"
                
                return (True, result)
            except Exception as e:
                return (False, f"搜索失败：{str(e)}")
            
            result += "\n👉 访问：https://localhost/momhand/ 查看全部"
            return (True, result)
        
        elif action == 'add_item':
            if not self.momhand_manager:
                return (False, "Momhand 服务暂时不可用")
            
            item_name = params.get('item_name', '物品')
            location = params.get('location', '未指定')
            original_message = params.get('original_message', '')
            
            # 智能识别物品类型
            item_type = '其他'
            if any(kw in item_name.lower() for kw in ['相机', 'action', '摄影', '摄像', 'dji']):
                item_type = '电子产品'
            elif any(kw in item_name for kw in ['书', '籍', '杂志']):
                item_type = '书籍'
            elif any(kw in item_name for kw in ['药', '药品']):
                item_type = '药品'
            elif any(kw in item_name for kw in ['工具']):
                item_type = '工具'
            elif any(kw in item_name for kw in ['证件']):
                item_type = '证件'
            
            item_data = {
                "name": item_name,
                "type": item_type,
                "location": location,
                "usage": f"用户记录：{original_message[:50]}" if original_message else ""
            }
            
            item = self.momhand_manager.add_item(item_data)
            
            return (True, f"""✅ 已记录物品位置

📦 物品：{item_name}
📍 位置：{location}
📂 类型：{item_type}

👉 访问：https://localhost/momhand/ 查看所有物品""")
        
        return (False, "未知的 Momhand 操作")


# 全局实例
processor = MessageProcessor()
