"""
Utilities for compressing and storing numpy arrays.

This module provides functions for compressing numpy arrays using meshoptimizer's
encoding functions and storing/loading them to/from files or zip archives.
"""
import ctypes
import json
import zipfile
from io import BytesIO
from typing import Optional, Union, Dict, Any, Tuple, List
import os
import struct
import numpy as np
from ._loader import lib
from .data import EncodedMesh

class EncodedArray:
    """
    A class representing an encoded numpy array with metadata.
    
    Attributes:
        data: Encoded data as bytes
        shape: Original array shape
        dtype: Original array data type
        itemsize: Size of each item in bytes
    """
    def __init__(self, data: bytes, shape: Tuple[int, ...], dtype: np.dtype, itemsize: int):
        self.data = data
        self.shape = shape
        self.dtype = dtype
        self.itemsize = itemsize
    
    def __len__(self) -> int:
        """Return the length of the encoded data in bytes."""
        return len(self.data)

def encode_array(array: np.ndarray) -> EncodedArray:
    """
    Encode a numpy array using meshoptimizer's vertex buffer encoding.
    
    Args:
        array: numpy array to encode
        
    Returns:
        EncodedArray object containing the encoded data and metadata
    """
    # Store original shape and dtype
    original_shape = array.shape
    original_dtype = array.dtype
    
    # Flatten the array if it's multi-dimensional
    flattened = array.reshape(-1)
    
    # Convert to float32 if not already (meshoptimizer expects float32)
    if array.dtype != np.float32:
        flattened = flattened.astype(np.float32)
    
    # Calculate parameters for encoding
    item_count = len(flattened)
    item_size = flattened.itemsize
    
    # Calculate buffer size
    bound = lib.meshopt_encodeVertexBufferBound(item_count, item_size)
    
    # Allocate buffer
    buffer = np.zeros(bound, dtype=np.uint8)
    
    # Call C function
    result_size = lib.meshopt_encodeVertexBuffer(
        buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
        bound,
        flattened.ctypes.data_as(ctypes.c_void_p),
        item_count,
        item_size
    )
    
    if result_size == 0:
        raise RuntimeError("Failed to encode array")
    
    # Return only the used portion of the buffer
    encoded_data = bytes(buffer[:result_size])
    
    return EncodedArray(
        data=encoded_data,
        shape=original_shape,
        dtype=original_dtype,
        itemsize=item_size
    )

def decode_array(encoded_array: EncodedArray) -> np.ndarray:
    """
    Decode an encoded array.
    
    Args:
        encoded_array: EncodedArray object containing encoded data and metadata
        
    Returns:
        Decoded numpy array
    """
    # Calculate total number of items
    total_items = np.prod(encoded_array.shape)
    
    # Create buffer for encoded data
    buffer_array = np.frombuffer(encoded_array.data, dtype=np.uint8)
    
    # Create destination array for float32 data
    float_count = total_items
    destination = np.zeros(float_count, dtype=np.float32)
    
    # Call C function
    result = lib.meshopt_decodeVertexBuffer(
        destination.ctypes.data_as(ctypes.c_void_p),
        total_items,
        encoded_array.itemsize,
        buffer_array.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
        len(buffer_array)
    )
    
    if result != 0:
        raise RuntimeError(f"Failed to decode array: error code {result}")
    
    # Reshape the array to its original shape
    reshaped = destination.reshape(encoded_array.shape)
    
    # Convert back to original dtype if needed
    if encoded_array.dtype != np.float32:
        reshaped = reshaped.astype(encoded_array.dtype)
    
    return reshaped

def save_encoded_array_to_file(encoded_array: EncodedArray, file_path: str) -> None:
    """
    Save an encoded array to a file.
    
    Args:
        encoded_array: EncodedArray object to save
        file_path: Path to the output file
    """
    # Create metadata
    metadata = {
        "shape": encoded_array.shape,
        "dtype": str(encoded_array.dtype),
        "itemsize": encoded_array.itemsize
    }
    
    # Convert metadata to JSON
    metadata_json = json.dumps(metadata)
    
    # Write to file
    with open(file_path, 'wb') as f:
        # Write metadata length as 4-byte integer
        f.write(struct.pack('<I', len(metadata_json)))
        
        # Write metadata as JSON
        f.write(metadata_json.encode('utf-8'))
        
        # Write encoded data
        f.write(encoded_array.data)

def load_encoded_array_from_file(file_path: str) -> EncodedArray:
    """
    Load an encoded array from a file.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        EncodedArray object loaded from the file
    """
    with open(file_path, 'rb') as f:
        # Read metadata length
        metadata_length = struct.unpack('<I', f.read(4))[0]
        
        # Read metadata
        metadata_json = f.read(metadata_length).decode('utf-8')
        metadata = json.loads(metadata_json)
        
        # Read encoded data
        encoded_data = f.read()
    
    # Create EncodedArray object
    return EncodedArray(
        data=encoded_data,
        shape=tuple(metadata["shape"]),
        dtype=np.dtype(metadata["dtype"]),
        itemsize=metadata["itemsize"]
    )

def save_array_to_file(array: np.ndarray, file_path: str) -> None:
    """
    Encode and save a numpy array to a file.
    
    Args:
        array: numpy array to encode and save
        file_path: Path to the output file
    """
    encoded_array = encode_array(array)
    save_encoded_array_to_file(encoded_array, file_path)

