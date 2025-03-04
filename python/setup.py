from setuptools import setup, Extension, find_packages, Distribution
import os
import platform
import sys
import re
import shutil
from setuptools.command.build_ext import build_ext

# Read long description from README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, "r", encoding="utf-8") as f:
    long_description = f.read()

# List of source files needed for the extension
source_files = [
    'allocator.cpp',
    'clusterizer.cpp',
    'indexcodec.cpp',
    'indexgenerator.cpp',
    'overdrawanalyzer.cpp',
    'overdrawoptimizer.cpp',
    'simplifier.cpp',
    'spatialorder.cpp',
    'stripifier.cpp',
    'vcacheanalyzer.cpp',
    'vcacheoptimizer.cpp',
    'vertexcodec.cpp',
    'vertexfilter.cpp',
    'vfetchanalyzer.cpp',
    'vfetchoptimizer.cpp',
    'quantization.cpp',
    'partition.cpp',
]

# Custom build_ext command to copy source files
class CopySourceBuildExt(build_ext):
    def run(self):
        # Create src directory in the build directory
        src_dir = os.path.join(self.build_temp, 'src')
        os.makedirs(src_dir, exist_ok=True)
        
        # Copy source files from parent directory
        parent_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
        for src_file in source_files:
            src_path = os.path.join(parent_src_dir, src_file)
            dst_path = os.path.join(src_dir, src_file)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                raise RuntimeError(f"Source file not found: {src_path}")
        
        # Also copy the header file
        header_path = os.path.join(parent_src_dir, 'meshoptimizer.h')
        if os.path.exists(header_path):
            shutil.copy2(header_path, os.path.join(src_dir, 'meshoptimizer.h'))
        else:
            raise RuntimeError(f"Header file not found: {header_path}")
        
        # Run the original build_ext command
        super().run()

# Read version from package or use a default
def get_version():
    try:
        # Try to read version from meshoptimizer.h
        header_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'meshoptimizer.h'))
        with open(header_path, 'r') as f:
            content = f.read()
            version_match = re.search(r'#define\s+MESHOPTIMIZER_VERSION\s+(\d+)', content)
            if version_match:
                version = int(version_match.group(1))
                major = version // 10000
                minor = (version // 100) % 100
                patch = version % 100
                return f"{major}.{minor}.{patch}"
    except:
        pass
    return '0.1.0'  # Default version if unable to extract

# Get long description from README
def get_long_description():
    try:
        readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
        with open(readme_path, 'r') as f:
            return f.read()
    except:
        return 'Python wrapper for meshoptimizer library'

# Platform-specific compile arguments
extra_compile_args = ['-std=c++11']
if platform.system() != 'Windows':
    extra_compile_args.append('-fPIC')
if platform.system() == 'Darwin':
    extra_compile_args.extend(['-stdlib=libc++', '-mmacosx-version-min=10.9'])

# Define the extension module
meshoptimizer_module = Extension(
    'meshoptimizer._meshoptimizer',
    sources=['src/' + f for f in source_files],  # Use relative paths with src/ prefix
    include_dirs=['src'],  # Use relative path to src directory
    extra_compile_args=extra_compile_args,
    language='c++',
)

# Custom Distribution to include C++ source files
class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True

setup(
    name='meshoptimizer',
    version=get_version(),
    description='Python wrapper for meshoptimizer library',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/zeux/meshoptimizer',
    packages=find_packages(),
    ext_modules=[meshoptimizer_module],
    cmdclass={
        'build_ext': CopySourceBuildExt,
    },
    distclass=BinaryDistribution,
    install_requires=[
        'numpy>=1.19.0',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='mesh optimization graphics 3d',
)