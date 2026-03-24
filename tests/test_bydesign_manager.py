"""
ByDesignManager 单元测试
"""
import pytest


class TestChecklist:
    """通用检查清单测试"""

    def test_get_checklist_default(self, bydesign_manager):
        items = bydesign_manager.get_checklist()
        assert len(items) == 5
        assert items[0]['text'] == '关闭所有窗户'

    def test_add_checklist_item(self, bydesign_manager):
        item = bydesign_manager.add_checklist_item('带钥匙')
        assert item is not None
        assert item['text'] == '带钥匙'
        assert item['completed'] is False
        assert 'id' in item

    def test_add_duplicate_checklist_item(self, bydesign_manager):
        bydesign_manager.add_checklist_item('测试项')
        duplicate = bydesign_manager.add_checklist_item('测试项')
        assert duplicate is None

    def test_add_duplicate_case_insensitive(self, bydesign_manager):
        bydesign_manager.add_checklist_item('Test Item')
        duplicate = bydesign_manager.add_checklist_item('test item')
        assert duplicate is None

    def test_update_checklist_item(self, bydesign_manager):
        items = bydesign_manager.get_checklist()
        item_id = items[0]['id']
        updated = bydesign_manager.update_checklist_item(item_id, {'completed': True})
        assert updated is not None
        assert updated['completed'] is True

    def test_update_nonexistent_item(self, bydesign_manager):
        result = bydesign_manager.update_checklist_item('nonexistent-id', {'completed': True})
        assert result is None

    def test_delete_checklist_item(self, bydesign_manager):
        items = bydesign_manager.get_checklist()
        original_count = len(items)
        item_id = items[0]['id']
        bydesign_manager.delete_checklist_item(item_id)
        assert len(bydesign_manager.get_checklist()) == original_count - 1

    def test_reset_checklist(self, bydesign_manager):
        items = bydesign_manager.get_checklist()
        bydesign_manager.update_checklist_item(items[0]['id'], {'completed': True})
        bydesign_manager.reset_checklist()
        for item in bydesign_manager.get_checklist():
            assert item['completed'] is False

    def test_add_checklist_items_batch(self, bydesign_manager):
        texts = ['带雨伞', '带充电宝', '关闭所有窗户']  # last one is a default duplicate
        added = bydesign_manager.add_checklist_items_batch(texts)
        assert len(added) == 2  # 关闭所有窗户 is duplicate


