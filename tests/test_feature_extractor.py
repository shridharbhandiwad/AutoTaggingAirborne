"""
Unit tests for FeatureExtractor
"""

import pytest
import numpy as np

from radar_analyzer import FeatureExtractor


class TestFeatureExtractor:
    """Test suite for FeatureExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create a feature extractor instance."""
        config = {
            'window_size': 10,
            'sharp_turn_angle': 45.0,
            'high_g': 5.0
        }
        return FeatureExtractor(config)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample radar data."""
        num_samples = 100
        t = np.linspace(0, 10, num_samples)
        
        # Create trajectory
        x = 100 * t
        y = 50 * np.sin(0.5 * t)
        z = 5000 + 10 * t
        position = np.column_stack([x, y, z])
        
        # Create velocity
        vx = 100 * np.ones(num_samples)
        vy = 25 * np.cos(0.5 * t)
        vz = 10 * np.ones(num_samples)
        velocity = np.column_stack([vx, vy, vz])
        
        # Create Doppler data
        doppler = np.abs(np.fft.fft(np.random.randn(num_samples)))
        
        # Create raw data
        raw_data = np.random.randn(num_samples) + 1j * np.random.randn(num_samples)
        
        return {
            'position': position,
            'velocity': velocity,
            'doppler': doppler,
            'raw_data': raw_data,
            'timestamps': t
        }
    
    def test_extractor_initialization(self, extractor):
        """Test extractor initialization."""
        assert extractor is not None
        assert extractor.window_size == 10
    
    def test_extract_velocity_features(self, extractor, sample_data):
        """Test velocity feature extraction."""
        features = extractor.extract_velocity_features(sample_data['velocity'])
        
        assert 'speed' in features
        assert 'speed_mean' in features
        assert 'speed_std' in features
        assert 'speed_max' in features
        assert 'speed_min' in features
        
        # Check that speed is computed correctly
        assert isinstance(features['speed_mean'], (float, np.floating))
        assert features['speed_mean'] > 0
    
    def test_extract_trajectory_features(self, extractor, sample_data):
        """Test trajectory feature extraction."""
        features = extractor.extract_trajectory_features(sample_data['position'])
        
        assert 'total_path_length' in features
        assert 'mean_turn_angle' in features
        assert 'altitude_mean' in features
        assert 'sharp_turns_count' in features
        
        # Check reasonable values
        assert features['total_path_length'] > 0
        assert features['altitude_mean'] > 4000  # Should be around 5000m
    
    def test_extract_acceleration_features(self, extractor, sample_data):
        """Test acceleration feature extraction."""
        # Compute acceleration
        velocity = sample_data['velocity']
        timestamps = sample_data['timestamps']
        dt = np.diff(timestamps)
        acceleration = np.diff(velocity, axis=0) / dt[:, np.newaxis]
        acceleration = np.vstack([acceleration, acceleration[-1]])
        
        features = extractor.extract_acceleration_features(acceleration)
        
        assert 'g_force' in features
        assert 'g_force_mean' in features
        assert 'g_force_max' in features
        assert 'high_g_events' in features
        
        # Check types
        assert isinstance(features['g_force_mean'], (float, np.floating))
    
    def test_extract_doppler_features(self, extractor, sample_data):
        """Test Doppler feature extraction."""
        features = extractor.extract_doppler_features(sample_data['doppler'])
        
        assert 'doppler_mean' in features
        assert 'doppler_std' in features
        assert 'doppler_peaks_count' in features
        assert 'doppler_bandwidth' in features
    
    def test_extract_rcs_features(self, extractor, sample_data):
        """Test RCS feature extraction."""
        features = extractor.extract_rcs_features(sample_data['raw_data'])
        
        assert 'rcs_mean_db' in features
        assert 'rcs_std_db' in features
        assert 'rcs_max_db' in features
        assert 'rcs_fluctuation' in features
    
    def test_extract_all_features(self, extractor, sample_data):
        """Test extracting all features."""
        features = extractor.extract_all_features(sample_data)
        
        # Should have features from all categories
        assert len(features) > 20
        
        # Check presence of key features
        assert 'speed_mean' in features
        assert 'total_path_length' in features
        assert 'doppler_mean' in features
        assert 'rcs_mean_db' in features
    
    def test_compute_turn_angles(self, extractor):
        """Test turn angle computation."""
        # Create a path with a 90-degree turn
        position = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [2, 0, 0],
            [2, 1, 0],
            [2, 2, 0]
        ])
        
        angles = extractor._compute_turn_angles(position)
        
        assert len(angles) > 0
        # Should detect the turn
        assert np.any(np.abs(angles) > 45)
    
    def test_compute_curvature(self, extractor):
        """Test curvature computation."""
        # Create a circular path
        t = np.linspace(0, 2 * np.pi, 100)
        x = np.cos(t)
        y = np.sin(t)
        z = np.zeros_like(t)
        position = np.column_stack([x, y, z])
        
        curvature = extractor._compute_curvature(position)
        
        assert len(curvature) > 0
        # Circle should have constant curvature
        assert np.std(curvature) < 0.5
    
    def test_prepare_dataset(self, extractor, sample_data):
        """Test dataset preparation."""
        features1 = extractor.extract_all_features(sample_data)
        features2 = extractor.extract_all_features(sample_data)
        
        features_list = [features1, features2]
        labels = ['high_speed', 'medium_speed']
        
        X, y = extractor.prepare_dataset(features_list, labels)
        
        assert X.shape[0] == 2  # Two samples
        assert X.shape[1] > 0   # Multiple features
        assert len(y) == 2
        assert y[0] == 'high_speed'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
