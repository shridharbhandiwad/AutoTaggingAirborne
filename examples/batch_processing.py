#!/usr/bin/env python3
"""
Batch Processing Example

Demonstrates how to process multiple radar files in batch.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from radar_analyzer import (
    RadarDataLoader,
    FeatureExtractor,
    TaggingEngine,
    SyntheticDataGenerator
)


def main():
    print("Batch Processing Example")
    print("=" * 60)
    
    # Step 1: Generate multiple test targets
    print("\n1. Generating test dataset...")
    generator = SyntheticDataGenerator({'duration': 30.0})
    
    behaviors = ['high_speed', 'medium_speed', 'g_turn', 'hovering', 'evasive_maneuver']
    dataset = []
    
    for i, behavior in enumerate(behaviors):
        data = generator.generate_target(behavior, target_id=i)
        dataset.append(data)
        print(f"   Generated target {i+1}: {behavior}")
    
    # Step 2: Process all targets
    print("\n2. Processing all targets...")
    extractor = FeatureExtractor()
    tagger = TaggingEngine()
    
    all_features = []
    all_tags = []
    
    for i, data in enumerate(dataset):
        print(f"\n   Processing target {i+1}...")
        
        # Extract features
        features = extractor.extract_all_features(data)
        all_features.append(features)
        
        # Tag behavior
        tags = tagger.tag_target(features)
        all_tags.append(tags)
        
        # Show summary
        ground_truth = data['ground_truth_behavior']
        speed = features.get('speed_mean', 0)
        print(f"   - Ground Truth: {ground_truth}")
        print(f"   - Detected Tags: {', '.join(tags)}")
        print(f"   - Avg Speed: {speed:.1f} m/s")
    
    # Step 3: Generate summary statistics
    print("\n3. Summary Statistics")
    print("=" * 60)
    
    # Count tag occurrences
    tag_counts = {}
    for tags in all_tags:
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\nTag Distribution:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tag}: {count} targets")
    
    # Speed statistics
    speeds = [f.get('speed_mean', 0) for f in all_features]
    print(f"\nSpeed Statistics:")
    print(f"  Min: {min(speeds):.1f} m/s")
    print(f"  Max: {max(speeds):.1f} m/s")
    print(f"  Average: {sum(speeds)/len(speeds):.1f} m/s")
    
    # G-force statistics
    g_forces = [f.get('g_force_max', 0) for f in all_features]
    print(f"\nG-Force Statistics:")
    print(f"  Max across all: {max(g_forces):.2f} g")
    print(f"  Average max: {sum(g_forces)/len(g_forces):.2f} g")
    
    print("\n" + "=" * 60)
    print("Batch Processing Complete!")
    print(f"Processed {len(dataset)} targets successfully")
    print("=" * 60)


if __name__ == '__main__':
    main()
