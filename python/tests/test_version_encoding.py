"""
Tests for version encoding functions.
"""
import unittest
from meshoptimizer import encode_vertex_version, encode_index_version

class TestVersionEncoding(unittest.TestCase):
    """Test version encoding functionality."""
    
    def test_encode_vertex_version(self):
        """Test that encode_vertex_version returns version 1."""
        version = encode_vertex_version()
        self.assertEqual(version, 1)
    
    def test_encode_index_version(self):
        """Test that encode_index_version returns version 1."""
        version = encode_index_version()
        self.assertEqual(version, 1)

if __name__ == '__main__':
    unittest.main()