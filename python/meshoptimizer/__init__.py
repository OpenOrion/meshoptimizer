"""
Python wrapper for the meshoptimizer library.

This package provides Python bindings for the meshoptimizer C++ library,
which offers various algorithms for optimizing 3D meshes for GPU rendering.
It also provides utilities for compressing and storing numpy arrays.
"""

from .data import EncodedMesh

from .encoder import (
    encode_vertex_buffer,
    encode_index_buffer,
    encode_vertex_version,
    encode_index_version,
    encode_mesh,
)

from .decoder import (
    decode_vertex_buffer,
    decode_index_buffer,
    decode_vertex_version,
    decode_index_version,
    decode_filter_oct,
    decode_filter_quat,
    decode_filter_exp,
    decode_mesh,
)

from .optimizer import (
    optimize_vertex_cache,
    optimize_vertex_cache_strip,
    optimize_vertex_cache_fifo,
    optimize_overdraw,
    optimize_vertex_fetch,
    optimize_vertex_fetch_remap,
)

from .simplifier import (
    simplify,
    simplify_with_attributes,
    simplify_sloppy,
    simplify_points,
    simplify_scale,
    SIMPLIFY_LOCK_BORDER,
    SIMPLIFY_SPARSE,
    SIMPLIFY_ERROR_ABSOLUTE,
    SIMPLIFY_PRUNE,
)

from .utils import (
    generate_vertex_remap,
    remap_vertex_buffer,
    remap_index_buffer,
)

from .ziputils import (
    save_encoded_mesh_to_zip,
    load_encoded_mesh_from_zip,
    save_mesh_to_zip,
    load_mesh_from_zip,
)

from .arrayutils import (
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

import numpy as np
from typing import Optional, Union, Dict, Any, ClassVar, Type, TypeVar
from .data import EncodedMesh

T = TypeVar('T', bound='Mesh')

class Mesh:
    """
    A class representing a 3D mesh with optimization capabilities.
    """
    
    def __init__(self, vertices: np.ndarray, indices: Optional[np.ndarray] = None) -> None:
        """
        Initialize a mesh with vertices and optional indices.
        
        Args:
            vertices: numpy array of vertex data
            indices: numpy array of indices (optional)
        """
        self.vertices = np.asarray(vertices, dtype=np.float32)
        self.indices = np.asarray(indices, dtype=np.uint32) if indices is not None else None
        self.vertex_count = len(vertices)
        self.index_count = len(indices) if indices is not None else 0
    
    def optimize_vertex_cache(self) -> 'Mesh':
        """
        Optimize the mesh for vertex cache efficiency.
        
        Returns:
            self (for method chaining)
        """
        if self.indices is None:
            raise ValueError("Mesh has no indices to optimize")
        
        # Create output array
        optimized_indices = np.zeros_like(self.indices)
        
        # Call optimization function
        optimize_vertex_cache(
            optimized_indices, 
            self.indices, 
            self.index_count, 
            self.vertex_count
        )
        
        self.indices = optimized_indices
        return self
    
    def optimize_overdraw(self, threshold: float = 1.05) -> 'Mesh':
        """
        Optimize the mesh for overdraw.
        
        Args:
            threshold: threshold for optimization (default: 1.05)
            
        Returns:
            self (for method chaining)
        """
        if self.indices is None:
            raise ValueError("Mesh has no indices to optimize")
        
        # Create output array
        optimized_indices = np.zeros_like(self.indices)
        
        # Call optimization function
        optimize_overdraw(
            optimized_indices, 
            self.indices, 
            self.vertices, 
            self.index_count, 
            self.vertex_count, 
            self.vertices.itemsize * self.vertices.shape[1], 
            threshold
        )
        
        self.indices = optimized_indices
        return self
    
    def optimize_vertex_fetch(self) -> 'Mesh':
        """
        Optimize the mesh for vertex fetch efficiency.
        
        Returns:
            self (for method chaining)
        """
        if self.indices is None:
            raise ValueError("Mesh has no indices to optimize")
        
        # Create output array
        optimized_vertices = np.zeros_like(self.vertices)
        
        # Call optimization function
        unique_vertex_count = optimize_vertex_fetch(
            optimized_vertices, 
            self.indices, 
            self.vertices, 
            self.index_count, 
            self.vertex_count, 
            self.vertices.itemsize * self.vertices.shape[1]
        )
        
        self.vertices = optimized_vertices[:unique_vertex_count]
        self.vertex_count = unique_vertex_count
        return self
    
    def simplify(self, target_ratio: float = 0.25, target_error: float = 0.01, options: int = 0) -> 'Mesh':
        """
        Simplify the mesh.
        
        Args:
            target_ratio: ratio of triangles to keep (default: 0.25)
            target_error: target error (default: 0.01)
            options: simplification options (default: 0)
            
        Returns:
            self (for method chaining)
        """
        if self.indices is None:
            raise ValueError("Mesh has no indices to simplify")
        
        # Calculate target index count
        target_index_count = int(self.index_count * target_ratio)
        
        # Create output array
        simplified_indices = np.zeros(self.index_count, dtype=np.uint32)
        
        # Call simplification function
        result_error = np.array([0.0], dtype=np.float32)
        new_index_count = simplify(
            simplified_indices, 
            self.indices, 
            self.vertices, 
            self.index_count, 
            self.vertex_count, 
            self.vertices.itemsize * self.vertices.shape[1], 
            target_index_count, 
            target_error, 
            options, 
            result_error
        )
        
        self.indices = simplified_indices[:new_index_count]
        self.index_count = new_index_count
        return self
    
    def encode(self) -> EncodedMesh:
        """
        Encode the mesh for efficient transmission.
        
        Returns:
            EncodedMesh object containing encoded buffers and size information
        """
        return encode_mesh(
            self.vertices,
            self.indices,
            self.vertex_count,
            self.vertices.itemsize * self.vertices.shape[1],
            self.index_count
        )
    
    @classmethod
    def decode(cls: Type[T], encoded_data: Union[Dict[str, bytes], EncodedMesh],
              vertex_count: Optional[int] = None,
              vertex_size: Optional[int] = None,
              index_count: Optional[int] = None,
              index_size: int = 4) -> T:
        """
        Decode an encoded mesh.
        
        Args:
            encoded_data: Either an EncodedMesh object or a dictionary with encoded vertices and indices
            vertex_count: Number of vertices (optional if encoded_data is EncodedMesh)
            vertex_size: Size of each vertex in bytes (optional if encoded_data is EncodedMesh)
            index_count: Number of indices (optional if encoded_data is EncodedMesh)
            index_size: Size of each index in bytes (default: 4)
            
        Returns:
            Decoded Mesh object
        """
        if isinstance(encoded_data, EncodedMesh):
            # Use the EncodedMesh object directly
            vertices, indices = decode_mesh(encoded_data)
        else:
            # Legacy dictionary format
            if vertex_count is None or vertex_size is None:
                raise ValueError("vertex_count and vertex_size must be provided when using dictionary format")
            
            # Decode vertices
            vertices = decode_vertex_buffer(
                vertex_count,
                vertex_size,
                encoded_data['vertices']
            )
            
            # Decode indices if present
            indices = None
            if encoded_data['indices'] is not None and index_count is not None:
                indices = decode_index_buffer(
                    index_count,
                    index_size,
                    encoded_data['indices']
                )
        
        return cls(vertices, indices)

# Version information
__version__ = '0.1.0'