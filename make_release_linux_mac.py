from molecular import bl_info
from zipfile import ZipFile, ZIP_DEFLATED
from os import path, walk, remove, chdir, getcwd
import shutil
import platform
import sys
from subprocess import Popen, PIPE

is_linux = platform.architecture()[1] == "ELF" or platform.system() == "Linux"

name = 'mac'
if is_linux:
    name = 'linux'

chdir(getcwd()+"/sources")

try:
    if is_linux:
        remove("core_37_64.cpython-37m-x86_64-linux-gnu.so")
    else:
        remove("core_37_64.cpython-37m-darwin.so")
    remove("core.html")
    remove("core.c")
    shutil.rmtree("build")
except:
    pass

#TODO, blenders (or a compatible) python bin needs to be in $PATH, and if you use blender's you need to copy the python includes from SVN
#into the include folder of blenders python, too

with Popen([sys.executable, "setup.py", "build_ext", "--inplace"], stdout=PIPE) as proc:
    print(proc.stdout.read())
    if is_linux: #TODO, test
        shutil.move("core_37_64.cpython-37m-x86_64-linux-gnu.so", "../molecular/core_37_64.cpython-37m-x86_64-linux-gnu.so")
    else:
        shutil.move("core_37_64.cpython-37m-darwin.so", "../molecular/core_37_64.cpython-37m-darwin.so")

    chdir("..")

    with ZipFile('molecular_{}_'.format(('.'.join(map(str, bl_info['version'])))) + name +'.zip', 'w') as z:
        for root, _, files in walk('molecular'):
            for file in files:
                if not file.endswith('.py') and not file.endswith('.so'):
                    continue
                z.write(path.join(root, file), compress_type=ZIP_DEFLATED)

    chdir(getcwd()+"/molecular")
    try:
        if is_linux:
            remove("core_37_64.cpython-37m-x86_64-linux-gnu.so")
        else:
            remove("core_37_64.cpython-37m-darwin.so")
    except:
        pass
    chdir("..")
