import os, shutil, platform
from setuptools import Extension, setup
import Cython.Compiler.Options
from Cython.Build import cythonize

DEBUG_MODE = False

os_name = platform.system()

# Check if Build exists then remove it
if os.path.exists('build'):
    shutil.rmtree('build')

# Check if compiled core.* exists then remove it
if os.path.isfile('core.html'):
    os.remove('core.html')
if os.path.isfile('core.c'):
    os.remove('core.c')

filenames = ['simulate.pyx', 'update.pyx', 'init.pyx', 'links.pyx', 'kdtree.pyx',
             'collide.pyx', 'memory.pyx', 'utils.pyx', 'structures.pyx']

with open('core.pyx', 'w') as outfile:
    # This will clear the file before writing to it
    outfile.truncate(0)
    for fname in filenames:
        with open(fname) as infile:
            outfile.write(infile.read())
            outfile.write('\n')  # Add a newline character at the end of each file

Cython.Compiler.Options.annotate = True
module_name = 'core'

if not DEBUG_MODE:
    if os_name == "Windows":
        ext_modules = [Extension(
            module_name,
            ['core.pyx'],
            extra_compile_args=['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast']#['/Ox','/openmp:llvm','/GT','/arch:SSE2','/fp:fast', '/wd4244', '/MD']
        )]

    elif os_name == "Linux":
        ext_modules = [Extension(
            module_name,
            ['core.pyx'],
            extra_compile_args=['-O3', '-msse4.2', '-ffast-math', '-fno-builtin','-fopenmp'],
            extra_link_args=['-lm','-fopenmp']
        )]
    elif os_name == "Darwin":
        ext_modules = [Extension(
            module_name,
            ['core.pyx'],
            extra_compile_args=['-msse4.2', '-O3', '-ffast-math', '-fno-builtin', '-arch', 'x86_64', '-Xclang', '-fopenmp', '-isystem./openmp/x86_64/include'],
            extra_link_args=['-lm', '-L./openmp/x86_64/lib', '-lomp', '-arch', 'x86_64']
        )]
else:
    if os_name == "Windows":
        ext_modules = [Extension(
            module_name,
            ['core.pyx'],
            extra_compile_args=['/O0','/openmp','/GT','/arch:SSE2','/fp:fast']#['/Zi', '/O0','/openmp:llvm', '/MD']
        )]

    elif os_name == "Linux":
        ext_modules = [Extension(
            module_name,
            ['core.pyx'],
            extra_compile_args=['-O3', '-g','-fopenmp'],
            extra_link_args=['-lm','-fopenmp']
        )]
    elif os_name == "Darwin":
        ext_modules = [Extension(
            module_name,
            ['core.pyx'],
            extra_compile_args=['-msse4.2', '-O0', '-g', '-arch', 'x86_64', '-Xclang', '-fopenmp', '-isystem./openmp/x86_64/include'],
            extra_link_args=['-lm', '-L./openmp/x86_64/lib', '-lomp', '-arch', 'x86_64']
        )]

setup(
    name = 'Molecular script',
    ext_modules=cythonize(ext_modules)
)

# Delete the files after the build
if os.path.isfile('core.html'):
    os.remove('core.html')
if os.path.isfile('core.c'):
    os.remove('core.c')

if not DEBUG_MODE:
    if os.path.isfile('core.pyx'):
        os.remove('core.pyx')