class TestTrips:
    """出行记录测试"""

    def test_create_trip(self, bydesign_manager):
        trip = bydesign_manager.create_trip('北京出差', '为期3天')
        assert trip['name'] == '北京出差'
        assert trip['description'] == '为期3天'
        assert trip['status'] == 'planning'
        assert 'id' in trip
        assert 'checklist_snapshot' in trip
        assert len(trip['checklist_snapshot']) == 5

    def test_get_all_trips(self, bydesign_manager):
        bydesign_manager.create_trip('出行1')
        bydesign_manager.create_trip('出行2')
        trips = bydesign_manager.get_all_trips()
        assert len(trips) == 2

    def test_get_trip(self, bydesign_manager):
        created = bydesign_manager.create_trip('测试出行')
        trip = bydesign_manager.get_trip(created['id'])
        assert trip is not None
        assert trip['name'] == '测试出行'

    def test_get_nonexistent_trip(self, bydesign_manager):
        trip = bydesign_manager.get_trip('nonexistent-id')
        assert trip is None

    def test_add_custom_item(self, bydesign_manager):
        trip = bydesign_manager.create_trip('出差')
        item = bydesign_manager.add_custom_item(trip['id'], '带护照')
        assert item is not None
        assert item['text'] == '带护照'

    def test_add_custom_item_to_nonexistent_trip(self, bydesign_manager):
        item = bydesign_manager.add_custom_item('nonexistent', '带护照')
        assert item is None

    def test_update_trip_item_checklist(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试')
        item_id = trip['checklist_snapshot'][0]['id']
        updated = bydesign_manager.update_trip_item(trip['id'], item_id, {'completed': True})
        assert updated['completed'] is True

    def test_update_trip_item_custom(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试')
        custom = bydesign_manager.add_custom_item(trip['id'], '测试项')
        updated = bydesign_manager.update_trip_item(trip['id'], custom['id'], {'completed': True}, is_custom=True)
        assert updated['completed'] is True

    def test_delete_trip(self, bydesign_manager):
        trip = bydesign_manager.create_trip('待删除')
        bydesign_manager.delete_trip(trip['id'])
        assert bydesign_manager.get_trip(trip['id']) is None

    def test_complete_trip(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试完成')
        completed = bydesign_manager.complete_trip(trip['id'])
        assert completed['status'] == 'completed'
        assert 'completed_at' in completed

    def test_get_trip_progress(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试进度')
        bydesign_manager.add_custom_item(trip['id'], '自定义项')
        progress = bydesign_manager.get_trip_progress(trip['id'])
        assert progress['checklist']['total'] == 5
        assert progress['custom']['total'] == 1
        assert progress['overall']['total'] == 6
        assert progress['overall']['done'] == 0

    def test_get_trip_progress_nonexistent(self, bydesign_manager):
        result = bydesign_manager.get_trip_progress('nonexistent')
        assert result is None

    def test_update_trip_checklist_item(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试')
        item_id = trip['checklist_snapshot'][0]['id']
        updated = bydesign_manager.update_trip_checklist_item(trip['id'], item_id, {'completed': True})
        assert updated is not None
        assert updated['completed'] is True

    def test_update_trip_checklist_item_nonexistent_trip(self, bydesign_manager):
        result = bydesign_manager.update_trip_checklist_item('bad-id', 'item-id', {'completed': True})
        assert result is None

    def test_update_trip_checklist_item_nonexistent_item(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试')
        result = bydesign_manager.update_trip_checklist_item(trip['id'], 'bad-item', {'completed': True})
        assert result is None

    def test_update_trip_custom_item(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试')
        custom = bydesign_manager.add_custom_item(trip['id'], '带护照')
        updated = bydesign_manager.update_trip_custom_item(trip['id'], custom['id'], {'completed': True})
        assert updated is not None
        assert updated['completed'] is True

    def test_update_trip_custom_item_nonexistent(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试')
        result = bydesign_manager.update_trip_custom_item(trip['id'], 'bad-id', {'completed': True})
        assert result is None

    def test_delete_trip_custom_item(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试')
        custom = bydesign_manager.add_custom_item(trip['id'], '待删除项')
        result = bydesign_manager.delete_trip_custom_item(trip['id'], custom['id'])
        assert result is True
        refreshed = bydesign_manager.get_trip(trip['id'])
        assert len(refreshed['custom_items']) == 0

    def test_delete_trip_custom_item_nonexistent_trip(self, bydesign_manager):
        result = bydesign_manager.delete_trip_custom_item('bad-id', 'item-id')
        assert result is False


class TestTemplates:
    """模板管理测试"""

    def test_get_templates_empty(self, bydesign_manager):
        templates = bydesign_manager.get_templates()
        assert templates == []

    def test_create_template(self, bydesign_manager):
        items = [{'text': '带身份证'}, {'text': '带充电宝'}]
        template = bydesign_manager.create_template('出差模板', items)
        assert template['name'] == '出差模板'
        assert len(template['items']) == 2

    def test_create_template_dedup(self, bydesign_manager):
        items = [{'text': '带身份证'}, {'text': '带身份证'}, {'text': '带充电宝'}]
        template = bydesign_manager.create_template('去重测试', items)
        assert len(template['items']) == 2

    def test_delete_template(self, bydesign_manager):
        template = bydesign_manager.create_template('待删除', [{'text': '项1'}])
        bydesign_manager.delete_template(template['id'])
        assert len(bydesign_manager.get_templates()) == 0

    def test_import_template_to_trip(self, bydesign_manager):
        template = bydesign_manager.create_template('导入模板', [{'text': '带护照'}, {'text': '换外币'}])
        trip = bydesign_manager.create_trip('出国')
        result = bydesign_manager.import_template_to_trip(trip['id'], template['id'])
        assert result is not None
        assert result['imported'] == 2
        assert result['skipped'] == 0

    def test_import_template_dedup(self, bydesign_manager):
        template = bydesign_manager.create_template('模板', [{'text': '关闭所有窗户'}])
        trip = bydesign_manager.create_trip('测试')
        result = bydesign_manager.import_template_to_trip(trip['id'], template['id'])
        assert result['imported'] == 0
        assert result['skipped'] == 1

    def test_import_template_nonexistent_trip(self, bydesign_manager):
        template = bydesign_manager.create_template('模板', [{'text': '项1'}])
        result = bydesign_manager.import_template_to_trip('nonexistent', template['id'])
        assert result is None

    def test_import_nonexistent_template(self, bydesign_manager):
        trip = bydesign_manager.create_trip('测试')
        result = bydesign_manager.import_template_to_trip(trip['id'], 'nonexistent')
        assert result is None
