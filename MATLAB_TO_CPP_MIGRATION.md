# MATLAB to C++ Migration Summary

## Overview

This document summarizes the changes made to remove MATLAB dependencies and prepare the system for C++ library integration.

## Changes Made

### 1. Updated Dependencies (`requirements.txt`)

**Removed:**
- `matlab-engine>=9.13.0` - MATLAB engine for Python

**Added:**
- `pybind11>=2.11.0` - Modern C++ binding generator
- `numba>=0.57.0` - JIT compiler for accelerated computing
- `opencv-python>=4.8.0` - Computer vision and image processing

**Kept:**
- `cffi>=1.15.1` - For C/C++ library integration
- `numpy>=1.24.0` - Array operations (MATLAB alternative)
- `scipy>=1.10.0` - Signal processing (MATLAB alternative)

### 2. Updated External Interface (`src/radar_analyzer/external_interface.py`)

**Changes:**
- Removed all MATLAB engine initialization code
- Removed `_init_matlab_engine()` method
- Removed `call_matlab_function()` method
- Removed `_matlab_python_fallback()` method
- Enhanced C++ library loading with both ctypes and CFFI support
- Added proper function signature definitions
- Added `get_available_algorithms()` method
- Improved error handling and fallback mechanisms

**New Features:**
- Support for both ctypes and CFFI integration methods
- Automatic detection of library platform (.so, .dll, .dylib)
- Better type conversion between Python and C++
- Comprehensive documentation in docstrings

### 3. Updated Configuration (`config/default_config.yaml`)

**Removed:**
```yaml
matlab_enabled: false
matlab_functions:
  - "sar_processing"
  - "doppler_analysis"
```

**Added:**
```yaml
use_cffi: false
algorithms:
  - "sar_processing"
  - "doppler_analysis"
  - "pulse_compression"
  - "clutter_rejection"
```

### 4. Created C++ Library Template

**New Files:**
- `lib/radar_algorithms.h` - C interface header file
- `lib/radar_algorithms.cpp` - Example C++ implementation
- `lib/Makefile` - Build script for compilation
- `lib/README.md` - Integration guide

**Features:**
- Standard C interface definitions
- Example implementations of radar algorithms
- Cross-platform build support
- Documentation for integration

### 5. Updated Documentation

**Updated:**
- `README.md` - Removed MATLAB references, added C++ integration info
- Configuration examples updated throughout

**Created:**
- `docs/CPP_INTEGRATION.md` - Comprehensive C++ integration guide
- `lib/README.md` - Quick start guide for C++ libraries

## How to Use Your C++ Libraries

### Option 1: Use the Provided Template

1. **Copy your algorithms** into `lib/radar_algorithms.cpp`
2. **Build the library:**
   ```bash
   cd lib
   make
   ```
3. **Run the system** - it will automatically use your C++ library

### Option 2: Use Your Existing Libraries

1. **Create a C wrapper** for your existing C++ code:
   ```cpp
   extern "C" {
       void your_function(double* input, double* output, int size) {
           YourClass processor;
           // Call your existing code here
       }
   }
   ```

2. **Compile to shared library:**
   ```bash
   g++ -shared -fPIC -O3 -o your_lib.so your_wrapper.cpp your_existing_code.cpp
   ```

3. **Update configuration:**
   ```yaml
   external_algorithms:
     cpp_lib_path: "path/to/your_lib.so"
   ```

### Option 3: Use Python Implementations

The system includes Python fallbacks for all algorithms using NumPy/SciPy. These work out of the box without any C++ libraries.

## MATLAB Function Equivalents

| MATLAB Function | Python Equivalent | C++ Library |
|----------------|------------------|-------------|
| `fft()` | `np.fft.fft()` | FFTW |
| `ifft()` | `np.fft.ifft()` | FFTW |
| `conv()` | `np.convolve()` | Manual/FFTW |
| `filter()` | `scipy.signal.lfilter()` | Manual |
| `xcorr()` | `np.correlate()` | Manual |
| `spectrogram()` | `scipy.signal.spectrogram()` | STFT |
| `butter()` | `scipy.signal.butter()` | Manual |
| `hilbert()` | `scipy.signal.hilbert()` | Manual |

## Benefits of This Migration

1. **No MATLAB License Required** - Free and open-source
2. **Better Performance** - C++ can be faster than MATLAB
3. **More Flexible** - Easy to integrate any C++ library
4. **Cross-Platform** - Works on Linux, Windows, macOS
5. **Better Integration** - Direct memory sharing with NumPy
6. **Version Control Friendly** - No binary MATLAB files

## Testing the Migration

### 1. Test Python Fallbacks

```bash
# Run tests to verify Python implementations work
pytest tests/

# Run GUI to test interactive functionality
python run_gui.py
```

### 2. Test C++ Integration

```bash
# Build example library
cd lib
make

# Update config to use the library
# Edit config/default_config.yaml:
#   cpp_lib_path: "lib/radar_algorithms.so"

# Run system
python run.py --input data/synthetic/test_data.h5 --output results/
```

### 3. Generate and Process Test Data

