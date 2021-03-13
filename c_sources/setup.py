import platform
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options

is_linux = platform.architecture()[1] == "ELF" or platform.system() == "Linux"
is_windows = platform.architecture()[1] == "WindowsPE" or platform.system() == "Windows"

name = 'MacOS'
if is_linux:
    name = 'linux'
elif is_windows:
    name = 'win'

os_name = platform.architecture()[1]
Cython.Compiler.Options.annotate = True
module_name = 'core'

if os_name == "win":
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast']
    )]

elif os_name == "linux":
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['-O3', '-msse4.2', '-ffast-math', '-fno-builtin','-fopenmp'],
        extra_link_args=['-lm','-fopenmp']
    )]
else:
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['-march=x86-64','-msse4.2', '-O3','-ffast-math','-fopenmp'],
        extra_link_args=['-lm','-fopenmp']
    )]

setup(
    name = 'Molecular script',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
