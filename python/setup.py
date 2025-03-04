from setuptools import setup, Extension, find_packages, Distribution
import os
import platform
import re
import shutil
from pathlib import Path
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist

# Environment setup
IN_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') == 'true'
ROOT_DIR = Path(__file__).parent
PARENT_SRC_DIR = ROOT_DIR.parent.joinpath('src')
LOCAL_SRC_DIR = Path('src')

# Source files needed for the extension - define explicitly to avoid issues
SOURCE_FILES = [
    'allocator.cpp', 'clusterizer.cpp', 'indexcodec.cpp', 'indexgenerator.cpp',
    'overdrawanalyzer.cpp', 'overdrawoptimizer.cpp', 'simplifier.cpp',
    'spatialorder.cpp', 'stripifier.cpp', 'vcacheanalyzer.cpp',
    'vcacheoptimizer.cpp', 'vertexcodec.cpp', 'vertexfilter.cpp',
    'vfetchanalyzer.cpp', 'vfetchoptimizer.cpp', 'quantization.cpp',
    'partition.cpp',
]

HEADER_FILES = ['meshoptimizer.h']
ALL_CPP_FILES = SOURCE_FILES + HEADER_FILES

# Read long description from README
README_PATH = ROOT_DIR.joinpath("README.md")
try:
    with open(README_PATH, "r", encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
except:
    LONG_DESCRIPTION = "Python wrapper for meshoptimizer library"


def get_version():
    """Extract version from meshoptimizer.h"""
    # Possible locations for meshoptimizer.h
    header_paths = [
        PARENT_SRC_DIR.joinpath('meshoptimizer.h'),
        LOCAL_SRC_DIR.joinpath('meshoptimizer.h')
    ]

    for header_path in header_paths:
        if not header_path.exists():
            continue

        try:
            content = header_path.read_text()
            version_match = re.search(
                r'#define\s+MESHOPTIMIZER_VERSION\s+(\d+)', content)
            if version_match:
                version = int(version_match.group(1))
                major = version // 10000
                minor = (version // 100) % 100
                patch = version % 100
                return f"{major}.{minor}.{patch}"
        except Exception:
            continue

    # Default version if unable to extract
    return '0.1.0'


def copy_cpp_sources(source_dir, target_dir):
    """Copy C++ source files from source_dir to target_dir"""
    if isinstance(target_dir, str):
        target_dir = Path(target_dir)
        
    target_dir.mkdir(exist_ok=True)
    
    # Determine the source directory to use
    if not source_dir.exists():
        # Try alternate path if source_dir doesn't exist
        alt_source_dir = Path('..').joinpath('src')
        if alt_source_dir.exists():
            source_dir = alt_source_dir
        else:
            # If we're building from sdist, files should be in LOCAL_SRC_DIR already
            # If no source files are found, we'll get errors later when trying to build
            return
    
    # Copy all files from source to target
    for src_file in ALL_CPP_FILES:
        src_path = source_dir.joinpath(src_file)
        dst_path = target_dir.joinpath(src_file)
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
        else:
            # Try to find the file in alternate locations before failing
            alt_paths = [
                Path('..').joinpath('src', src_file),
                LOCAL_SRC_DIR.joinpath(src_file)
            ]
            found = False
            for alt_path in alt_paths:
                if alt_path.exists():
                    shutil.copy2(alt_path, dst_path)
                    found = True
                    break
            
            # Only raise an error if file is essential and nowhere to be found
            if not found and src_file in HEADER_FILES:
                raise RuntimeError(f"Essential file not found: {src_file}")


# Shared mixin for common source copying functionality
class SourceCopyMixin:
    """Mixin class providing C++ source file copying functionality"""
    def copy_sources_if_needed(self, target_dir=None):
        """Copy C++ sources if in GitHub Actions and needed"""
        if not IN_GITHUB_ACTIONS:
            return
            
        if target_dir is None:
            target_dir = LOCAL_SRC_DIR
            
        copy_cpp_sources(PARENT_SRC_DIR, target_dir)


class CustomSdist(SourceCopyMixin, sdist):
    """Custom sdist command to include C++ source files"""
    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        self.copy_sources_if_needed(Path(base_dir).joinpath('src'))


class CustomBuildExt(SourceCopyMixin, build_ext):
    """Custom build_ext command to handle source files"""
    def run(self):
        self.copy_sources_if_needed()
        super().run()


# Platform-specific compile arguments
def get_compile_args():
    """Get platform-specific compilation arguments"""
    args = ['-std=c++11']
    
    if platform.system() != 'Windows':
        args.append('-fPIC')
    
    if platform.system() == 'Darwin':
        args.extend(['-stdlib=libc++', '-mmacosx-version-min=10.9'])
    
    return args


# Define the extension module
def get_extension_module():
    """Create the extension module with appropriate paths"""
    compile_args = get_compile_args()
    
    if IN_GITHUB_ACTIONS or not PARENT_SRC_DIR.exists():
        # In GitHub Actions or when building from sdist, use the local src directory
        sources = [str(LOCAL_SRC_DIR.joinpath(f)) for f in SOURCE_FILES]
        include_dirs = [str(LOCAL_SRC_DIR)]
    else:
        # When building locally, use the parent src directory
        sources = [str(PARENT_SRC_DIR.joinpath(f)) for f in SOURCE_FILES]
        include_dirs = [str(PARENT_SRC_DIR)]
    
    return Extension(
        'meshoptimizer._meshoptimizer',
        sources=sources,
        include_dirs=include_dirs,
        extra_compile_args=compile_args,
        language='c++',
    )


class BinaryDistribution(Distribution):
    """Custom Distribution to include C++ source files"""
    def has_ext_modules(self):
        return True


if __name__ == "__main__":
    setup(
        name='meshoptimizer',
        version=get_version(),
        description='Python wrapper for meshoptimizer library',
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        url='https://github.com/zeux/meshoptimizer',
        packages=find_packages(),
        ext_modules=[get_extension_module()],
        cmdclass={
            'build_ext': CustomBuildExt,
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