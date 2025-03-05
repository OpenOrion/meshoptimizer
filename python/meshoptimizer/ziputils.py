"""
Utilities for storing encoded meshes and arrays in zip files.

This module provides functions for storing and loading encoded meshes and arrays in zip files,
where binary data is stored as binary files and metadata is stored as JSON.
"""
import json
import zipfile
from io import BytesIO
from typing import Optional, Union, Dict, Any, Tuple, List
import os
import numpy as np

from .data import EncodedMesh
from .arrayutils import EncodedArray

def save_encoded_mesh_to_zip(encoded_mesh: EncodedMesh, 
                            zip_path: str, 
                            vertices_filename: str = "vertices.bin",
                            indices_filename: str = "indices.bin",
                            metadata_filename: str = "metadata.json") -> None:
    """
    Save an encoded mesh to a zip file.
    
    Args:
        encoded_mesh: EncodedMesh object to save
        zip_path: Path to the output zip file
        vertices_filename: Name of the vertices binary file within the zip (default: "vertices.bin")
        indices_filename: Name of the indices binary file within the zip (default: "indices.bin")
        metadata_filename: Name of the metadata JSON file within the zip (default: "metadata.json")
    """
    # Create metadata dictionary
    metadata = {
        "vertex_count": encoded_mesh.vertex_count,
        "vertex_size": encoded_mesh.vertex_size,
        "index_size": encoded_mesh.index_size,
    }
    
    # Add index_count to metadata if it exists
    if encoded_mesh.index_count is not None:
        metadata["index_count"] = encoded_mesh.index_count
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Write vertices binary file
        zipf.writestr(vertices_filename, encoded_mesh.vertices)
        
        # Write indices binary file if it exists
        if encoded_mesh.indices is not None:
            zipf.writestr(indices_filename, encoded_mesh.indices)
        
        # Write metadata JSON file
        zipf.writestr(metadata_filename, json.dumps(metadata, indent=2))

def load_encoded_mesh_from_zip(zip_path: str,
                              vertices_filename: str = "vertices.bin",
                              indices_filename: str = "indices.bin",
                              metadata_filename: str = "metadata.json") -> EncodedMesh:
    """
    Load an encoded mesh from a zip file.
    
    Args:
        zip_path: Path to the input zip file
        vertices_filename: Name of the vertices binary file within the zip (default: "vertices.bin")
        indices_filename: Name of the indices binary file within the zip (default: "indices.bin")
        metadata_filename: Name of the metadata JSON file within the zip (default: "metadata.json")
        
    Returns:
        EncodedMesh object loaded from the zip file
    """
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        # Read metadata JSON file
        with zipf.open(metadata_filename) as f:
            metadata = json.load(f)
        
        # Read vertices binary file
        with zipf.open(vertices_filename) as f:
            vertices = f.read()
        
        # Read indices binary file if it exists
        indices = None
        if indices_filename in zipf.namelist():
            with zipf.open(indices_filename) as f:
                indices = f.read()
        
        # Create EncodedMesh object
        return EncodedMesh(
            vertices=vertices,
            indices=indices,
            vertex_count=metadata["vertex_count"],
            vertex_size=metadata["vertex_size"],
            index_count=metadata.get("index_count"),  # Use get() to handle optional field
            index_size=metadata["index_size"]
        )

def save_mesh_to_zip(mesh, 
                    zip_path: str, 
                    vertices_filename: str = "vertices.bin",
                    indices_filename: str = "indices.bin",
                    metadata_filename: str = "metadata.json") -> None:
    """
    Encode and save a mesh to a zip file.
    
    Args:
        mesh: Mesh object to encode and save
        zip_path: Path to the output zip file
        vertices_filename: Name of the vertices binary file within the zip (default: "vertices.bin")
        indices_filename: Name of the indices binary file within the zip (default: "indices.bin")
        metadata_filename: Name of the metadata JSON file within the zip (default: "metadata.json")
    """
    encoded_mesh = mesh.encode()
    save_encoded_mesh_to_zip(
        encoded_mesh, 
        zip_path, 
        vertices_filename, 
        indices_filename, 
        metadata_filename
    )

def load_mesh_from_zip(mesh_class,
                       zip_path: str,
                       vertices_filename: str = "vertices.bin",
                       indices_filename: str = "indices.bin",
                       metadata_filename: str = "metadata.json"):
    """
    Load a mesh from a zip file.
    
    Args:
        mesh_class: Class to use for creating the mesh (e.g., Mesh)
        zip_path: Path to the input zip file
        vertices_filename: Name of the vertices binary file within the zip (default: "vertices.bin")
        indices_filename: Name of the indices binary file within the zip (default: "indices.bin")
        metadata_filename: Name of the metadata JSON file within the zip (default: "metadata.json")
        
    Returns:
        Mesh object loaded from the zip file
    """
    encoded_mesh = load_encoded_mesh_from_zip(
        zip_path,
        vertices_filename,
        indices_filename,
        metadata_filename
    )
    return mesh_class.decode(encoded_mesh)


