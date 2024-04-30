rem delete old files
del core.html
del core.c
rd /s /q build
del *.pyd

rem compiling
python setup.py build_ext --inplace
@REM "D:\Program Files\Blender Foundation\blender-4.0.2\4.0\python\bin\python.exe" setup.py build_ext --inplace

rem delete unnecessary files after compilation
del core.html
del core.c
rd /s /q build

rem move the core to the blender addon folder
xcopy /S /Q /Y /F "*.pyd" "%AppData%\Blender Foundation\Blender\4.1\scripts\addons\molecularplus\"
@REM xcopy /S /Q /Y /F "*.pyd" "%AppData%\Blender Foundation\Blender\4.0\scripts\addons\molecularplus\"

del *.pyd
pause
