"""
共享的测试配置和 fixtures

所有 manager 模块在 import 时都会尝试访问 /root 路径，
需要在 import 之前 patch 相关 Path 方法以避免 PermissionError。
"""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ---- 全局 patch: 让 /root 路径操作安全地失败 ----
_original_mkdir = Path.mkdir
_original_exists = Path.exists
_original_stat = os.stat
_original_sqlite_connect = sqlite3.connect
_temp_db = tempfile.mktemp(suffix='.db')


def _safe_mkdir(self, *args, **kwargs):
    if str(self).startswith('/root'):
        return
    _original_mkdir(self, *args, **kwargs)


def _safe_exists(self):
    if str(self).startswith('/root'):
        return False
    return _original_exists(self)


def _safe_stat(path, *args, **kwargs):
    if str(path).startswith('/root'):
        raise FileNotFoundError(f'mocked: {path}')
    return _original_stat(path, *args, **kwargs)


def _safe_sqlite_connect(db_path, *args, **kwargs):
    if str(db_path).startswith('/root'):
        return _original_sqlite_connect(_temp_db, *args, **kwargs)
    return _original_sqlite_connect(db_path, *args, **kwargs)


# 在 conftest 加载时立即 patch
_patches = [
    patch.object(Path, 'mkdir', _safe_mkdir),
    patch.object(Path, 'exists', _safe_exists),
    patch('os.stat', _safe_stat),
    patch('sqlite3.connect', _safe_sqlite_connect),
]
for p in _patches:
    p.start()

# 现在安全地 import 所有 manager 模块
import bydesign_manager as _bd_mod
import cherry_pick_manager as _cp_mod
import momhand_manager_db as _mh_mod
import siri_dream_manager as _sd_mod

# 恢复原始方法
for p in _patches:
    p.stop()

# 清理临时数据库
import atexit
atexit.register(lambda: os.unlink(_temp_db) if os.path.exists(_temp_db) else None)


@pytest.fixture
def tmp_data_dir(tmp_path):
    """提供一个临时数据目录"""
    return tmp_path


@pytest.fixture
def bydesign_manager(tmp_data_dir, monkeypatch):
    """提供一个使用临时目录的 ByDesignManager 实例"""
    monkeypatch.setattr(_bd_mod, 'DATA_DIR', tmp_data_dir)
    monkeypatch.setattr(_bd_mod, 'CHECKLIST_FILE', tmp_data_dir / 'checklist.json')
    monkeypatch.setattr(_bd_mod, 'TRIPS_FILE', tmp_data_dir / 'trips.json')
    monkeypatch.setattr(_bd_mod, 'TEMPLATES_FILE', tmp_data_dir / 'templates.json')
    return _bd_mod.ByDesignManager()


@pytest.fixture
def cherry_pick_manager(tmp_data_dir, monkeypatch):
    """提供一个使用临时目录的 CherryPickManager 实例"""
    monkeypatch.setattr(_cp_mod, 'DATA_DIR', tmp_data_dir)
    monkeypatch.setattr(_cp_mod, 'DB_FILE', tmp_data_dir / 'moves.json')
    monkeypatch.setattr(_cp_mod, 'MOMHAND_FILE', tmp_data_dir / 'momhand.db')
    return _cp_mod.CherryPickManager()


@pytest.fixture
def momhand_db_path(tmp_data_dir):
    """提供临时 SQLite 数据库路径"""
    return tmp_data_dir / 'momhand_test.db'


@pytest.fixture
def momhand_manager(momhand_db_path, monkeypatch):
    """提供一个使用临时数据库的 MomhandManager 实例"""
    monkeypatch.setattr(_mh_mod, 'DB_FILE', momhand_db_path)
    return _mh_mod.MomhandManager()


@pytest.fixture
def siri_dream_data_dir(tmp_data_dir, monkeypatch):
    """提供临时 Siri Dream 数据目录"""
    monkeypatch.setattr(_sd_mod, 'DATA_DIR', tmp_data_dir)
    monkeypatch.setattr(_sd_mod, 'MESSAGES_FILE', tmp_data_dir / 'messages.json')
    monkeypatch.setattr(_sd_mod, 'SETTINGS_FILE', tmp_data_dir / 'settings.json')
    return tmp_data_dir
