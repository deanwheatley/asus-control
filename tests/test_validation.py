"""
Tests for data validation logic.
"""

import pytest
from src.control.asusctl_interface import FanCurve, FanCurvePoint


class TestFanCurveValidation:
    """Test fan curve validation rules."""
    
    def test_curve_must_have_minimum_points(self):
        """Test that curve requires at least 2 points."""
        with pytest.raises(ValueError, match="at least 2"):
            FanCurve([FanCurvePoint(50, 50)])
    
    def test_curve_rejects_decreasing_speeds(self):
        """Test that curve rejects non-monotonic fan speeds."""
        points = [
            FanCurvePoint(30, 50),
            FanCurvePoint(50, 60),
            FanCurvePoint(70, 45)  # Decreasing!
        ]
        
        with pytest.raises(ValueError, match="decrease"):
            FanCurve(points)
    
    def test_curve_allows_equal_speeds(self):
        """Test that curve allows equal fan speeds."""
        points = [
            FanCurvePoint(30, 50),
            FanCurvePoint(50, 50),  # Equal speed is OK
            FanCurvePoint(70, 60)
        ]
        
        curve = FanCurve(points)
        assert len(curve.points) == 3
    
    def test_curve_rejects_duplicate_temperatures(self):
        """Test that curve rejects duplicate temperatures."""
        points = [
            FanCurvePoint(50, 50),
            FanCurvePoint(50, 60)  # Duplicate temp
        ]
        
        with pytest.raises(ValueError, match="duplicate"):
            FanCurve(points)
    
    def test_point_bounds_enforcement(self):
        """Test that points are clamped to valid ranges."""
        point = FanCurvePoint(100, 150)  # Both out of range
        
        assert point.temperature == 90  # Clamped
        assert point.fan_speed == 100   # Clamped
        
        point2 = FanCurvePoint(20, -10)  # Both below minimum
        assert point2.temperature == 30  # Clamped
        assert point2.fan_speed == 0     # Clamped
    
    def test_curve_interpolation(self):
        """Test fan speed interpolation between points."""
        curve = FanCurve([
            FanCurvePoint(30, 20),
            FanCurvePoint(70, 80)
        ])
        
        # Test at midpoint - should interpolate
        speed = curve.get_fan_speed_at_temp(50)
        assert 20 <= speed <= 80
        assert abs(speed - 50) < 10  # Should be approximately 50
        
        # Test below first point
        assert curve.get_fan_speed_at_temp(20) == 20
        
        # Test above last point
        assert curve.get_fan_speed_at_temp(90) == 80

