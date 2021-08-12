import platform
from setuptools import Extension, setup
#from distutils.core import setup
#from distutils.extension import Extension
#from Cython.Distutils import build_ext
import Cython.Compiler.Options
from Cython.Build import cythonize

os_name = platform.system()

Cython.Compiler.Options.annotate = True
module_name = 'core'

if os_name == "Windows":
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast']
    )]

elif os_name == "Linux":
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['-O3', '-msse4.2', '-ffast-math', '-fno-builtin','-fopenmp'],
        extra_link_args=['-lm','-fopenmp']
    )]
elif os_name == "Darwin":
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['-msse4.2', '-O3','-ffast-math', '-Xclang', '-fopenmp'],
        extra_link_args=['-lomp']
    )]

setup(
    name = 'Molecular script',
#    cmdclass = {'build_ext': build_ext},
#    ext_modules = ext_modules
    ext_modules=cythonize(ext_modules)
)
