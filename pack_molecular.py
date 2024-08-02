import sys
from zipfile import ZipFile, ZIP_DEFLATED
from os import path, walk, remove, rmdir, chdir, getcwd, mkdir, rename
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

temp_folder = "molecularplus" + name
mkdir(temp_folder)

pyfiles = (
    "__init__.py", "creators.py", "descriptions.py", "names.py", "operators.py", "properties.py",
    "simulate.py", "ui.py", "utils.py", "addon_prefrences.py")

for file in pyfiles:
    shutil.copy(file, f".//{temp_folder}//{file}")

from molecularplus import bl_info

chdir(getcwd() + "//c_sources")

# TODO, blenders (or a compatible) python bin needs to be in $PATH, and if you use blender's you need to copy the python includes from SVN
# into the include folder of blenders python, too

version = '.'.join(map(str, bl_info['version']))

with Popen([sys.executable, "setup.py", "build_ext", "--inplace"], stdout=PIPE) as proc:
    proc.stdout.read()

    if is_linux:  # TODO, test
        shutil.move(f"core.cpython-{v}-x86_64-linux-gnu.so",
                    f"..//{temp_folder}//core.cpython-{v}-x86_64-linux-gnu.so")
    elif is_windows:
        shutil.move(f"core.cp{v}-win_amd64.pyd", f"..//{temp_folder}//core.cp{v}-win_amd64.pyd")
    else:
        shutil.move(f"core.cpython-{v}-darwin.so", f"..//{temp_folder}//core.cpython-{v}-darwin.so")

    chdir("..")

    molfiles = (
    "__init__.py", "creators.py", "descriptions.py", "names.py", "operators.py", "properties.py", "addon_prefrences.py",
    "simulate.py", "ui.py", "utils.py", f'core.cpython-{v}-darwin.so', f'core.cp{v}-win_amd64.pyd', f'core.cpython-{v}-x86_64-linux-gnu.so')

    with ZipFile(f'molecular-plus_{version}_' + f'{v}_{name}.zip', 'w') as z:
        for root, _, files in walk(temp_folder):
            for file in files:
                if file not in molfiles:
                    continue
                z.write(path.join(root, file), compress_type=ZIP_DEFLATED)

    # cleanup

    shutil.rmtree(f".//{temp_folder}")

    # chdir(getcwd() + "//molecularplus")
    # try:
    #     remove("*.*")
    # except:
    #     pass
    # chdir("..")
    
    chdir(getcwd() + "//c_sources")

    try:
        remove("core.html")
        remove("core.c")
        shutil.rmtree("build")
    except:
        pass

    chdir("..")

print(version)
