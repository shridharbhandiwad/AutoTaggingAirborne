# Airborne Radar Target Behavior Analysis System

A comprehensive Python-based system for analyzing airborne radar target behavior, extracting features, automatically tagging targets based on behavioral patterns, and generating synthetic radar data for testing and training.

## 🚀 Features

### Core Capabilities
- **Multi-format Data Loading**: Support for binary (.bin, .dat) and HDF5 (.h5, .hdf5) radar data files
- **Advanced Feature Extraction**: 
  - Kinematic features (velocity, acceleration, G-force)
  - Trajectory analysis (turn angles, curvature, path smoothness)
  - Doppler spectrum analysis
  - Radar Cross Section (RCS) characteristics
  - Statistical metrics
- **Intelligent Behavior Tagging**: Automatic classification of target behaviors including:
  - Speed categories (high-speed, medium-speed, low-speed, hovering)
  - Maneuver patterns (G-turns, sharp trajectory, smooth trajectory, evasive maneuvers)
  - Flight profiles (ascending, descending, straight-line, spiral, loitering)
- **External Algorithm Integration**: Interface for C++ and MATLAB algorithm integration
- **Synthetic Data Generation**: Generate realistic synthetic radar data with configurable behaviors
- **Interactive GUI**: Full-featured PyQt5 graphical interface
- **Command-Line Interface**: Powerful CLI for batch processing and automation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [GUI Mode](#gui-mode)
  - [Command-Line Mode](#command-line-mode)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Data Formats](#data-formats)
- [Behavior Tags](#behavior-tags)
- [Examples](#examples)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) MATLAB R2021a or higher for MATLAB integration
- (Optional) C++ compiler for custom algorithm compilation

### Standard Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd workspace
```

2. **Create virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install the package** (optional):
```bash
pip install -e .
```

### Development Installation

For development with testing capabilities:
```bash
pip install -e ".[dev]"
```

## 🏃 Quick Start

### Launch GUI
```bash
# Using run script (no installation needed)
python run_gui.py

# Or if installed
radar-analyzer gui
```

### Analyze a Single File
```bash
python run.py analyze -i data/sample_radar_data.bin -o results.json
```

### Generate Synthetic Data
```bash
python run.py generate -o data/synthetic/ -n 50
```

## 📖 Usage

### GUI Mode

The GUI provides an intuitive interface with multiple tabs:

1. **Data Loading Tab**
   - Select and load radar data files
   - View data information and metadata
   - Visualize Doppler spectrum

2. **Analysis & Tagging Tab**
   - Extract features from loaded data
   - Automatically tag target behavior
   - Visualize trajectories
   - View detailed analysis reports

3. **Synthetic Data Tab**
   - Generate synthetic datasets
   - Create test scenarios
   - Configure generation parameters

4. **Configuration Tab**
   - Edit system configuration
   - Load/save configuration files
   - Adjust thresholds and parameters

5. **Results Tab**
   - View detailed analysis reports
   - Export results

#### Launching the GUI
```bash
# Method 1: Direct script
python run_gui.py

# Method 2: Main launcher
python run.py gui

# Method 3: Installed command
radar-analyzer gui
```

### Command-Line Mode

#### Analyze Single File
```bash
python run.py analyze -i <input_file> -o <output_file> [options]

# Example
python run.py analyze -i data/radar_track.bin -o results/track_analysis.json
```

#### Batch Analysis
Process multiple files in a directory:
```bash
python run.py batch -i <input_dir> -o <output_dir> [options]

# Example
python run.py batch -i data/raw/ -o results/batch_analysis/
```

#### Generate Synthetic Data
```bash
python run.py generate -o <output_dir> -n <num_targets> [options]

# Example - Generate 100 synthetic targets
python run.py generate -o data/synthetic/ -n 100

# With custom configuration
python run.py generate -o data/synthetic/ -n 100 -c config/custom_config.yaml
```

#### Generate Test Scenarios
```bash
python run.py test -o <output_dir>

# Example
python run.py test -o data/test_scenarios/
```

#### CLI Options
- `-i, --input`: Input file or directory
- `-o, --output`: Output file or directory
- `-c, --config`: Configuration file path
- `-n, --num-targets`: Number of synthetic targets
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Log file path

## 🏗️ Architecture

### Project Structure
```
workspace/
├── src/
│   └── radar_analyzer/
│       ├── __init__.py              # Main package
│       ├── data_loader.py           # Data loading and I/O
│       ├── external_interface.py    # C++/MATLAB integration
│       ├── feature_extractor.py     # Feature extraction
│       ├── tagging_engine.py        # Behavior tagging
│       ├── synthetic_generator.py   # Synthetic data generation
│       ├── main.py                  # CLI entry point
│       └── gui/
│           ├── __init__.py
│           └── main_window.py       # GUI implementation
├── config/
│   └── default_config.yaml          # Default configuration
├── tests/
│   ├── test_data_loader.py
│   ├── test_feature_extractor.py
│   └── test_tagging_engine.py
├── data/
│   ├── raw/                         # Raw radar data
│   ├── processed/                   # Processed data
│   └── synthetic/                   # Synthetic data
├── docs/
│   ├── API.md                       # API documentation
│   ├── ALGORITHMS.md                # Algorithm descriptions
│   └── CONFIGURATION.md             # Configuration guide
├── requirements.txt
├── setup.py
├── run.py                           # Quick launch script
├── run_gui.py                       # GUI launch script
└── README.md
```

### Module Overview

#### `data_loader.py`
- Loads binary and HDF5 radar data files
- Parses headers and metadata
- Extracts position, velocity, and Doppler data
- Handles multiple data formats

#### `feature_extractor.py`
- Extracts kinematic features (velocity, acceleration)
- Computes trajectory characteristics (turns, curvature)
- Analyzes Doppler spectrum
- Calculates RCS metrics
- Prepares datasets for machine learning

#### `tagging_engine.py`
- Classifies target behavior based on features
- Applies configurable thresholds
- Generates human-readable reports
- Exports results in JSON format

#### `synthetic_generator.py`
- Generates realistic target trajectories
- Simulates radar returns (IQ data)
- Creates Doppler spectra
- Supports multiple behavior patterns

#### `external_interface.py`
- Interfaces with C++ shared libraries
- Calls MATLAB engine functions
- Provides Python fallback implementations
- Implements common radar algorithms (SAR, Doppler, MTI)

## ⚙️ Configuration

Configuration is managed through YAML files. The default configuration is in `config/default_config.yaml`.

### Key Configuration Sections

#### Feature Thresholds
```yaml
features:
  velocity_threshold:
    high_speed: 300.0    # m/s
    medium_speed: 150.0  # m/s
    low_speed: 50.0      # m/s
  
  acceleration_threshold:
    high_g: 5.0          # g-force
    medium_g: 2.0        # g-force
  
  trajectory:
    sharp_turn_angle: 45.0   # degrees
    smooth_turn_angle: 15.0  # degrees
```

#### External Algorithms
```yaml
external_algorithms:
  cpp_lib_path: "lib/radar_algorithms.so"
  matlab_enabled: false
  matlab_functions:
    - "sar_processing"
    - "doppler_analysis"
```

#### Synthetic Data
```yaml
synthetic_data:
  num_samples: 10000
  duration: 60.0        # seconds
  noise_level: 0.05
  num_targets: 5
```

See `docs/CONFIGURATION.md` for detailed configuration options.

## 📊 Data Formats

### Input Formats

#### Binary Format (.bin, .dat)
```
Header (256 bytes):
  - Bytes 0-3:   Magic number (uint32)
  - Bytes 4-7:   Version (uint32)
  - Bytes 8-11:  Sampling rate (uint32)
  - Bytes 12-15: Number of channels (uint32)
  - Bytes 16-19: Samples per pulse (uint32)
  - Bytes 20-23: PRF (float32)
  - Bytes 24-27: Center frequency (float32)
  - Bytes 28-255: Reserved

Data Section:
  - Complex IQ samples (float32 pairs: I, Q)
```

#### HDF5 Format (.h5, .hdf5)
```
Datasets:
  - /raw_data: Complex radar samples
  - /position: Position data (Nx3: x, y, z)
  - /velocity: Velocity data (Nx3: vx, vy, vz)
  - /timestamps: Time array
  - /doppler: Doppler spectrum
  
Attributes:
  - metadata/*: Various metadata fields
```

### Output Formats

#### JSON Export
```json
{
  "features": {
    "speed_mean": 245.3,
    "g_force_max": 4.2,
    "mean_turn_angle": 32.5,
    ...
  },
  "tags": [
    "high_speed",
    "g_turn",
    "evasive_maneuver"
  ]
}
```

## 🏷️ Behavior Tags

The system can automatically detect and tag the following behaviors:

### Speed-Based
- **high_speed**: > 300 m/s (e.g., fighter jets, missiles)
- **medium_speed**: 150-300 m/s (e.g., commercial aircraft)
- **low_speed**: 50-150 m/s (e.g., helicopters, drones)
- **hovering**: < 5 m/s (e.g., stationary helicopters)

### Maneuver-Based
- **g_turn**: High G-force turns (> 5g)
- **sharp_trajectory**: Sharp direction changes (> 45°)
- **smooth_trajectory**: Gradual turns (< 15°)
- **evasive_maneuver**: Combination of high speed + high G + sharp turns
- **straight_line**: Minimal course deviation

### Flight Profile
- **ascending**: Positive altitude rate (> 10 m/s)
- **descending**: Negative altitude rate (< -10 m/s)
- **spiral**: Circular pattern with consistent turns
- **loitering**: Low speed circular pattern
- **accelerating**: Increasing speed trend
- **decelerating**: Decreasing speed trend

## 📚 Examples

### Example 1: Analyze a Combat Maneuver
```python
from radar_analyzer import RadarDataLoader, FeatureExtractor, TaggingEngine

# Load data
loader = RadarDataLoader()
data = loader.load_file('combat_maneuver.bin')

# Extract features
extractor = FeatureExtractor()
features = extractor.extract_all_features(data)

# Tag behavior
tagger = TaggingEngine()
tags = tagger.tag_target(features)

# Generate report
report = tagger.generate_report(features, tags)
print(report)
```

### Example 2: Generate Synthetic Training Data
```python
from radar_analyzer import SyntheticDataGenerator

# Create generator
generator = SyntheticDataGenerator({
    'num_targets': 100,
    'duration': 60.0,
    'noise_level': 0.05
})

# Generate dataset with specific behavior distribution
dataset = generator.generate_dataset({
    'high_speed': 0.3,
    'g_turn': 0.2,
    'evasive_maneuver': 0.2,
    'hovering': 0.15,
    'medium_speed': 0.15
})

# Save dataset
generator.save_synthetic_dataset(dataset, 'training_data/')
```

### Example 3: Batch Processing with Custom Config
```bash
# Create custom configuration
cat > my_config.yaml << EOF
features:
  velocity_threshold:
    high_speed: 350.0  # Higher threshold
  acceleration_threshold:
    high_g: 6.0        # Higher G threshold
EOF

# Run batch analysis
python run.py batch -i data/mission_tracks/ -o results/ -c my_config.yaml
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=radar_analyzer tests/

# Run specific test
pytest tests/test_feature_extractor.py
```

### Generate Test Data
```bash
# Generate test scenarios
python run.py test -o data/test_scenarios/

# This creates 5 test files with different behaviors
```

### Manual Testing with GUI
1. Launch GUI: `python run_gui.py`
2. Go to "Synthetic Data" tab
3. Click "Generate Test Scenarios"
4. Select output directory
5. Go back to "Data Loading" tab
6. Load generated test files
7. Analyze and verify tags

## 📝 Documentation

Detailed documentation is available in the `docs/` directory:

- **API.md**: Complete API reference
- **ALGORITHMS.md**: Algorithm descriptions and mathematical details
- **CONFIGURATION.md**: Configuration options and examples
- **INTEGRATION.md**: Guide for C++/MATLAB integration
- **EXAMPLES.md**: More usage examples

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check documentation in `docs/` directory
- Review examples in the `examples/` directory

## 🔮 Future Enhancements

- Machine learning-based classification
- Real-time data streaming support
- Advanced visualization (3D trajectories)
- Multi-target tracking
- Clutter rejection algorithms
- SAR image formation
- Integration with more external tools

## 📊 System Requirements

### Minimum
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Storage: 1 GB free space
- OS: Windows 10, Linux (Ubuntu 18.04+), macOS 10.14+

### Recommended
- CPU: Quad-core 3.0 GHz or better
- RAM: 8 GB or more
- Storage: 10 GB free space (for datasets)
- GPU: Optional, for future ML features

## 🎯 Use Cases

- **Military**: Combat aircraft behavior analysis, threat assessment
- **Aviation**: Air traffic pattern analysis, safety monitoring
- **Research**: Radar algorithm development, dataset generation
- **Training**: Synthetic data for ML model training
- **Testing**: Validation of radar processing algorithms

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-04  
**Authors**: Radar Analysis Team
