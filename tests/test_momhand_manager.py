"""
MomhandManager 单元测试
"""
import pytest


class TestItems:
    """物品 CRUD 测试"""

    def test_add_item(self, momhand_manager):
        item = momhand_manager.add_item({
            'name': '感冒药',
            'type': '药品',
            'location': '药箱',
            'usage': '感冒时吃'
        })
        assert item is not None
        assert item['name'] == '感冒药'
        assert item['type'] == '药品'
        assert item['location'] == '药箱'

    def test_add_item_defaults(self, momhand_manager):
        item = momhand_manager.add_item({'name': '测试物品'})
        assert item['type'] == '其他'
        assert item['usage'] == ''

    def test_get_all_items(self, momhand_manager):
        momhand_manager.add_item({'name': '物品1', 'location': '位置1'})
        momhand_manager.add_item({'name': '物品2', 'location': '位置2'})
        items = momhand_manager.get_all_items()
        assert len(items) == 2

    def test_get_item_by_id(self, momhand_manager):
        created = momhand_manager.add_item({'name': '测试', 'location': '这里'})
        item = momhand_manager.get_item_by_id(created['id'])
        assert item is not None
        assert item['name'] == '测试'

    def test_get_nonexistent_item(self, momhand_manager):
        item = momhand_manager.get_item_by_id(99999)
        assert item is None

    def test_delete_item(self, momhand_manager):
        created = momhand_manager.add_item({'name': '待删除'})
        result = momhand_manager.delete_item(created['id'])
        assert result['success'] is True
        assert momhand_manager.get_item_by_id(created['id']) is None

    def test_delete_nonexistent_item(self, momhand_manager):
        result = momhand_manager.delete_item(99999)
        assert result['success'] is False

    def test_update_item(self, momhand_manager):
        created = momhand_manager.add_item({'name': '旧名', 'location': '旧位置'})
        updated = momhand_manager.update_item(created['id'], {'name': '新名', 'location': '新位置'})
        assert updated is not None
        assert updated['name'] == '新名'
        assert updated['location'] == '新位置'

    def test_update_item_partial(self, momhand_manager):
        created = momhand_manager.add_item({'name': '测试', 'type': '工具', 'location': '工具箱'})
        updated = momhand_manager.update_item(created['id'], {'location': '抽屉'})
        assert updated['name'] == '测试'
        assert updated['location'] == '抽屉'

    def test_update_item_no_valid_fields(self, momhand_manager):
        created = momhand_manager.add_item({'name': '测试'})
        result = momhand_manager.update_item(created['id'], {'invalid': 'value'})
        assert result is None

    def test_update_location(self, momhand_manager):
        created = momhand_manager.add_item({'name': '测试', 'location': '旧位置'})
        updated = momhand_manager.update_location(created['id'], '新位置')
        assert updated['location'] == '新位置'


class TestSearch:
    """搜索测试"""

    def test_search_by_name(self, momhand_manager):
        momhand_manager.add_item({'name': '感冒药', 'type': '药品', 'location': '药箱'})
        momhand_manager.add_item({'name': '锤子', 'type': '工具', 'location': '工具箱'})
        results = momhand_manager.search_items('感冒')
        assert len(results) == 1
        assert results[0]['name'] == '感冒药'

    def test_search_by_location(self, momhand_manager):
        momhand_manager.add_item({'name': '物品1', 'location': '客厅'})
        momhand_manager.add_item({'name': '物品2', 'location': '卧室'})
        results = momhand_manager.search_items('客厅')
        assert len(results) == 1

    def test_search_by_type(self, momhand_manager):
        momhand_manager.add_item({'name': '感冒药', 'type': '药品'})
        momhand_manager.add_item({'name': '锤子', 'type': '工具'})
        results = momhand_manager.search_items('药品')
        assert len(results) == 1

    def test_search_no_results(self, momhand_manager):
        momhand_manager.add_item({'name': '测试'})
        results = momhand_manager.search_items('不存在的东西')
        assert len(results) == 0


class TestStatistics:
    """统计信息测试"""

    def test_statistics_empty(self, momhand_manager):
        stats = momhand_manager.get_statistics()
        assert stats['total'] == 0
        assert stats['expiring_soon'] == 0
        assert stats['expired'] == 0

    def test_statistics_total(self, momhand_manager):
        momhand_manager.add_item({'name': '物品1'})
        momhand_manager.add_item({'name': '物品2'})
        stats = momhand_manager.get_statistics()
        assert stats['total'] == 2

    def test_statistics_by_location(self, momhand_manager):
        momhand_manager.add_item({'name': '物品1', 'location': '客厅'})
        momhand_manager.add_item({'name': '物品2', 'location': '客厅'})
        momhand_manager.add_item({'name': '物品3', 'location': '卧室'})
        stats = momhand_manager.get_statistics()
        assert stats['by_location']['客厅'] == 2
        assert stats['by_location']['卧室'] == 1
