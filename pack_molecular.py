import sys
from zipfile import ZipFile, ZIP_DEFLATED
from os import path, walk, remove, rmdir, chdir, getcwd, mkdir, rename, listdir
import shutil
import platform
import subprocess
from subprocess import Popen, PIPE
import sys

is_linux = platform.system() == "Linux"
is_windows = platform.system() == "Windows"

# in python 3.8.x, sys.abiflags attribute doesnt seem to exist any more instead of returning empty string.
# so better check for existence here before accessing it.
abiflags = ""
if hasattr(sys, "abiflags"):
    abiflags = sys.abiflags

v = str(sys.version_info.major) + str(sys.version_info.minor) + abiflags

name = "macos"
if is_linux:
    name = "linux"
elif is_windows:
    name = "win"

mkdir(".//molecularplus")

pyfiles = (
    "blender_manifest.toml",
    "__init__.py",
    "creators.py",
    "descriptions.py",
    "names.py",
    "operators.py",
    "properties.py",
    "simulate.py",
    "ui.py",
    "utils.py",
    "addon_prefrences.py",
)

for file in pyfiles:
    shutil.copy(file, ".//molecularplus//" + file)

from molecularplus import bl_info

chdir(getcwd() + "//c_sources")

# TODO, blenders (or a compatible) python bin needs to be in $PATH, and if you use blender's you need to copy the python includes from SVN
# into the include folder of blenders python, too

version = ".".join(map(str, bl_info["version"]))

# Create wheels directory if it doesn't exist
wheels_dir = "..//molecularplus//wheels"
if not path.exists(wheels_dir):
    mkdir(wheels_dir)

# Print debug information to stderr
# print("Creating wheel...", file=sys.stderr)
process = Popen([sys.executable, "setup.py", "bdist_wheel"], stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()

# Move the wheel to the wheels directory
for root, _, files in walk("dist"):
    for file in files:
        if file.endswith(".whl"):
            source = path.join(root, file)
            destination = path.join(wheels_dir, file)
            shutil.move(source, destination)

chdir("..")

shutil.rmtree(".//molecularplus//__pycache__")

# print("zipping Extension...")
with ZipFile(
    "molecular-plus_{}_{}_{}.zip".format(version, v, name),
    "w",
    compression=ZIP_DEFLATED,
) as z:
    for root, _, files in walk("molecularplus"):
        for file in files:
            file_path = path.join(root, file)
            archive_path = path.relpath(file_path)
            z.write(file_path, archive_path)

shutil.rmtree(".//molecularplus")
print(version)
