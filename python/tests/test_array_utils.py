"""
Tests for the arrayutils module.
"""
import os
import tempfile
import unittest
import numpy as np
from meshoptimizer import (
    EncodedArray,
    encode_array,
    decode_array,
    save_encoded_array_to_file,
    load_encoded_array_from_file,
    save_array_to_file,
    load_array_from_file,
    save_encoded_array_to_zip,
    load_encoded_array_from_zip,
    save_array_to_zip,
    load_array_from_zip,
    save_arrays_to_zip,
    load_arrays_from_zip,
)

class TestArrayUtils(unittest.TestCase):
    """Test cases for the arrayutils module."""
    
    def setUp(self):
        """Set up test data."""
        # Create test arrays
        self.array_1d = np.linspace(0, 10, 100, dtype=np.float32)
        self.array_2d = np.random.random((50, 3)).astype(np.float32)
        self.array_3d = np.random.random((10, 10, 10)).astype(np.float32)
        self.array_int = np.random.randint(0, 100, (20, 20), dtype=np.int32)
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        # Remove temporary files
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)
    
    def test_encode_decode_array_1d(self):
        """Test encoding and decoding a 1D array."""
        encoded = encode_array(self.array_1d)
        decoded = decode_array(encoded)
        
        # Check that the decoded array matches the original
        np.testing.assert_allclose(decoded, self.array_1d, rtol=1e-5)
        
        # Check that the encoded data is smaller than the original
        self.assertLess(len(encoded.data), self.array_1d.nbytes)
        
        # Print compression ratio
        print(f"1D array compression ratio: {len(encoded.data) / self.array_1d.nbytes:.2f}")
    
    def test_encode_decode_array_2d(self):
        """Test encoding and decoding a 2D array."""
        encoded = encode_array(self.array_2d)
        decoded = decode_array(encoded)
        
        # Check that the decoded array matches the original
        np.testing.assert_allclose(decoded, self.array_2d, rtol=1e-5)
        
        # Check that the encoded data is smaller than the original
        self.assertLess(len(encoded.data), self.array_2d.nbytes)
        
        # Print compression ratio
        print(f"2D array compression ratio: {len(encoded.data) / self.array_2d.nbytes:.2f}")
    
    def test_encode_decode_array_3d(self):
        """Test encoding and decoding a 3D array."""
        encoded = encode_array(self.array_3d)
        decoded = decode_array(encoded)
        
        # Check that the decoded array matches the original
        np.testing.assert_allclose(decoded, self.array_3d, rtol=1e-5)
        
        # Check that the encoded data is smaller than the original
        self.assertLess(len(encoded.data), self.array_3d.nbytes)
        
        # Print compression ratio
        print(f"3D array compression ratio: {len(encoded.data) / self.array_3d.nbytes:.2f}")
    
    def test_encode_decode_array_int(self):
        """Test encoding and decoding an integer array."""
        encoded = encode_array(self.array_int)
        decoded = decode_array(encoded)
        
        # Check that the decoded array matches the original
        np.testing.assert_allclose(decoded, self.array_int, rtol=1e-5)
        
        # Check that the encoded data is smaller than the original
        self.assertLess(len(encoded.data), self.array_int.nbytes)
        
        # Print compression ratio
        print(f"Integer array compression ratio: {len(encoded.data) / self.array_int.nbytes:.2f}")
    
    def test_save_load_file(self):
        """Test saving and loading an array to/from a file."""
        file_path = os.path.join(self.temp_dir, "test_array.bin")
        
        # Create a larger array for this test to ensure compression is effective
        large_array = np.random.random((1000, 3)).astype(np.float32)
        
        # Save the array to a file
        save_array_to_file(large_array, file_path)
        
        # Load the array from the file
        loaded = load_array_from_file(file_path)
        
        # Check that the loaded array matches the original
        np.testing.assert_allclose(loaded, large_array, rtol=1e-5)
        
        # Check that the file is smaller than the original array
        self.assertLess(os.path.getsize(file_path), large_array.nbytes)
        
        # Print compression ratio
        print(f"File compression ratio: {os.path.getsize(file_path) / large_array.nbytes:.2f}")
    
    def test_save_load_encoded_file(self):
        """Test saving and loading an encoded array to/from a file."""
        file_path = os.path.join(self.temp_dir, "test_encoded_array.bin")
        
        # Encode the array
        encoded = encode_array(self.array_2d)
        
        # Save the encoded array to a file
        save_encoded_array_to_file(encoded, file_path)
        
        # Load the encoded array from the file
        loaded_encoded = load_encoded_array_from_file(file_path)
        
        # Decode the loaded array
        decoded = decode_array(loaded_encoded)
        
        # Check that the decoded array matches the original
        np.testing.assert_allclose(decoded, self.array_2d, rtol=1e-5)
    
    def test_save_load_zip(self):
        """Test saving and loading an array to/from a zip file."""
        zip_path = os.path.join(self.temp_dir, "test_array.zip")
        
        # Create a larger array for this test to ensure compression is effective
        large_array = np.random.random((1000, 3)).astype(np.float32)
        
        # Save the array to a zip file
        save_array_to_zip(large_array, zip_path)
        
        # Load the array from the zip file
        loaded = load_array_from_zip(zip_path)
        
        # Check that the loaded array matches the original
        np.testing.assert_allclose(loaded, large_array, rtol=1e-5)
        
        # Check that the zip file is smaller than the original array
        self.assertLess(os.path.getsize(zip_path), large_array.nbytes)
        
        # Print compression ratio
        print(f"Zip compression ratio: {os.path.getsize(zip_path) / large_array.nbytes:.2f}")
    
    def test_save_load_encoded_zip(self):
        """Test saving and loading an encoded array to/from a zip file."""
        zip_path = os.path.join(self.temp_dir, "test_encoded_array.zip")
        
        # Encode the array
        encoded = encode_array(self.array_2d)
        
        # Save the encoded array to a zip file
        save_encoded_array_to_zip(encoded, zip_path)
        
        # Load the encoded array from the zip file
        loaded_encoded = load_encoded_array_from_zip(zip_path)
        
        # Decode the loaded array
        decoded = decode_array(loaded_encoded)
        
        # Check that the decoded array matches the original
        np.testing.assert_allclose(decoded, self.array_2d, rtol=1e-5)
    
    def test_save_load_multiple_arrays(self):
        """Test saving and loading multiple arrays to/from a zip file."""
        zip_path = os.path.join(self.temp_dir, "test_multiple_arrays.zip")
        
        # Create a dictionary of arrays
        arrays = {
            "array_1d": self.array_1d,
            "array_2d": self.array_2d,
            "array_3d": self.array_3d,
            "array_int": self.array_int
        }
        
        # Save the arrays to a zip file
        save_arrays_to_zip(arrays, zip_path)
        
        # Load the arrays from the zip file
        loaded_arrays = load_arrays_from_zip(zip_path)
        
        # Check that all arrays were loaded
        self.assertEqual(set(loaded_arrays.keys()), set(arrays.keys()))
        
        # Check that each loaded array matches the original
        for name, array in arrays.items():
            np.testing.assert_allclose(loaded_arrays[name], array, rtol=1e-5)
        
        # Check that the zip file is smaller than the combined size of all arrays
        total_size = sum(array.nbytes for array in arrays.values())
        self.assertLess(os.path.getsize(zip_path), total_size)
        
        # Print compression ratio
        print(f"Multiple arrays compression ratio: {os.path.getsize(zip_path) / total_size:.2f}")

if __name__ == "__main__":
    unittest.main()