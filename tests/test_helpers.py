"""
Helper utilities for testing.
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import json

from src.control.asusctl_interface import FanCurve, FanCurvePoint


def create_test_fan_curve():
    """Create a test fan curve."""
    return FanCurve([
        FanCurvePoint(30, 20),
        FanCurvePoint(50, 50),
        FanCurvePoint(70, 80)
    ])


def create_test_profile(name="Test Profile", description="Test"):
    """Create a test profile."""
    from src.control.profile_manager import SavedProfile
    
    return SavedProfile(
        name=name,
        description=description,
        cpu_fan_curve=create_test_fan_curve()
    )


def mock_asusctl_success():
    """Create a mock subprocess.run that simulates successful asusctl call."""
    def _mock_run(cmd, **kwargs):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        return mock_result
    return _mock_run


def mock_asusctl_profile_output(profile="Balanced"):
    """Create mock asusctl profile output."""
    def _mock_run(cmd, **kwargs):
        mock_result = Mock()
        mock_result.returncode = 0
        if 'profile' in cmd and '-p' in cmd:
            mock_result.stdout = profile
        else:
            mock_result.stdout = ""
        return mock_result
    return _mock_run

