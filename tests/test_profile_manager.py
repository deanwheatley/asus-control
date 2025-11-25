"""
Tests for profile manager module.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import shutil

from src.control.profile_manager import (
    ProfileManager,
    SavedProfile
)
from src.control.asusctl_interface import FanCurve, FanCurvePoint


class TestSavedProfile:
    """Test SavedProfile class."""
    
    def test_profile_creation(self):
        """Test creating a saved profile."""
        profile = SavedProfile(
            name="Test Profile",
            description="Test description"
        )
        
        assert profile.name == "Test Profile"
        assert profile.description == "Test description"
        assert profile.cpu_fan_curve is None
        assert profile.gpu_fan_curve is None
    
    def test_profile_with_curves(self):
        """Test profile with fan curves."""
        cpu_curve = FanCurve([
            FanCurvePoint(30, 20),
            FanCurvePoint(70, 80)
        ])
        
        profile = SavedProfile(
            name="Test Profile",
            cpu_fan_curve=cpu_curve
        )
        
        assert profile.cpu_fan_curve is not None
        assert len(profile.cpu_fan_curve.points) == 2
    
    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        profile = SavedProfile(
            name="Test Profile",
            description="Test"
        )
        
        data = profile.to_dict()
        
        assert data['name'] == "Test Profile"
        assert data['description'] == "Test"
        assert 'created_at' in data
    
    def test_profile_from_dict(self):
        """Test creating profile from dictionary."""
        data = {
            'name': 'Test Profile',
            'description': 'Test',
            'created_at': '2024-01-01T00:00:00',
            'cpu_fan_curve': {
                'points': [
                    {'temperature': 30, 'fan_speed': 20},
                    {'temperature': 70, 'fan_speed': 80}
                ]
            }
        }
        
        profile = SavedProfile.from_dict(data)
        
        assert profile.name == "Test Profile"
        assert profile.cpu_fan_curve is not None
        assert len(profile.cpu_fan_curve.points) == 2


class TestProfileManager:
    """Test ProfileManager class."""
    
    def test_manager_initialization(self, tmp_path):
        """Test profile manager initialization."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        assert manager.profiles_dir == tmp_path
        assert tmp_path.exists()
    
    def test_get_profile_path(self, tmp_path):
        """Test getting profile file path."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        path = manager.get_profile_path("Test Profile")
        
        assert isinstance(path, Path)
        assert "Test_Profile" in str(path)
        assert path.suffix == ".json"
    
    def test_save_profile(self, tmp_path):
        """Test saving a profile."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        profile = SavedProfile(
            name="Test Profile",
            description="Test"
        )
        
        success = manager.save_profile(profile)
        
        assert success == True
        assert (tmp_path / "Test_Profile.json").exists()
        
        # Verify content
        with open(tmp_path / "Test_Profile.json") as f:
            data = json.load(f)
            assert data['name'] == "Test Profile"
    
    def test_load_profile(self, tmp_path):
        """Test loading a profile."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        # Create a profile file
        profile_data = {
            'name': 'Test Profile',
            'description': 'Test',
            'created_at': '2024-01-01T00:00:00'
        }
        
        with open(tmp_path / "Test_Profile.json", 'w') as f:
            json.dump(profile_data, f)
        
        profile = manager.load_profile("Test Profile")
        
        assert profile is not None
        assert profile.name == "Test Profile"
    
    def test_load_profile_not_found(self, tmp_path):
        """Test loading non-existent profile."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        profile = manager.load_profile("NonExistent")
        
        assert profile is None
    
    def test_load_all_profiles(self, tmp_path):
        """Test loading all profiles."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        # Create multiple profile files
        for i in range(3):
            profile_data = {
                'name': f'Profile {i}',
                'description': f'Test {i}',
                'created_at': '2024-01-01T00:00:00'
            }
            with open(tmp_path / f"Profile_{i}.json", 'w') as f:
                json.dump(profile_data, f)
        
        manager.load_all_profiles()
        
        profiles = manager.list_profiles()
        assert len(profiles) == 3
    
    def test_delete_profile(self, tmp_path):
        """Test deleting a profile."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        # Create and save a profile
        profile = SavedProfile(name="Test Profile")
        manager.save_profile(profile)
        
        # Delete it
        success = manager.delete_profile("Test Profile")
        
        assert success == True
        assert not (tmp_path / "Test_Profile.json").exists()
        assert "Test Profile" not in manager.profiles
    
    def test_list_profiles(self, tmp_path):
        """Test listing profiles."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        # Create profiles
        for name in ["Profile A", "Profile B"]:
            profile = SavedProfile(name=name)
            manager.save_profile(profile)
        
        profiles = manager.list_profiles()
        
        assert len(profiles) == 2
        assert "Profile A" in profiles
        assert "Profile B" in profiles
    
    def test_get_profile(self, tmp_path):
        """Test getting profile by name."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        profile = SavedProfile(name="Test Profile")
        manager.save_profile(profile)
        
        retrieved = manager.get_profile("Test Profile")
        
        assert retrieved is not None
        assert retrieved.name == "Test Profile"
    
    def test_export_profile(self, tmp_path):
        """Test exporting profile."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        profile = SavedProfile(name="Test Profile")
        manager.save_profile(profile)
        
        export_path = tmp_path / "export.json"
        success = manager.export_profile("Test Profile", export_path, 'json')
        
        assert success == True
        assert export_path.exists()
        
        with open(export_path) as f:
            data = json.load(f)
            assert data['name'] == "Test Profile"
    
    def test_import_profile(self, tmp_path):
        """Test importing profile."""
        manager = ProfileManager(profiles_dir=tmp_path)
        
        # Create export file
        profile_data = {
            'name': 'Imported Profile',
            'description': 'Imported',
            'created_at': '2024-01-01T00:00:00'
        }
        
        import_path = tmp_path / "import.json"
        with open(import_path, 'w') as f:
            json.dump(profile_data, f)
        
        profile = manager.import_profile(import_path)
        
        assert profile is not None
        assert profile.name == "Imported Profile"
        assert "Imported Profile" in manager.list_profiles()

