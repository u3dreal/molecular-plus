rem compiling
python setup.py build_ext --inplace
@REM "D:\Program Files\Blender Foundation\blender-4.0.2\4.0\python\bin\python.exe" setup.py build_ext --inplace

rem move the core to the blender addon folder
xcopy /S /Q /Y /F "*.pyd" "%appdata%\Blender Foundation\Blender\4.1\scripts\addons\molecularplus\"

@REM pause