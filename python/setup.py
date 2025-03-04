from setuptools import setup, Extension, find_packages, Distribution
import os
import platform
import sys
import re
import shutil
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist

# Check if we're running in GitHub Actions
IN_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') == 'true'

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

# Custom sdist command to include C++ source files
class CustomSdist(sdist):
    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        
        # Only include C++ source files in the sdist when in GitHub Actions
        if IN_GITHUB_ACTIONS:
            # Create src directory in the distribution
            src_dir = os.path.join(base_dir, 'src')
            os.makedirs(src_dir, exist_ok=True)
            
            # Copy source files from parent directory
            parent_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
            for src_file in source_files + ['meshoptimizer.h']:
                src_path = os.path.join(parent_src_dir, src_file)
                dst_path = os.path.join(src_dir, src_file)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                else:
                    raise RuntimeError(f"Source file not found: {src_path}")

# Custom build_ext command to handle source files
class GithubActionsBuildExt(build_ext):
    def run(self):
        # Only copy files when in GitHub Actions
        if IN_GITHUB_ACTIONS and not os.path.exists('src'):
            os.makedirs('src', exist_ok=True)
            
            # Copy source files from parent directory
            parent_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
            for src_file in source_files + ['meshoptimizer.h']:
                src_path = os.path.join(parent_src_dir, src_file)
                dst_path = os.path.join('src', src_file)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                elif os.path.exists(os.path.join('..', 'src', src_file)):
                    # Try alternative path
                    alt_src_path = os.path.join('..', 'src', src_file)
                    shutil.copy2(alt_src_path, dst_path)
                else:
                    raise RuntimeError(f"Source file not found: {src_path}")
        
        # Run the original build_ext command
        super().run()

# Read version from package or use a default
def get_version():
    # Try to read version from meshoptimizer.h in parent directory
    try:
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
        # If that fails, try to read from local src directory (when building from sdist)
        try:
            if os.path.exists('src/meshoptimizer.h'):
                with open('src/meshoptimizer.h', 'r') as f:
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
if IN_GITHUB_ACTIONS:
    # In GitHub Actions, use the local src directory
    meshoptimizer_module = Extension(
        'meshoptimizer._meshoptimizer',
        sources=['src/' + f for f in source_files],  # Use relative paths with src/ prefix
        include_dirs=['src'],  # Use relative path to src directory
        extra_compile_args=extra_compile_args,
        language='c++',
    )
else:
    # When building locally, use the parent src directory
    parent_src_dir = os.path.join('..', 'src')
    meshoptimizer_module = Extension(
        'meshoptimizer._meshoptimizer',
        sources=[os.path.join(parent_src_dir, f) for f in source_files],
        include_dirs=[parent_src_dir],
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
        'build_ext': GithubActionsBuildExt,
        'sdist': CustomSdist,
    },
    distclass=BinaryDistribution,
    include_package_data=True,
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