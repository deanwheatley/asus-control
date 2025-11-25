"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from collections import deque

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Mock subprocess.run for testing."""
    def _mock_run(*args, **kwargs):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        return mock_result
    
    monkeypatch.setattr("subprocess.run", _mock_run)
    return _mock_run


@pytest.fixture
def mock_psutil(monkeypatch):
    """Mock psutil for testing."""
    mock_cpu = Mock()
    mock_cpu.percent = 45.0
    mock_cpu.freq = Mock(current=2400.0)
    
    mock_vmem = Mock()
    mock_vmem.percent = 50.0
    mock_vmem.used = 4 * (1024 ** 3)  # 4 GB
    mock_vmem.total = 8 * (1024 ** 3)  # 8 GB
    
    mock_swap = Mock()
    mock_swap.percent = 10.0
    
    def mock_cpu_percent(*args, **kwargs):
        return 45.0
    
    def mock_cpu_percent_percpu(*args, **kwargs):
        return [45.0, 50.0, 40.0, 45.0]
    
    def mock_cpu_freq():
        return mock_cpu.freq
    
    def mock_virtual_memory():
        return mock_vmem
    
    def mock_swap_memory():
        return mock_swap
    
    monkeypatch.setattr("psutil.cpu_percent", mock_cpu_percent)
    monkeypatch.setattr("psutil.cpu_freq", mock_cpu_freq)
    monkeypatch.setattr("psutil.virtual_memory", mock_virtual_memory)
    monkeypatch.setattr("psutil.swap_memory", mock_swap_memory)
    
    return {
        'cpu_percent': mock_cpu_percent,
        'cpu_freq': mock_cpu_freq,
        'virtual_memory': mock_virtual_memory,
        'swap_memory': mock_swap_memory,
    }


@pytest.fixture
def mock_file_system(monkeypatch, tmp_path):
    """Mock file system operations."""
    # Mock Path.home() to return temp directory
    mock_home = tmp_path / "home" / "user"
    mock_home.mkdir(parents=True)
    
    monkeypatch.setattr("pathlib.Path.home", lambda: mock_home)
    
    return mock_home


@pytest.fixture
def qapp(qtbot):
    """Create QApplication for UI tests."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

