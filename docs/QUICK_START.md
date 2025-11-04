# Quick Start Guide

Get up and running with the Radar Target Analyzer in minutes!

## Installation

### 1. Clone and Setup
```bash
# Clone repository
cd workspace

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## First Run

### Option 1: GUI (Recommended for Beginners)

```bash
# Launch the GUI
python run_gui.py
```

The GUI will open with five tabs:
1. **Data Loading** - Load radar files
2. **Analysis & Tagging** - Analyze and tag behaviors
3. **Synthetic Data** - Generate test data
4. **Configuration** - Adjust settings
5. **Results** - View reports

### Option 2: Generate and Analyze Test Data

Since you don't have real radar data yet, let's generate some test data:

```bash
# Step 1: Generate test scenarios
python run.py test -o data/test_scenarios/

# Step 2: Analyze a test file
python run.py analyze -i data/test_scenarios/synthetic_target_000.h5 -o results/test_analysis.json

# Step 3: View results
cat results/test_analysis.json
```

## Complete Workflow Example

### Using GUI

1. **Launch GUI**
   ```bash
   python run_gui.py
   ```

2. **Generate Test Data**
   - Go to "Synthetic Data" tab
   - Set "Number of Targets" to 5
   - Click "Generate Test Scenarios"
   - Select output folder (e.g., `data/test`)

3. **Load Data**
   - Go to "Data Loading" tab
   - Click "Select Radar Data File"
   - Choose one of the generated .h5 files
   - Click "Load Data"
   - View the Doppler spectrum plot

4. **Analyze**
   - Go to "Analysis & Tagging" tab
   - Click "Extract Features"
   - Click "Tag Behavior"
   - View results in the Features table and Tags panel
   - See trajectory visualization

5. **Export**
   - Click "Export Results"
   - Choose output location
   - Open the JSON file to see detailed results

### Using Command Line

```bash
# 1. Generate synthetic training dataset (100 targets)
python run.py generate -o data/synthetic_dataset/ -n 100

# 2. Generate test scenarios (5 specific behavior patterns)
python run.py test -o data/test_scenarios/

# 3. Analyze a single file
python run.py analyze \
    -i data/test_scenarios/synthetic_target_000.h5 \
    -o results/analysis_000.json

# 4. Batch process all test files
python run.py batch \
    -i data/test_scenarios/ \
    -o results/batch_results/

# 5. View the combined results
cat results/batch_results/combined_results.json
```

## Understanding the Output

### Analysis Report
When you analyze a target, you'll see a report like this:

```
============================================================
TARGET BEHAVIOR ANALYSIS REPORT
============================================================

BEHAVIOR TAGS:
  • High Speed
  • G Turn
  • Evasive Maneuver

KEY METRICS:
  Speed: 345.2 m/s (avg), 412.8 m/s (max)
  G-Force: 6.23 g (max)
  Turn Angles: 38.5° (avg), 67.2° (max)
  Altitude: 7200.0 m (avg), +500.0 m (change)
  Path Length: 18450.3 m over 52.5 s

============================================================
```

### JSON Export
The JSON file contains:
```json
{
  "features": {
    "speed_mean": 345.2,
    "speed_max": 412.8,
    "g_force_max": 6.23,
    "mean_turn_angle": 38.5,
    ...
  },
  "tags": [
    "high_speed",
    "g_turn",
    "evasive_maneuver"
  ]
}
```

## Configuration

The default configuration works well for most cases. To customize:

### Using GUI
1. Go to "Configuration" tab
2. Edit the YAML directly
3. Click "Apply Config"

### Using Config File
```bash
# Copy default config
cp config/default_config.yaml config/my_config.yaml

# Edit with your favorite editor
nano config/my_config.yaml

# Use custom config
python run.py analyze -i data.bin -o results.json -c config/my_config.yaml
```

### Important Config Parameters

```yaml
# Adjust speed thresholds
features:
  velocity_threshold:
    high_speed: 300.0    # m/s
    medium_speed: 150.0  # m/s
    low_speed: 50.0      # m/s