def save_combined_data_to_zip(
    encoded_mesh: EncodedMesh,
    encoded_arrays: Dict[str, EncodedArray],
    metadata: Optional[Dict[str, Any]] = None,
    zip_path: str = "combined_data.zip",
    mesh_dir: str = "mesh",
    arrays_dir: str = "arrays"
) -> None:
    """
    Save an encoded mesh and multiple encoded arrays to a single zip file with organized directory structure.
    
    This function creates a zip file with the following structure:
    - mesh/vertices.bin: Encoded mesh vertices
    - mesh/indices.bin: Encoded mesh indices
    - mesh/metadata.json: Mesh metadata
    - arrays/[array_name].bin: Encoded array data for each array
    - arrays/metadata.json: Metadata for all arrays
    - metadata.json: General metadata (optional)
    
    Args:
        encoded_mesh: EncodedMesh object to save
        encoded_arrays: Dictionary mapping array names to EncodedArray objects
        metadata: Optional general metadata to include in the zip file
        zip_path: Path to the output zip file (default: "combined_data.zip")
        mesh_dir: Directory name for mesh data within the zip (default: "mesh")
        arrays_dir: Directory name for array data within the zip (default: "arrays")
        
    Raises:
        ValueError: If encoded_mesh is None or encoded_arrays is empty
        IOError: If there's an error writing to the zip file
    """
    # Validate inputs
    if encoded_mesh is None:
        raise ValueError("encoded_mesh cannot be None")
    
    if not encoded_arrays:
        raise ValueError("encoded_arrays dictionary cannot be empty")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Save the encoded mesh
            zipf.writestr(f"{mesh_dir}/vertices.bin", encoded_mesh.vertices)
            zipf.writestr(f"{mesh_dir}/indices.bin", encoded_mesh.indices)
            
            # Save mesh metadata
            mesh_metadata = {
                "vertex_count": encoded_mesh.vertex_count,
                "vertex_size": encoded_mesh.vertex_size,
                "index_count": encoded_mesh.index_count,
                "index_size": encoded_mesh.index_size
            }
            zipf.writestr(f"{mesh_dir}/metadata.json", json.dumps(mesh_metadata, indent=2))
            
            # Save the encoded arrays
            arrays_metadata = {}
            for name, encoded_array in encoded_arrays.items():
                # Save array data
                zipf.writestr(f"{arrays_dir}/{name}.bin", encoded_array.data)
                
                # Add to metadata
                arrays_metadata[name] = {
                    "shape": encoded_array.shape,
                    "dtype": str(encoded_array.dtype),
                    "itemsize": encoded_array.itemsize
                }
            
            # Save array metadata
            zipf.writestr(f"{arrays_dir}/metadata.json", json.dumps(arrays_metadata, indent=2))
            
            # Save general metadata if provided
            if metadata is not None:
                zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
                
        return True
    except Exception as e:
        raise IOError(f"Error saving combined data to zip file: {str(e)}")


def load_combined_data_from_zip(
    zip_path: str,
    mesh_dir: str = "mesh",
    arrays_dir: str = "arrays"
) -> Tuple[EncodedMesh, Dict[str, EncodedArray], Optional[Dict[str, Any]]]:
    """
    Load an encoded mesh and multiple encoded arrays from a zip file.
    
    Args:
        zip_path: Path to the input zip file
        mesh_dir: Directory name for mesh data within the zip (default: "mesh")
        arrays_dir: Directory name for array data within the zip (default: "arrays")
        
    Returns:
        Tuple containing:
        - EncodedMesh object
        - Dictionary mapping array names to EncodedArray objects
        - General metadata dictionary (or None if not present)
        
    Raises:
        FileNotFoundError: If the zip file doesn't exist
        ValueError: If the zip file doesn't contain the expected structure
        IOError: If there's an error reading from the zip file
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Load mesh data
            mesh_vertices_data = zipf.read(f"{mesh_dir}/vertices.bin")
            mesh_indices_data = zipf.read(f"{mesh_dir}/indices.bin")
            mesh_metadata = json.loads(zipf.read(f"{mesh_dir}/metadata.json"))
            
            # Create EncodedMesh object
            encoded_mesh = EncodedMesh(
                vertices=mesh_vertices_data,
                indices=mesh_indices_data,
                vertex_count=mesh_metadata["vertex_count"],
                vertex_size=mesh_metadata["vertex_size"],
                index_count=mesh_metadata["index_count"],
                index_size=mesh_metadata["index_size"]
            )
            
            # Load array metadata
            arrays_metadata = json.loads(zipf.read(f"{arrays_dir}/metadata.json"))
            
            # Load array data
            encoded_arrays = {}
            for name, metadata in arrays_metadata.items():
                array_data = zipf.read(f"{arrays_dir}/{name}.bin")
                
                encoded_arrays[name] = EncodedArray(
                    data=array_data,
                    shape=tuple(metadata["shape"]),
                    dtype=np.dtype(metadata["dtype"]),
                    itemsize=metadata["itemsize"]
                )
            
            # Load general metadata if present
            general_metadata = None
            try:
                general_metadata = json.loads(zipf.read("metadata.json"))
            except KeyError:
                # Metadata file not found, that's okay
                pass
            
            return encoded_mesh, encoded_arrays, general_metadata
    except zipfile.BadZipFile:
        raise ValueError(f"Invalid zip file: {zip_path}")
    except KeyError as e:
        raise ValueError(f"Missing expected file in zip: {str(e)}")
    except Exception as e:
        raise IOError(f"Error loading combined data from zip file: {str(e)}")