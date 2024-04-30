import sys
#from molecular import bl_info
from os import chdir, path, getcwd, system, remove, rename
import shutil
import platform
from subprocess import Popen, PIPE

is_linux = platform.system() == "Linux"
is_windows = platform.system() == "Windows"

# in python 3.8.x, sys.abiflags attribute doesnt seem to exist any more instead of returning empty string.
# so better check for existence here before accessing it.
abiflags = ''
if hasattr(sys, 'abiflags'):
    abiflags = sys.abiflags

v = str(sys.version_info.major) + str(sys.version_info.minor) + abiflags

name = 'macos'
if is_linux:
    name = 'linux'
elif is_windows:
    name = 'win'
    
if is_windows:
    cwd = getcwd()
    
    # Get the parent directory
    parent_dir = path.dirname(cwd)

    # Construct the path to the 'c_sources' directory
    path_to_c_sources = path.join(parent_dir, "c_sources")
    chdir(path_to_c_sources)
else:
    chdir(getcwd() + "//c_sources")

# TODO, blenders (or a compatible) python bin needs to be in $PATH, and if you use blender's you need to copy the python includes from SVN
# into the include folder of blenders python, too

#version = '.'.join(map(str, bl_info['version']))

with Popen([sys.executable, "setup.py", "build_ext", "--inplace"], stdout=PIPE) as proc:
    proc.stdout.read()

    if is_linux:  # TODO, test
        shutil.move("core.cpython-{}-x86_64-linux-gnu.so".format(v),
                    "..//core.cpython-{}-x86_64-linux-gnu.so".format(v))
    elif is_windows:
        shutil.move("core.cp{}-win_amd64.pyd".format(v), "..//core.cp{}-win_amd64.pyd".format(v))
    else:
        shutil.move("core.cpython-{}-darwin.so".format(v), "..//core.cpython-{}-darwin.so".format(v))

    #chdir("..")

    # molfiles = (
    # "__init__.py", "_version.py", "creators.py", "descriptions.py", "names.py", "operators.py", "properties.py",
    # "simulate.py", "ui.py", "utils.py", "core.cpython*.so", "core.cpython*.pyd", 'core.cpython-{}-darwin.so'.format(v), 'core.cp{}-win_amd64.pyd'.format(v), 'core.cpython-{}-x86_64-linux-gnu.so'.format(v))
    #
    # with ZipFile('molecular-plus_{}_'.format(version) + '{}_'.format(v) + name + '.zip', 'w') as z:
    #     for root, _, files in walk('molecular'):
    #         for file in files:
    #             if file not in molfiles:
    #                 continue
    #             z.write(path.join(root, file), compress_type=ZIP_DEFLATED)
    # # cleanup
    # chdir(getcwd() + "//molecular")
    # try:
    #     if is_linux:
    #         remove("core.cpython-{}-x86_64-linux-gnu.so".format(v))
    #     elif is_windows:
    #         remove("core.cp{}-win_amd64.pyd".format(v))
    #     else:
    #         remove("core.cpython-{}-darwin.so".format(v))
    # except:
    #     pass
    # chdir("..")
    # chdir(getcwd() + "//c_sources")

    chdir("..")

#print(version)

system("/Users/drquader/Desktop/Blender.app/Contents/MacOS/Blender")