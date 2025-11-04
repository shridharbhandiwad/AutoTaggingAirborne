"""
Data Loader Module for Airborne Radar Data

Handles loading and parsing of binary radar data files containing
radar measurements, SAR images, and other sensor data.
"""

import struct
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import h5py

logger = logging.getLogger(__name__)


class RadarDataLoader:
    """
    Loader for binary radar data files.
    Supports various radar data formats and provides unified interface.
    """
    
    SUPPORTED_FORMATS = ['bin', 'dat', 'h5', 'hdf5']
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the radar data loader.
        
        Args:
            config: Configuration dictionary for data processing
        """
        self.config = config or {}
        self.chunk_size = self.config.get('chunk_size', 10000)
        self.sampling_rate = self.config.get('sampling_rate', 1000)
        self.data_buffer = None
        self.metadata = {}
        
    def load_file(self, filepath: str) -> Dict[str, Any]:
        """
        Load radar data from file.
        
        Args:
            filepath: Path to the radar data file
            
        Returns:
            Dictionary containing loaded data and metadata
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
            
        file_ext = path.suffix[1:].lower()
        
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {file_ext}. Supported: {self.SUPPORTED_FORMATS}")
        
        logger.info(f"Loading radar data from: {filepath}")
        
        if file_ext in ['h5', 'hdf5']:
            return self._load_hdf5(path)
        else:
            return self._load_binary(path)
    
    def _load_binary(self, filepath: Path) -> Dict[str, Any]:
        """
        Load binary radar data file.
        
        Binary format structure (customizable):
        - Header (256 bytes): metadata
        - Data section: continuous radar samples
        """
        with open(filepath, 'rb') as f:
            # Read header (first 256 bytes)
            header = f.read(256)
            self.metadata = self._parse_header(header)
            
            # Read remaining data
            remaining_data = f.read()
            
            # Parse radar samples (assuming complex float format)
            num_samples = len(remaining_data) // 8  # 2 floats (I and Q) = 8 bytes
            
            if num_samples * 8 != len(remaining_data):
                logger.warning("Data length not aligned to sample size. Truncating.")
                remaining_data = remaining_data[:num_samples * 8]
            
            # Parse as complex samples (IQ data)
            iq_data = np.frombuffer(remaining_data, dtype=np.float32)
            iq_data = iq_data.reshape(-1, 2)
            complex_data = iq_data[:, 0] + 1j * iq_data[:, 1]
            
            # Extract position and velocity data (simulated from metadata)
            num_pulses = len(complex_data) // self.metadata.get('samples_per_pulse', 1024)
            
            result = {
                'raw_data': complex_data,
                'metadata': self.metadata,
                'timestamps': self._generate_timestamps(len(complex_data)),
                'position': self._extract_position_data(num_pulses),
                'velocity': self._extract_velocity_data(num_pulses),
                'doppler': self._compute_doppler(complex_data),
                'file_path': str(filepath)
            }
            
            logger.info(f"Loaded {len(complex_data)} samples from binary file")
            return result
    
    def _load_hdf5(self, filepath: Path) -> Dict[str, Any]:
        """
        Load HDF5 format radar data.
        """
        result = {}
        
        with h5py.File(filepath, 'r') as f:
            # Load datasets
            if 'raw_data' in f:
                result['raw_data'] = f['raw_data'][:]
            
            if 'timestamps' in f:
                result['timestamps'] = f['timestamps'][:]
            
            if 'position' in f:
                result['position'] = f['position'][:]
            
            if 'velocity' in f:
                result['velocity'] = f['velocity'][:]
            
            if 'doppler' in f:
                result['doppler'] = f['doppler'][:]
                
            # Load metadata
            if 'metadata' in f:
                self.metadata = dict(f['metadata'].attrs)
                result['metadata'] = self.metadata
        
        result['file_path'] = str(filepath)
        logger.info(f"Loaded data from HDF5 file: {filepath}")
        return result
    
    def _parse_header(self, header: bytes) -> Dict[str, Any]:
        """
        Parse binary header to extract metadata.
        
        Header format (example):
        - Bytes 0-3: Magic number (uint32)
        - Bytes 4-7: Version (uint32)
        - Bytes 8-11: Sampling rate (uint32)
        - Bytes 12-15: Number of channels (uint32)
        - Bytes 16-19: Samples per pulse (uint32)
        - Bytes 20-23: PRF (Pulse Repetition Frequency) (float32)
        - Bytes 24-27: Center frequency (float32)
        - Rest: Reserved
        """
        metadata = {}
        
        try:
            metadata['magic_number'] = struct.unpack('<I', header[0:4])[0]
            metadata['version'] = struct.unpack('<I', header[4:8])[0]
            metadata['sampling_rate'] = struct.unpack('<I', header[8:12])[0]
            metadata['num_channels'] = struct.unpack('<I', header[12:16])[0]
            metadata['samples_per_pulse'] = struct.unpack('<I', header[16:20])[0]
            metadata['prf'] = struct.unpack('<f', header[20:24])[0]
            metadata['center_frequency'] = struct.unpack('<f', header[24:28])[0]
        except Exception as e:
            logger.warning(f"Error parsing header: {e}. Using defaults.")
            metadata = {
                'sampling_rate': self.sampling_rate,
                'num_channels': 1,
                'samples_per_pulse': 1024,
                'prf': 1000.0,
                'center_frequency': 10e9
            }
        
        return metadata
    
    def _generate_timestamps(self, num_samples: int) -> np.ndarray:
        """Generate timestamps for samples."""
        dt = 1.0 / self.sampling_rate
        return np.arange(num_samples) * dt
    
    def _extract_position_data(self, num_pulses: int) -> np.ndarray:
        """
        Extract or simulate position data (x, y, z).
        In real scenario, this would parse actual GPS/INS data from file.
        """
        # Simulate position data for demonstration
        t = np.linspace(0, num_pulses / self.metadata.get('prf', 1000), num_pulses)
        x = 1000 * np.sin(0.1 * t)
        y = 1000 * np.cos(0.1 * t)
        z = 5000 + 100 * np.sin(0.05 * t)
        
        return np.column_stack([x, y, z])
    
    def _extract_velocity_data(self, num_pulses: int) -> np.ndarray:
        """
        Extract or compute velocity data (vx, vy, vz).
        """
        position = self._extract_position_data(num_pulses)
        
        # Compute velocity from position differences
        velocity = np.zeros_like(position)
        dt = 1.0 / self.metadata.get('prf', 1000)
        
        if len(position) > 1:
            velocity[1:] = np.diff(position, axis=0) / dt
            velocity[0] = velocity[1]  # Copy first velocity
        
        return velocity
    
    def _compute_doppler(self, complex_data: np.ndarray) -> np.ndarray:
        """
        Compute Doppler shift from complex radar data.
        """
        # Compute FFT for Doppler analysis
        fft_data = np.fft.fft(complex_data)
        doppler_spectrum = np.abs(fft_data)
        
        return doppler_spectrum
    
    def save_data(self, data: Dict[str, Any], output_path: str, format: str = 'hdf5'):
        """
        Save processed radar data to file.
        
        Args:
            data: Data dictionary to save
            output_path: Output file path
            format: Output format ('hdf5', 'npz', 'csv')
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'hdf5':
            self._save_hdf5(data, path)
        elif format == 'npz':
            self._save_npz(data, path)
        else:
            raise ValueError(f"Unsupported output format: {format}")
        
        logger.info(f"Saved data to: {output_path}")
    
    def _save_hdf5(self, data: Dict[str, Any], filepath: Path):
        """Save data in HDF5 format."""
        with h5py.File(filepath, 'w') as f:
            for key, value in data.items():
                if key == 'metadata' and isinstance(value, dict):
                    grp = f.create_group('metadata')
                    for k, v in value.items():
                        grp.attrs[k] = v
                elif isinstance(value, np.ndarray):
                    f.create_dataset(key, data=value, compression='gzip')
                elif isinstance(value, (int, float, str)):
                    f.attrs[key] = value
    
    def _save_npz(self, data: Dict[str, Any], filepath: Path):
        """Save data in NumPy compressed format."""
        arrays = {k: v for k, v in data.items() if isinstance(v, np.ndarray)}
        np.savez_compressed(filepath, **arrays)