def load_array_from_file(file_path: str) -> np.ndarray:
    """
    Load and decode a numpy array from a file.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        Decoded numpy array
    """
    encoded_array = load_encoded_array_from_file(file_path)
    return decode_array(encoded_array)

def save_encoded_array_to_zip(encoded_array: EncodedArray, 
                             zip_path: str, 
                             data_filename: str = "data.bin",
                             metadata_filename: str = "metadata.json") -> None:
    """
    Save an encoded array to a zip file.
    
    Args:
        encoded_array: EncodedArray object to save
        zip_path: Path to the output zip file
        data_filename: Name of the data binary file within the zip (default: "data.bin")
        metadata_filename: Name of the metadata JSON file within the zip (default: "metadata.json")
    """
    # Create metadata dictionary
    metadata = {
        "shape": encoded_array.shape,
        "dtype": str(encoded_array.dtype),
        "itemsize": encoded_array.itemsize
    }
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Write data binary file
        zipf.writestr(data_filename, encoded_array.data)
        
        # Write metadata JSON file
        zipf.writestr(metadata_filename, json.dumps(metadata, indent=2))

def load_encoded_array_from_zip(zip_path: str,
                               data_filename: str = "data.bin",
                               metadata_filename: str = "metadata.json") -> EncodedArray:
    """
    Load an encoded array from a zip file.
    
    Args:
        zip_path: Path to the input zip file
        data_filename: Name of the data binary file within the zip (default: "data.bin")
        metadata_filename: Name of the metadata JSON file within the zip (default: "metadata.json")
        
    Returns:
        EncodedArray object loaded from the zip file
    """
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        # Read metadata JSON file
        with zipf.open(metadata_filename) as f:
            metadata = json.load(f)
        
        # Read data binary file
        with zipf.open(data_filename) as f:
            data = f.read()
    
    # Create EncodedArray object
    return EncodedArray(
        data=data,
        shape=tuple(metadata["shape"]),
        dtype=np.dtype(metadata["dtype"]),
        itemsize=metadata["itemsize"]
    )

def save_array_to_zip(array: np.ndarray, 
                     zip_path: str, 
                     data_filename: str = "data.bin",
                     metadata_filename: str = "metadata.json") -> None:
    """
    Encode and save a numpy array to a zip file.
    
    Args:
        array: numpy array to encode and save
        zip_path: Path to the output zip file
        data_filename: Name of the data binary file within the zip (default: "data.bin")
        metadata_filename: Name of the metadata JSON file within the zip (default: "metadata.json")
    """
    encoded_array = encode_array(array)
    save_encoded_array_to_zip(
        encoded_array, 
        zip_path, 
        data_filename, 
        metadata_filename
    )

def load_array_from_zip(zip_path: str,
                       data_filename: str = "data.bin",
                       metadata_filename: str = "metadata.json") -> np.ndarray:
    """
    Load and decode a numpy array from a zip file.
    
    Args:
        zip_path: Path to the input zip file
        data_filename: Name of the data binary file within the zip (default: "data.bin")
        metadata_filename: Name of the metadata JSON file within the zip (default: "metadata.json")
        
    Returns:
        Decoded numpy array
    """
    encoded_array = load_encoded_array_from_zip(
        zip_path, 
        data_filename, 
        metadata_filename
    )
    return decode_array(encoded_array)

def save_arrays_to_zip(arrays: Dict[str, np.ndarray], zip_path: str) -> None:
    """
    Encode and save multiple numpy arrays to a zip file.
    
    Args:
        arrays: Dictionary mapping array names to numpy arrays
        zip_path: Path to the output zip file
    """
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Create a metadata dictionary for all arrays
        all_metadata = {}
        
        for name, array in arrays.items():
            # Encode the array
            encoded_array = encode_array(array)
            
            # Add metadata to the dictionary
            all_metadata[name] = {
                "shape": encoded_array.shape,
                "dtype": str(encoded_array.dtype),
                "itemsize": encoded_array.itemsize,
                "filename": f"{name}.bin"
            }
            
            # Write data binary file
            zipf.writestr(f"{name}.bin", encoded_array.data)
        
        # Write metadata JSON file
        zipf.writestr("metadata.json", json.dumps(all_metadata, indent=2))

def load_arrays_from_zip(zip_path: str) -> Dict[str, np.ndarray]:
    """
    Load and decode multiple numpy arrays from a zip file.
    
    Args:
        zip_path: Path to the input zip file
        
    Returns:
        Dictionary mapping array names to decoded numpy arrays
    """
    result = {}
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        # Read metadata JSON file
        with zipf.open("metadata.json") as f:
            all_metadata = json.load(f)
        
        # Process each array
        for name, metadata in all_metadata.items():
            # Read data binary file
            with zipf.open(metadata["filename"]) as f:
                data = f.read()
            
            # Create EncodedArray object
            encoded_array = EncodedArray(
                data=data,
                shape=tuple(metadata["shape"]),
                dtype=np.dtype(metadata["dtype"]),
                itemsize=metadata["itemsize"]
            )
            
            # Decode the array
            result[name] = decode_array(encoded_array)
    
    return result