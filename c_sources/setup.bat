rem delete old files
del core.html
del core.c
rd /s /q build
del *.pyd

rem compiling
"C:\Python 3.11\python.exe" setup.py build_ext --inplace

rem delete unnecessary files after compilation
del core.html
del core.c
rd /s /q build

rem move the core to the blender addon folder
xcopy /S /Q /Y /F "*.pyd" "%AppData%\Roaming\Blender Foundation\Blender\4.1\scripts\addons\molecularplus\"

pause
