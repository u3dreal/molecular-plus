import sys
import platform
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options 

Cython.Compiler.Options.annotate = True

bit_depth = platform.architecture()[0]

if sys.version_info.major == 3 and sys.version_info.minor == 5 and bit_depth == '64bit':
    module_name = 'core_35_64'
elif sys.version_info.major == 3 and sys.version_info.minor == 7 and bit_depth == '64bit':
    module_name = 'core_37_64'
elif sys.version_info.major == 3 and sys.version_info.minor == 5 and bit_depth == '32bit':
    module_name = 'core_35_32'
elif sys.version_info.major == 3 and sys.version_info.minor == 7 and bit_depth == '32bit':
    module_name = 'core_37_32'
else:
    raise BaseException('Unsupported python version')

ext_modules = [Extension(module_name, ['core' + '.pyx'],extra_compile_args=['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast'])]

setup(
name = 'Molecular script',
cmdclass = {'build_ext': build_ext},
ext_modules = ext_modules
)
