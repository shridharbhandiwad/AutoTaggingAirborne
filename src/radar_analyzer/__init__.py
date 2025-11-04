"""
Airborne Radar Target Behavior Analysis System

A comprehensive system for analyzing radar target behavior, extracting features,
tagging targets, and generating synthetic radar data.
"""

__version__ = "1.0.0"
__author__ = "Radar Analysis Team"

from .data_loader import RadarDataLoader
from .feature_extractor import FeatureExtractor
from .tagging_engine import TaggingEngine
from .synthetic_generator import SyntheticDataGenerator

__all__ = [
    "RadarDataLoader",
    "FeatureExtractor",
    "TaggingEngine",
    "SyntheticDataGenerator",
]
