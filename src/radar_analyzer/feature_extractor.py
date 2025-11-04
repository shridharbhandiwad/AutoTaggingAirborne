"""
Feature Extraction Module

Extracts relevant features from radar data for target behavior classification.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from scipy import signal, stats
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extract features from radar data for target behavior analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize feature extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.feature_scaler = StandardScaler()
        self.window_size = self.config.get('window_size', 10)
        
    def extract_all_features(self, data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Extract all features from radar data.
        
        Args:
            data: Radar data dictionary containing position, velocity, doppler, etc.
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Kinematic features
        if 'velocity' in data:
            features.update(self.extract_velocity_features(data['velocity']))
        
        if 'position' in data:
            features.update(self.extract_trajectory_features(data['position']))
        
        # Acceleration features
        if 'velocity' in data:
            acceleration = self._compute_acceleration(data['velocity'], 
                                                     data.get('timestamps'))
            features.update(self.extract_acceleration_features(acceleration))
        
        # Radar signature features
        if 'doppler' in data:
            features.update(self.extract_doppler_features(data['doppler']))
        
        if 'raw_data' in data:
            features.update(self.extract_rcs_features(data['raw_data']))
        
        # Statistical features
        features.update(self.extract_statistical_features(data))
        
        logger.info(f"Extracted {len(features)} feature sets")
        return features
    
    def extract_velocity_features(self, velocity: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract velocity-based features.
        
        Args:
            velocity: Velocity array (Nx3 for vx, vy, vz)
            
        Returns:
            Dictionary of velocity features
        """
        features = {}
        
        # Compute speed (magnitude)
        speed = np.linalg.norm(velocity, axis=1)
        features['speed'] = speed
        features['speed_mean'] = np.mean(speed)
        features['speed_std'] = np.std(speed)
        features['speed_max'] = np.max(speed)
        features['speed_min'] = np.min(speed)
        
        # Speed variation
        features['speed_variance'] = np.var(speed)
        features['speed_range'] = np.ptp(speed)
        
        # Velocity components
        features['vx_mean'] = np.mean(velocity[:, 0])
        features['vy_mean'] = np.mean(velocity[:, 1])
        features['vz_mean'] = np.mean(velocity[:, 2])
        
        # Speed percentiles
        features['speed_p25'] = np.percentile(speed, 25)
        features['speed_p50'] = np.percentile(speed, 50)
        features['speed_p75'] = np.percentile(speed, 75)
        features['speed_p95'] = np.percentile(speed, 95)
        
        return features
    
    def extract_trajectory_features(self, position: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract trajectory-based features.
        
        Args:
            position: Position array (Nx3 for x, y, z)
            
        Returns:
            Dictionary of trajectory features
        """
        features = {}
        
        # Path length
        path_segments = np.diff(position, axis=0)
        segment_lengths = np.linalg.norm(path_segments, axis=1)
        features['total_path_length'] = np.sum(segment_lengths)
        features['mean_segment_length'] = np.mean(segment_lengths)
        
        # Turn angles
        turn_angles = self._compute_turn_angles(position)
        features['turn_angles'] = turn_angles
        features['mean_turn_angle'] = np.mean(np.abs(turn_angles))
        features['max_turn_angle'] = np.max(np.abs(turn_angles))
        features['std_turn_angle'] = np.std(turn_angles)
        
        # Sharp turns count
        sharp_threshold = self.config.get('sharp_turn_angle', 45.0)
        features['sharp_turns_count'] = np.sum(np.abs(turn_angles) > sharp_threshold)
        
        # Altitude features
        altitude = position[:, 2]
        features['altitude_mean'] = np.mean(altitude)
        features['altitude_std'] = np.std(altitude)
        features['altitude_change'] = altitude[-1] - altitude[0]
        features['altitude_max'] = np.max(altitude)
        features['altitude_min'] = np.min(altitude)
        
        # Trajectory smoothness (curvature)
        curvature = self._compute_curvature(position)
        features['curvature_mean'] = np.mean(curvature)
        features['curvature_max'] = np.max(curvature)
        
        return features
    
    def extract_acceleration_features(self, acceleration: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract acceleration-based features.
        
        Args:
            acceleration: Acceleration array (Nx3)
            
        Returns:
            Dictionary of acceleration features
        """
        features = {}
        
        # G-force computation (assuming m/s^2)
        g_constant = 9.81
        g_force = np.linalg.norm(acceleration, axis=1) / g_constant
        
        features['g_force'] = g_force
        features['g_force_mean'] = np.mean(g_force)
        features['g_force_max'] = np.max(g_force)
        features['g_force_std'] = np.std(g_force)
        
        # High-G events
        high_g_threshold = self.config.get('high_g', 5.0)
        features['high_g_events'] = np.sum(g_force > high_g_threshold)
        
        # Acceleration components
        features['ax_mean'] = np.mean(acceleration[:, 0])
        features['ay_mean'] = np.mean(acceleration[:, 1])
        features['az_mean'] = np.mean(acceleration[:, 2])
        
        # Jerk (rate of change of acceleration)
        jerk = np.diff(acceleration, axis=0)
        jerk_magnitude = np.linalg.norm(jerk, axis=1)
        features['jerk_mean'] = np.mean(jerk_magnitude)
        features['jerk_max'] = np.max(jerk_magnitude)
        
        return features
    
    def extract_doppler_features(self, doppler: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract Doppler-based features.
        
        Args:
            doppler: Doppler spectrum data
            
        Returns:
            Dictionary of Doppler features
        """
        features = {}
        
        # Doppler spectrum statistics
        features['doppler_mean'] = np.mean(doppler)
        features['doppler_std'] = np.std(doppler)
        features['doppler_max'] = np.max(doppler)
        
        # Peak detection
        peaks, _ = signal.find_peaks(doppler, height=np.mean(doppler))
        features['doppler_peaks_count'] = len(peaks)
        
        if len(peaks) > 0:
            features['doppler_peak_max'] = np.max(doppler[peaks])
            features['doppler_peak_mean'] = np.mean(doppler[peaks])
        else:
            features['doppler_peak_max'] = 0
            features['doppler_peak_mean'] = 0
        
        # Bandwidth
        threshold = 0.5 * np.max(doppler)
        bandwidth_indices = np.where(doppler > threshold)[0]
        if len(bandwidth_indices) > 0:
            features['doppler_bandwidth'] = bandwidth_indices[-1] - bandwidth_indices[0]
        else:
            features['doppler_bandwidth'] = 0
        
        return features
    
    def extract_rcs_features(self, raw_data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract Radar Cross Section (RCS) features.
        
        Args:
            raw_data: Raw radar complex data
            
        Returns:
            Dictionary of RCS features
        """
        features = {}
        
        # Compute power (RCS proxy)
        power = np.abs(raw_data) ** 2
        power_db = 10 * np.log10(power + 1e-10)
        
        features['rcs_mean_db'] = np.mean(power_db)
        features['rcs_std_db'] = np.std(power_db)
        features['rcs_max_db'] = np.max(power_db)
        features['rcs_min_db'] = np.min(power_db)
        
        # RCS fluctuation
        features['rcs_fluctuation'] = np.std(power_db) / (np.mean(power_db) + 1e-10)
        
        return features
    
    def extract_statistical_features(self, data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Extract general statistical features.
        
        Args:
            data: Full radar data dictionary
            
        Returns:
            Dictionary of statistical features
        """
        features = {}
        
        # Time-based features
        if 'timestamps' in data:
            timestamps = data['timestamps']
            features['duration'] = timestamps[-1] - timestamps[0]
            features['num_samples'] = len(timestamps)
        
        # Add any metadata features
        if 'metadata' in data:
            metadata = data['metadata']
            features['prf'] = metadata.get('prf', 0)
            features['center_frequency'] = metadata.get('center_frequency', 0)
        
        return features
    
    def _compute_acceleration(self, velocity: np.ndarray, 
                            timestamps: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute acceleration from velocity.
        
        Args:
            velocity: Velocity array
            timestamps: Time array (optional)
            
        Returns:
            Acceleration array
        """
        if timestamps is not None and len(timestamps) > 1:
            dt = np.diff(timestamps)
            dt = np.append(dt, dt[-1])
            acceleration = np.diff(velocity, axis=0) / dt[:-1, np.newaxis]
        else:
            # Assume constant time step
            acceleration = np.diff(velocity, axis=0)
        
        # Pad to maintain length
        acceleration = np.vstack([acceleration, acceleration[-1]])
        
        return acceleration
    
    def _compute_turn_angles(self, position: np.ndarray) -> np.ndarray:
        """
        Compute turn angles from position trajectory.
        
        Args:
            position: Position array (Nx3)
            
        Returns:
            Array of turn angles in degrees
        """
        if len(position) < 3:
            return np.array([])
        
        # Compute vectors between consecutive points
        vectors = np.diff(position, axis=0)
        
        # Compute angles between consecutive vectors
        angles = []
        for i in range(len(vectors) - 1):
            v1 = vectors[i]
            v2 = vectors[i + 1]
            
            # Compute angle using dot product
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
            cos_angle = np.clip(cos_angle, -1, 1)
            angle = np.arccos(cos_angle)
            angles.append(np.degrees(angle))
        
        return np.array(angles)
    
    def _compute_curvature(self, position: np.ndarray) -> np.ndarray:
        """
        Compute trajectory curvature.
        
        Args:
            position: Position array (Nx3)
            
        Returns:
            Array of curvature values
        """
        if len(position) < 3:
            return np.array([0])
        
        # Compute first and second derivatives
        velocity = np.diff(position, axis=0)
        acceleration = np.diff(velocity, axis=0)
        
        # Curvature = |v x a| / |v|^3
        curvature = []
        for i in range(len(acceleration)):
            v = velocity[i + 1]
            a = acceleration[i]
            
            cross = np.cross(v, a)
            v_mag = np.linalg.norm(v)
            
            if v_mag > 1e-6:
                k = np.linalg.norm(cross) / (v_mag ** 3)
            else:
                k = 0
            
            curvature.append(k)
        
        return np.array(curvature)
    
    def prepare_dataset(self, features_list: List[Dict[str, Any]], 
                       labels: Optional[List[str]] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Prepare feature dataset for machine learning.
        
        Args:
            features_list: List of feature dictionaries
            labels: Optional list of labels
            
        Returns:
            Tuple of (feature_matrix, labels)
        """
        # Convert to feature matrix
        feature_names = []
        feature_matrix = []
        
        for features in features_list:
            feature_vector = []
            if not feature_names:
                # First iteration, establish feature names
                for key, value in features.items():
                    if isinstance(value, (int, float, np.number)):
                        feature_names.append(key)
                        feature_vector.append(float(value))
            else:
                # Extract features in consistent order
                for name in feature_names:
                    value = features.get(name, 0)
                    if isinstance(value, (int, float, np.number)):
                        feature_vector.append(float(value))
                    else:
                        feature_vector.append(0)
            
            feature_matrix.append(feature_vector)
        
        feature_matrix = np.array(feature_matrix)
        
        # Normalize features
        if len(feature_matrix) > 0:
            feature_matrix = self.feature_scaler.fit_transform(feature_matrix)
        
        label_array = np.array(labels) if labels else None
        
        logger.info(f"Prepared dataset: {feature_matrix.shape[0]} samples, {feature_matrix.shape[1]} features")
        
        return feature_matrix, label_array
