import os, shutil, platform
from setuptools import Extension, setup
import Cython.Compiler.Options
from Cython.Build import cythonize

core_version = "1.20.2"

DEBUG_MODE = False

os_name = platform.system()

# Check if Build exists then remove it
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('molecular_core'):
    shutil.rmtree('molecular_core')
    shutil.rmtree('molecular_core.egg-info')

# Check if compiled core.* exists then remove it
if os.path.isfile('core.html'):
    os.remove('core.html')
if os.path.isfile('core.c'):
    os.remove('core.c')

os.mkdir("./molecular_core")
shutil.copy("__init__.py", "./molecular_core/__init__.py")
# Copy libomp.dylib to molecular_plus_core/ if needed

if os_name == "Darwin":
    shutil.copyfile(
        "/opt/homebrew/opt/libomp/lib/libomp.dylib",
        "./molecular_core/libomp.dylib"
    )

filenames = ['simulate.pyx', 'update.pyx', 'init.pyx', 'links.pyx', 'kdtree.pyx',
             'collide.pyx', 'memory.pyx', 'utils.pyx', 'structures.pyx']

with open('./molecular_core/core.pyx', 'w') as outfile:
    # This will clear the file before writing to it
    outfile.truncate(0)
    for fname in filenames:
        with open(fname) as infile:
            outfile.write(infile.read())
            outfile.write('\n')  # Add a newline character at the end of each file

Cython.Compiler.Options.annotate = True
module_name = 'molecular_core.core'

if not DEBUG_MODE:
    if os_name == "Windows":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast', '/wd4244', '/MD']
        )]

    elif os_name == "Linux":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=['-O3', '-msse4.2', '-ffast-math', '-fno-builtin','-fopenmp'],
            extra_link_args=['-lm','-fopenmp']
        )]
    elif os_name == "Darwin":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=['-O3', '-ffast-math', '-fno-builtin', '-arch', 'arm64', '-Xclang', '-fopenmp', '-isystem/opt/homebrew/opt/libomp/include'],
            extra_link_args=['-lm', '-L/opt/homebrew/opt/libomp/lib', '-lomp', '-arch', 'arm64', '-Wl,-rpath,@executable_path']
        )]
else:
    if os_name == "Windows":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=['/Zi', '/O0','/openmp', '/MD']
        )]

    elif os_name == "Linux":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=['-O3', '-g','-fopenmp'],
            extra_link_args=['-lm','-fopenmp']
        )]
    elif os_name == "Darwin":
        ext_modules = [Extension(
            module_name,
            ['molecular_core/core.pyx'],
            extra_compile_args=['-O0', '-g', '-arch', 'arm64', '-Xclang', '-fopenmp', '-isystem/opt/homebrew/opt/libomp/include'],
            extra_link_args=['-lm', '-L/opt/homebrew/opt/libomp/lib', '-lomp', '-arch', 'arm64', '-Wl,-rpath,@executable_path']
        )]

setup(
    name = 'molecular_core',
    version = core_version,
    ext_modules=cythonize(ext_modules),
    packages=["molecular_core"],
    package_data={"molecular_core": ["libomp.dylib"]} if os_name == "Darwin" else [],
    zip_safe=False,
)

# Delete the files after the build
if os_name == "Darwin" and os.path.exists("molecular_core/libomp.dylib"):
    os.remove("molecular_core/libomp.dylib")

if os.path.isfile('core.html'):
    os.remove('core.html')
if os.path.isfile('core.c'):
    os.remove('core.c')

if not DEBUG_MODE:
    if os.path.isfile('core.pyx'):
        os.remove('core.pyx')
