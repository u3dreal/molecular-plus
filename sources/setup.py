import platform
from distutils.core import setup
from Cython.Distutils import build_ext, Extension
import Cython.Compiler.Options


os_name = platform.architecture()[1]
Cython.Compiler.Options.annotate = True
module_name = 'core'

if os_name == "WindowsPE":
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast'],
        cython_directives={'language_level' : "3"}
    )]
else:
    ext_modules = [Extension(
        module_name,
        ['core' + '.pyx'],
        extra_compile_args=['-O3','-msse4.2','-ffast-math','-fno-builtin'],
        extra_link_args=['-lm'],
        cython_directives={'language_level' : "3"}
    )]

setup(
    name = 'Molecular script',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
