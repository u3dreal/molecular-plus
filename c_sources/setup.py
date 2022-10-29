import platform
from setuptools import Extension, setup
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
        extra_compile_args=['-msse4.2', '-O3', '-ffast-math', '-fno-builtin','-arch','arm64','-arch','arm64e','-arch','x86_64', '-Xclang', '-fopenmp', '-isystem./openmp/include'],
        extra_link_args=['-lm', '-L./openmp/lib', '-lomp', '-arch','arm64', '-arch','arm64e','-arch','x86_64']
    )]

setup(
    name = 'Molecular script',
    ext_modules=cythonize(ext_modules)
)
