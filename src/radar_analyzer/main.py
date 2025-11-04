#!/usr/bin/env python3
"""
Main Entry Point for Radar Target Analyzer

Provides both CLI and GUI interfaces for the application.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
import yaml

from radar_analyzer import (
    RadarDataLoader,
    FeatureExtractor,
    TaggingEngine,
    SyntheticDataGenerator
)


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        level: Logging level
        log_file: Optional log file path
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )


def load_config(config_path: Optional[str] = None) -> dict:
    """
    Load configuration file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Use default config
        default_config_path = Path(__file__).parent.parent.parent / 'config' / 'default_config.yaml'
        if default_config_path.exists():
            with open(default_config_path, 'r') as f:
                return yaml.safe_load(f)
    
    return {}


def analyze_file(input_file: str, config: dict, output_file: Optional[str] = None):
    """
    Analyze a single radar data file.
    
    Args:
        input_file: Input radar data file path
        config: Configuration dictionary
        output_file: Optional output file path
    """
    logger = logging.getLogger(__name__)
    
    logger.info(f"Analyzing file: {input_file}")
    
    # Initialize modules
    data_loader = RadarDataLoader(config.get('data_processing', {}))
    feature_extractor = FeatureExtractor(config.get('features', {}))
    tagging_engine = TaggingEngine(config.get('features', {}))
    
    # Load data
    logger.info("Loading radar data...")
    data = data_loader.load_file(input_file)
    
    # Extract features
    logger.info("Extracting features...")
    features = feature_extractor.extract_all_features(data)
    
    # Tag behavior
    logger.info("Tagging target behavior...")
    tags = tagging_engine.tag_target(features)
    
    # Generate report
    report = tagging_engine.generate_report(features, tags)
    print("\n" + report)
    
    # Export results
    if output_file:
        logger.info(f"Exporting results to: {output_file}")
        tagging_engine.export_tags([features], [tags], output_file)
    
    logger.info("Analysis complete!")


def analyze_batch(input_dir: str, config: dict, output_dir: str):
    """
    Analyze multiple radar data files in batch.
    
    Args:
        input_dir: Input directory containing radar data files
        config: Configuration dictionary
        output_dir: Output directory for results
    """
    logger = logging.getLogger(__name__)
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all supported files
    supported_exts = ['.bin', '.dat', '.h5', '.hdf5']
    files = []
    for ext in supported_exts:
        files.extend(input_path.glob(f'*{ext}'))
    
    logger.info(f"Found {len(files)} files to analyze")
    
    # Initialize modules
    data_loader = RadarDataLoader(config.get('data_processing', {}))
    feature_extractor = FeatureExtractor(config.get('features', {}))
    tagging_engine = TaggingEngine(config.get('features', {}))
    
    all_features = []
    all_tags = []
    
    for i, file_path in enumerate(files):
        logger.info(f"Processing file {i+1}/{len(files)}: {file_path.name}")
        
        try:
            # Load and analyze
            data = data_loader.load_file(str(file_path))
            features = feature_extractor.extract_all_features(data)
            tags = tagging_engine.tag_target(features)
            
            all_features.append(features)
            all_tags.append(tags)
            
            # Generate individual report
            report = tagging_engine.generate_report(features, tags)
            report_path = output_path / f"{file_path.stem}_report.txt"
            with open(report_path, 'w') as f:
                f.write(report)
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            continue
    
    # Export combined results
    combined_output = output_path / "combined_results.json"
    tagging_engine.export_tags(all_features, all_tags, str(combined_output))
    
    logger.info(f"Batch analysis complete! Processed {len(all_features)} files")


def generate_synthetic(config: dict, output_dir: str, num_targets: Optional[int] = None):
    """
    Generate synthetic radar data.
    
    Args:
        config: Configuration dictionary
        output_dir: Output directory
        num_targets: Optional number of targets to generate
    """
    logger = logging.getLogger(__name__)
    
    # Update config if num_targets specified
    synth_config = config.get('synthetic_data', {}).copy()
    if num_targets:
        synth_config['num_targets'] = num_targets
    
    generator = SyntheticDataGenerator(synth_config)
    
    logger.info(f"Generating {synth_config.get('num_targets', 5)} synthetic targets...")
    dataset = generator.generate_dataset()
    
    logger.info(f"Saving to: {output_dir}")
    generator.save_synthetic_dataset(dataset, output_dir)
    
    logger.info("Synthetic data generation complete!")


def generate_test_scenarios(config: dict, output_dir: str):
    """
    Generate test scenarios.
    
    Args:
        config: Configuration dictionary
        output_dir: Output directory
    """
    logger = logging.getLogger(__name__)
    
    generator = SyntheticDataGenerator(config.get('synthetic_data', {}))
    
    logger.info("Generating test scenarios...")
    scenarios = generator.generate_test_scenarios()
    
    logger.info(f"Saving to: {output_dir}")
    generator.save_synthetic_dataset(scenarios, output_dir)
    
    logger.info("Test scenarios generated!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Airborne Radar Target Behavior Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch GUI
  radar-analyzer gui
  
  # Analyze single file
  radar-analyzer analyze -i data.bin -o results.json
  
  # Batch analysis
  radar-analyzer batch -i data_dir/ -o results_dir/
  
  # Generate synthetic data
  radar-analyzer generate -o synthetic_data/ -n 100
  
  # Generate test scenarios
  radar-analyzer test -o test_scenarios/
        """
    )
    
    parser.add_argument(
        'command',
        choices=['gui', 'analyze', 'batch', 'generate', 'test'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '-i', '--input',
        help='Input file or directory'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file or directory'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '-n', '--num-targets',
        type=int,
        help='Number of synthetic targets to generate'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log file path'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = load_config(args.config)
    
    try:
        if args.command == 'gui':
            # Launch GUI
            logger.info("Launching GUI...")
            from radar_analyzer.gui import launch_gui
            launch_gui()
        
        elif args.command == 'analyze':
            # Analyze single file
            if not args.input:
                parser.error("analyze command requires -i/--input")
            analyze_file(args.input, config, args.output)
        
        elif args.command == 'batch':
            # Batch analysis
            if not args.input or not args.output:
                parser.error("batch command requires -i/--input and -o/--output")
            analyze_batch(args.input, config, args.output)
        
        elif args.command == 'generate':
            # Generate synthetic data
            if not args.output:
                parser.error("generate command requires -o/--output")
            generate_synthetic(config, args.output, args.num_targets)
        
        elif args.command == 'test':
            # Generate test scenarios
            if not args.output:
                parser.error("test command requires -o/--output")
            generate_test_scenarios(config, args.output)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
