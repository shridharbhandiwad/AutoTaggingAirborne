# Getting Started with Radar Target Analyzer

Welcome! This guide will help you get the Radar Target Analyzer up and running in just a few minutes.

## Prerequisites

- Python 3.8 or higher installed
- pip package manager
- Basic command-line knowledge

## Installation (5 minutes)

### Step 1: Navigate to Project Directory
```bash
cd workspace
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
```

Activate it:
- **Linux/Mac**: `source venv/bin/activate`
- **Windows**: `venv\Scripts\activate`

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

That's it! Installation complete.

## Your First Analysis (2 minutes)

### Quick Test with GUI

Launch the graphical interface:
```bash
python run_gui.py
```

In the GUI:
1. Go to **"Synthetic Data"** tab
2. Click **"Generate Test Scenarios"**
3. Select a folder (e.g., `data/test`)
4. Go to **"Data Loading"** tab
5. Click **"Select Radar Data File"** and choose a generated file
6. Click **"Load Data"**
7. Go to **"Analysis & Tagging"** tab
8. Click **"Extract Features"**
9. Click **"Tag Behavior"**
10. View results!

### Quick Test with Command Line

```bash
# Generate test data
python run.py test -o data/test_scenarios/

# Analyze one file
python run.py analyze -i data/test_scenarios/synthetic_target_000.h5 -o results.json

# View results
cat results.json
```

## Running the Examples

Try the included examples:

```bash
# Basic usage example
python examples/basic_usage.py

# Batch processing example
python examples/batch_processing.py
```

## Understanding the Output

When you analyze a target, you'll see:

### 1. Behavior Tags
What the target is doing:
- `high_speed` - Fast moving (>300 m/s)
- `g_turn` - High-G maneuver
- `evasive_maneuver` - Combat-style evasion
- `hovering` - Nearly stationary
- And more...

### 2. Key Metrics
Numerical data:
- Speed (average and maximum)
- G-force (maximum experienced)
- Turn angles
- Altitude changes
- Path length

### 3. Visual Plots (GUI only)
- Doppler spectrum
- Trajectory (top view)
- Feature values

## Common Use Cases

### Use Case 1: Analyze Your Own Data

If you have a radar data file:

```bash
python run.py analyze -i your_file.bin -o analysis_results.json
```

Supported formats: `.bin`, `.dat`, `.h5`, `.hdf5`

### Use Case 2: Generate Training Data

For machine learning:

```bash
python run.py generate -o training_data/ -n 1000
```

This creates 1000 synthetic radar targets with various behaviors.

### Use Case 3: Batch Process Many Files

Process a whole directory:

```bash
python run.py batch -i data_directory/ -o results_directory/
```

### Use Case 4: Customize Thresholds

Create a custom config:

```bash
cp config/default_config.yaml config/my_config.yaml
# Edit my_config.yaml with your preferred thresholds
python run.py analyze -i data.bin -o results.json -c config/my_config.yaml
```

## Configuration Basics

The main configuration file is `config/default_config.yaml`.

Key settings you might want to adjust:

```yaml
features:
  velocity_threshold:
    high_speed: 300.0    # Adjust for your target types
  
  acceleration_threshold:
    high_g: 5.0          # Adjust sensitivity
  
  trajectory:
    sharp_turn_angle: 45.0  # What counts as "sharp"
```

## Troubleshooting

### "No module named 'radar_analyzer'"
Make sure you're in the `workspace` directory and use `python run.py` or `python run_gui.py`.

### GUI won't launch
Install PyQt5: `pip install PyQt5`

### "File format not supported"
Ensure your file has extension: `.bin`, `.dat`, `.h5`, or `.hdf5`

### Analysis seems wrong
The default thresholds are for military aircraft. Adjust them in the config for drones, helicopters, etc.

## What's Next?

1. **Read the Full Docs**
   - `README.md` - Complete documentation
   - `docs/QUICK_START.md` - Detailed quick start
   - `docs/` - More documentation

2. **Try Different Behaviors**
   Generate and analyze different target types:
   - High-speed intercepts
   - Combat maneuvers
   - Surveillance patterns
   - Helicopter operations

3. **Customize for Your Needs**
   - Adjust configuration thresholds
   - Add your own behavior tags
   - Integrate external algorithms

4. **Integrate into Your Workflow**
   - Use CLI for automation
   - Export results for further analysis
   - Generate datasets for ML training

## Getting Help

- **Documentation**: Check `README.md` and `docs/` directory
- **Examples**: See `examples/` directory
- **Issues**: Open a GitHub issue

## System Architecture

```
Your Data File
     ↓
Data Loader ──→ Extract Features ──→ Tag Behavior ──→ Generate Report
                                          ↓
                                     Export Results
```

## Performance Notes

- Loading large files: ~1-5 seconds
- Feature extraction: ~0.1-1 second per target
- Tagging: Nearly instantaneous
- Synthetic generation: ~0.1 second per target

## Next Steps Checklist

- [ ] Install dependencies
- [ ] Run GUI or command-line test
- [ ] Run example scripts
- [ ] Generate test scenarios
- [ ] Analyze synthetic data
- [ ] Try with your own data (if available)
- [ ] Customize configuration
- [ ] Read full documentation

---

**Congratulations!** You're now ready to analyze radar targets! 🎉

For detailed information, see:
- Full documentation: `README.md`
- Quick start guide: `docs/QUICK_START.md`
- API reference: `docs/API.md` (coming soon)
- Examples: `examples/`

Happy analyzing!