# Adjust G-force thresholds
  acceleration_threshold:
    high_g: 5.0          # g-force
    medium_g: 2.0        # g-force

# Adjust turn angle thresholds
  trajectory:
    sharp_turn_angle: 45.0   # degrees
    smooth_turn_angle: 15.0  # degrees
```

## Common Tasks

### Task 1: Analyze Your Own Radar Data

If you have a binary radar file:

```bash
python run.py analyze -i your_radar_file.bin -o your_results.json
```

The system will:
- Auto-detect the file format
- Parse the header
- Extract features
- Tag behaviors
- Generate a report

### Task 2: Generate Training Data

For machine learning projects:

```bash
# Generate 1000 samples with specific distribution
python run.py generate -o training_data/ -n 1000
```

This creates diverse target behaviors suitable for ML training.

### Task 3: Batch Process Multiple Files

```bash
# Process all .bin files in a directory
python run.py batch -i raw_data_dir/ -o processed_results/
```

The system will:
- Find all supported files
- Process each one
- Generate individual reports
- Create combined results

### Task 4: Compare Different Configurations

```bash
# Test with standard config
python run.py analyze -i test.h5 -o results_standard.json

# Test with sensitive config (lower thresholds)
python run.py analyze -i test.h5 -o results_sensitive.json -c config/sensitive.yaml

# Compare results
diff results_standard.json results_sensitive.json
```

## Troubleshooting

### Issue: "No module named 'radar_analyzer'"

**Solution**: Make sure you're in the workspace directory and Python can find the src folder:
```bash
cd workspace
python run.py gui
```

### Issue: GUI doesn't launch

**Solution**: Install PyQt5:
```bash
pip install PyQt5
```

### Issue: MATLAB functions not working

**Solution**: This is normal. MATLAB integration is optional. The system uses Python fallbacks automatically. To enable MATLAB:
1. Install MATLAB
2. Install matlab-engine: `pip install matlabengine`
3. Enable in config: `matlab_enabled: true`

### Issue: "File format not recognized"

**Solution**: Ensure your file has the correct extension:
- Binary files: `.bin` or `.dat`
- HDF5 files: `.h5` or `.hdf5`

### Issue: Analysis seems incorrect

**Solution**: Adjust thresholds in configuration. Default values are for typical military aircraft. Adjust for your specific use case (drones, helicopters, etc.).

## Next Steps

Now that you're up and running:

1. **Read the Full Documentation**
   - `README.md` - Complete system overview
   - `docs/CONFIGURATION.md` - Detailed config guide
   - `docs/API.md` - API reference

2. **Try the Examples**
   - See `docs/EXAMPLES.md` for more code examples

3. **Customize for Your Needs**
   - Adjust thresholds in configuration
   - Add custom behavior tags
   - Integrate your own algorithms

4. **Integrate with Your Workflow**
   - Use CLI for automation
   - Batch process large datasets
   - Export results for further analysis

## Getting Help

- **Documentation**: Check `docs/` directory
- **Examples**: See `docs/EXAMPLES.md`
- **Issues**: Report bugs on GitHub
- **Configuration**: See `docs/CONFIGURATION.md`

## Example Session

Here's a complete example session from start to finish:

```bash
# Setup
cd workspace
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate test data
python run.py test -o data/test/
# Output: Generated 5 test scenarios

# Analyze each scenario
python run.py batch -i data/test/ -o results/
# Output: Processed 5 files

# Check results
cat results/combined_results.json
# Shows all features and tags

# Launch GUI for visual analysis
python run_gui.py
# Load files from data/test/ and explore interactively
```

---

**Congratulations!** You're now ready to use the Radar Target Analyzer. 🎉

For more advanced usage, continue to the full README.md and documentation in the `docs/` directory.
