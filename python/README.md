# Meshoptimizer Python

Python bindings for the [meshoptimizer](https://github.com/zeux/meshoptimizer) library, which provides algorithms for optimizing 3D meshes for GPU rendering.

## Installation

```bash
pip install meshoptimizer
```

Or install from source:

```bash
git clone https://github.com/zeux/meshoptimizer.git
cd meshoptimizer/python
pip install -e .
```

## Features

- Vertex cache optimization
- Overdraw optimization
- Vertex fetch optimization
- Mesh simplification
- Vertex/index buffer compression and decompression
- Zip file storage for encoded meshes
- Numpy array compression and storage
- And more...

## Usage

### Basic Usage

```python
import numpy as np
from meshoptimizer import Mesh

# Create a simple mesh (a cube)
vertices = np.array([
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

indices = np.array([
    0, 1, 2, 2, 3, 0,  # front
    1, 5, 6, 6, 2, 1,  # right
    5, 4, 7, 7, 6, 5,  # back
    4, 0, 3, 3, 7, 4,  # left
    3, 2, 6, 6, 7, 3,  # top
    4, 5, 1, 1, 0, 4   # bottom
], dtype=np.uint32)

# Create a mesh
mesh = Mesh(vertices, indices)

# Optimize the mesh
mesh.optimize_vertex_cache()
mesh.optimize_overdraw()
mesh.optimize_vertex_fetch()

# Simplify the mesh
mesh.simplify(target_ratio=0.5)  # Keep 50% of triangles

# Encode the mesh for efficient transmission
encoded = mesh.encode()

# Decode the mesh
decoded = Mesh.decode(
    encoded,
    vertex_count=len(mesh.vertices),
    vertex_size=mesh.vertices.itemsize * mesh.vertices.shape[1],
    index_count=len(mesh.indices)
)
```

### Low-level API

If you need more control, you can use the low-level API directly:

```python
import numpy as np
from meshoptimizer import (
    optimize_vertex_cache,
    optimize_overdraw,
    optimize_vertex_fetch,
    simplify,
    encode_vertex_buffer,
    decode_vertex_buffer,
    encode_index_buffer,
    decode_index_buffer
)

# Optimize vertex cache
optimized_indices = np.zeros_like(indices)
optimize_vertex_cache(optimized_indices, indices, len(indices), len(vertices))

# Optimize overdraw
optimized_indices2 = np.zeros_like(indices)
optimize_overdraw(
    optimized_indices2,
    optimized_indices,
    vertices,
    len(indices),
    len(vertices),
    vertices.itemsize * vertices.shape[1],
    1.05  # threshold
)

# And so on...
```
## Notes on Index Encoding/Decoding

When using the index buffer encoding and decoding functions, note that the decoded indices may not exactly match the original indices, even though the mesh geometry remains the same. This is due to how the meshoptimizer library internally encodes and decodes the indices. The triangles may be in a different order, but the resulting mesh is still valid and represents the same geometry.

## Zip File Storage

You can store encoded meshes in zip files for easy distribution and storage:

```python
import numpy as np
from meshoptimizer import Mesh, save_mesh_to_zip, load_mesh_from_zip

# Create a mesh
vertices = np.array([[-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5]], dtype=np.float32)
indices = np.array([0, 1, 2], dtype=np.uint32)
mesh = Mesh(vertices, indices)

# Save the mesh to a zip file
save_mesh_to_zip(mesh, "mesh.zip")

# Load the mesh from the zip file
loaded_mesh = load_mesh_from_zip(Mesh, "mesh.zip")

# You can also work with encoded meshes directly
from meshoptimizer import encode_mesh, save_encoded_mesh_to_zip, load_encoded_mesh_from_zip

# Encode the mesh
encoded_mesh = encode_mesh(vertices, indices)

# Save the encoded mesh to a zip file with custom filenames
save_encoded_mesh_to_zip(
    encoded_mesh,
    "encoded_mesh.zip",
    vertices_filename="verts.bin",
    indices_filename="idx.bin",
    metadata_filename="meta.json"
)

# Load the encoded mesh from the zip file
loaded_encoded_mesh = load_encoded_mesh_from_zip(
    "encoded_mesh.zip",
    vertices_filename="verts.bin",
    indices_filename="idx.bin",
    metadata_filename="meta.json"
)
```

The zip file contains:
- Binary file for encoded vertices
- Binary file for encoded indices
- JSON file with metadata (vertex_count, vertex_size, index_count, index_size)

## Numpy Array Compression

You can compress and store any numpy array using the meshoptimizer encoding functions:

```python
import numpy as np
from meshoptimizer import (
    encode_array,
    decode_array,
    save_array_to_file,
    load_array_from_file,
    save_array_to_zip,
    load_array_from_zip,
    save_arrays_to_zip,
    load_arrays_from_zip
)

# Create a numpy array
array_2d = np.random.random((1000, 3)).astype(np.float32)
print(f"Original array size: {array_2d.nbytes} bytes")

# Encode the array
encoded_array = encode_array(array_2d)
print(f"Encoded size: {len(encoded_array.data)} bytes")
print(f"Compression ratio: {len(encoded_array.data) / array_2d.nbytes:.2f}")

# Decode the array
decoded_array = decode_array(encoded_array)
print(f"Decoded array shape: {decoded_array.shape}")

# Verify the decoded array matches the original
is_close = np.allclose(decoded_array, array_2d, rtol=1e-5)
print(f"Decoded array matches original: {is_close}")

# Save to a file
save_array_to_file(array_2d, "compressed_array.bin")

# Load from a file
loaded_array = load_array_from_file("compressed_array.bin")

# Save to a zip file
save_array_to_zip(array_2d, "compressed_array.zip")

# Load from a zip file
loaded_array = load_array_from_zip("compressed_array.zip")

# Work with multiple arrays
arrays = {
    "positions": np.random.random((1000, 3)).astype(np.float32),
    "normals": np.random.random((1000, 3)).astype(np.float32),
    "colors": np.random.random((1000, 4)).astype(np.float32),
    "indices": np.random.randint(0, 1000, (2000,), dtype=np.uint32)
}

# Save multiple arrays to a single zip file
save_arrays_to_zip(arrays, "multiple_arrays.zip")

# Load multiple arrays from a zip file
loaded_arrays = load_arrays_from_zip("multiple_arrays.zip")
```

The array compression works with arrays of any shape and most numeric data types. The compression is particularly effective for arrays with spatial coherence, such as vertex positions, normals, or other 3D data.

## API Reference

### High-level API

#### `Mesh` class

- `__init__(vertices, indices=None)`: Initialize a mesh with vertices and optional indices.
- `optimize_vertex_cache()`: Optimize the mesh for vertex cache efficiency.
- `optimize_overdraw(threshold=1.05)`: Optimize the mesh for overdraw.
- `optimize_vertex_fetch()`: Optimize the mesh for vertex fetch efficiency.
- `simplify(target_ratio=0.25, target_error=0.01, options=0)`: Simplify the mesh.
- `encode()`: Encode the mesh for efficient transmission.
- `decode(encoded_data, vertex_count, vertex_size, index_count=None, index_size=4)` (class method): Decode an encoded mesh.

### Low-level API

#### Vertex Remapping

- `generate_vertex_remap(destination, indices, index_count, vertices, vertex_count, vertex_size)`: Generate vertex remap table.
- `remap_vertex_buffer(destination, vertices, vertex_count, vertex_size, remap)`: Remap vertex buffer.
- `remap_index_buffer(destination, indices, index_count, remap)`: Remap index buffer.

#### Optimization

- `optimize_vertex_cache(destination, indices, index_count, vertex_count)`: Optimize vertex cache.
- `optimize_vertex_cache_strip(destination, indices, index_count, vertex_count)`: Optimize vertex cache for strip-like caches.
- `optimize_vertex_cache_fifo(destination, indices, index_count, vertex_count, cache_size)`: Optimize vertex cache for FIFO caches.
- `optimize_overdraw(destination, indices, vertex_positions, index_count, vertex_count, vertex_positions_stride, threshold)`: Optimize overdraw.
- `optimize_vertex_fetch(destination_vertices, indices, source_vertices, index_count, vertex_count, vertex_size)`: Optimize vertex fetch.
- `optimize_vertex_fetch_remap(destination, indices, index_count, vertex_count)`: Generate vertex remap to optimize vertex fetch.

#### Simplification

- `simplify(destination, indices, vertex_positions, index_count, vertex_count, vertex_positions_stride, target_index_count, target_error, options, result_error)`: Simplify mesh.
- `simplify_with_attributes(destination, indices, vertex_positions, vertex_attributes, attribute_weights, index_count, vertex_count, vertex_positions_stride, vertex_attributes_stride, attribute_count, vertex_lock, target_index_count, target_error, options, result_error)`: Simplify mesh with attribute metric.
- `simplify_sloppy(destination, indices, vertex_positions, index_count, vertex_count, vertex_positions_stride, target_index_count, target_error, result_error)`: Simplify mesh (sloppy).
- `simplify_points(destination, vertex_positions, vertex_colors, vertex_count, vertex_positions_stride, vertex_colors_stride, color_weight, target_vertex_count)`: Simplify point cloud.
- `simplify_scale(vertex_positions, vertex_count, vertex_positions_stride)`: Get the scale factor for simplification error.

#### Encoding/Decoding

- `encode_vertex_buffer(vertices, vertex_count, vertex_size)`: Encode vertex buffer.
- `encode_index_buffer(indices, index_count, vertex_count)`: Encode index buffer.
- `encode_vertex_version(version)`: Set vertex encoder format version.
- `encode_index_version(version)`: Set index encoder format version.
- `decode_vertex_buffer(destination, vertex_count, vertex_size, buffer)`: Decode vertex buffer.
- `decode_index_buffer(destination, index_count, index_size, buffer)`: Decode index buffer.
- `decode_vertex_version(buffer)`: Get encoded vertex format version.
- `decode_index_version(buffer)`: Get encoded index format version.
- `decode_filter_oct(buffer, count, stride)`: Apply octahedral filter to decoded data.
- `decode_filter_quat(buffer, count, stride)`: Apply quaternion filter to decoded data.
- `decode_filter_exp(buffer, count, stride)`: Apply exponential filter to decoded data.

#### Zip File Storage

- `save_encoded_mesh_to_zip(encoded_mesh, zip_path, vertices_filename="vertices.bin", indices_filename="indices.bin", metadata_filename="metadata.json")`: Save an encoded mesh to a zip file.
- `load_encoded_mesh_from_zip(zip_path, vertices_filename="vertices.bin", indices_filename="indices.bin", metadata_filename="metadata.json")`: Load an encoded mesh from a zip file.
- `save_mesh_to_zip(mesh, zip_path, vertices_filename="vertices.bin", indices_filename="indices.bin", metadata_filename="metadata.json")`: Encode and save a mesh to a zip file.
- `load_mesh_from_zip(mesh_class, zip_path, vertices_filename="vertices.bin", indices_filename="indices.bin", metadata_filename="metadata.json")`: Load a mesh from a zip file.

#### Array Compression

- `encode_array(array)`: Encode a numpy array using meshoptimizer's vertex buffer encoding.
- `decode_array(encoded_array)`: Decode an encoded array.
- `save_encoded_array_to_file(encoded_array, file_path)`: Save an encoded array to a file.
- `load_encoded_array_from_file(file_path)`: Load an encoded array from a file.
- `save_array_to_file(array, file_path)`: Encode and save a numpy array to a file.
- `load_array_from_file(file_path)`: Load and decode a numpy array from a file.
- `save_encoded_array_to_zip(encoded_array, zip_path, data_filename="data.bin", metadata_filename="metadata.json")`: Save an encoded array to a zip file.
- `load_encoded_array_from_zip(zip_path, data_filename="data.bin", metadata_filename="metadata.json")`: Load an encoded array from a zip file.
- `save_array_to_zip(array, zip_path, data_filename="data.bin", metadata_filename="metadata.json")`: Encode and save a numpy array to a zip file.
- `load_array_from_zip(zip_path, data_filename="data.bin", metadata_filename="metadata.json")`: Load and decode a numpy array from a zip file.
- `save_arrays_to_zip(arrays, zip_path)`: Encode and save multiple numpy arrays to a zip file.
- `load_arrays_from_zip(zip_path)`: Load and decode multiple numpy arrays from a zip file.

## License

MIT License