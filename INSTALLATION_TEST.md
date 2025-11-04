# Installation and Testing Guide

This document provides step-by-step instructions to verify your installation and test the system.

## Installation Verification

### Step 1: Check Python Version
```bash
python --version
# Should show Python 3.8 or higher
```

### Step 2: Install Dependencies
```bash
cd /workspace
pip install -r requirements.txt
```

Expected output:
- Successfully installed numpy, scipy, pandas, PyQt5, matplotlib, h5py, scikit-learn, pyyaml, and other packages
- No error messages

### Step 3: Verify Module Import
```bash
python -c "import sys; sys.path.insert(0, 'src'); from radar_analyzer import RadarDataLoader, FeatureExtractor, TaggingEngine, SyntheticDataGenerator; print('✓ All modules imported successfully')"
```

Expected output:
```
✓ All modules imported successfully
```

## Quick Functionality Tests

### Test 1: Generate Synthetic Data (CLI)
```bash
python run.py test -o data/test_scenarios/
```

Expected output:
```
INFO - Generating test scenarios...
INFO - Generated 5 test scenarios
INFO - Saved 5 synthetic targets to: data/test_scenarios/
INFO - Test scenarios generated!
```

Verify: Check that 5 .h5 files were created in `data/test_scenarios/`

### Test 2: Analyze a File (CLI)
```bash
python run.py analyze -i data/test_scenarios/synthetic_target_000.h5 -o test_result.json
```

Expected output:
- Loading message
- Feature extraction message
- Tagging message
- Behavior analysis report showing tags and metrics
- "Analysis complete!" message

Verify: Check that `test_result.json` was created

### Test 3: Run Example Script
```bash
python examples/basic_usage.py
```

Expected output:
- Step-by-step progress messages
- Generated synthetic data
- Extracted features
- Detected behavior tags
- Detailed report
- Validation against ground truth

### Test 4: GUI Launch (if PyQt5 available)
```bash
python run_gui.py
```

Expected: GUI window opens with 5 tabs

If GUI doesn't launch:
1. Install PyQt5: `pip install PyQt5`
2. On Linux, you may need: `sudo apt-get install python3-pyqt5`
3. Try again

### Test 5: Run Unit Tests
```bash
pytest tests/ -v
```

Expected output:
- All tests should PASS
- No FAILED tests
- Coverage summary

If pytest is not installed:
```bash
pip install pytest
pytest tests/ -v
```

## Troubleshooting

### Issue: Module not found errors
**Solution:**
```bash
cd /workspace
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
# Or on Windows: set PYTHONPATH=%PYTHONPATH%;%CD%\src
```

### Issue: PyQt5 import errors
**Solution:**
```bash
pip install PyQt5
```

On Ubuntu/Debian:
```bash
sudo apt-get install python3-pyqt5
```

### Issue: MATLAB-related warnings
**Note:** These are expected and can be ignored. MATLAB integration is optional. The system uses Python fallbacks automatically.

### Issue: HDF5 errors
**Solution:**
```bash
pip install --upgrade h5py
```

### Issue: Numpy/Scipy errors
**Solution:**
```bash
pip install --upgrade numpy scipy
```

## Detailed Functionality Tests

### Test Suite 1: Data Loading

```bash
# Test with different formats
python -c "
import sys
sys.path.insert(0, 'src')
from radar_analyzer import RadarDataLoader
loader = RadarDataLoader()
print('✓ Data loader initialized')
"
```

### Test Suite 2: Feature Extraction

```bash
python -c "
import sys
import numpy as np
sys.path.insert(0, 'src')
from radar_analyzer import FeatureExtractor

extractor = FeatureExtractor()
dummy_data = {
    'position': np.random.randn(100, 3) * 1000,
    'velocity': np.random.randn(100, 3) * 100,
    'timestamps': np.linspace(0, 10, 100),
    'doppler': np.random.randn(100),
    'raw_data': np.random.randn(100) + 1j * np.random.randn(100)
}
features = extractor.extract_all_features(dummy_data)
print(f'✓ Extracted {len(features)} features')
"
```

### Test Suite 3: Behavior Tagging

```bash
python -c "
import sys
sys.path.insert(0, 'src')
from radar_analyzer import TaggingEngine

engine = TaggingEngine()
features = {
    'speed_mean': 350.0,
    'g_force_max': 6.0,
    'mean_turn_angle': 50.0,
    'altitude_change': 100.0,
    'duration': 60.0,
    'speed': [350] * 10,
    'g_force_mean': 3.0,
    'high_g_events': 2,
    'max_turn_angle': 70.0,
    'sharp_turns_count': 3,
    'curvature_mean': 0.01,
    'std_turn_angle': 10.0
}
tags = engine.tag_target(features)
print(f'✓ Generated {len(tags)} behavior tags: {tags}')
"
```

### Test Suite 4: Synthetic Generation

```bash
python -c "
import sys
sys.path.insert(0, 'src')
from radar_analyzer import SyntheticDataGenerator

generator = SyntheticDataGenerator({'duration': 30.0})
data = generator.generate_target('high_speed', target_id=1)
print(f'✓ Generated synthetic target with {len(data[\"position\"])} samples')
"
```

## Complete System Test

Run this complete end-to-end test:

```bash
# 1. Generate test data
echo "1. Generating test data..."
python run.py test -o data/system_test/

# 2. Analyze all generated files
echo "2. Running batch analysis..."
python run.py batch -i data/system_test/ -o results/system_test/

# 3. Check results
echo "3. Checking results..."
ls -lh results/system_test/
cat results/system_test/combined_results.json

# 4. Run examples
echo "4. Running examples..."
python examples/basic_usage.py
python examples/batch_processing.py

echo "✓ Complete system test passed!"
```

## Performance Benchmarks

Run these to check performance:

```bash
# Benchmark synthetic generation
time python -c "
import sys
sys.path.insert(0, 'src')
from radar_analyzer import SyntheticDataGenerator
gen = SyntheticDataGenerator({'num_targets': 100})
dataset = gen.generate_dataset()
print(f'Generated {len(dataset)} targets')
"

# Should complete in < 30 seconds
```

## Success Criteria

Your installation is successful if:

- ✅ All Python modules import without errors
- ✅ Test data can be generated
- ✅ Files can be analyzed
- ✅ Example scripts run to completion
- ✅ Unit tests pass (if pytest installed)
- ✅ GUI launches (if PyQt5 installed)

## Next Steps After Verification

Once all tests pass:

1. **Read the Documentation**
   - `README.md` - Full system documentation
   - `GETTING_STARTED.md` - Quick start guide
   - `docs/QUICK_START.md` - Detailed tutorial

2. **Try with Your Data**
   - Place your radar files in `data/raw/`
   - Analyze with: `python run.py analyze -i data/raw/yourfile.bin -o results/analysis.json`

3. **Customize Configuration**
   - Edit `config/default_config.yaml`
   - Adjust thresholds for your use case

4. **Explore Examples**
   - `examples/basic_usage.py`
   - `examples/batch_processing.py`

## Getting Help

If tests fail:
1. Check error messages carefully
2. Verify Python version (3.8+)
3. Ensure all dependencies are installed
4. Check file permissions
5. Review troubleshooting section above

For additional help:
- Check documentation in `docs/`
- Review example scripts in `examples/`
- Open an issue on GitHub

---

**Installation Complete!** 🎉

You're now ready to use the Radar Target Analyzer system.
