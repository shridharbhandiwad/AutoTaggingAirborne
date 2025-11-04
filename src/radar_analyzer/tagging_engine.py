"""
Tagging Engine Module

Tags radar targets based on extracted features and behavior patterns.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class BehaviorTag(Enum):
    """Enumeration of target behavior tags."""
    HIGH_SPEED = "high_speed"
    MEDIUM_SPEED = "medium_speed"
    LOW_SPEED = "low_speed"
    G_TURN = "g_turn"
    SHARP_TRAJECTORY = "sharp_trajectory"
    SMOOTH_TRAJECTORY = "smooth_trajectory"
    HOVERING = "hovering"
    ASCENDING = "ascending"
    DESCENDING = "descending"
    EVASIVE_MANEUVER = "evasive_maneuver"
    ACCELERATING = "accelerating"
    DECELERATING = "decelerating"
    STRAIGHT_LINE = "straight_line"
    SPIRAL = "spiral"
    LOITERING = "loitering"


class TaggingEngine:
    """
    Engine for tagging radar targets based on behavior analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize tagging engine.
        
        Args:
            config: Configuration dictionary with thresholds
        """
        self.config = config or {}
        self._load_thresholds()
        
    def _load_thresholds(self):
        """Load classification thresholds from config."""
        # Velocity thresholds
        vel_config = self.config.get('velocity_threshold', {})
        self.high_speed_thresh = vel_config.get('high_speed', 300.0)  # m/s
        self.medium_speed_thresh = vel_config.get('medium_speed', 150.0)  # m/s
        self.low_speed_thresh = vel_config.get('low_speed', 50.0)  # m/s
        self.hovering_speed_thresh = 5.0  # m/s
        
        # Acceleration thresholds
        accel_config = self.config.get('acceleration_threshold', {})
        self.high_g_thresh = accel_config.get('high_g', 5.0)  # g-force
        self.medium_g_thresh = accel_config.get('medium_g', 2.0)  # g-force
        
        # Trajectory thresholds
        traj_config = self.config.get('trajectory', {})
        self.sharp_turn_thresh = traj_config.get('sharp_turn_angle', 45.0)  # degrees
        self.smooth_turn_thresh = traj_config.get('smooth_turn_angle', 15.0)  # degrees
        
        # Altitude thresholds
        self.ascending_rate_thresh = 10.0  # m/s
        self.descending_rate_thresh = -10.0  # m/s
        
    def tag_target(self, features: Dict[str, Any]) -> List[str]:
        """
        Tag a single target based on its features.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            List of behavior tags
        """
        tags = set()
        
        # Speed-based tags
        tags.update(self._tag_speed(features))
        
        # Acceleration-based tags
        tags.update(self._tag_acceleration(features))
        
        # Trajectory-based tags
        tags.update(self._tag_trajectory(features))
        
        # Altitude-based tags
        tags.update(self._tag_altitude(features))
        
        # Complex behavior patterns
        tags.update(self._tag_complex_behaviors(features))
        
        tag_list = sorted(list(tags))
        logger.info(f"Tagged target with: {', '.join(tag_list)}")
        
        return tag_list
    
    def _tag_speed(self, features: Dict[str, Any]) -> Set[str]:
        """Tag based on speed characteristics."""
        tags = set()
        
        speed_mean = features.get('speed_mean', 0)
        speed_std = features.get('speed_std', 0)
        
        # Speed categories
        if speed_mean >= self.high_speed_thresh:
            tags.add(BehaviorTag.HIGH_SPEED.value)
        elif speed_mean >= self.medium_speed_thresh:
            tags.add(BehaviorTag.MEDIUM_SPEED.value)
        elif speed_mean >= self.low_speed_thresh:
            tags.add(BehaviorTag.LOW_SPEED.value)
        elif speed_mean < self.hovering_speed_thresh:
            tags.add(BehaviorTag.HOVERING.value)
        
        # Acceleration/deceleration based on speed variance
        if speed_std > 0.3 * speed_mean:
            # High speed variance indicates acceleration/deceleration
            speed = features.get('speed', np.array([]))
            if isinstance(speed, np.ndarray) and len(speed) > 2:
                speed_trend = np.polyfit(range(len(speed)), speed, 1)[0]
                if speed_trend > 5.0:
                    tags.add(BehaviorTag.ACCELERATING.value)
                elif speed_trend < -5.0:
                    tags.add(BehaviorTag.DECELERATING.value)
        
        return tags
    
    def _tag_acceleration(self, features: Dict[str, Any]) -> Set[str]:
        """Tag based on acceleration characteristics."""
        tags = set()
        
        g_force_max = features.get('g_force_max', 0)
        g_force_mean = features.get('g_force_mean', 0)
        high_g_events = features.get('high_g_events', 0)
        
        # High-G maneuvers
        if g_force_max > self.high_g_thresh or high_g_events > 0:
            tags.add(BehaviorTag.G_TURN.value)
            tags.add(BehaviorTag.EVASIVE_MANEUVER.value)
        
        return tags
    
    def _tag_trajectory(self, features: Dict[str, Any]) -> Set[str]:
        """Tag based on trajectory characteristics."""
        tags = set()
        
        mean_turn_angle = features.get('mean_turn_angle', 0)
        max_turn_angle = features.get('max_turn_angle', 0)
        sharp_turns_count = features.get('sharp_turns_count', 0)
        curvature_mean = features.get('curvature_mean', 0)
        
        # Trajectory smoothness
        if sharp_turns_count > 2 or max_turn_angle > self.sharp_turn_thresh:
            tags.add(BehaviorTag.SHARP_TRAJECTORY.value)
        elif mean_turn_angle < self.smooth_turn_thresh:
            tags.add(BehaviorTag.SMOOTH_TRAJECTORY.value)
        
        # Straight line motion
        if mean_turn_angle < 5.0 and curvature_mean < 0.001:
            tags.add(BehaviorTag.STRAIGHT_LINE.value)
        
        # Spiral pattern (high curvature, consistent turns)
        if curvature_mean > 0.01 and mean_turn_angle > 20.0:
            std_turn = features.get('std_turn_angle', 0)
            if std_turn < 0.3 * mean_turn_angle:
                tags.add(BehaviorTag.SPIRAL.value)
        
        return tags
    
    def _tag_altitude(self, features: Dict[str, Any]) -> Set[str]:
        """Tag based on altitude characteristics."""
        tags = set()
        
        altitude_change = features.get('altitude_change', 0)
        duration = features.get('duration', 1.0)
        
        if duration > 0:
            altitude_rate = altitude_change / duration
            
            if altitude_rate > self.ascending_rate_thresh:
                tags.add(BehaviorTag.ASCENDING.value)
            elif altitude_rate < self.descending_rate_thresh:
                tags.add(BehaviorTag.DESCENDING.value)
        
        return tags
    
    def _tag_complex_behaviors(self, features: Dict[str, Any]) -> Set[str]:
        """Tag complex behavior patterns."""
        tags = set()
        
        speed_mean = features.get('speed_mean', 0)
        speed_std = features.get('speed_std', 0)
        mean_turn_angle = features.get('mean_turn_angle', 0)
        path_length = features.get('total_path_length', 0)
        
        # Loitering (low speed, circular pattern)
        if speed_mean < self.low_speed_thresh:
            if mean_turn_angle > 10.0 and path_length > 1000:
                tags.add(BehaviorTag.LOITERING.value)
        
        # Evasive maneuver (combination of high speed, high G, sharp turns)
        if BehaviorTag.G_TURN.value in tags and BehaviorTag.SHARP_TRAJECTORY.value in tags:
            if speed_mean > self.medium_speed_thresh:
                tags.add(BehaviorTag.EVASIVE_MANEUVER.value)
        
        return tags
    
    def batch_tag(self, features_list: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Tag multiple targets in batch.
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            List of tag lists for each target
        """
        all_tags = []
        
        for i, features in enumerate(features_list):
            logger.info(f"Tagging target {i+1}/{len(features_list)}")
            tags = self.tag_target(features)
            all_tags.append(tags)
        
        return all_tags
    
    def generate_report(self, features: Dict[str, Any], tags: List[str]) -> str:
        """
        Generate a human-readable report for a tagged target.
        
        Args:
            features: Feature dictionary
            tags: List of tags
            
        Returns:
            Report string
        """
        report = []
        report.append("=" * 60)
        report.append("TARGET BEHAVIOR ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Tags
        report.append("BEHAVIOR TAGS:")
        for tag in tags:
            report.append(f"  • {tag.replace('_', ' ').title()}")
        report.append("")
        
        # Key metrics
        report.append("KEY METRICS:")
        
        # Speed
        speed_mean = features.get('speed_mean', 0)
        speed_max = features.get('speed_max', 0)
        report.append(f"  Speed: {speed_mean:.1f} m/s (avg), {speed_max:.1f} m/s (max)")
        
        # Acceleration
        g_force_max = features.get('g_force_max', 0)
        report.append(f"  G-Force: {g_force_max:.2f} g (max)")
        
        # Trajectory
        mean_turn = features.get('mean_turn_angle', 0)
        max_turn = features.get('max_turn_angle', 0)
        report.append(f"  Turn Angles: {mean_turn:.1f}° (avg), {max_turn:.1f}° (max)")
        
        # Altitude
        alt_mean = features.get('altitude_mean', 0)
        alt_change = features.get('altitude_change', 0)
        report.append(f"  Altitude: {alt_mean:.1f} m (avg), {alt_change:+.1f} m (change)")
        
        # Path
        path_length = features.get('total_path_length', 0)
        duration = features.get('duration', 0)
        report.append(f"  Path Length: {path_length:.1f} m over {duration:.1f} s")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def export_tags(self, features_list: List[Dict[str, Any]], 
                   tags_list: List[List[str]],
                   output_path: str):
        """
        Export tags and features to file.
        
        Args:
            features_list: List of feature dictionaries
            tags_list: List of tag lists
            output_path: Output file path
        """
        import json
        from pathlib import Path
        
        export_data = []
        
        for features, tags in zip(features_list, tags_list):
            # Convert numpy arrays to lists for JSON serialization
            features_serializable = {}
            for key, value in features.items():
                if isinstance(value, np.ndarray):
                    features_serializable[key] = value.tolist()
                elif isinstance(value, (np.integer, np.floating)):
                    features_serializable[key] = float(value)
                else:
                    features_serializable[key] = value
            
            export_data.append({
                'features': features_serializable,
                'tags': tags
            })
        
        # Save to JSON
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported tags to: {output_path}")
