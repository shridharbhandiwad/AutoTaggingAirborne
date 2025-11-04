"""
Synthetic Data Generator Module

Generates synthetic radar data for testing and training purposes.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from scipy import signal
import h5py
from pathlib import Path

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """
    Generate synthetic airborne radar target data with various behavior patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize synthetic data generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.num_samples = self.config.get('num_samples', 10000)
        self.duration = self.config.get('duration', 60.0)  # seconds
        self.sampling_rate = self.config.get('sampling_rate', 1000)  # Hz
        self.noise_level = self.config.get('noise_level', 0.05)
        self.num_targets = self.config.get('num_targets', 5)
        
        # Radar parameters
        self.center_frequency = 10e9  # 10 GHz (X-band)
        self.prf = 1000.0  # Pulse Repetition Frequency
        self.bandwidth = 100e6  # 100 MHz
        
    def generate_dataset(self, behavior_distribution: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Generate a complete synthetic dataset with multiple targets.
        
        Args:
            behavior_distribution: Distribution of behaviors to generate
                                 e.g., {'high_speed': 0.3, 'g_turn': 0.2, ...}
            
        Returns:
            List of synthetic radar data dictionaries
        """
        if behavior_distribution is None:
            behavior_distribution = {
                'high_speed': 0.25,
                'medium_speed': 0.25,
                'g_turn': 0.15,
                'sharp_trajectory': 0.15,
                'hovering': 0.10,
                'evasive_maneuver': 0.10
            }
        
        dataset = []
        behaviors = list(behavior_distribution.keys())
        probabilities = list(behavior_distribution.values())
        
        # Normalize probabilities
        total_prob = sum(probabilities)
        probabilities = [p / total_prob for p in probabilities]
        
        logger.info(f"Generating {self.num_targets} synthetic targets...")
        
        for i in range(self.num_targets):
            # Select behavior based on distribution
            behavior = np.random.choice(behaviors, p=probabilities)
            
            # Generate target data
            target_data = self.generate_target(behavior, target_id=i)
            dataset.append(target_data)
            
            logger.info(f"Generated target {i+1}/{self.num_targets} with behavior: {behavior}")
        
        return dataset
    
    def generate_target(self, behavior: str, target_id: int = 0) -> Dict[str, Any]:
        """
        Generate synthetic radar data for a single target with specified behavior.
        
        Args:
            behavior: Target behavior type
            target_id: Unique target identifier
            
        Returns:
            Dictionary containing synthetic radar data
        """
        # Generate time array
        num_samples = int(self.duration * self.prf)
        timestamps = np.linspace(0, self.duration, num_samples)
        
        # Generate trajectory based on behavior
        if behavior == 'high_speed':
            position, velocity = self._generate_high_speed_trajectory(timestamps)
        elif behavior == 'medium_speed':
            position, velocity = self._generate_medium_speed_trajectory(timestamps)
        elif behavior == 'g_turn':
            position, velocity = self._generate_g_turn_trajectory(timestamps)
        elif behavior == 'sharp_trajectory':
            position, velocity = self._generate_sharp_trajectory(timestamps)
        elif behavior == 'hovering':
            position, velocity = self._generate_hovering_trajectory(timestamps)
        elif behavior == 'evasive_maneuver':
            position, velocity = self._generate_evasive_trajectory(timestamps)
        elif behavior == 'spiral':
            position, velocity = self._generate_spiral_trajectory(timestamps)
        else:
            position, velocity = self._generate_default_trajectory(timestamps)
        
        # Generate raw radar data
        raw_data = self._generate_radar_returns(position, velocity, timestamps)
        
        # Generate Doppler data
        doppler = self._generate_doppler_spectrum(velocity)
        
        # Add metadata
        metadata = {
            'target_id': target_id,
            'behavior': behavior,
            'sampling_rate': self.sampling_rate,
            'prf': self.prf,
            'center_frequency': self.center_frequency,
            'duration': self.duration,
            'num_samples': num_samples
        }
        
        return {
            'raw_data': raw_data,
            'position': position,
            'velocity': velocity,
            'timestamps': timestamps,
            'doppler': doppler,
            'metadata': metadata,
            'ground_truth_behavior': behavior
        }
    
    def _generate_high_speed_trajectory(self, timestamps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate high-speed trajectory (>300 m/s)."""
        num_points = len(timestamps)
        t = timestamps
        
        # Fast moving target
        speed = 350 + 50 * np.sin(0.5 * t)
        direction = 0.2 * t
        
        x = np.cumsum(speed * np.cos(direction) * np.diff(t, prepend=t[0]))
        y = np.cumsum(speed * np.sin(direction) * np.diff(t, prepend=t[0]))
        z = 8000 + 500 * np.sin(0.1 * t)
        
        position = np.column_stack([x, y, z])
        
        # Compute velocity
        velocity = np.zeros_like(position)
        if len(position) > 1:
            velocity[1:] = np.diff(position, axis=0) / np.diff(t)[:, np.newaxis]
            velocity[0] = velocity[1]
        
        return position, velocity
    
    def _generate_medium_speed_trajectory(self, timestamps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate medium-speed trajectory (150-300 m/s)."""
        t = timestamps
        
        speed = 200 + 30 * np.sin(0.3 * t)
        direction = 0.15 * t + 0.5 * np.sin(0.2 * t)
        
        x = np.cumsum(speed * np.cos(direction) * np.diff(t, prepend=t[0]))
        y = np.cumsum(speed * np.sin(direction) * np.diff(t, prepend=t[0]))
        z = 5000 + 300 * np.cos(0.15 * t)
        
        position = np.column_stack([x, y, z])
        velocity = self._compute_velocity(position, t)
        
        return position, velocity
    
    def _generate_g_turn_trajectory(self, timestamps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate trajectory with high-G turns."""
        t = timestamps
        
        # Sharp turns at specific times
        speed = 250 * np.ones_like(t)
        direction = np.zeros_like(t)
        
        # Add sharp turns
        turn_times = [15, 30, 45]
        for turn_time in turn_times:
            mask = (t > turn_time) & (t < turn_time + 2)
            direction[mask] += np.pi * (t[mask] - turn_time) / 2
        
        direction = np.cumsum(direction * np.diff(t, prepend=t[0]))
        
        x = np.cumsum(speed * np.cos(direction) * np.diff(t, prepend=t[0]))
        y = np.cumsum(speed * np.sin(direction) * np.diff(t, prepend=t[0]))
        z = 6000 + 200 * np.sin(0.1 * t)
        
        position = np.column_stack([x, y, z])
        velocity = self._compute_velocity(position, t)
        
        return position, velocity
    
    def _generate_sharp_trajectory(self, timestamps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate trajectory with sharp turns."""
        t = timestamps
        
        # Zigzag pattern
        speed = 180 * np.ones_like(t)
        direction = 2 * np.sin(0.5 * t)  # Rapid direction changes
        
        x = np.cumsum(speed * np.cos(direction) * np.diff(t, prepend=t[0]))
        y = np.cumsum(speed * np.sin(direction) * np.diff(t, prepend=t[0]))
        z = 4000 + 100 * np.sin(0.2 * t)
        
        position = np.column_stack([x, y, z])
        velocity = self._compute_velocity(position, t)
        
        return position, velocity
    
    def _generate_hovering_trajectory(self, timestamps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate hovering trajectory (very low speed)."""
        t = timestamps
        
        # Small random movements
        x = 100 * np.sin(0.1 * t) + 5 * np.random.randn(len(t))
        y = 100 * np.cos(0.1 * t) + 5 * np.random.randn(len(t))
        z = 3000 + 10 * np.sin(0.05 * t)
        
        position = np.column_stack([x, y, z])
        velocity = self._compute_velocity(position, t)
        
        return position, velocity
    
    def _generate_evasive_trajectory(self, timestamps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate evasive maneuver trajectory."""
        t = timestamps
        
        # Combination of high speed and sharp maneuvers
        speed = 300 + 50 * np.sin(t)
        direction = 3 * np.sin(0.8 * t) * np.cos(0.3 * t)
        
        x = np.cumsum(speed * np.cos(direction) * np.diff(t, prepend=t[0]))
        y = np.cumsum(speed * np.sin(direction) * np.diff(t, prepend=t[0]))
        
        # Rapid altitude changes
        z = 7000 + 1000 * np.sin(0.4 * t)
        
        position = np.column_stack([x, y, z])
        velocity = self._compute_velocity(position, t)
        
        return position, velocity
    
    def _generate_spiral_trajectory(self, timestamps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate spiral trajectory."""
        t = timestamps
        
        # Spiral pattern
        radius = 2000 + 500 * t / t[-1]
        angle = 2 * np.pi * t / 10
        
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 5000 + 100 * t
        
        position = np.column_stack([x, y, z])
        velocity = self._compute_velocity(position, t)
        
        return position, velocity
    
    def _generate_default_trajectory(self, timestamps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate default trajectory."""
        t = timestamps
        
        speed = 150 * np.ones_like(t)
        direction = 0.1 * t
        
        x = np.cumsum(speed * np.cos(direction) * np.diff(t, prepend=t[0]))
        y = np.cumsum(speed * np.sin(direction) * np.diff(t, prepend=t[0]))
        z = 5000 * np.ones_like(t)
        
        position = np.column_stack([x, y, z])
        velocity = self._compute_velocity(position, t)
        
        return position, velocity
    
    def _compute_velocity(self, position: np.ndarray, timestamps: np.ndarray) -> np.ndarray:
        """Compute velocity from position."""
        velocity = np.zeros_like(position)
        
        if len(position) > 1:
            dt = np.diff(timestamps)
            velocity[1:] = np.diff(position, axis=0) / dt[:, np.newaxis]
            velocity[0] = velocity[1]
        
        return velocity
    
    def _generate_radar_returns(self, position: np.ndarray, 
                               velocity: np.ndarray,
                               timestamps: np.ndarray) -> np.ndarray:
        """
        Generate synthetic radar return signal (complex IQ data).
        
        Args:
            position: Target position array
            velocity: Target velocity array
            timestamps: Time array
            
        Returns:
            Complex radar signal
        """
        num_samples = len(timestamps)
        
        # Range to target
        radar_position = np.array([0, 0, 0])  # Radar at origin
        ranges = np.linalg.norm(position - radar_position, axis=1)
        
        # Doppler frequency
        radial_velocity = np.sum(velocity * (position - radar_position) / ranges[:, np.newaxis], axis=1)
        doppler_freq = 2 * radial_velocity * self.center_frequency / 3e8
        
        # Generate chirp signal
        t = timestamps
        chirp_rate = self.bandwidth / (1 / self.prf)
        
        # Complex signal
        phase = 2 * np.pi * (self.center_frequency * t + doppler_freq * t + 0.5 * chirp_rate * t**2)
        amplitude = 1.0 / (ranges / 1000 + 1)  # Amplitude decreases with range
        
        signal = amplitude * np.exp(1j * phase)
        
        # Add noise
        noise = self.noise_level * (np.random.randn(num_samples) + 1j * np.random.randn(num_samples))
        signal += noise
        
        return signal
    
    def _generate_doppler_spectrum(self, velocity: np.ndarray) -> np.ndarray:
        """
        Generate Doppler spectrum from velocity.
        
        Args:
            velocity: Velocity array
            
        Returns:
            Doppler spectrum
        """
        # Compute speed
        speed = np.linalg.norm(velocity, axis=1)
        
        # FFT of speed variations
        doppler_spectrum = np.fft.fft(speed)
        doppler_spectrum = np.fft.fftshift(np.abs(doppler_spectrum))
        
        return doppler_spectrum
    
    def save_synthetic_dataset(self, dataset: List[Dict[str, Any]], 
                              output_dir: str):
        """
        Save synthetic dataset to disk.
        
        Args:
            dataset: List of synthetic target data
            output_dir: Output directory path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, data in enumerate(dataset):
            filename = output_path / f"synthetic_target_{i:03d}.h5"
            
            with h5py.File(filename, 'w') as f:
                # Save arrays
                f.create_dataset('raw_data', data=data['raw_data'], compression='gzip')
                f.create_dataset('position', data=data['position'], compression='gzip')
                f.create_dataset('velocity', data=data['velocity'], compression='gzip')
                f.create_dataset('timestamps', data=data['timestamps'], compression='gzip')
                f.create_dataset('doppler', data=data['doppler'], compression='gzip')
                
                # Save metadata
                metadata_grp = f.create_group('metadata')
                for key, value in data['metadata'].items():
                    metadata_grp.attrs[key] = value
                
                # Save ground truth
                f.attrs['ground_truth_behavior'] = data['ground_truth_behavior']
        
        logger.info(f"Saved {len(dataset)} synthetic targets to: {output_dir}")
    
    def generate_test_scenarios(self) -> List[Dict[str, Any]]:
        """
        Generate specific test scenarios for validation.
        
        Returns:
            List of test scenario data
        """
        scenarios = []
        
        # Scenario 1: High-speed intercept
        scenarios.append(self.generate_target('high_speed', target_id=1001))
        
        # Scenario 2: Combat maneuvers
        scenarios.append(self.generate_target('evasive_maneuver', target_id=1002))
        
        # Scenario 3: Surveillance pattern
        scenarios.append(self.generate_target('medium_speed', target_id=1003))
        
        # Scenario 4: Helicopter hovering
        scenarios.append(self.generate_target('hovering', target_id=1004))
        
        # Scenario 5: Sharp evasive action
        scenarios.append(self.generate_target('sharp_trajectory', target_id=1005))
        
        logger.info(f"Generated {len(scenarios)} test scenarios")
        return scenarios
