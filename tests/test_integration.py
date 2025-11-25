"""
Integration tests for the application.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from src.monitoring.system_monitor import SystemMonitor
from src.control.profile_manager import ProfileManager, SavedProfile
from src.control.asusctl_interface import FanCurve, get_preset_curve
from src.utils.dependency_checker import DependencyChecker


@pytest.mark.integration
class TestSystemMonitoringIntegration:
    """Integration tests for system monitoring."""
    
    @patch('src.monitoring.system_monitor.psutil')
    def test_full_monitoring_cycle(self, mock_psutil):
        """Test complete monitoring cycle."""
        # Setup mocks
        mock_psutil.cpu_percent.return_value = 50.0
        mock_freq = Mock()
        mock_freq.current = 2400.0
        mock_psutil.cpu_freq.return_value = mock_freq
        
        mock_mem = Mock()
        mock_mem.percent = 50.0
        mock_mem.used = 4 * (1024 ** 3)
        mock_mem.total = 8 * (1024 ** 3)
        mock_psutil.virtual_memory.return_value = mock_mem
        
        mock_swap = Mock()
        mock_swap.percent = 10.0
        mock_psutil.swap_memory.return_value = mock_swap
        
        monitor = SystemMonitor(update_interval=0.1, history_size=10)
        
        # Update metrics multiple times
        for _ in range(5):
            monitor.update_metrics()
        
        # Check metrics
        metrics = monitor.get_metrics()
        assert metrics['cpu_percent'] == 50.0
        assert metrics['memory_percent'] == 50.0
        
        # Check history
        history = monitor.get_history()
        assert len(history['cpu_percent']) >= 5
        assert len(history['timestamp']) >= 5


@pytest.mark.integration
class TestProfileManagementIntegration:
    """Integration tests for profile management."""
    
    def test_profile_save_load_cycle(self, tmp_path):
        """Test complete profile save/load cycle."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        # Create a profile with fan curves
        cpu_curve = get_preset_curve('balanced')
        
        profile = SavedProfile(
            name="Test Profile",
            description="Integration test profile",
            cpu_fan_curve=cpu_curve
        )
        
        # Save
        assert manager.save_profile(profile) == True
        
        # Load
        loaded = manager.load_profile("Test Profile")
        assert loaded is not None
        assert loaded.name == "Test Profile"
        assert loaded.cpu_fan_curve is not None
        assert len(loaded.cpu_fan_curve.points) == len(cpu_curve.points)
        
        # Export
        export_path = tmp_path / "export.json"
        assert manager.export_profile("Test Profile", export_path, 'json') == True
        assert export_path.exists()
        
        # Import
        imported = manager.import_profile(export_path)
        assert imported is not None
        assert imported.name == "Test Profile"


@pytest.mark.integration
class TestFanCurveWorkflow:
    """Integration tests for fan curve workflow."""
    
    def test_preset_to_profile_workflow(self, tmp_path):
        """Test workflow from preset to saved profile."""
        # Get preset
        preset = get_preset_curve('balanced')
        assert len(preset.points) > 0
        
        # Modify preset
        preset.add_point(55, 55)
        assert len(preset.points) > 3  # Should have original + 1
        
        # Save as profile
        manager = ProfileManager(profiles_dir=tmp_path)
        profile = SavedProfile(
            name="Modified Balanced",
            cpu_fan_curve=preset
        )
        
        assert manager.save_profile(profile) == True
        
        # Verify save
        loaded = manager.load_profile("Modified Balanced")
        assert loaded.cpu_fan_curve is not None
        assert any(p.temperature == 55 for p in loaded.cpu_fan_curve.points)

