import platform
from setuptools import Extension, setup
#from distutils.core import setup
#from distutils.extension import Extension
#from Cython.Distutils import build_ext
import Cython.Compiler.Options
from Cython.Build import cythonize

os_name = platform.architecture()[1]
print(os_name)

is_linux = os_name == "ELF" or platform.system() == "Linux"
is_windows = os_name == "WindowsPE" or platform.system() == "Windows"

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
        extra_compile_args=['-O3', '-msse4.2', '-ffast-math', '-fno-builtin','-fopenmp','-static'],
        extra_link_args=['-lm','-fopenmp','-static']
    )]
else:
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['-march=x86-64','-msse4.2', '-O3','-ffast-math','-fopenmp','-static'],
        extra_link_args=['-lm','-fopenmp','-static']
    )]

setup(
    name = 'Molecular script',
#    cmdclass = {'build_ext': build_ext},
#    ext_modules = ext_modules
    ext_modules=cythonize(ext_modules)
)
