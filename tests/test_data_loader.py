"""
Unit tests for RadarDataLoader
"""

import pytest
import numpy as np
from pathlib import Path
import h5py
import tempfile
import os

from radar_analyzer import RadarDataLoader


class TestRadarDataLoader:
    """Test suite for RadarDataLoader."""
    
    @pytest.fixture
    def loader(self):
        """Create a data loader instance."""
        config = {
            'chunk_size': 1000,
            'sampling_rate': 1000
        }
        return RadarDataLoader(config)
    
    @pytest.fixture
    def sample_binary_file(self):
        """Create a sample binary radar file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            # Write header (256 bytes)
            header = bytearray(256)
            # Magic number
            header[0:4] = (0x12345678).to_bytes(4, byteorder='little')
            # Version
            header[4:8] = (1).to_bytes(4, byteorder='little')
            # Sampling rate
            header[8:12] = (1000).to_bytes(4, byteorder='little')
            # Num channels
            header[12:16] = (1).to_bytes(4, byteorder='little')
            # Samples per pulse
            header[16:20] = (1024).to_bytes(4, byteorder='little')
            
            f.write(header)
            
            # Write some sample IQ data (100 samples)
            for i in range(100):
                # I component (float32)
                f.write(np.float32(np.cos(2 * np.pi * i / 10)).tobytes())
                # Q component (float32)
                f.write(np.float32(np.sin(2 * np.pi * i / 10)).tobytes())
            
            filename = f.name
        
        yield filename
        
        # Cleanup
        os.unlink(filename)
    
    @pytest.fixture
    def sample_hdf5_file(self):
        """Create a sample HDF5 radar file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as f:
            filename = f.name
        
        # Create HDF5 file
        with h5py.File(filename, 'w') as f:
            # Create datasets
            raw_data = np.random.randn(100) + 1j * np.random.randn(100)
            f.create_dataset('raw_data', data=raw_data)
            
            timestamps = np.linspace(0, 1, 100)
            f.create_dataset('timestamps', data=timestamps)
            
            position = np.random.randn(100, 3) * 1000
            f.create_dataset('position', data=position)
            
            velocity = np.random.randn(100, 3) * 100
            f.create_dataset('velocity', data=velocity)
            
            # Add metadata
            metadata_grp = f.create_group('metadata')
            metadata_grp.attrs['prf'] = 1000.0
            metadata_grp.attrs['center_frequency'] = 10e9
        
        yield filename
        
        # Cleanup
        os.unlink(filename)
    
    def test_loader_initialization(self, loader):
        """Test loader initialization."""
        assert loader is not None
        assert loader.chunk_size == 1000
        assert loader.sampling_rate == 1000
    
    def test_load_binary_file(self, loader, sample_binary_file):
        """Test loading binary file."""
        data = loader.load_file(sample_binary_file)
        
        assert 'raw_data' in data
        assert 'metadata' in data
        assert 'timestamps' in data
        assert 'position' in data
        assert 'velocity' in data
        
        # Check data types
        assert isinstance(data['raw_data'], np.ndarray)
        assert data['raw_data'].dtype == np.complex64 or data['raw_data'].dtype == np.complex128
        assert len(data['raw_data']) == 100
    
    def test_load_hdf5_file(self, loader, sample_hdf5_file):
        """Test loading HDF5 file."""
        data = loader.load_file(sample_hdf5_file)
        
        assert 'raw_data' in data
        assert 'timestamps' in data
        assert 'position' in data
        assert 'velocity' in data
        assert 'metadata' in data
        
        # Check shapes
        assert len(data['raw_data']) == 100
        assert data['position'].shape == (100, 3)
        assert data['velocity'].shape == (100, 3)
    
    def test_file_not_found(self, loader):
        """Test error handling for missing file."""
        with pytest.raises(FileNotFoundError):
            loader.load_file('nonexistent_file.bin')
    
    def test_unsupported_format(self, loader):
        """Test error handling for unsupported format."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
            filename = f.name
        
        try:
            with pytest.raises(ValueError):
                loader.load_file(filename)
        finally:
            os.unlink(filename)
    
    def test_save_hdf5(self, loader):
        """Test saving data to HDF5."""
        # Create sample data
        data = {
            'raw_data': np.random.randn(100) + 1j * np.random.randn(100),
            'position': np.random.randn(100, 3),
            'velocity': np.random.randn(100, 3),
            'timestamps': np.linspace(0, 1, 100),
            'metadata': {'prf': 1000.0, 'center_frequency': 10e9}
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_output.h5'
            loader.save_data(data, str(output_path), format='hdf5')
            
            assert output_path.exists()
            
            # Verify saved data
            with h5py.File(output_path, 'r') as f:
                assert 'raw_data' in f
                assert 'position' in f
                assert len(f['raw_data']) == 100
    
    def test_doppler_computation(self, loader):
        """Test Doppler spectrum computation."""
        complex_data = np.exp(1j * 2 * np.pi * np.linspace(0, 10, 100))
        doppler = loader._compute_doppler(complex_data)
        
        assert isinstance(doppler, np.ndarray)
        assert len(doppler) == len(complex_data)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
