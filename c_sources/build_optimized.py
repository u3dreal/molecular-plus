#!/usr/bin/env python3
"""
Optimized build script for Molecular particle solver
This script provides advanced compiler optimizations for maximum performance
"""

import os
import shutil
import platform
import subprocess
import sys
from setuptools import Extension, setup
import Cython.Compiler.Options
from Cython.Build import cythonize

def get_cpu_info():
    """Detect CPU features for optimal compilation"""
    try:
        if platform.system() == "Linux":
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return cpuinfo
        elif platform.system() == "Darwin":
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.features'], 
                                  capture_output=True, text=True)
            return result.stdout
    except:
        return ""

def get_optimized_flags():
    """Get CPU-specific optimization flags"""
    os_name = platform.system()
    cpu_info = get_cpu_info().upper()
    
    base_flags = ['-O3', '-ffast-math', '-fno-builtin', '-funroll-loops', 
                  '-fomit-frame-pointer', '-DNDEBUG']
    
    # Add CPU-specific optimizations
    if 'AVX512' in cpu_info:
        base_flags.extend(['-mavx512f', '-mavx512cd'])
    elif 'AVX2' in cpu_info:
        base_flags.extend(['-mavx2', '-mfma'])
    elif 'AVX' in cpu_info:
        base_flags.append('-mavx')
    
    if 'SSE4_2' in cpu_info or 'SSE4.2' in cpu_info:
        base_flags.append('-msse4.2')
    elif 'SSE4_1' in cpu_info or 'SSE4.1' in cpu_info:
        base_flags.append('-msse4.1')
    
    # Add march=native for best performance on target machine
    base_flags.extend(['-march=native', '-mtune=native'])
    
    return base_flags

def get_version_from_init():
    """Extract version from __init__.py bl_info"""
    try:
        # Read __init__.py from addon directory
        with open('../addon/__init__.py', 'r') as f:
            content = f.read()
        
        # Find the bl_info dictionary and extract version
        import re
        version_match = re.search(r'"version":\s*\((\d+),\s*(\d+),\s*(\d+)\)', content)
        if version_match:
            major, minor, patch = version_match.groups()
            return f"{major}.{minor}.{patch}"
        else:
            print("⚠️  Could not extract version from __init__.py, using fallback")
            return "1.18.0"
    except Exception as e:
        print(f"⚠️  Error reading version from __init__.py: {e}")
        return "1.18.0"

def build_optimized():
    """Build with maximum optimizations"""
    # Get version from __init__.py (single source of truth)
    version = get_version_from_init()
    core_version = f"{version}.1"
    print(f"Building version: {version} (core: {core_version})")
    
    DEBUG_MODE = False
    os_name = platform.system()
    
    print(f"Building optimized molecular core for {os_name}")
    print("Detected CPU features:", get_cpu_info()[:100] + "...")
    
    # Clean previous builds
    for path in ['build', 'molecular_core', 'molecular_core.egg-info']:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    # Clean compiled files
    for file in ['core.html', 'core.c']:
        if os.path.isfile(file):
            os.remove(file)
    
    # Create molecular_core directory
    os.mkdir("./molecular_core")
    shutil.copy("__init__.py", "./molecular_core/__init__.py")
    
    # Copy OpenMP library for macOS
    if os_name == "Darwin":
        if os.path.exists("./openmp/x86_64/lib/libomp.dylib"):
            shutil.copyfile("./openmp/x86_64/lib/libomp.dylib", 
                           "./molecular_core/libomp.dylib")
            print("OpenMP library copied to molecular_core/")
    
    # Combine all Cython files
    filenames = ['simulate.pyx', 'update.pyx', 'init.pyx', 'links.pyx', 
                'kdtree.pyx', 'collide.pyx', 'memory.pyx', 'utils.pyx', 'structures.pyx']
    
    with open('./molecular_core/core.pyx', 'w') as outfile:
        outfile.truncate(0)
        for fname in filenames:
            with open(fname) as infile:
                outfile.write(infile.read())
                outfile.write('\n')
    
    # Enable Cython optimizations
    Cython.Compiler.Options.annotate = True
    module_name = 'molecular_core.core'
    
    # Get optimized compiler flags
    opt_flags = get_optimized_flags()
    
    if os_name == "Windows":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=['/Ox', '/openmp', '/GT', '/arch:AVX2', '/fp:fast', '/GL'],
            extra_link_args=['/LTCG']
        )]
    elif os_name == "Linux":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=opt_flags + ['-fopenmp', '-flto'],
            extra_link_args=['-lm', '-fopenmp', '-flto']
        )]
    elif os_name == "Darwin":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=opt_flags + ['-arch', 'x86_64', '-Xclang', '-fopenmp', 
                                          '-isystem./openmp/x86_64/include'],
            extra_link_args=['-lm', '-L./openmp/x86_64/lib', '-lomp', 
                           '-arch', 'x86_64', '-Wl,-rpath,@loader_path']
        )]
    
    # Build the extension
    setup(
        name='molecular_core',
        version=core_version,
        ext_modules=cythonize(ext_modules, compiler_directives={
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'initializedcheck': False,
            'overflowcheck': False,
            'profile': False
        }),
        packages=["molecular_core"],
        package_data={"molecular_core": ["libomp.dylib"]} if os_name == "Darwin" else [],
        zip_safe=False,
    )
    
    # Keep OpenMP library for runtime - don't remove it
    # if os_name == "Darwin" and os.path.exists("molecular_core/libomp.dylib"):
    #     os.remove("molecular_core/libomp.dylib")
    
    for file in ['core.html', 'core.c']:
        if os.path.isfile(file):
            os.remove(file)
    
    print("Optimized build completed successfully!")

if __name__ == "__main__":
    build_optimized()