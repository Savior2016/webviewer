"""
CherryPickManager 单元测试
"""
import pytest


class TestMoves:
    """搬家活动测试"""

    def test_create_move(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('搬到新家')
        assert move['name'] == '搬到新家'
        assert move['status'] == 'active'
        assert 'id' in move

    def test_get_all_moves(self, cherry_pick_manager):
        cherry_pick_manager.create_move('搬家1')
        cherry_pick_manager.create_move('搬家2')
        moves = cherry_pick_manager.get_all_moves()
        assert len(moves) == 2

    def test_get_all_moves_sorted(self, cherry_pick_manager):
        cherry_pick_manager.create_move('第一次')
        cherry_pick_manager.create_move('第二次')
        moves = cherry_pick_manager.get_all_moves()
        assert moves[0]['created_at'] >= moves[1]['created_at']

    def test_get_move(self, cherry_pick_manager):
        created = cherry_pick_manager.create_move('测试搬家')
        move = cherry_pick_manager.get_move(created['id'])
        assert move is not None
        assert move['name'] == '测试搬家'

    def test_get_nonexistent_move(self, cherry_pick_manager):
        move = cherry_pick_manager.get_move('nonexistent')
        assert move is None

    def test_delete_move(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('待删除')
        cherry_pick_manager.delete_move(move['id'])
        assert cherry_pick_manager.get_move(move['id']) is None

    def test_delete_move_cascades_items(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('待删除')
        cherry_pick_manager.add_item(move['id'], '物品1')
        cherry_pick_manager.delete_move(move['id'])
        items = cherry_pick_manager.get_items(move['id'])
        assert len(items) == 0


class TestItems:
    """物品管理测试"""

    def test_add_item(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('搬家')
        item = cherry_pick_manager.add_item(move['id'], '书籍')
        assert item is not None
        assert item['name'] == '书籍'
        assert item['move_id'] == move['id']

    def test_add_item_with_locations(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('搬家')
        item = cherry_pick_manager.add_item(move['id'], '电脑', before_location='书房', pack_location='纸箱1')
        assert item['before_location'] == '书房'
        assert item['pack_location'] == '纸箱1'
        assert item['after_location'] == ''

    def test_add_item_to_nonexistent_move(self, cherry_pick_manager):
        item = cherry_pick_manager.add_item('nonexistent', '物品')
        assert item is None

    def test_get_items(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('搬家')
        cherry_pick_manager.add_item(move['id'], '物品1')
        cherry_pick_manager.add_item(move['id'], '物品2')
        items = cherry_pick_manager.get_items(move['id'])
        assert len(items) == 2

    def test_update_item(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('搬家')
        item = cherry_pick_manager.add_item(move['id'], '书籍')
        updated = cherry_pick_manager.update_item(item['id'], {'before_location': '客厅'})
        assert updated is not None
        assert updated['before_location'] == '客厅'

    def test_update_nonexistent_item(self, cherry_pick_manager):
        result = cherry_pick_manager.update_item('nonexistent', {'name': '新名'})
        assert result is None

    def test_delete_item(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('搬家')
        item = cherry_pick_manager.add_item(move['id'], '待删除')
        cherry_pick_manager.delete_item(item['id'])
        items = cherry_pick_manager.get_items(move['id'])
        assert len(items) == 0

    def test_update_item_ignores_invalid_keys(self, cherry_pick_manager):
        move = cherry_pick_manager.create_move('搬家')
        item = cherry_pick_manager.add_item(move['id'], '测试')
        updated = cherry_pick_manager.update_item(item['id'], {'invalid_key': 'value', 'name': '新名'})
        assert updated['name'] == '新名'


class TestMomhandSync:
    """cherry_pick → momhand 同步测试"""

    def test_add_item_with_after_location_syncs_to_momhand(self, cherry_pick_manager, momhand_manager):
        move = cherry_pick_manager.create_move('搬家')
        item = cherry_pick_manager.add_item(
            move['id'], '电脑', after_location='新书房'
        )
        assert item is not None
        assert item['synced_to_momhand'] is True
        assert 'momhand_item_id' in item

        momhand_item = momhand_manager.get_item_by_id(item['momhand_item_id'])
        assert momhand_item is not None
        assert momhand_item['name'] == '电脑'
        assert momhand_item['location'] == '新书房'

    def test_add_item_without_after_location_no_sync(self, cherry_pick_manager, momhand_manager):
        move = cherry_pick_manager.create_move('搬家')
        item = cherry_pick_manager.add_item(move['id'], '书籍')
        assert item.get('synced_to_momhand') is False
        all_items = momhand_manager.get_all_items()
        assert len(all_items) == 0

    def test_update_item_triggers_sync(self, cherry_pick_manager, momhand_manager):
        move = cherry_pick_manager.create_move('搬家')
        item = cherry_pick_manager.add_item(move['id'], '台灯')
        updated = cherry_pick_manager.update_item(item['id'], {'after_location': '卧室'})
        assert updated['synced_to_momhand'] is True

        all_items = momhand_manager.get_all_items()
        assert len(all_items) == 1
        assert all_items[0]['location'] == '卧室'
