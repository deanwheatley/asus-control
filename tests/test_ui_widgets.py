"""
Tests for UI widgets (using pytest-qt).
"""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication

from src.ui.dashboard_widgets import MetricCard, GraphWidget


@pytest.mark.ui
class TestMetricCard:
    """Test MetricCard widget."""
    
    def test_metric_card_creation(self, qapp):
        """Test creating a metric card."""
        card = MetricCard("CPU Usage", "%", color="#2196F3")
        
        assert card.title == "CPU Usage"
        assert card.unit == "%"
        assert card.color == "#2196F3"
    
    def test_metric_card_set_value(self, qapp):
        """Test setting metric value."""
        card = MetricCard("CPU Usage", "%")
        
        card.set_value(45.5)
        
        assert card.value == 45.5
        assert "45.5" in card.value_label.text()
    
    def test_metric_card_set_value_none(self, qapp):
        """Test setting metric value to None."""
        card = MetricCard("CPU Usage", "%")
        
        card.set_value(None)
        
        assert card.value_label.text() == "--"
    
    def test_metric_card_set_custom_text(self, qapp):
        """Test setting custom text instead of value."""
        card = MetricCard("CPU Usage", "%")
        
        card.set_value(None, text="N/A")
        
        assert card.value_label.text() == "N/A"


@pytest.mark.ui
class TestGraphWidget:
    """Test GraphWidget."""
    
    def test_graph_widget_creation(self, qapp):
        """Test creating graph widget."""
        widget = GraphWidget()
        
        assert widget is not None
        assert widget.graph is not None
    
    def test_graph_widget_update_data(self, qapp):
        """Test updating graph with data."""
        widget = GraphWidget()
        
        history = {
            'timestamp': [1.0, 2.0, 3.0],
            'cpu_percent': [50.0, 60.0, 55.0],
            'memory_percent': [40.0, 45.0, 42.0]
        }
        
        widget.update_data(history)
        
        # Graph should be updated (no exception means success)
        assert True


