"""
Tests for dependency checker module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

from src.utils.dependency_checker import (
    DependencyChecker,
    Dependency,
    DependencyStatus,
    check_dependencies
)


class TestDependency:
    """Test Dependency class."""
    
    def test_dependency_creation(self):
        """Test dependency object creation."""
        dep = Dependency(
            name="TestPackage",
            pip_package="test-package",
            import_name="testpackage",
            description="Test package description"
        )
        
        assert dep.name == "TestPackage"
        assert dep.pip_package == "test-package"
        assert dep.import_name == "testpackage"
        assert dep.description == "Test package description"
        assert dep.is_optional == False
    
    def test_dependency_optional(self):
        """Test optional dependency."""
        dep = Dependency(
            name="OptionalPackage",
            pip_package="optional-package",
            is_optional=True
        )
        
        assert dep.is_optional == True


class TestDependencyChecker:
    """Test DependencyChecker class."""
    
    def test_checker_initialization(self):
        """Test dependency checker initialization."""
        checker = DependencyChecker()
        
        assert len(checker.dependencies) > 0
        assert any(dep.name == "PyQt6" for dep in checker.dependencies)
    
    @patch('importlib.import_module')
    def test_check_python_package_installed(self, mock_import):
        """Test checking installed Python package."""
        mock_import.return_value = Mock()
        
        checker = DependencyChecker()
        dep = Dependency(
            name="TestPackage",
            import_name="testpackage"
        )
        
        status = checker._check_dependency(dep)
        assert status == DependencyStatus.INSTALLED
    
    @patch('importlib.import_module')
    def test_check_python_package_not_installed(self, mock_import):
        """Test checking missing Python package."""
        mock_import.side_effect = ImportError()
        
        checker = DependencyChecker()
        dep = Dependency(
            name="TestPackage",
            import_name="testpackage"
        )
        
        status = checker._check_dependency(dep)
        assert status == DependencyStatus.NOT_INSTALLED
    
    @patch('shutil.which')
    def test_check_system_command_available(self, mock_which):
        """Test checking available system command."""
        mock_which.return_value = "/usr/bin/command"
        
        checker = DependencyChecker()
        dep = Dependency(
            name="TestCommand",
            system_command="test-command"
        )
        
        status = checker._check_dependency(dep)
        assert status == DependencyStatus.SYSTEM_COMMAND
    
    @patch('shutil.which')
    def test_check_system_command_not_available(self, mock_which):
        """Test checking missing system command."""
        mock_which.return_value = None
        
        checker = DependencyChecker()
        dep = Dependency(
            name="TestCommand",
            system_command="test-command"
        )
        
        status = checker._check_dependency(dep)
        assert status == DependencyStatus.NOT_INSTALLED
    
    def test_check_all_dependencies(self):
        """Test checking all dependencies."""
        checker = DependencyChecker()
        
        results = checker.check_all()
        
        assert 'all_installed' in results
        assert 'required_installed' in results
        assert 'missing_required' in results
        assert 'missing_optional' in results
        assert 'details' in results
        assert isinstance(results['missing_required'], list)
        assert isinstance(results['missing_optional'], list)
    
    def test_can_install_via_pip(self):
        """Test checking if dependency can be installed via pip."""
        checker = DependencyChecker()
        
        dep_pip = Dependency(
            name="TestPackage",
            pip_package="test-package"
        )
        assert checker.can_install_via_pip(dep_pip) == True
        
        dep_system = Dependency(
            name="TestCommand",
            system_command="test-command"
        )
        assert checker.can_install_via_pip(dep_system) == False
    
    @patch('subprocess.run')
    def test_install_via_pip_success(self, mock_run):
        """Test successful pip installation."""
        mock_run.return_value = Mock(returncode=0, stdout="Success")
        
        checker = DependencyChecker()
        dep = Dependency(
            name="TestPackage",
            pip_package="test-package"
        )
        
        success, message = checker.install_via_pip(dep)
        
        assert success == True
        assert "Successfully installed" in message
    
    @patch('subprocess.run')
    def test_install_via_pip_failure(self, mock_run):
        """Test failed pip installation."""
        mock_run.return_value = Mock(returncode=1, stderr="Error occurred")
        
        checker = DependencyChecker()
        dep = Dependency(
            name="TestPackage",
            pip_package="test-package"
        )
        
        success, message = checker.install_via_pip(dep)
        
        assert success == False
        assert "failed" in message.lower()
    
    def test_get_install_instructions(self):
        """Test getting installation instructions."""
        checker = DependencyChecker()
        dep = Dependency(
            name="TestPackage",
            pip_package="test-package",
            description="Test package",
            install_instructions="pip install test-package"
        )
        
        instructions = checker.get_install_instructions(dep)
        
        assert "TestPackage" in instructions
        assert "pip install test-package" in instructions
    
    def test_check_dependencies_function(self):
        """Test convenience check_dependencies function."""
        results = check_dependencies()
        
        assert isinstance(results, dict)
        assert 'all_installed' in results
        assert 'required_installed' in results

