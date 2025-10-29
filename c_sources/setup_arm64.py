import os, shutil, platform, subprocess
from setuptools import Extension, setup, Command
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import Cython.Compiler.Options

core_version = "1.21.8"

DEBUG_MODE = False

os_name = platform.system()

# Check if Build exists then remove it
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("molecular_core"):
    shutil.rmtree("molecular_core")
if os.path.exists("molecular_core.egg-info"):
    shutil.rmtree("molecular_core.egg-info")

# Check if compiled core.* exists then remove it
if os.path.isfile("core.html"):
    os.remove("core.html")
if os.path.isfile("core.c"):
    os.remove("core.c")

os.mkdir("./molecular_core")
shutil.copy("__init__.py", "./molecular_core/__init__.py")
# Copy libomp.dylib to molecular_core/ if needed

filenames = [
    "simulate.pyx",
    "update.pyx",
    "init.pyx",
    "links.pyx",
    "spatial_hash.pyx",
    "collide.pyx",
    "memory.pyx",
    "utils.pyx",
    "structures.pyx",
]

with open("./molecular_core/core.pyx", "w") as outfile:
    # This will clear the file before writing to it
    outfile.truncate(0)
    for fname in filenames:
        with open(fname) as infile:
            outfile.write(infile.read())
            outfile.write("\n")  # Add a newline character at the end of each file

Cython.Compiler.Options.annotate = True
module_name = "molecular_core.core"

if not DEBUG_MODE:
    if os_name == "Windows":
        ext_modules = [
            Extension(
                module_name,
                ["molecular_core/core.pyx"],
                extra_compile_args=[
                    "/Ox",
                    "/openmp",
                    "/GT",
                    "/arch:SSE2",
                    "/fp:fast",
                    "/wd4244",
                    "/MD",
                ],
            )
        ]

    elif os_name == "Linux":
        ext_modules = [
            Extension(
                module_name,
                ["molecular_core/core.pyx"],
                extra_compile_args=[
                    "-O3",
                    "-msse4.2",
                    "-ffast-math",
                    "-fno-builtin",
                    "-fopenmp",
                ],
                extra_link_args=["-lm", "-fopenmp"],
            )
        ]
    elif os_name == "Darwin":
        ext_modules = [
            Extension(
                module_name,
                ["molecular_core/core.pyx"],
                extra_compile_args=[
                    "-O3",
                    "-ffast-math",
                    "-fno-builtin",
                    "-arch",
                    "arm64",
                    "-mcpu=apple-m1",
                    "-Xclang",
                    "-fopenmp",
                    "-isystem/opt/homebrew/opt/libomp/include",
                ],
                extra_link_args=[
                    "-lm",
                    "-L/opt/homebrew/opt/libomp/lib",
                    "-lomp",
                    "-arch",
                    "arm64",
                    "-Wl,-rpath,@loader_path",
                ],
            )
        ]
else:
    if os_name == "Windows":
        ext_modules = [
            Extension(
                module_name,
                ["molecular_core/core.pyx"],
                extra_compile_args=["/Zi", "/O0", "/openmp", "/MD"],
            )
        ]

    elif os_name == "Linux":
        ext_modules = [
            Extension(
                module_name,
                ["molecular_core/core.pyx"],
                extra_compile_args=["-O3", "-g", "-fopenmp"],
                extra_link_args=["-lm", "-fopenmp"],
            )
        ]
    elif os_name == "Darwin":
        ext_modules = [
            Extension(
                module_name,
                ["molecular_core/core.pyx"],
                extra_compile_args=[
                    "-O0",
                    "-g",
                    "-arch",
                    "arm64",
                    "-Xclang",
                    "-fopenmp",
                    "-isystem/opt/homebrew/opt/libomp/include",
                ],
                extra_link_args=[
                    "-lm",
                    "-L/opt/homebrew/opt/libomp/lib",
                    "-lomp",
                    "-arch",
                    "arm64",
                    "-Wl,-rpath,@executable_path",
                ],
            )
        ]


# === macOS: Custom build_ext to patch .so after build ===
class DarwinBuildExt(build_ext):
    def run(self):
        super().run()
        if os_name == "Darwin":
            for ext in self.extensions:
                so_path = self.get_ext_fullpath(ext.name)
                if os.path.exists(so_path):
                    print(f"🔧 Patching {so_path} to use @loader_path/libomp.dylib")
                    libomp_dst = os.path.join(os.path.dirname(so_path), "libomp.dylib")
                    # Ensure libomp.dylib is present (in case not copied earlier)
                    if not os.path.exists(libomp_dst):
                        shutil.copyfile(
                            "/opt/homebrew/opt/libomp/lib/libomp.dylib", libomp_dst
                        )
                    # Fix the .so to reference @loader_path
                    subprocess.run(
                        [
                            "install_name_tool",
                            "-change",
                            "/opt/homebrew/opt/libomp/lib/libomp.dylib",
                            "@loader_path/libomp.dylib",
                            so_path,
                        ],
                        check=True,
                    )


# Use custom build_ext only on macOS
cmdclass = {"build_ext": DarwinBuildExt} if os_name == "Darwin" else {}

# === Run setup ===
setup(
    name="molecular_core",
    version=core_version,
    ext_modules=cythonize(ext_modules),
    packages=["molecular_core"],
    package_data={"molecular_core": ["libomp.dylib"]} if os_name == "Darwin" else {},
    cmdclass=cmdclass,
    zip_safe=False,
)

# === Build wheel automatically after setup ===
print("📦 Building wheel...")
subprocess.run(["python", "setup.py", "bdist_wheel"], check=True)
print("✅ Wheel built successfully in dist/")
