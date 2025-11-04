"""
Unit tests for TaggingEngine
"""

import pytest
import numpy as np

from radar_analyzer import TaggingEngine


class TestTaggingEngine:
    """Test suite for TaggingEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a tagging engine instance."""
        config = {
            'velocity_threshold': {
                'high_speed': 300.0,
                'medium_speed': 150.0,
                'low_speed': 50.0
            },
            'acceleration_threshold': {
                'high_g': 5.0,
                'medium_g': 2.0
            },
            'trajectory': {
                'sharp_turn_angle': 45.0,
                'smooth_turn_angle': 15.0
            }
        }
        return TaggingEngine(config)
    
    @pytest.fixture
    def high_speed_features(self):
        """Create features for high-speed target."""
        return {
            'speed_mean': 350.0,
            'speed_max': 400.0,
            'speed_std': 20.0,
            'g_force_max': 2.0,
            'g_force_mean': 1.5,
            'high_g_events': 0,
            'mean_turn_angle': 10.0,
            'max_turn_angle': 25.0,
            'sharp_turns_count': 0,
            'curvature_mean': 0.0005,
            'altitude_change': 100.0,
            'duration': 60.0,
            'speed': np.linspace(340, 360, 100)
        }
    
    @pytest.fixture
    def g_turn_features(self):
        """Create features for G-turn maneuver."""
        return {
            'speed_mean': 250.0,
            'speed_max': 280.0,
            'speed_std': 15.0,
            'g_force_max': 6.5,
            'g_force_mean': 3.2,
            'high_g_events': 3,
            'mean_turn_angle': 50.0,
            'max_turn_angle': 75.0,
            'sharp_turns_count': 2,
            'curvature_mean': 0.02,
            'altitude_change': -50.0,
            'duration': 45.0,
            'speed': np.ones(100) * 250
        }
    
    @pytest.fixture
    def hovering_features(self):
        """Create features for hovering target."""
        return {
            'speed_mean': 3.5,
            'speed_max': 8.0,
            'speed_std': 2.0,
            'g_force_max': 0.5,
            'g_force_mean': 0.2,
            'high_g_events': 0,
            'mean_turn_angle': 5.0,
            'max_turn_angle': 12.0,
            'sharp_turns_count': 0,
            'curvature_mean': 0.0001,
            'altitude_change': 5.0,
            'duration': 120.0,
            'speed': np.ones(100) * 3.5
        }
    
    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine is not None
        assert engine.high_speed_thresh == 300.0
        assert engine.medium_speed_thresh == 150.0
        assert engine.high_g_thresh == 5.0
    
    def test_tag_high_speed(self, engine, high_speed_features):
        """Test tagging high-speed target."""
        tags = engine.tag_target(high_speed_features)
        
        assert 'high_speed' in tags
        assert 'g_turn' not in tags
        # Should have smooth trajectory due to low turn angles
        assert 'smooth_trajectory' in tags or 'straight_line' in tags
    
    def test_tag_g_turn(self, engine, g_turn_features):
        """Test tagging G-turn maneuver."""
        tags = engine.tag_target(g_turn_features)
        
        assert 'g_turn' in tags
        assert 'sharp_trajectory' in tags
        assert 'evasive_maneuver' in tags  # Combination of G-turn and sharp trajectory
    
    def test_tag_hovering(self, engine, hovering_features):
        """Test tagging hovering target."""
        tags = engine.tag_target(hovering_features)
        
        assert 'hovering' in tags
        assert 'high_speed' not in tags
        assert 'g_turn' not in tags
    
    def test_tag_speed(self, engine):
        """Test speed-based tagging."""
        # High speed
        features = {'speed_mean': 350.0, 'speed_std': 10.0, 'speed': np.ones(10) * 350}
        tags = engine._tag_speed(features)
        assert 'high_speed' in tags
        
        # Medium speed
        features = {'speed_mean': 200.0, 'speed_std': 10.0, 'speed': np.ones(10) * 200}
        tags = engine._tag_speed(features)
        assert 'medium_speed' in tags
        
        # Low speed
        features = {'speed_mean': 80.0, 'speed_std': 5.0, 'speed': np.ones(10) * 80}
        tags = engine._tag_speed(features)
        assert 'low_speed' in tags
        
        # Hovering
        features = {'speed_mean': 3.0, 'speed_std': 1.0, 'speed': np.ones(10) * 3}
        tags = engine._tag_speed(features)
        assert 'hovering' in tags
    
    def test_tag_acceleration(self, engine):
        """Test acceleration-based tagging."""
        # High G
        features = {
            'g_force_max': 6.0,
            'g_force_mean': 3.0,
            'high_g_events': 2
        }
        tags = engine._tag_acceleration(features)
        assert 'g_turn' in tags
        assert 'evasive_maneuver' in tags
        
        # Normal acceleration
        features = {
            'g_force_max': 2.0,
            'g_force_mean': 1.0,
            'high_g_events': 0
        }
        tags = engine._tag_acceleration(features)
        assert 'g_turn' not in tags
    
    def test_tag_trajectory(self, engine):
        """Test trajectory-based tagging."""
        # Sharp trajectory
        features = {
            'mean_turn_angle': 50.0,
            'max_turn_angle': 80.0,
            'sharp_turns_count': 3,
            'curvature_mean': 0.01,
            'std_turn_angle': 10.0
        }
        tags = engine._tag_trajectory(features)
        assert 'sharp_trajectory' in tags
        
        # Smooth trajectory
        features = {
            'mean_turn_angle': 8.0,
            'max_turn_angle': 12.0,
            'sharp_turns_count': 0,
            'curvature_mean': 0.0005,
            'std_turn_angle': 2.0
        }
        tags = engine._tag_trajectory(features)
        assert 'smooth_trajectory' in tags
        
        # Straight line
        features = {
            'mean_turn_angle': 2.0,
            'max_turn_angle': 5.0,
            'sharp_turns_count': 0,
            'curvature_mean': 0.0001,
            'std_turn_angle': 1.0
        }
        tags = engine._tag_trajectory(features)
        assert 'straight_line' in tags
    
    def test_tag_altitude(self, engine):
        """Test altitude-based tagging."""
        # Ascending
        features = {'altitude_change': 800.0, 'duration': 60.0}
        tags = engine._tag_altitude(features)
        assert 'ascending' in tags
        
        # Descending
        features = {'altitude_change': -900.0, 'duration': 60.0}
        tags = engine._tag_altitude(features)
        assert 'descending' in tags
        
        # Level flight
        features = {'altitude_change': 50.0, 'duration': 60.0}
        tags = engine._tag_altitude(features)
        assert 'ascending' not in tags
        assert 'descending' not in tags
    
    def test_batch_tag(self, engine, high_speed_features, g_turn_features):
        """Test batch tagging."""
        features_list = [high_speed_features, g_turn_features]
        all_tags = engine.batch_tag(features_list)
        
        assert len(all_tags) == 2
        assert 'high_speed' in all_tags[0]
        assert 'g_turn' in all_tags[1]
    
    def test_generate_report(self, engine, high_speed_features):
        """Test report generation."""
        tags = engine.tag_target(high_speed_features)
        report = engine.generate_report(high_speed_features, tags)
        
        assert isinstance(report, str)
        assert 'TARGET BEHAVIOR ANALYSIS REPORT' in report
        assert 'BEHAVIOR TAGS' in report
        assert 'KEY METRICS' in report
        assert 'Speed:' in report
    
    def test_export_tags(self, engine, high_speed_features, tmp_path):
        """Test exporting tags to file."""
        tags = engine.tag_target(high_speed_features)
        output_file = tmp_path / "tags_export.json"
        
        engine.export_tags([high_speed_features], [tags], str(output_file))
        
        assert output_file.exists()
        
        # Verify content
        import json
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert 'features' in data[0]
        assert 'tags' in data[0]
        assert data[0]['tags'] == tags


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
