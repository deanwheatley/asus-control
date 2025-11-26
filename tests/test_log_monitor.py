#!/usr/bin/env python3
"""
Tests for log monitoring module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import subprocess

from src.monitoring.log_monitor import (
    LogMonitor, LogEntry, LogPriority
)


class TestLogPriority:
    """Tests for LogPriority enum."""
    
    def test_from_string(self):
        """Test priority conversion from string."""
        assert LogPriority.from_string('0') == LogPriority.EMERG
        assert LogPriority.from_string('1') == LogPriority.ALERT
        assert LogPriority.from_string('3') == LogPriority.ERR
        assert LogPriority.from_string('err') == LogPriority.ERR
        assert LogPriority.from_string('error') == LogPriority.ERR
        assert LogPriority.from_string('warning') == LogPriority.WARNING
        assert LogPriority.from_string('info') == LogPriority.INFO
        assert LogPriority.from_string('debug') == LogPriority.DEBUG
        assert LogPriority.from_string('unknown') == LogPriority.INFO  # Default
    
    def test_color_code(self):
        """Test color code generation."""
        assert LogPriority.ERR.color_code() == '#F44336'  # Red
        assert LogPriority.WARNING.color_code() == '#FF9800'  # Orange
        assert LogPriority.INFO.color_code() == '#2196F3'  # Blue
        assert LogPriority.DEBUG.color_code() == '#9E9E9E'  # Gray
    
    def test_bg_color_code(self):
        """Test background color for critical priorities."""
        assert LogPriority.EMERG.bg_color_code() == '#F44336'  # Red background
        assert LogPriority.ALERT.bg_color_code() == '#F44336'
        assert LogPriority.CRIT.bg_color_code() == '#F44336'
        assert LogPriority.ERR.bg_color_code() is None
        assert LogPriority.INFO.bg_color_code() is None


class TestLogEntry:
    """Tests for LogEntry class."""
    
    def test_create_from_json(self):
        """Test creating LogEntry from journalctl JSON."""
        json_data = {
            '__REALTIME_TIMESTAMP': '1703520000000000',  # Microseconds
            'PRIORITY': '3',
            'MESSAGE': 'Test error message',
            '_SYSTEMD_UNIT': 'test.service',
            '_PID': '1234',
            '_HOSTNAME': 'test-host',
            '_BOOT_ID': 'test-boot-id'
        }
        
        entry = LogEntry(json_data)
        
        assert entry.priority == LogPriority.ERR
        assert entry.message == 'Test error message'
        assert entry.source == 'test'  # .service stripped
        assert entry.pid == '1234'
        assert entry.hostname == 'test-host'
    
    def test_source_without_service_suffix(self):
        """Test source name handling when no .service suffix."""
        json_data = {
            '__REALTIME_TIMESTAMP': '1703520000000000',
            'PRIORITY': '6',
            'MESSAGE': 'Test message',
            'SYSLOG_IDENTIFIER': 'kernel'
        }
        
        entry = LogEntry(json_data)
        assert entry.source == 'kernel'
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        json_data = {
            '__REALTIME_TIMESTAMP': '1703520000000000',
            'PRIORITY': '3',
            'MESSAGE': 'Test message',
            '_SYSTEMD_UNIT': 'test.service'
        }
        
        entry = LogEntry(json_data)
        entry_dict = entry.to_dict()
        
        assert entry_dict['priority'] == 'ERR'
        assert entry_dict['priority_level'] == 3
        assert entry_dict['message'] == 'Test message'
        assert entry_dict['source'] == 'test'
    
    def test_to_display_string(self):
        """Test display string formatting."""
        json_data = {
            '__REALTIME_TIMESTAMP': '1703520000000000',
            'PRIORITY': '3',
            'MESSAGE': 'Test error',
            '_SYSTEMD_UNIT': 'test.service'
        }
        
        entry = LogEntry(json_data)
        display_str = entry.to_display_string()
        
        assert 'ERR' in display_str
        assert 'Test error' in display_str
        assert 'test' in display_str


class TestLogMonitor:
    """Tests for LogMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create a LogMonitor instance for testing."""
        return LogMonitor(update_interval=0.1, max_entries=100)
    
    def test_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.update_interval == 0.1
        assert monitor.max_entries == 100
        assert len(monitor.entries) == 0
        assert monitor.is_running == False
        assert monitor.is_paused == False
    
    @patch('subprocess.run')
    def test_load_initial_logs(self, mock_run, monitor):
        """Test loading initial logs."""
        # Mock journalctl output
        log_json_1 = json.dumps({
            '__REALTIME_TIMESTAMP': '1703520000000000',
            'PRIORITY': '3',
            'MESSAGE': 'Error 1',
            '_SYSTEMD_UNIT': 'test.service'
        })
        
        log_json_2 = json.dumps({
            '__REALTIME_TIMESTAMP': '1703520001000000',
            'PRIORITY': '6',
            'MESSAGE': 'Info message',
            '_SYSTEMD_UNIT': 'test.service'
        })
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = log_json_1 + '\n' + log_json_2 + '\n'
        mock_run.return_value = mock_result
        
        monitor._load_initial_logs()
        
        assert len(monitor.entries) == 2
        assert monitor.entries[0].message == 'Error 1'
        assert monitor.entries[1].message == 'Info message'
    
    @patch('subprocess.run')
    def test_load_initial_logs_timeout(self, mock_run, monitor):
        """Test handling timeout when loading logs."""
        mock_run.side_effect = subprocess.TimeoutExpired('journalctl', 10)
        
        error_called = []
        def on_error(msg):
            error_called.append(msg)
        
        monitor.on_error = on_error
        monitor._load_initial_logs()
        
        assert len(error_called) > 0
        assert 'Timeout' in error_called[0]
    
    @patch('subprocess.run')
    def test_load_initial_logs_not_found(self, mock_run, monitor):
        """Test handling when journalctl is not found."""
        mock_run.side_effect = FileNotFoundError()
        
        error_called = []
        def on_error(msg):
            error_called.append(msg)
        
        monitor.on_error = on_error
        monitor._load_initial_logs()
        
        assert len(error_called) > 0
        assert 'journalctl not found' in error_called[0]
    
    def test_priority_filter(self, monitor):
        """Test priority filtering."""
        # Create test entries
        entries = [
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520000000000',
                'PRIORITY': '3',
                'MESSAGE': 'Error',
                '_SYSTEMD_UNIT': 'test.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520001000000',
                'PRIORITY': '6',
                'MESSAGE': 'Info',
                '_SYSTEMD_UNIT': 'test.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520002000000',
                'PRIORITY': '4',
                'MESSAGE': 'Warning',
                '_SYSTEMD_UNIT': 'test.service'
            })
        ]
        
        for entry in entries:
            monitor.entries.append(entry)
        
        # Filter for errors only
        monitor.set_priority_filter([LogPriority.ERR])
        monitor._apply_filters()
        
        filtered = monitor.get_filtered_entries()
        assert len(filtered) == 1
        assert filtered[0].priority == LogPriority.ERR
    
    def test_source_filter(self, monitor):
        """Test source filtering."""
        entries = [
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520000000000',
                'PRIORITY': '3',
                'MESSAGE': 'Message 1',
                '_SYSTEMD_UNIT': 'service1.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520001000000',
                'PRIORITY': '3',
                'MESSAGE': 'Message 2',
                '_SYSTEMD_UNIT': 'service2.service'
            })
        ]
        
        for entry in entries:
            monitor.entries.append(entry)
        
        monitor.set_source_filter(['service1'])
        monitor._apply_filters()
        
        filtered = monitor.get_filtered_entries()
        assert len(filtered) == 1
        assert filtered[0].source == 'service1'
    
    def test_text_filter(self, monitor):
        """Test text search filtering."""
        entries = [
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520000000000',
                'PRIORITY': '3',
                'MESSAGE': 'Database connection failed',
                '_SYSTEMD_UNIT': 'test.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520001000000',
                'PRIORITY': '6',
                'MESSAGE': 'Service started successfully',
                '_SYSTEMD_UNIT': 'test.service'
            })
        ]
        
        for entry in entries:
            monitor.entries.append(entry)
        
        monitor.set_text_filter('database')
        monitor._apply_filters()
        
        filtered = monitor.get_filtered_entries()
        assert len(filtered) == 1
        assert 'database' in filtered[0].message.lower()
    
    def test_time_range_filter(self, monitor):
        """Test time range filtering."""
        now = datetime.now()
        
        entries = [
            LogEntry({
                '__REALTIME_TIMESTAMP': str(int((now - timedelta(hours=2)).timestamp() * 1000000)),
                'PRIORITY': '3',
                'MESSAGE': 'Old error',
                '_SYSTEMD_UNIT': 'test.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': str(int((now - timedelta(minutes=30)).timestamp() * 1000000)),
                'PRIORITY': '3',
                'MESSAGE': 'Recent error',
                '_SYSTEMD_UNIT': 'test.service'
            })
        ]
        
        for entry in entries:
            monitor.entries.append(entry)
        
        # Filter for last hour
        start = now - timedelta(hours=1)
        monitor.set_time_range_filter(start, None)
        monitor._apply_filters()
        
        filtered = monitor.get_filtered_entries()
        assert len(filtered) == 1
        assert filtered[0].message == 'Recent error'
    
    def test_clear_filters(self, monitor):
        """Test clearing all filters."""
        monitor.set_priority_filter([LogPriority.ERR])
        monitor.set_source_filter(['test'])
        monitor.set_text_filter('error')
        
        monitor.clear_filters()
        
        assert len(monitor.priority_filter) == 0
        assert len(monitor.source_filter) == 0
        assert monitor.text_filter == ""
        assert monitor.time_range_filter is None
    
    def test_error_tracking(self, monitor):
        """Test error count tracking."""
        entries = [
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520000000000',
                'PRIORITY': '2',  # Critical
                'MESSAGE': 'Critical error',
                '_SYSTEMD_UNIT': 'test.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520001000000',
                'PRIORITY': '3',  # Error
                'MESSAGE': 'Regular error',
                '_SYSTEMD_UNIT': 'test.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520002000000',
                'PRIORITY': '4',  # Warning
                'MESSAGE': 'Warning',
                '_SYSTEMD_UNIT': 'test.service'
            })
        ]
        
        for entry in entries:
            monitor._update_error_counts(entry)
        
        assert monitor.error_counts['critical'] == 1
        assert monitor.error_counts['errors'] == 1
        assert monitor.error_counts['warnings'] == 1
        assert monitor.error_counts['total_errors'] == 2
    
    def test_get_error_summary(self, monitor):
        """Test error summary generation."""
        now = datetime.now()
        
        # Add recent errors
        recent_entry = LogEntry({
            '__REALTIME_TIMESTAMP': str(int((now - timedelta(minutes=30)).timestamp() * 1000000)),
            'PRIORITY': '3',
            'MESSAGE': 'Recent error',
            '_SYSTEMD_UNIT': 'test.service'
        })
        
        old_entry = LogEntry({
            '__REALTIME_TIMESTAMP': str(int((now - timedelta(hours=2)).timestamp() * 1000000)),
            'PRIORITY': '2',
            'MESSAGE': 'Old critical',
            '_SYSTEMD_UNIT': 'test.service'
        })
        
        monitor.entries.append(recent_entry)
        monitor.entries.append(old_entry)
        
        summary = monitor.get_error_summary()
        
        assert 'recent_critical_1h' in summary
        assert 'recent_errors_1h' in summary
        assert summary['recent_errors_1h'] == 1
        assert summary['recent_critical_1h'] == 0  # Old critical not in last hour
    
    def test_get_available_sources(self, monitor):
        """Test getting available log sources."""
        entries = [
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520000000000',
                'PRIORITY': '3',
                'MESSAGE': 'Message 1',
                '_SYSTEMD_UNIT': 'service1.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520001000000',
                'PRIORITY': '6',
                'MESSAGE': 'Message 2',
                '_SYSTEMD_UNIT': 'service2.service'
            }),
            LogEntry({
                '__REALTIME_TIMESTAMP': '1703520002000000',
                'PRIORITY': '3',
                'MESSAGE': 'Message 3',
                '_SYSTEMD_UNIT': 'service1.service'
            })
        ]
        
        for entry in entries:
            monitor.entries.append(entry)
        
        sources = monitor.get_available_sources()
        
        assert 'service1' in sources
        assert 'service2' in sources
        assert len(sources) == 2
    
    def test_pause_resume(self, monitor):
        """Test pause and resume functionality."""
        assert monitor.is_paused == False
        
        monitor.pause()
        assert monitor.is_paused == True
        
        monitor.resume()
        assert monitor.is_paused == False
    
    @patch('subprocess.run')
    def test_start_stop(self, mock_run, monitor):
        """Test starting and stopping monitor."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        monitor.start()
        assert monitor.is_running == True
        
        monitor.stop()
        # Wait a bit for thread to stop
        import time
        time.sleep(0.2)
        # Thread should have stopped or be stopping


@pytest.mark.integration
class TestLogMonitorIntegration:
    """Integration tests for log monitoring."""
    
    def test_real_journalctl_access(self):
        """Test accessing real journalctl (if available)."""
        try:
            result = subprocess.run(
                ['journalctl', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # journalctl is available, test basic functionality
                monitor = LogMonitor(update_interval=1.0, max_entries=10)
                monitor.start()
                
                # Wait briefly
                import time
                time.sleep(1.5)
                
                # Should have loaded some entries
                monitor.stop()
                
                # This test just verifies we can start/stop without errors
                assert True
            else:
                pytest.skip("journalctl not available")
        except FileNotFoundError:
            pytest.skip("journalctl not installed")
        except subprocess.TimeoutExpired:
            pytest.skip("journalctl timeout")

