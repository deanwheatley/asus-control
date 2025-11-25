#!/usr/bin/env python3
"""
Main Application Window

PyQt6 main window with dashboard for system monitoring.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTabWidget, QPushButton, QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction

from ..monitoring.system_monitor import SystemMonitor
from .dashboard_widgets import MetricCard, GraphWidget
from .dependency_dialog import DependencyDialog
from .fan_curve_editor import FanCurveEditor
from .profile_manager_tab import ProfileManagerTab
from .help_dialog import HelpDialog
from ..control.asusctl_interface import AsusctlInterface, Profile
from ..control.profile_manager import ProfileManager


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASUS Fan Control")
        self.setGeometry(100, 100, 1200, 800)
        
        # Modern window styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
        """)
        
        # Initialize system monitor
        self.monitor = SystemMonitor(update_interval=1.0)
        self.monitor.start()
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create tab widget with modern styling
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 0px;
            }
            QTabBar::tab {
                background: #f5f5f5;
                color: #666;
                padding: 14px 28px;
                margin-right: 1px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #2196F3;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background: #eeeeee;
            }
        """)
        main_layout.addWidget(self.tabs)
        
        # Initialize asusctl interface
        self.asusctl = AsusctlInterface()
        
        # Create dashboard tab
        self.dashboard_tab = self._create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Create fan curve editor tab
        self.fan_curve_tab = self._create_fan_curve_tab()
        self.tabs.addTab(self.fan_curve_tab, "Fan Curves")
        
        # Create profile manager tab
        self.profile_manager = ProfileManager()
        self.profile_tab = self._create_profile_tab()
        self.tabs.addTab(self.profile_tab, "Profiles")
        
        # Create placeholder tabs
        self.tabs.addTab(QWidget(), "Settings")
        
        # Status bar with modern styling
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #f5f5f5;
                color: #666;
                border-top: 1px solid #e0e0e0;
                padding: 4px;
            }
        """)
        self.statusBar().showMessage("Monitoring active")
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(1000)  # Update every second
        
        # Initial update
        self.update_dashboard()
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: white;
                color: #333;
                border-bottom: 1px solid #e0e0e0;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #f0f0f0;
            }
        """)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        help_action = QAction("Help Documentation", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        dependency_action = QAction("Check Dependencies", self)
        dependency_action.triggered.connect(self._show_dependency_dialog)
        help_menu.addAction(dependency_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _show_dependency_dialog(self):
        """Show the dependency check dialog."""
        dialog = DependencyDialog(self)
        dialog.exec()
        # Refresh check after dialog closes
        self._refresh_after_dependency_check()
    
    def _refresh_after_dependency_check(self):
        """Refresh the application after dependency check."""
        # Could restart monitoring or check for newly available features
        pass
    
    def _show_help(self):
        """Show help documentation dialog."""
        dialog = HelpDialog(self)
        dialog.exec()
    
    def _show_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About ASUS Fan Control",
            "<h2>ASUS Fan Control</h2>"
            "<p>Version 0.1.0</p>"
            "<p>A modern GUI application for managing ASUS laptop fan curves "
            "with real-time system monitoring.</p>"
            "<p>© 2024</p>"
            "<p>Press <b>F1</b> for help documentation</p>"
        )
    
    def _create_dashboard_tab(self) -> QWidget:
        """Create the dashboard tab with metrics and graphs."""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title section with minimal design
        title_layout = QHBoxLayout()
        title = QLabel("System Monitor")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title.setStyleSheet("color: #212121; margin-bottom: 10px;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(15)
        
        # CPU metrics
        self.cpu_percent_card = MetricCard("CPU Usage", "%", color="#2196F3")
        self.cpu_temp_card = MetricCard("CPU Temperature", "°C", color="#F44336")
        self.cpu_freq_card = MetricCard("CPU Frequency", "MHz", color="#4CAF50")
        
        # Memory metrics
        self.memory_card = MetricCard("Memory", "%", color="#FF9800")
        self.memory_used_card = MetricCard("Memory Used", "GB", color="#9C27B0")
        
        # GPU metrics
        self.gpu_util_card = MetricCard("GPU Usage", "%", color="#00BCD4")
        self.gpu_temp_card = MetricCard("GPU Temperature", "°C", color="#E91E63")
        self.gpu_memory_card = MetricCard("GPU Memory", "%", color="#3F51B5")
        
        # Add to grid
        row = 0
        metrics_grid.addWidget(self.cpu_percent_card, row, 0)
        metrics_grid.addWidget(self.cpu_temp_card, row, 1)
        metrics_grid.addWidget(self.cpu_freq_card, row, 2)
        
        row = 1
        metrics_grid.addWidget(self.memory_card, row, 0)
        metrics_grid.addWidget(self.memory_used_card, row, 1)
        metrics_grid.addWidget(self.gpu_util_card, row, 2)
        
        row = 2
        metrics_grid.addWidget(self.gpu_temp_card, row, 0)
        metrics_grid.addWidget(self.gpu_memory_card, row, 1)
        
        layout.addLayout(metrics_grid)
        
        # Graphs
        self.graph_widget = GraphWidget()
        layout.addWidget(self.graph_widget)
        
        # Stretch
        layout.addStretch()
        
        return widget
    
    def _create_fan_curve_tab(self) -> QWidget:
        """Create the fan curve editor tab."""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Check if asusctl is available
        if not self.asusctl.is_available():
            warning_widget = QWidget()
            warning_layout = QVBoxLayout(warning_widget)
            warning_layout.setContentsMargins(30, 30, 30, 30)
            
            warning_label = QLabel(
                "⚠️ asusctl is not available on this system.\n\n"
                "Fan curve editing requires asusctl to be installed.\n"
                "Please install asusctl to use this feature.\n\n"
                "See Help → Check Dependencies for installation instructions."
            )
            warning_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 12pt;
                    padding: 20px;
                    background-color: #fff3e0;
                    border-radius: 8px;
                    border: 1px solid #ffcc80;
                }
            """)
            warning_label.setWordWrap(True)
            warning_layout.addWidget(warning_label)
            warning_layout.addStretch()
            
            layout.addWidget(warning_widget)
            return widget
        
        # Create fan curve editor
        self.fan_curve_editor = FanCurveEditor()
        self.fan_curve_editor.curve_changed.connect(self._on_fan_curve_changed)
        layout.addWidget(self.fan_curve_editor)
        
        return widget
    
    def _on_fan_curve_changed(self, curve):
        """Handle fan curve changes."""
        # Get current profile
        current_profile = self.asusctl.get_current_profile() or Profile.BALANCED
        
        # Determine which fan to apply to (simplified - could be improved)
        fan_name = "CPU"  # Could be determined from UI selection
        
        # Apply the curve
        success, message = self.asusctl.set_fan_curve(current_profile, fan_name, curve)
        
        if success:
            self.statusBar().showMessage(f"Fan curve applied for {fan_name}", 3000)
            # Update profile tab with current curves
            if hasattr(self, 'profile_tab') and hasattr(self, 'fan_curve_editor'):
                self.profile_tab.set_current_curves(
                    self.fan_curve_editor.current_curve,
                    None  # GPU curve if available
                )
        else:
            QMessageBox.warning(self, "Error", f"Failed to apply fan curve:\n{message}")
    
    def _create_profile_tab(self) -> QWidget:
        """Create the profile manager tab."""
        from .profile_manager_tab import ProfileManagerTab
        
        profile_tab = ProfileManagerTab(self)
        
        # Connect profile selection to fan curve editor
        profile_tab.profile_selected.connect(self._on_profile_selected)
        
        return profile_tab
    
    def _on_profile_selected(self, profile_name: str):
        """Handle profile selection - load into fan curve editor."""
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            return
        
        # Switch to fan curve tab
        self.tabs.setCurrentIndex(1)  # Fan Curves tab
        
        # Load CPU curve if available
        if profile.cpu_fan_curve and hasattr(self, 'fan_curve_editor'):
            self.fan_curve_editor.load_curve(profile.cpu_fan_curve)
            
            # Update profile tab with current curves
            if hasattr(self, 'profile_tab'):
                self.profile_tab.set_current_curves(
                    profile.cpu_fan_curve,
                    profile.gpu_fan_curve
                )
    
    def update_dashboard(self):
        """Update all dashboard widgets with latest metrics."""
        metrics = self.monitor.get_metrics()
        history = self.monitor.get_history()
        
        # Update metric cards
        self.cpu_percent_card.set_value(metrics['cpu_percent'])
        if metrics['cpu_temp']:
            self.cpu_temp_card.set_value(metrics['cpu_temp'])
        else:
            self.cpu_temp_card.set_value(None, text="N/A")
        self.cpu_freq_card.set_value(metrics['cpu_freq'])
        
        self.memory_card.set_value(metrics['memory_percent'])
        self.memory_used_card.set_value(metrics['memory_used_gb'], decimals=2)
        
        if metrics['gpu_utilization'] is not None:
            self.gpu_util_card.set_value(metrics['gpu_utilization'])
        else:
            self.gpu_util_card.set_value(None, text="N/A")
            
        if metrics['gpu_temp'] is not None:
            self.gpu_temp_card.set_value(metrics['gpu_temp'])
        else:
            self.gpu_temp_card.set_value(None, text="N/A")
            
        if metrics['gpu_memory_percent'] is not None:
            self.gpu_memory_card.set_value(metrics['gpu_memory_percent'])
        else:
            self.gpu_memory_card.set_value(None, text="N/A")
        
        # Update graphs
        self.graph_widget.update_data(history)
        
        # Update status bar
        status_msg = f"Monitoring active | "
        if metrics['cpu_temp']:
            status_msg += f"CPU: {metrics['cpu_temp']:.1f}°C | "
        if metrics['gpu_temp']:
            status_msg += f"GPU: {metrics['gpu_temp']:.1f}°C | "
        status_msg += f"CPU: {metrics['cpu_percent']:.1f}% | Memory: {metrics['memory_percent']:.1f}%"
        self.statusBar().showMessage(status_msg)
    
    def closeEvent(self, event):
        """Clean up on window close."""
        self.monitor.stop()
        event.accept()

