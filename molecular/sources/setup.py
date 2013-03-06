from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options 

Cython.Compiler.Options.annotate = True

ext_modules = [Extension("cmolcore", ["cmolcore.pyx"],extra_compile_args=['-march=i686'])]
#ext_modules = [Extension("cmolcore", ["cmolcore.pyx"],extra_compile_args=['-march=i686','-O3','-ffast-math'])]

setup(
  name = 'Molecular script',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