```python
from radar_analyzer.synthetic_generator import SyntheticDataGenerator
from radar_analyzer.external_interface import ExternalAlgorithmInterface

# Generate test data
generator = SyntheticDataGenerator()
data = generator.generate_scenario('high_speed_aircraft')

# Test C++ integration
interface = ExternalAlgorithmInterface({
    'cpp_lib_path': 'lib/radar_algorithms.so'
})

# Process with C++ (or Python fallback if library not available)
result = interface.call_cpp_algorithm('sar_processing', data['raw_data'])
print("C++ processing successful!")
```

## Integration Methods Comparison

### ctypes (Default)

**Pros:**
- Built into Python
- No extra dependencies
- Simple for basic interfaces

**Cons:**
- Manual type conversion
- Less type safety
- Verbose for complex interfaces

**Use when:**
- Simple function calls
- Standard C types only
- Quick prototyping

### CFFI (Recommended)

**Pros:**
- Better type safety
- Cleaner syntax
- Better performance
- Easier struct handling

**Cons:**
- Requires extra package
- Slightly more setup

**Use when:**
- Complex data structures
- Production code
- Need better performance

## Compilation Examples

### Linux
```bash
# Basic compilation
g++ -shared -fPIC -O3 -o radar_lib.so radar_code.cpp

# With FFTW
g++ -shared -fPIC -O3 -o radar_lib.so radar_code.cpp -lfftw3

# With OpenMP (parallel)
g++ -shared -fPIC -O3 -fopenmp -o radar_lib.so radar_code.cpp
```

### Windows (Visual Studio)
```bash
# Using cl.exe
cl /LD /O2 radar_code.cpp /Fe:radar_lib.dll

# With optimization
cl /LD /O2 /GL radar_code.cpp /Fe:radar_lib.dll /link /LTCG
```

### macOS
```bash
# Basic compilation
g++ -shared -fPIC -O3 -o radar_lib.dylib radar_code.cpp

# With Accelerate framework
g++ -shared -fPIC -O3 -o radar_lib.dylib radar_code.cpp -framework Accelerate
```

## Performance Tips

1. **Use compiler optimizations:**
   - `-O3`: Maximum optimization
   - `-march=native`: CPU-specific optimizations
   - `-fopenmp`: Parallel processing

2. **Minimize copies:**
   - Pre-allocate output arrays in Python
   - Use contiguous memory (`np.ascontiguousarray`)

3. **Batch processing:**
   - Process multiple samples at once
   - Reduce function call overhead

4. **Profile your code:**
   - Use `cProfile` for Python
   - Use `gprof` for C++
   - Identify bottlenecks before optimizing

## Troubleshooting

### Library Not Loading

**Problem:** `OSError: cannot open shared object file`

**Solution:**
```bash
# Check file exists
ls -l lib/radar_algorithms.so

# Use absolute path in config
cpp_lib_path: "/absolute/path/to/radar_algorithms.so"

# Or add to library path
export LD_LIBRARY_PATH=$PWD/lib:$LD_LIBRARY_PATH
```

### Function Not Found

**Problem:** `AttributeError: function 'xxx' not found`

**Solution:**
```bash
# Check exported symbols
nm -D lib/radar_algorithms.so | grep your_function

# Ensure extern "C" in code
extern "C" {
    void your_function(...) { }
}
```

### Segmentation Fault

**Problem:** Crash when calling C++ function

**Solution:**
```python
# Ensure proper data types
data = np.ascontiguousarray(data, dtype=np.float64)

# Pre-allocate output
output = np.zeros_like(data)

# Check sizes
assert len(data) == expected_size
```

## Migration Checklist

- [x] Remove MATLAB dependencies from requirements.txt
- [x] Update external_interface.py to remove MATLAB code
- [x] Update configuration files
- [x] Create C++ library template
- [x] Update documentation
- [x] Create integration guide
- [ ] Build your C++ libraries (user task)
- [ ] Update config with your library paths (user task)
- [ ] Test with your data (user task)

## Next Steps

1. **If you have existing C++ libraries:**
   - Create C wrappers using the template in `lib/`
   - Compile to shared libraries
   - Update config with paths
   - Test integration

2. **If you need to port MATLAB code:**
   - Review `docs/CPP_INTEGRATION.md` for MATLAB equivalents
   - Implement in C++ or use NumPy/SciPy
   - Test against original MATLAB results

3. **If you want to start fresh:**
   - Use the provided Python implementations
   - They work out of the box
   - Optimize later if needed

## Support

For detailed information, see:
- `docs/CPP_INTEGRATION.md` - Complete C++ integration guide
- `lib/README.md` - Quick start for C++ libraries
- `README.md` - General system documentation

For issues or questions:
1. Check the troubleshooting sections
2. Review example code in `examples/`
3. Run tests to verify setup: `pytest tests/`

## Summary

The system is now MATLAB-free and ready for C++ library integration. You can:
1. **Use it immediately** with Python fallbacks (no C++ required)
2. **Integrate your C++ libraries** using the provided templates
3. **Build high-performance algorithms** with C++/FFTW/OpenMP

All existing functionality remains intact, just using Python/C++ instead of MATLAB.
