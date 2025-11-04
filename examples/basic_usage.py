#!/usr/bin/env python3
"""
Basic Usage Example for Radar Target Analyzer

This example demonstrates the basic workflow of the system.
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
    print("=" * 60)
    print("Radar Target Analyzer - Basic Usage Example")
    print("=" * 60)
    print()
    
    # Step 1: Generate synthetic test data
    print("Step 1: Generating synthetic test data...")
    generator = SyntheticDataGenerator({
        'duration': 60.0,
        'noise_level': 0.05
    })
    
    # Generate a high-speed target
    target_data = generator.generate_target('high_speed', target_id=1)
    print(f"✓ Generated synthetic {target_data['ground_truth_behavior']} target")
    print()
    
    # Step 2: Extract features
    print("Step 2: Extracting features...")
    extractor = FeatureExtractor()
    features = extractor.extract_all_features(target_data)
    print(f"✓ Extracted {len([k for k in features.keys() if not k.startswith('_')])} features")
    
    # Display some key features
    print("\nKey Features:")
    print(f"  - Average Speed: {features.get('speed_mean', 0):.1f} m/s")
    print(f"  - Max Speed: {features.get('speed_max', 0):.1f} m/s")
    print(f"  - Max G-Force: {features.get('g_force_max', 0):.2f} g")
    print(f"  - Mean Turn Angle: {features.get('mean_turn_angle', 0):.1f}°")
    print(f"  - Path Length: {features.get('total_path_length', 0):.1f} m")
    print()
    
    # Step 3: Tag behavior
    print("Step 3: Tagging target behavior...")
    tagger = TaggingEngine()
    tags = tagger.tag_target(features)
    print(f"✓ Identified {len(tags)} behavior tags")
    
    print("\nDetected Behaviors:")
    for tag in tags:
        print(f"  • {tag.replace('_', ' ').title()}")
    print()
    
    # Step 4: Generate report
    print("Step 4: Generating detailed report...")
    report = tagger.generate_report(features, tags)
    print(report)
    print()
    
    # Step 5: Compare with ground truth
    print("Step 5: Validation")
    ground_truth = target_data['ground_truth_behavior']
    print(f"Ground Truth Behavior: {ground_truth}")
    
    if ground_truth in tags or any(ground_truth in tag for tag in tags):
        print("✓ Ground truth behavior correctly identified!")
    else:
        print("⚠ Ground truth behavior not in detected tags")
        print(f"  (This is normal as tags may be more specific than ground truth)")
    
    print()
    print("=" * 60)
    print("Example Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
