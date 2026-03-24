"""
Siri Dream Manager 单元测试
"""
import pytest
import siri_dream_manager as sdm


class TestMessages:
    """消息管理测试"""

    def test_add_message(self, siri_dream_data_dir):
        msg = sdm.add_message('测试消息')
        assert msg is not None
        assert msg['text'] == '测试消息'
        assert msg['status'] == 'pending'
        assert 'id' in msg

    def test_add_message_with_metadata(self, siri_dream_data_dir):
        msg = sdm.add_message('测试', source='web', metadata={'user': 'test'})
        assert msg['source'] == 'web'
        assert msg['metadata']['user'] == 'test'

    def test_get_messages(self, siri_dream_data_dir):
        sdm.add_message('消息1')
        sdm.add_message('消息2')
        messages = sdm.get_messages()
        assert len(messages) == 2

    def test_get_messages_limit(self, siri_dream_data_dir):
        for i in range(5):
            sdm.add_message(f'消息{i}')
        messages = sdm.get_messages(limit=3)
        assert len(messages) == 3

    def test_get_messages_offset(self, siri_dream_data_dir):
        for i in range(5):
            sdm.add_message(f'消息{i}')
        messages = sdm.get_messages(limit=2, offset=2)
        assert len(messages) == 2

    def test_get_message(self, siri_dream_data_dir):
        created = sdm.add_message('测试')
        msg = sdm.get_message(created['id'])
        assert msg is not None
        assert msg['text'] == '测试'

    def test_get_nonexistent_message(self, siri_dream_data_dir):
        msg = sdm.get_message('nonexistent')
        assert msg is None

    def test_update_message_status(self, siri_dream_data_dir):
        msg = sdm.add_message('测试')
        sdm.update_message_status(msg['id'], 'completed', result={'data': '结果'})
        updated = sdm.get_message(msg['id'])
        assert updated['status'] == 'completed'
        assert updated['result']['data'] == '结果'

    def test_delete_message(self, siri_dream_data_dir):
        msg = sdm.add_message('待删除')
        sdm.delete_message(msg['id'])
        assert sdm.get_message(msg['id']) is None

    def test_clear_messages(self, siri_dream_data_dir):
        sdm.add_message('消息1')
        sdm.add_message('消息2')
        sdm.clear_messages()
        assert len(sdm.get_messages()) == 0

    def test_message_limit_100(self, siri_dream_data_dir):
        for i in range(105):
            sdm.add_message(f'消息{i}')
        messages = sdm.load_messages()
        assert len(messages) <= 100


class TestStatistics:
    """统计信息测试"""

    def test_statistics_empty(self, siri_dream_data_dir):
        stats = sdm.get_statistics()
        assert stats['total'] == 0
        assert stats['pending'] == 0

    def test_statistics_counts(self, siri_dream_data_dir):
        msg1 = sdm.add_message('消息1')
        msg2 = sdm.add_message('消息2')
        sdm.update_message_status(msg1['id'], 'completed')
        sdm.update_message_status(msg2['id'], 'failed')
        sdm.add_message('消息3')

        stats = sdm.get_statistics()
        assert stats['total'] == 3
        assert stats['completed'] == 1
        assert stats['failed'] == 1
        assert stats['pending'] == 1


class TestSettings:
    """设置管理测试"""

    def test_load_default_settings(self, siri_dream_data_dir):
        settings = sdm.load_settings()
        assert 'system_prompt' in settings

    def test_save_settings(self, siri_dream_data_dir):
        sdm.save_settings({'system_prompt': '自定义提示词', 'extra': 'value'})
        settings = sdm.load_settings()
        assert settings['system_prompt'] == '自定义提示词'

    def test_get_system_prompt_default(self, siri_dream_data_dir):
        prompt = sdm.get_system_prompt()
        assert prompt == sdm.DEFAULT_SYSTEM_PROMPT

    def test_save_system_prompt(self, siri_dream_data_dir):
        sdm.save_system_prompt('新提示词')
        prompt = sdm.get_system_prompt()
        assert prompt == '新提示词'
