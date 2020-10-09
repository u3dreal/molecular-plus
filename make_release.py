from molecular import bl_info
from zipfile import ZipFile, ZIP_DEFLATED
from os import path, walk, remove, chdir, getcwd
import shutil
import platform
import sys
import pathlib
from subprocess import Popen, PIPE

is_linux = platform.architecture()[1] == "ELF" or platform.system() == "Linux"
is_windows = platform.architecture()[1] == "WindowsPE" or platform.system() == "Windows"

#in python 3.8.x, sys.abiflags attribute doesnt seem to exist any more instead of returning empty string.
#so better check for existence here before accessing it.
abiflags = ''
if hasattr(sys, 'abiflags'):
    abiflags = sys.abiflags

v = str(sys.version_info.major) + str(sys.version_info.minor) + abiflags

name = 'mac'
if is_linux:
    name = 'linux'
elif is_windows:
    name = 'win'

chdir(getcwd()+"//sources")

#TODO, blenders (or a compatible) python bin needs to be in $PATH, and if you use blender's you need to copy the python includes from SVN
#into the include folder of blenders python, too

with Popen([sys.executable, "setup.py", "build_ext", "--inplace"], stdout=PIPE) as proc:
    #print(proc.stdout.read())
    if is_linux: #TODO, test
        shutil.move("core.cpython-{}-x86_64-linux-gnu.so".format(v), "..//molecular//core.cpython-{}-x86_64-linux-gnu.so".format(v))
    elif is_windows: 
        shutil.move("core.cp{}-win_amd64.pyd".format(v), "..//molecular//core.cp{}-win_amd64.pyd").format(v)
    else:
        shutil.move("core.cpython-{}-darwin.so".format(v), "..//molecular//core.cpython-{}-darwin.so".format(v))

    chdir("..")

    with ZipFile('molecular_{}_'.format(('.'.join(map(str, bl_info['version'])))) + name +'.zip', 'w') as z:
        for root, _, files in walk('molecular'):
            for file in files:
                if not file.endswith('.py') and not file.endswith('.so') and not file.endswith('.pyd'):
                    continue
                z.write(path.join(root, file), compress_type=ZIP_DEFLATED)
    #cleanup
    chdir(getcwd()+"//molecular")
    try:
        if is_linux:
            remove("core.cpython-{}-x86_64-linux-gnu.so".format(v))
        elif is_windows:
            remove("core.cp{}-win_amd64.pyd".format(v))
        else:
            remove("core.cpython-{}-darwin.so".format(v))
    except:
        pass
    chdir("..")
    chdir(getcwd()+"//sources")

    try:
        remove("core.html")
        remove("core.c")
        shutil.rmtree("build")
    except:
        pass

    chdir("..")
    
print(bl_info['version'])
