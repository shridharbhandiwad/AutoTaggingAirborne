# C++ Library Integration Guide

This guide explains how to integrate your existing C++ radar processing libraries with the Radar Target Behavior Analysis System.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Integration Methods](#integration-methods)
4. [Creating C++ Wrapper](#creating-c-wrapper)
5. [Building and Compiling](#building-and-compiling)
6. [Configuration](#configuration)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)

## Overview

The system supports calling external C++ libraries through two methods:
- **ctypes**: Python's built-in FFI (Foreign Function Interface)
- **CFFI**: C Foreign Function Interface (recommended for complex interfaces)

Both methods allow seamless integration of high-performance C++ code without requiring MATLAB.

## Quick Start

### 1. Prepare Your C++ Library

Create a C interface wrapper for your C++ code:

```cpp
// my_radar_lib.cpp
#include <cmath>

extern "C" {
    void sar_processing(double* input, double* output, int size) {
        // Your SAR algorithm here
        for (int i = 0; i < size; i++) {
            output[i] = /* your processing */;
        }
    }
}
```

### 2. Compile to Shared Library

```bash
# Linux
g++ -shared -fPIC -O3 -o my_radar_lib.so my_radar_lib.cpp

# macOS
g++ -shared -fPIC -O3 -o my_radar_lib.dylib my_radar_lib.cpp

# Windows
cl /LD /O2 my_radar_lib.cpp /Fe:my_radar_lib.dll
```

### 3. Update Configuration

Edit `config/default_config.yaml`:

```yaml
external_algorithms:
  cpp_lib_path: "path/to/my_radar_lib.so"
  use_cffi: false
```

### 4. Use in Python

```python
from radar_analyzer.external_interface import ExternalAlgorithmInterface
import numpy as np

# Initialize
config = {'cpp_lib_path': 'path/to/my_radar_lib.so'}
interface = ExternalAlgorithmInterface(config)

# Call C++ function
data = np.random.randn(1024)
result = interface.call_cpp_algorithm('sar_processing', data)
```

## Integration Methods

### Method 1: ctypes (Default)

**Advantages:**
- Built into Python (no extra dependencies)
- Simple to use for basic interfaces
- Good performance

**Example:**
```python
import ctypes
import numpy as np

# Load library
lib = ctypes.CDLL('my_radar_lib.so')

# Define function signature
lib.sar_processing.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64),
    np.ctypeslib.ndpointer(dtype=np.float64),
    ctypes.c_int
]
lib.sar_processing.restype = None

# Call function
input_data = np.array([1.0, 2.0, 3.0])
output_data = np.zeros_like(input_data)
lib.sar_processing(input_data, output_data, len(input_data))
```

### Method 2: CFFI (Recommended)

**Advantages:**
- Better type safety
- Cleaner syntax for complex interfaces
- Better performance for struct/array operations
- Easier to work with C++ classes (via C wrapper)

**Setup:**
```bash
pip install cffi
```

**Example:**
```python
from cffi import FFI
import numpy as np

# Initialize FFI
ffi = FFI()

# Define C interface
ffi.cdef("""
    void sar_processing(double* input, double* output, int size);
""")

# Load library
lib = ffi.dlopen('my_radar_lib.so')

# Call function
input_data = np.array([1.0, 2.0, 3.0])
output_data = np.zeros_like(input_data)

input_ptr = ffi.cast("double*", ffi.from_buffer(input_data))
output_ptr = ffi.cast("double*", ffi.from_buffer(output_data))

lib.sar_processing(input_ptr, output_ptr, len(input_data))
```

## Creating C++ Wrapper

### Basic Wrapper Template

```cpp
// radar_wrapper.h
#ifndef RADAR_WRAPPER_H
#define RADAR_WRAPPER_H

#ifdef __cplusplus
extern "C" {
#endif

// Simple function
void process_data(double* input, double* output, int size);

// With parameters
void process_with_params(
    double* input, 
    double* output, 
    int size,
    double param1,
    int param2
);

#ifdef __cplusplus
}
#endif

#endif
```

```cpp
// radar_wrapper.cpp
#include "radar_wrapper.h"
#include "your_existing_cpp_class.hpp"

extern "C" {

void process_data(double* input, double* output, int size) {
    // Use your existing C++ code
    YourRadarClass processor;
    std::vector<double> vec(input, input + size);
    auto result = processor.process(vec);
    std::copy(result.begin(), result.end(), output);
}

void process_with_params(
    double* input, 
    double* output, 
    int size,
    double param1,
    int param2
) {
    YourRadarClass processor;
    processor.setParameter1(param1);
    processor.setParameter2(param2);
    
    std::vector<double> vec(input, input + size);
    auto result = processor.process(vec);
    std::copy(result.begin(), result.end(), output);
}

}
```

### Handling Complex Data Types

#### 1. Complex Numbers

```cpp
// C++ side
extern "C" {
void process_complex(double* real, double* imag, int size) {
    for (int i = 0; i < size; i++) {
        std::complex<double> c(real[i], imag[i]);
        // Process...
        real[i] = c.real();
        imag[i] = c.imag();
    }
}
}
```

```python
# Python side
data = np.array([1+2j, 3+4j, 5+6j])
real = np.ascontiguousarray(data.real)
imag = np.ascontiguousarray(data.imag)
lib.process_complex(real, imag, len(data))
result = real + 1j * imag
```

#### 2. Structures

```cpp
// C++ side
typedef struct {
    double sampling_rate;
    double prf;
    double center_freq;
} RadarParams;

extern "C" {
void init_with_struct(RadarParams* params) {
    // Use params...
}
}
```

```python
# Python side (CFFI)
ffi.cdef("""
    typedef struct {
        double sampling_rate;
        double prf;
        double center_freq;
    } RadarParams;
    
    void init_with_struct(RadarParams* params);
""")

params = ffi.new("RadarParams*")
params.sampling_rate = 1000.0
params.prf = 1000.0
params.center_freq = 10e9
lib.init_with_struct(params)
```

#### 3. Multi-dimensional Arrays

```cpp
// C++ side - flatten 2D array
extern "C" {
void process_2d(double* data, int rows, int cols) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            int idx = i * cols + j;
            data[idx] = /* process */;
        }
    }
}
}
```

```python
# Python side
data_2d = np.random.randn(10, 20)
data_flat = np.ascontiguousarray(data_2d.flatten())
lib.process_2d(data_flat, 10, 20)
result = data_flat.reshape(10, 20)
```

## Building and Compiling

### Using Makefile

```makefile
# Makefile
CXX = g++
CXXFLAGS = -O3 -fPIC -std=c++11 -Wall
LDFLAGS = -shared

# Detect platform
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    EXT = so
endif
ifeq ($(UNAME_S),Darwin)
    EXT = dylib
endif

TARGET = radar_lib.$(EXT)
SOURCES = radar_wrapper.cpp your_code.cpp
HEADERS = radar_wrapper.h your_code.hpp

$(TARGET): $(SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $(TARGET) $(SOURCES)

clean:
	rm -f $(TARGET)
```

### Using CMake

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(RadarLib)

set(CMAKE_CXX_STANDARD 11)

# Build shared library
add_library(radar_lib SHARED
    radar_wrapper.cpp
    your_code.cpp
)

# Set optimization flags
target_compile_options(radar_lib PRIVATE -O3)

# Link math library if needed
target_link_libraries(radar_lib m)

# Installation
install(TARGETS radar_lib
    LIBRARY DESTINATION lib
)
```

Build:
```bash
mkdir build && cd build
cmake ..
make
```

### Compiler Flags

**Recommended flags:**
- `-O3`: Maximum optimization
- `-fPIC`: Position-independent code (required for shared libraries)
- `-march=native`: Optimize for your CPU (use carefully)
- `-fopenmp`: Enable OpenMP for parallelization
- `-DNDEBUG`: Disable assertions in release

**Example:**
```bash
g++ -shared -fPIC -O3 -march=native -fopenmp \
    -o radar_lib.so radar_wrapper.cpp your_code.cpp -lm
```

## Configuration

### Configuration File

Full configuration in `config/default_config.yaml`:

```yaml
external_algorithms:
  # Path to shared library
  cpp_lib_path: "lib/radar_algorithms.so"
  
  # Use CFFI (true) or ctypes (false)
  use_cffi: false
  
  # List of available algorithms
  algorithms:
    - "sar_processing"
    - "doppler_analysis"
    - "pulse_compression"
    - "clutter_rejection"
    - "your_custom_algorithm"
```

### Runtime Configuration

```python
from radar_analyzer.external_interface import ExternalAlgorithmInterface

config = {
    'cpp_lib_path': '/absolute/path/to/library.so',
    'use_cffi': True  # Use CFFI instead of ctypes
}

interface = ExternalAlgorithmInterface(config)
```

## Usage Examples

### Example 1: SAR Processing

```python
from radar_analyzer.external_interface import ExternalAlgorithmInterface
import numpy as np

# Load interface
interface = ExternalAlgorithmInterface({
    'cpp_lib_path': 'lib/radar_algorithms.so'
})

# Prepare SAR data
sar_data = np.random.randn(256, 256).flatten()

# Process with C++ library
sar_image = interface.call_cpp_algorithm(
    'sar_processing',
    sar_data,
    params={'azimuth_res': 1.0, 'range_res': 1.0}
)

# Reshape result
sar_image = sar_image.reshape(256, 256)
```

### Example 2: Doppler Analysis

```python
# Generate radar pulse train
pulses = np.random.randn(1024) + 1j * np.random.randn(1024)

# Convert to interleaved real/imag for C++
data = np.empty(2048)
data[0::2] = pulses.real
data[1::2] = pulses.imag

# Compute Doppler spectrum
doppler = interface.call_cpp_algorithm('doppler_analysis', data)

# Extract spectrum
spectrum = doppler[0::2] + 1j * doppler[1::2]
```

### Example 3: Batch Processing

```python
import h5py
from pathlib import Path

# Process multiple files
input_dir = Path('data/raw')
output_dir = Path('data/processed')

for input_file in input_dir.glob('*.h5'):
    # Load data
    with h5py.File(input_file, 'r') as f:
        data = f['raw_data'][:]
    
    # Process with C++ library
    processed = interface.call_cpp_algorithm('pulse_compression', data)
    
    # Save result
    output_file = output_dir / input_file.name
    with h5py.File(output_file, 'w') as f:
        f.create_dataset('processed_data', data=processed)
```

## Troubleshooting

### Library Not Found

**Error:** `OSError: cannot open shared object file`

**Solutions:**
1. Use absolute path:
   ```python
   config = {'cpp_lib_path': '/absolute/path/to/lib.so'}
   ```

2. Add to library path:
   ```bash
   export LD_LIBRARY_PATH=/path/to/lib:$LD_LIBRARY_PATH
   ```

3. Check file exists:
   ```bash
   ls -l /path/to/lib.so
   ```

### Symbol Not Found

**Error:** `AttributeError: function 'xxx' not found`

**Solutions:**
1. Check symbol with `nm`:
   ```bash
   nm -D radar_lib.so | grep sar_processing
   ```

2. Ensure `extern "C"`:
   ```cpp
   extern "C" {
       void my_function(...) { }
   }
   ```

3. Check name mangling:
   ```bash
   c++filt _Z15my_function...
   ```

### Segmentation Fault

**Common Causes:**
1. Array size mismatch
2. Null pointer
3. Memory not allocated
4. Wrong data type

**Debug:**
```bash
# Run with core dump
ulimit -c unlimited
python your_script.py

# Analyze with gdb
gdb python core
(gdb) bt
```

**Solutions:**
```python
# Pre-allocate output
output = np.zeros_like(input_data)

# Ensure contiguous memory
input_data = np.ascontiguousarray(input_data, dtype=np.float64)

# Check sizes
assert len(input_data) == expected_size
```

### Type Mismatch

**Error:** `ctypes ArgumentError: argument type mismatch`

**Solution:**
```python
# Ensure correct dtype
data = np.array(data, dtype=np.float64)

# Check data is contiguous
if not data.flags['C_CONTIGUOUS']:
    data = np.ascontiguousarray(data)

# Use proper ctypes types
size = ctypes.c_int(len(data))
```

## Performance Optimization

### 1. Memory Layout

Use C-contiguous arrays:
```python
# Good
data = np.ascontiguousarray(data)

# Bad (Fortran order)
data = data.T  # May not be contiguous
```

### 2. Avoid Copies

```python
# Pre-allocate output
output = np.zeros(size, dtype=np.float64)
lib.process(input_data, output, size)

# Instead of:
# output = lib.process_with_return(input_data)  # Creates copy
```

### 3. Batch Processing

```python
# Process in batches
batch_size = 10000
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    result[i:i+batch_size] = interface.call_cpp_algorithm('process', batch)
```

### 4. Parallel Processing

**C++ side:**
```cpp
#include <omp.h>

extern "C" {
void parallel_process(double* data, int size) {
    #pragma omp parallel for
    for (int i = 0; i < size; i++) {
        data[i] = /* compute */;
    }
}
}
```

**Compile with:**
```bash
g++ -shared -fPIC -O3 -fopenmp -o lib.so code.cpp
```

### 5. SIMD Optimization

```cpp
#include <immintrin.h>  // AVX

extern "C" {
void simd_process(double* data, int size) {
    for (int i = 0; i < size; i += 4) {
        __m256d vec = _mm256_load_pd(&data[i]);
        // SIMD operations...
        _mm256_store_pd(&data[i], vec);
    }
}
}
```

**Compile with:**
```bash
g++ -shared -fPIC -O3 -mavx2 -o lib.so code.cpp
```

## Replacing MATLAB Functions

### Common MATLAB to C++/Python Equivalents

| MATLAB | C++ | Python (NumPy/SciPy) |
|--------|-----|----------------------|
| `fft(x)` | FFTW library | `np.fft.fft(x)` |
| `ifft(x)` | FFTW library | `np.fft.ifft(x)` |
| `conv(a,b)` | Manual loop | `np.convolve(a, b)` |
| `filter(b,a,x)` | Manual IIR | `scipy.signal.lfilter(b, a, x)` |
| `xcorr(x,y)` | Manual correlation | `np.correlate(x, y)` |
| `spectrogram(x)` | STFT | `scipy.signal.spectrogram(x)` |
| `butter(n,Wn)` | Manual Butterworth | `scipy.signal.butter(n, Wn)` |

### Using FFTW in C++

```cpp
#include <fftw3.h>

extern "C" {
void fft_process(double* real_in, double* imag_out, int size) {
    fftw_complex *in, *out;
    fftw_plan plan;
    
    in = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * size);
    out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * size);
    
    // Copy input
    for (int i = 0; i < size; i++) {
        in[i][0] = real_in[i];
        in[i][1] = 0.0;
    }
    
    // Create plan and execute
    plan = fftw_plan_dft_1d(size, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(plan);
    
    // Copy output
    for (int i = 0; i < size; i++) {
        real_in[i] = out[i][0];
        imag_out[i] = out[i][1];
    }
    
    fftw_destroy_plan(plan);
    fftw_free(in);
    fftw_free(out);
}
}
```

**Link with:**
```bash
g++ -shared -fPIC -O3 -o lib.so code.cpp -lfftw3
```

## Best Practices

1. **Always use `extern "C"`** for functions called from Python
2. **Pre-allocate memory** in Python, pass pointers to C++
3. **Use contiguous arrays** (`np.ascontiguousarray`)
4. **Handle errors** gracefully in C++ (don't throw exceptions across FFI boundary)
5. **Document function signatures** clearly
6. **Test with small data** first
7. **Profile performance** to identify bottlenecks
8. **Use proper compiler optimization** flags
9. **Validate input** data sizes and types
10. **Cleanup resources** properly

## Additional Resources

- [ctypes Documentation](https://docs.python.org/3/library/ctypes.html)
- [CFFI Documentation](https://cffi.readthedocs.io/)
- [NumPy C-API](https://numpy.org/doc/stable/reference/c-api/)
- [FFTW Library](http://www.fftw.org/)
- [pybind11](https://pybind11.readthedocs.io/) - For more complex C++ integration
