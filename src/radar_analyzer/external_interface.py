"""
External Algorithm Interface Module

Provides interface to call C++ algorithms for radar processing.
Supports both ctypes and CFFI for flexible C++ library integration.
"""

import logging
import numpy as np
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import json

logger = logging.getLogger(__name__)


class ExternalAlgorithmInterface:
    """
    Interface for calling external C++ algorithms via ctypes/CFFI.
    Provides Python fallbacks for all algorithms when C++ libraries are not available.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize external algorithm interface.
        
        Args:
            config: Configuration dictionary with 'cpp_lib_path' and 'use_cffi'
        """
        self.config = config or {}
        self.cpp_lib_path = self.config.get('cpp_lib_path')
        self.use_cffi = self.config.get('use_cffi', False)
        self.cpp_lib = None
        self.ffi = None
        
        # Try to load C++ library
        self._load_cpp_library()
    
    def _load_cpp_library(self):
        """
        Load C++ shared library using ctypes or CFFI.
        
        Supported library extensions:
        - Linux: .so
        - Windows: .dll
        - macOS: .dylib
        """
        if not self.cpp_lib_path:
            logger.info("C++ library path not specified. Using Python fallback implementations.")
            return
        
        lib_path = Path(self.cpp_lib_path)
        if not lib_path.exists():
            logger.warning(f"C++ library not found: {self.cpp_lib_path}. Using Python fallback.")
            return
        
        try:
            if self.use_cffi:
                # Use CFFI for C++ library loading
                from cffi import FFI
                self.ffi = FFI()
                
                # Define C interface (user should provide this in config or separate file)
                # This is an example interface definition
                self.ffi.cdef("""
                    void sar_processing(double* input, double* output, int size);
                    void doppler_analysis(double* input, double* output, int size);
                    void pulse_compression(double* input, double* output, int size);
                    void clutter_rejection(double* input, double* output, int size);
                """)
                
                self.cpp_lib = self.ffi.dlopen(str(lib_path))
                logger.info(f"Loaded C++ library via CFFI: {self.cpp_lib_path}")
            else:
                # Use ctypes for C++ library loading
                import ctypes
                self.cpp_lib = ctypes.CDLL(str(lib_path))
                logger.info(f"Loaded C++ library via ctypes: {self.cpp_lib_path}")
                
                # Define function signatures for ctypes
                # Example for a function: double* func(double* input, int size)
                # self.cpp_lib.sar_processing.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]
                # self.cpp_lib.sar_processing.restype = ctypes.POINTER(ctypes.c_double)
                
        except Exception as e:
            logger.error(f"Failed to load C++ library: {e}")
            logger.info("Falling back to Python implementations")
            self.cpp_lib = None
            self.ffi = None
    
    
    def call_cpp_algorithm(self, algorithm_name: str, 
                          input_data: np.ndarray,
                          params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Call a C++ algorithm function via ctypes or CFFI.
        
        Args:
            algorithm_name: Name of the algorithm (e.g., 'sar_processing', 'doppler_analysis')
            input_data: Input numpy array (complex64 or float64)
            params: Algorithm parameters dictionary
            
        Returns:
            Result numpy array
            
        Supported algorithms:
            - sar_processing: SAR image formation
            - doppler_analysis: Doppler spectrum analysis
            - pulse_compression: Matched filter pulse compression
            - clutter_rejection: MTI filter for clutter suppression
        """
        if self.cpp_lib is None:
            logger.info(f"C++ library not available. Using Python fallback for {algorithm_name}")
            return self._python_fallback(algorithm_name, input_data, params)
        
        try:
            logger.info(f"Calling C++ algorithm: {algorithm_name}")
            
            # Ensure input data is contiguous and correct type
            input_data = np.ascontiguousarray(input_data, dtype=np.float64)
            output_data = np.zeros_like(input_data)
            
            if self.use_cffi and self.ffi is not None:
                # CFFI approach
                input_ptr = self.ffi.cast("double*", self.ffi.from_buffer(input_data))
                output_ptr = self.ffi.cast("double*", self.ffi.from_buffer(output_data))
                size = len(input_data)
                
                # Call the C++ function
                func = getattr(self.cpp_lib, algorithm_name)
                func(input_ptr, output_ptr, size)
                
            else:
                # ctypes approach
                import ctypes
                func = getattr(self.cpp_lib, algorithm_name)
                
                # Set up argument and return types
                func.argtypes = [
                    np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS'),
                    np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS'),
                    ctypes.c_int
                ]
                func.restype = None
                
                # Call the function
                func(input_data, output_data, len(input_data))
            
            logger.info(f"C++ algorithm {algorithm_name} executed successfully")
            return output_data
            
        except AttributeError:
            logger.warning(f"C++ function '{algorithm_name}' not found in library. Using Python fallback.")
            return self._python_fallback(algorithm_name, input_data, params)
        except Exception as e:
            logger.error(f"C++ algorithm call failed: {e}. Using Python fallback.")
            return self._python_fallback(algorithm_name, input_data, params)
    
    def get_available_algorithms(self) -> List[str]:
        """
        Get list of available algorithms.
        
        Returns:
            List of algorithm names
        """
        return [
            "sar_processing",
            "doppler_analysis",
            "pulse_compression",
            "clutter_rejection"
        ]
    
    def _python_fallback(self, algorithm_name: str,
                        input_data: np.ndarray,
                        params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Python implementation fallback for C++ algorithms.
        """
        params = params or {}
        
        if algorithm_name == "sar_processing":
            return self._sar_processing_fallback(input_data, params)
        elif algorithm_name == "doppler_analysis":
            return self._doppler_analysis_fallback(input_data, params)
        elif algorithm_name == "clutter_rejection":
            return self._clutter_rejection_fallback(input_data, params)
        elif algorithm_name == "pulse_compression":
            return self._pulse_compression_fallback(input_data, params)
        else:
            logger.warning(f"Unknown algorithm: {algorithm_name}")
            return input_data
    
    
    def _sar_processing_fallback(self, data: np.ndarray, params: Dict) -> np.ndarray:
        """SAR image formation fallback."""
        logger.info("Executing SAR processing (Python fallback)")
        
        # Simple SAR processing simulation
        if len(data.shape) == 1:
            # Reshape to 2D for SAR processing
            size = int(np.sqrt(len(data)))
            data = data[:size*size].reshape(size, size)
        
        # Apply 2D FFT for range-Doppler processing
        sar_image = np.fft.fft2(data)
        sar_image = np.fft.fftshift(sar_image)
        
        return np.abs(sar_image)
    
    def _doppler_analysis_fallback(self, data: np.ndarray, params: Dict) -> np.ndarray:
        """Doppler analysis fallback."""
        logger.info("Executing Doppler analysis (Python fallback)")
        
        # Compute FFT for Doppler
        doppler_spectrum = np.fft.fft(data)
        doppler_spectrum = np.fft.fftshift(doppler_spectrum)
        
        return np.abs(doppler_spectrum)
    
    def _clutter_rejection_fallback(self, data: np.ndarray, params: Dict) -> np.ndarray:
        """Clutter rejection fallback using MTI filter."""
        logger.info("Executing clutter rejection (Python fallback)")
        
        # Simple Moving Target Indicator (MTI) filter
        if len(data) < 2:
            return data
        
        # Apply differencing filter
        filtered = np.diff(data)
        filtered = np.append(filtered, filtered[-1])  # Maintain length
        
        return filtered
    
    def _pulse_compression_fallback(self, data: np.ndarray, params: Dict) -> np.ndarray:
        """Pulse compression fallback."""
        logger.info("Executing pulse compression (Python fallback)")
        
        # Simple matched filter implementation
        # In practice, this would use a reference chirp signal
        matched_filter = np.conj(data[::-1])
        compressed = np.correlate(data, matched_filter, mode='same')
        
        return compressed
    
    def cleanup(self):
        """
        Clean up resources and unload libraries.
        """
        if self.cpp_lib is not None:
            logger.info("Cleaning up C++ library resources")
            self.cpp_lib = None
            self.ffi = None
