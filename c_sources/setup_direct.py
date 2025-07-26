#!/usr/bin/env python3
"""
Setup script to compile the direct memory access Cython module
"""

import os
import sys
import platform
from setuptools import Extension, setup
from Cython.Build import cythonize
import Cython.Compiler.Options

# Enable Cython optimizations
Cython.Compiler.Options.annotate = True

def get_optimized_flags():
    """Get CPU-specific optimization flags"""
    os_name = platform.system()
    
    base_flags = ['-O3', '-ffast-math', '-funroll-loops', '-fomit-frame-pointer', '-DNDEBUG']
    
    if os_name == "Darwin":
        base_flags.extend(['-march=native', '-mavx2', '-mfma'])
    elif os_name == "Linux":
        base_flags.extend(['-march=native', '-mavx2', '-mfma'])
    elif os_name == "Windows":
        base_flags = ['/Ox', '/arch:AVX2', '/fp:fast']
    
    return base_flags

def main():
    print("Compiling Direct Memory Access Cython Module...")
    
    # Get optimization flags
    opt_flags = get_optimized_flags()
    os_name = platform.system()
    
    # Configure extension
    if os_name == "Windows":
        ext_modules = [Extension(
            "simulate_direct",
            ["simulate_direct.pyx"],
            extra_compile_args=opt_flags + ['/openmp'],
            extra_link_args=['/LTCG']
        )]
    elif os_name == "Darwin":
        # macOS - use pthreads for parallel processing
        ext_modules = [Extension(
            "simulate_direct",
            ["simulate_direct.pyx"],
            extra_compile_args=opt_flags + ['-pthread'],
            extra_link_args=['-lm', '-lpthread']
        )]
    else:
        # Linux
        ext_modules = [Extension(
            "simulate_direct",
            ["simulate_direct.pyx"],
            extra_compile_args=opt_flags + ['-fopenmp'],
            extra_link_args=['-lm', '-fopenmp']
        )]
    
    # Build the extension
    setup(
        name='simulate_direct',
        ext_modules=cythonize(ext_modules, compiler_directives={
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'initializedcheck': False,
            'overflowcheck': False,
            'profile': False
        }),
        zip_safe=False,
    )
    
    print("Compilation complete!")

if __name__ == "__main__":
    main()