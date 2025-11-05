# Setup Instructions - C++ Integration Ready

## ✅ Migration Complete

Your Radar Target Behavior Analysis System is now **MATLAB-free** and ready for C++ library integration!

## What Was Changed

### 1. Dependencies (`requirements.txt`)
- ✅ Removed `matlab-engine` 
- ✅ Added `pybind11` for C++ binding
- ✅ Added `numba` for JIT acceleration
- ✅ Added `opencv-python` for image processing
- ✅ Kept `numpy`, `scipy`, `cffi` for signal processing and C++ integration

### 2. Code Updates
- ✅ `src/radar_analyzer/external_interface.py` - Removed all MATLAB code, enhanced C++ support
- ✅ `config/default_config.yaml` - Updated configuration for C++ libraries

### 3. New Files Created
- ✅ `lib/radar_algorithms.h` - C interface header template
- ✅ `lib/radar_algorithms.cpp` - Example C++ implementation
- ✅ `lib/Makefile` - Build script
- ✅ `lib/README.md` - Quick integration guide
- ✅ `docs/CPP_INTEGRATION.md` - Comprehensive integration documentation
- ✅ `MATLAB_TO_CPP_MIGRATION.md` - Migration summary

## 🚀 Quick Start

### Option 1: Use Python Implementation (No C++ Required)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system (uses Python fallbacks)
python run_gui.py
```

The system will work immediately with built-in Python implementations using NumPy/SciPy.

### Option 2: Build Example C++ Library

```bash
# Install dependencies
pip install -r requirements.txt

# Build the example C++ library
cd lib
make

# The library will be: radar_algorithms.so (Linux/Mac) or radar_algorithms.dll (Windows)
```

### Option 3: Integrate Your Existing C++ Libraries

See `docs/CPP_INTEGRATION.md` for detailed instructions.

## 📋 Next Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the system:**
   ```bash
   # Run tests
   pytest tests/
   
   # Start GUI
   python run_gui.py
   
   # Or use CLI
   python run.py --help
   ```

3. **If you have C++ libraries to integrate:**
   - Read `docs/CPP_INTEGRATION.md`
   - Check the template in `lib/`
   - Follow examples in `lib/README.md`

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | General system documentation |
| `MATLAB_TO_CPP_MIGRATION.md` | Summary of changes made |
| `docs/CPP_INTEGRATION.md` | Detailed C++ integration guide |
| `lib/README.md` | Quick start for C++ libraries |
| `START_HERE.md` | Getting started guide |

## 🔧 Configuration

Edit `config/default_config.yaml` to configure C++ library path:

```yaml
external_algorithms:
  # Path to your C++ shared library
  cpp_lib_path: "lib/radar_algorithms.so"
  
  # Use CFFI (true) or ctypes (false)
  use_cffi: false
  
  # Available algorithms
  algorithms:
    - "sar_processing"
    - "doppler_analysis"
    - "pulse_compression"
    - "clutter_rejection"
```

## 🎯 Key Features

- ✅ **No MATLAB Required** - Fully Python-based with C++ integration
- ✅ **Flexible Integration** - Support both ctypes and CFFI
- ✅ **Python Fallbacks** - Works without C++ libraries
- ✅ **Cross-Platform** - Linux, Windows, macOS support
- ✅ **High Performance** - C++ for speed-critical algorithms
- ✅ **Open Source** - No proprietary dependencies

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_external_interface.py

# Generate coverage report
pytest --cov=src/radar_analyzer tests/
```

## 💡 Example Usage

### Python Only (No C++)
```python
from radar_analyzer.external_interface import ExternalAlgorithmInterface
import numpy as np

# Initialize without C++ library
interface = ExternalAlgorithmInterface()

# Uses Python fallback automatically
data = np.random.randn(1024)
result = interface.call_cpp_algorithm('sar_processing', data)
```

### With C++ Library
```python
# Initialize with C++ library path
config = {'cpp_lib_path': 'lib/radar_algorithms.so'}
interface = ExternalAlgorithmInterface(config)

# Uses C++ library (faster)
data = np.random.randn(1024)
result = interface.call_cpp_algorithm('doppler_analysis', data)
```

## 🐛 Troubleshooting

### Python Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Or install individually
pip install numpy scipy pandas scikit-learn PyQt5 h5py cffi pybind11
```

### C++ Library Not Loading
- Check the path in `config/default_config.yaml`
- Verify the library file exists: `ls -l lib/radar_algorithms.so`
- Use absolute path if needed
- Check library dependencies: `ldd lib/radar_algorithms.so` (Linux)

### Build Errors
```bash
# Install C++ compiler
# Ubuntu/Debian:
sudo apt-get install build-essential

# macOS:
xcode-select --install

# Windows:
# Install Visual Studio Build Tools
```

## 📖 Additional Resources

### MATLAB to NumPy/SciPy Reference
- NumPy for Matlab users: https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
- SciPy signal processing: https://docs.scipy.org/doc/scipy/tutorial/signal.html

### C++ Integration
- ctypes documentation: https://docs.python.org/3/library/ctypes.html
- CFFI documentation: https://cffi.readthedocs.io/
- pybind11 documentation: https://pybind11.readthedocs.io/

### Signal Processing Libraries
- FFTW (Fastest FFT): http://www.fftw.org/
- Intel MKL: https://software.intel.com/mkl

## ✨ What You Get

The system now provides:

1. **Data Loading**
   - Binary (.bin, .dat) and HDF5 formats
   - Metadata parsing
   - Position/velocity extraction

2. **Feature Extraction**
   - Kinematic features (velocity, acceleration, G-force)
   - Trajectory analysis (turns, curvature)
   - Doppler spectrum analysis
   - RCS characteristics

3. **Behavior Tagging**
   - Speed classification
   - Maneuver detection
   - Flight profile identification

4. **Synthetic Data Generation**
   - Realistic radar returns
   - Multiple behavior patterns
   - Configurable scenarios

5. **GUI & CLI**
   - Interactive GUI with PyQt5
   - Command-line batch processing
   - Real-time visualization

6. **C++ Integration**
   - ctypes and CFFI support
   - Python fallbacks
   - Example templates

## 🎉 Summary

Your system is ready to use! It works immediately with Python implementations and can be enhanced with C++ libraries for better performance. All MATLAB dependencies have been removed successfully.

**To get started right now:**
```bash
pip install -r requirements.txt
python run_gui.py
```

That's it! 🚀
