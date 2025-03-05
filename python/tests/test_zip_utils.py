"""
Tests for the zip utilities functionality.

This file contains tests to verify that the zip utilities for storing and loading
encoded meshes in zip files work correctly.
"""
import os
import tempfile
import numpy as np
import unittest
from meshoptimizer import (
    Mesh, 
    EncodedMesh, 
    encode_mesh, 
    save_encoded_mesh_to_zip, 
    load_encoded_mesh_from_zip,
    save_mesh_to_zip,
    load_mesh_from_zip
)

class TestZipUtils(unittest.TestCase):
    """Test zip utilities functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create a simple mesh (a cube)
        self.vertices = np.array([
            # positions          
            [-0.5, -0.5, -0.5],
            [0.5, -0.5, -0.5],
            [0.5, 0.5, -0.5],
            [-0.5, 0.5, -0.5],
            [-0.5, -0.5, 0.5],
            [0.5, -0.5, 0.5],
            [0.5, 0.5, 0.5],
            [-0.5, 0.5, 0.5]
        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 2, 2, 3, 0,  # front
            1, 5, 6, 6, 2, 1,  # right
            5, 4, 7, 7, 6, 5,  # back
            4, 0, 3, 3, 7, 4,  # left
            3, 2, 6, 6, 7, 3,  # top
            4, 5, 1, 1, 0, 4   # bottom
        ], dtype=np.uint32)
        
        self.mesh = Mesh(self.vertices, self.indices)
        self.encoded_mesh = encode_mesh(self.vertices, self.indices)
    
    def get_triangles_set(self, vertices, indices):
        """
        Get a set of triangles from vertices and indices.
        Each triangle is represented as a frozenset of tuples of vertex coordinates.
        This makes the comparison invariant to vertex order within triangles.
        """
        triangles = set()
        for i in range(0, len(indices), 3):
            # Get the three vertices of the triangle
            v1 = tuple(vertices[indices[i]])
            v2 = tuple(vertices[indices[i+1]])
            v3 = tuple(vertices[indices[i+2]])
            # Create a frozenset of the vertices (order-invariant)
            triangle = frozenset([v1, v2, v3])
            triangles.add(triangle)
        return triangles
    
    def test_save_load_encoded_mesh(self):
        """Test saving and loading an encoded mesh to/from a zip file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            # Save the encoded mesh to the zip file
            save_encoded_mesh_to_zip(self.encoded_mesh, zip_path)
            
            # Load the encoded mesh from the zip file
            loaded_encoded_mesh = load_encoded_mesh_from_zip(zip_path)
            
            # Check that the loaded encoded mesh has the correct attributes
            self.assertEqual(loaded_encoded_mesh.vertex_count, self.encoded_mesh.vertex_count)
            self.assertEqual(loaded_encoded_mesh.vertex_size, self.encoded_mesh.vertex_size)
            self.assertEqual(loaded_encoded_mesh.index_count, self.encoded_mesh.index_count)
            self.assertEqual(loaded_encoded_mesh.index_size, self.encoded_mesh.index_size)
            self.assertEqual(loaded_encoded_mesh.vertices, self.encoded_mesh.vertices)
            self.assertEqual(loaded_encoded_mesh.indices, self.encoded_mesh.indices)
            
            # Decode the loaded encoded mesh
            from meshoptimizer import decode_mesh
            decoded_vertices, decoded_indices = decode_mesh(loaded_encoded_mesh)
            
            # Check that the decoded vertices match the original
            np.testing.assert_array_almost_equal(self.vertices, decoded_vertices)
            
            # Check that the triangles match
            original_triangles = self.get_triangles_set(self.vertices, self.indices)
            decoded_triangles = self.get_triangles_set(decoded_vertices, decoded_indices)
            
            self.assertEqual(original_triangles, decoded_triangles)
        finally:
            # Clean up the temporary file
            if os.path.exists(zip_path):
                os.unlink(zip_path)
    
    def test_save_load_mesh(self):
        """Test saving and loading a mesh to/from a zip file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            # Save the mesh to the zip file
            save_mesh_to_zip(self.mesh, zip_path)
            
            # Load the mesh from the zip file
            loaded_mesh = load_mesh_from_zip(Mesh, zip_path)
            
            # Check that the loaded mesh has the correct attributes
            self.assertEqual(loaded_mesh.vertex_count, self.mesh.vertex_count)
            self.assertEqual(loaded_mesh.index_count, self.mesh.index_count)
            
            # Check that the vertices match
            np.testing.assert_array_almost_equal(loaded_mesh.vertices, self.mesh.vertices)
            
            # Check that the triangles match
            original_triangles = self.get_triangles_set(self.mesh.vertices, self.mesh.indices)
            loaded_triangles = self.get_triangles_set(loaded_mesh.vertices, loaded_mesh.indices)
            
            self.assertEqual(original_triangles, loaded_triangles)
        finally:
            # Clean up the temporary file
            if os.path.exists(zip_path):
                os.unlink(zip_path)
    
    def test_custom_filenames(self):
        """Test saving and loading with custom filenames."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            # Custom filenames
            vertices_filename = "custom_vertices.bin"
            indices_filename = "custom_indices.bin"
            metadata_filename = "custom_metadata.json"
            
            # Save the encoded mesh to the zip file with custom filenames
            save_encoded_mesh_to_zip(
                self.encoded_mesh, 
                zip_path, 
                vertices_filename, 
                indices_filename, 
                metadata_filename
            )
            
            # Load the encoded mesh from the zip file with custom filenames
            loaded_encoded_mesh = load_encoded_mesh_from_zip(
                zip_path, 
                vertices_filename, 
                indices_filename, 
                metadata_filename
            )
            
            # Check that the loaded encoded mesh has the correct attributes
            self.assertEqual(loaded_encoded_mesh.vertex_count, self.encoded_mesh.vertex_count)
            self.assertEqual(loaded_encoded_mesh.vertex_size, self.encoded_mesh.vertex_size)
            self.assertEqual(loaded_encoded_mesh.index_count, self.encoded_mesh.index_count)
            self.assertEqual(loaded_encoded_mesh.index_size, self.encoded_mesh.index_size)
            self.assertEqual(loaded_encoded_mesh.vertices, self.encoded_mesh.vertices)
            self.assertEqual(loaded_encoded_mesh.indices, self.encoded_mesh.indices)
        finally:
            # Clean up the temporary file
            if os.path.exists(zip_path):
                os.unlink(zip_path)

if __name__ == '__main__':
    unittest.main()