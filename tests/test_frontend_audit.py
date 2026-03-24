"""
前端功能审计测试

使用正则表达式解析 HTML/JS 文件，验证：
1. 所有 onclick 处理器引用的函数都已定义
2. 所有页面的按钮行为一致
3. 共享组件行为一致
"""
import re
from pathlib import Path

import pytest

WWW_DIR = Path(__file__).parent.parent / 'www'
JS_DIR = WWW_DIR / 'js'


def extract_onclick_functions(html_content):
    """提取 HTML 中所有 onclick 调用的函数名"""
    pattern = r'onclick="([^"]+)"'
    matches = re.findall(pattern, html_content)
    functions = set()
    for match in matches:
        # 提取函数名（忽略参数）
        func_match = re.match(r'(\w+)\s*\(', match)
        if func_match:
            functions.add(func_match.group(1))
    return functions


def extract_defined_functions(content):
    """提取 JS/HTML 中定义的函数名"""
    patterns = [
        r'function\s+(\w+)\s*\(',           # function name(
        r'(\w+)\s*=\s*function\s*\(',        # name = function(
        r'(\w+)\s*=\s*async\s+function\s*\(',  # name = async function(
        r'async\s+function\s+(\w+)\s*\(',    # async function name(
        r'window\.(\w+)\s*=\s*(?:async\s+)?function',  # window.name = function
    ]
    functions = set()
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            functions.add(match.group(1))
    return functions


def read_file(path):
    return path.read_text(encoding='utf-8')


class TestHomepage:
    """首页功能测试"""

    @pytest.fixture
    def content(self):
        return read_file(WWW_DIR / 'index.html')

    def test_all_onclick_functions_defined(self, content):
        onclick_funcs = extract_onclick_functions(content)
        defined_funcs = extract_defined_functions(content)
        missing = onclick_funcs - defined_funcs
        assert not missing, f'首页缺少函数定义: {missing}'

    def test_has_send_message(self, content):
        assert 'sendMessage' in extract_defined_functions(content)

    def test_has_fill_example(self, content):
        assert 'fillExample' in extract_defined_functions(content)

    def test_has_show_settings(self, content):
        assert 'showSettings' in extract_defined_functions(content)

    def test_has_clear_history(self, content):
        assert 'clearHistory' in extract_defined_functions(content)

    def test_has_show_logs(self, content):
        assert 'showLogs' in extract_defined_functions(content)

    def test_has_show_version(self, content):
        assert 'showVersion' in extract_defined_functions(content)

    def test_enter_key_handler(self, content):
        assert "key === 'Enter'" in content or 'key === "Enter"' in content

    def test_escape_html_defined(self, content):
        assert 'escapeHtml' in extract_defined_functions(content)


class TestByDesign:
    """By Design 页面功能测试"""

    @pytest.fixture
    def content(self):
        return read_file(WWW_DIR / 'bydesign' / 'index.html')

    @pytest.fixture
    def agent_chat(self):
        return read_file(JS_DIR / 'agent-chat.js')

    def test_all_onclick_functions_defined(self, content, agent_chat):
        onclick_funcs = extract_onclick_functions(content)
        defined_funcs = extract_defined_functions(content) | extract_defined_functions(agent_chat)
        missing = onclick_funcs - defined_funcs
        assert not missing, f'By Design 缺少函数定义: {missing}'

    def test_has_crud_functions(self, content):
        funcs = extract_defined_functions(content)
        required = ['addChecklistItem', 'deleteChecklistItem', 'createTrip', 'deleteTrip', 'viewTrip']
        for func in required:
            assert func in funcs, f'缺少函数: {func}'

    def test_has_template_functions(self, content):
        funcs = extract_defined_functions(content)
        required = ['createTemplate', 'deleteTemplate', 'importTemplate', 'showTemplatesModal']
        for func in required:
            assert func in funcs, f'缺少函数: {func}'

    def test_init_agent_chat_called(self, content):
        assert 'initAgentChat' in content

    def test_has_default_system_prompt(self, content):
        assert 'DEFAULT_SYSTEM_PROMPT' in content


class TestCherryPick:
    """Cherry Pick 页面功能测试"""

    @pytest.fixture
    def content(self):
        return read_file(WWW_DIR / 'cherry-pick' / 'index.html')

    @pytest.fixture
    def agent_chat(self):
        return read_file(JS_DIR / 'agent-chat.js')

    def test_all_onclick_functions_defined(self, content, agent_chat):
        onclick_funcs = extract_onclick_functions(content)
        defined_funcs = extract_defined_functions(content) | extract_defined_functions(agent_chat)
        missing = onclick_funcs - defined_funcs
        assert not missing, f'Cherry Pick 缺少函数定义: {missing}'

    def test_has_crud_functions(self, content):
        funcs = extract_defined_functions(content)
        required = ['createMove', 'deleteMove', 'addItem', 'deleteItem', 'updateItem']
        for func in required:
            assert func in funcs, f'缺少函数: {func}'

    def test_init_agent_chat_called(self, content):
        assert 'initAgentChat' in content


class TestMomhand:
    """Momhand 页面功能测试"""

    @pytest.fixture
    def content(self):
        return read_file(WWW_DIR / 'momhand' / 'index.html')

    @pytest.fixture
    def agent_chat(self):
        return read_file(JS_DIR / 'agent-chat.js')

    def test_all_onclick_functions_defined(self, content, agent_chat):
        onclick_funcs = extract_onclick_functions(content)
        defined_funcs = extract_defined_functions(content) | extract_defined_functions(agent_chat)
        missing = onclick_funcs - defined_funcs
        assert not missing, f'Momhand 缺少函数定义: {missing}'

    def test_has_crud_functions(self, content):
        funcs = extract_defined_functions(content)
        required = ['loadItems', 'loadStats', 'quickSearch']
        for func in required:
            assert func in funcs, f'缺少函数: {func}'

    def test_has_edit_delete_via_window(self, content):
        assert 'window.deleteItem' in content
        assert 'window.editItem' in content

    def test_search_debounce(self, content):
        assert 'searchTimeout' in content or 'setTimeout' in content


