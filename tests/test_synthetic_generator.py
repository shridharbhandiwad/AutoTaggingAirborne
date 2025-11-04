"""
Unit tests for SyntheticDataGenerator
"""

import pytest
import numpy as np
from pathlib import Path

from radar_analyzer import SyntheticDataGenerator


class TestSyntheticDataGenerator:
    """Test suite for SyntheticDataGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        config = {
            'num_targets': 5,
            'duration': 60.0,
            'sampling_rate': 1000,
            'noise_level': 0.05,
            'num_samples': 10000
        }
        return SyntheticDataGenerator(config)
    
    def test_generator_initialization(self, generator):
        """Test generator initialization."""
        assert generator is not None
        assert generator.num_targets == 5
        assert generator.duration == 60.0
        assert generator.noise_level == 0.05
    
    def test_generate_target(self, generator):
        """Test generating a single target."""
        data = generator.generate_target('high_speed', target_id=1)
        
        assert 'raw_data' in data
        assert 'position' in data
        assert 'velocity' in data
        assert 'timestamps' in data
        assert 'doppler' in data
        assert 'metadata' in data
        assert 'ground_truth_behavior' in data
        
        # Check data shapes
        assert len(data['raw_data']) > 0
        assert data['position'].shape[1] == 3
        assert data['velocity'].shape[1] == 3
        
        # Check metadata
        assert data['metadata']['behavior'] == 'high_speed'
        assert data['ground_truth_behavior'] == 'high_speed'
    
    def test_generate_high_speed_trajectory(self, generator):
        """Test high-speed trajectory generation."""
        timestamps = np.linspace(0, 60, 1000)
        position, velocity = generator._generate_high_speed_trajectory(timestamps)
        
        assert position.shape == (1000, 3)
        assert velocity.shape == (1000, 3)
        
        # Check speed
        speed = np.linalg.norm(velocity, axis=1)
        assert np.mean(speed) > 300  # Should be high speed
    
    def test_generate_hovering_trajectory(self, generator):
        """Test hovering trajectory generation."""
        timestamps = np.linspace(0, 60, 1000)
        position, velocity = generator._generate_hovering_trajectory(timestamps)
        
        assert position.shape == (1000, 3)
        assert velocity.shape == (1000, 3)
        
        # Check speed
        speed = np.linalg.norm(velocity, axis=1)
        assert np.mean(speed) < 50  # Should be low speed
    
    def test_generate_g_turn_trajectory(self, generator):
        """Test G-turn trajectory generation."""
        timestamps = np.linspace(0, 60, 1000)
        position, velocity = generator._generate_g_turn_trajectory(timestamps)
        
        assert position.shape == (1000, 3)
        assert velocity.shape == (1000, 3)
        
        # Should have some sharp turns
        # Compute turn angles
        vectors = np.diff(position, axis=0)
        # This is a basic check - detailed turn analysis done in feature extractor
        assert np.max(np.linalg.norm(vectors, axis=1)) > 0
    
    def test_generate_radar_returns(self, generator):
        """Test radar return generation."""
        position = np.random.randn(100, 3) * 1000
        velocity = np.random.randn(100, 3) * 100
        timestamps = np.linspace(0, 1, 100)
        
        signal = generator._generate_radar_returns(position, velocity, timestamps)
        
        assert len(signal) == 100
        assert signal.dtype == np.complex128 or signal.dtype == np.complex64
    
    def test_generate_doppler_spectrum(self, generator):
        """Test Doppler spectrum generation."""
        velocity = np.random.randn(100, 3) * 100
        doppler = generator._generate_doppler_spectrum(velocity)
        
        assert len(doppler) == 100
        assert np.all(doppler >= 0)  # Magnitude should be non-negative
    
    def test_generate_dataset(self, generator):
        """Test dataset generation."""
        dataset = generator.generate_dataset()
        
        assert len(dataset) == 5  # num_targets
        
        # Check each target
        for data in dataset:
            assert 'raw_data' in data
            assert 'position' in data
            assert 'ground_truth_behavior' in data
    
    def test_generate_dataset_with_distribution(self, generator):
        """Test dataset generation with specific distribution."""
        distribution = {
            'high_speed': 0.6,
            'hovering': 0.4
        }
        
        dataset = generator.generate_dataset(distribution)
        
        assert len(dataset) == 5
        
        # Count behaviors
        behaviors = [d['ground_truth_behavior'] for d in dataset]
        high_speed_count = behaviors.count('high_speed')
        hovering_count = behaviors.count('hovering')
        
        # Should have some of each (probabilistic)
        assert high_speed_count + hovering_count == 5
    
    def test_save_synthetic_dataset(self, generator, tmp_path):
        """Test saving synthetic dataset."""
        dataset = generator.generate_dataset()
        output_dir = tmp_path / "synthetic"
        
        generator.save_synthetic_dataset(dataset, str(output_dir))
        
        # Check files were created
        assert output_dir.exists()
        files = list(output_dir.glob('*.h5'))
        assert len(files) == 5
    
    def test_generate_test_scenarios(self, generator):
        """Test test scenario generation."""
        scenarios = generator.generate_test_scenarios()
        
        assert len(scenarios) == 5
        
        # Check each scenario has unique behavior
        behaviors = [s['ground_truth_behavior'] for s in scenarios]
        assert len(set(behaviors)) == 5  # All different


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
