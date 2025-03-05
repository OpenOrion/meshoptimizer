"""
Data structures for meshoptimizer.
"""
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class EncodedMesh:
    """
    A dataclass representing encoded mesh data with size information.
    
    Attributes:
        vertices: Encoded vertex buffer as bytes
        indices: Encoded index buffer as bytes (optional)
        vertex_count: Number of vertices
        vertex_size: Size of each vertex in bytes
        index_count: Number of indices (optional)
        index_size: Size of each index in bytes (default: 4)
    """
    vertices: bytes
    indices: Optional[bytes] = None
    vertex_count: int = 0
    vertex_size: int = 0
    index_count: Optional[int] = None
    index_size: int = 4