class TestSiriDream:
    """Siri Dream 页面功能测试"""

    @pytest.fixture
    def content(self):
        return read_file(WWW_DIR / 'siri-dream' / 'index.html')

    @pytest.fixture
    def agent_chat(self):
        return read_file(JS_DIR / 'agent-chat.js')

    def test_all_onclick_functions_defined(self, content, agent_chat):
        onclick_funcs = extract_onclick_functions(content)
        defined_funcs = extract_defined_functions(content) | extract_defined_functions(agent_chat)
        missing = onclick_funcs - defined_funcs
        assert not missing, f'Siri Dream 缺少函数定义: {missing}'

    def test_has_core_functions(self, content):
        funcs = extract_defined_functions(content)
        required = ['sendTestMessage', 'deleteMessage', 'refreshMessages', 'loadMessages']
        for func in required:
            assert func in funcs, f'缺少函数: {func}'

    def test_auto_refresh(self, content):
        assert 'setInterval' in content

    def test_init_agent_chat_called(self, content):
        assert 'initAgentChat' in content


class TestAgentChat:
    """共享聊天组件测试"""

    @pytest.fixture
    def content(self):
        return read_file(JS_DIR / 'agent-chat.js')

    def test_exports_init(self, content):
        assert 'window.initAgentChat' in content

    def test_exports_fill_example(self, content):
        assert 'window.fillExample' in content

    def test_exports_send_message(self, content):
        assert 'window.sendMessage' in content

    def test_exports_show_settings(self, content):
        assert 'window.showSettings' in content

    def test_exports_hide_settings(self, content):
        assert 'window.hideSettings' in content

    def test_exports_save_settings(self, content):
        assert 'window.saveSettings' in content

    def test_exports_reset_prompt(self, content):
        assert 'window.resetPrompt' in content

    def test_has_stream_steps_for_all_projects(self, content):
        assert "'bydesign'" in content
        assert "'cherry_pick'" in content
        assert "'momhand'" in content

    def test_has_theme_colors_for_all_projects(self, content):
        assert "'bydesign'" in content
        assert "'cherry_pick'" in content
        assert "'momhand'" in content


class TestConsistency:
    """跨页面一致性测试"""

    @pytest.fixture
    def pages(self):
        return {
            'bydesign': read_file(WWW_DIR / 'bydesign' / 'index.html'),
            'cherry_pick': read_file(WWW_DIR / 'cherry-pick' / 'index.html'),
            'momhand': read_file(WWW_DIR / 'momhand' / 'index.html'),
            'siri_dream': read_file(WWW_DIR / 'siri-dream' / 'index.html'),
        }

    def test_all_pages_load_agent_chat(self, pages):
        for name, content in pages.items():
            assert 'agent-chat.js' in content, f'{name} 未加载 agent-chat.js'

    def test_all_pages_load_transitions_css(self, pages):
        for name, content in pages.items():
            assert 'transitions.css' in content, f'{name} 未加载 transitions.css'

    def test_all_pages_load_tailwind(self, pages):
        for name, content in pages.items():
            assert 'tailwindcss' in content, f'{name} 未加载 TailwindCSS'

    def test_all_pages_have_back_link(self, pages):
        for name, content in pages.items():
            assert '返回首页' in content, f'{name} 缺少返回首页链接'

    def test_all_pages_have_fab_button(self, pages):
        for name, content in pages.items():
            assert 'togglePanel' in content, f'{name} 缺少 FAB 按钮'

    def test_all_pages_have_settings_modal(self, pages):
        for name, content in pages.items():
            assert 'settingsModal' in content, f'{name} 缺少设置弹窗'

    def test_all_pages_have_escape_html(self, pages):
        for name, content in pages.items():
            assert 'escapeHtml' in content, f'{name} 缺少 escapeHtml'

    def test_all_subpages_call_init_agent_chat(self, pages):
        for name, content in pages.items():
            assert 'initAgentChat' in content, f'{name} 未调用 initAgentChat'

    def test_settings_modal_uses_glass_card(self, pages):
        """验证所有页面的设置弹窗使用 glass-card 类"""
        for name, content in pages.items():
            # 查找 settingsModal 内部是否有 glass-card 或 bg-white
            modal_match = re.search(r'id="settingsModal".*?</div>\s*</div>\s*</div>', content, re.DOTALL)
            if modal_match:
                modal_html = modal_match.group()
                if 'bg-white' in modal_html and 'glass-card' not in modal_html:
                    pytest.fail(f'{name} 设置弹窗使用 bg-white 而非 glass-card (不一致)')

    def test_save_button_text_consistent(self, pages):
        """验证保存按钮文本一致"""
        save_patterns = []
        for name, content in pages.items():
            # 查找 saveSettings 按钮的文本
            match = re.search(r'onclick="saveSettings\(\)"[^>]*>(.*?)</button>', content, re.DOTALL)
            if match:
                text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                save_patterns.append((name, text))

        # 检查是否所有页面的保存按钮文本一致
        if len(save_patterns) > 1:
            texts = [t for _, t in save_patterns]
            if len(set(texts)) > 1:
                details = ', '.join(f'{n}: "{t}"' for n, t in save_patterns)
                pytest.fail(f'保存按钮文本不一致: {details}')
