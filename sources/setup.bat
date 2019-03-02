del core.html
del core.c
rd /s /q build

"C:\Program Project\Python 3.5.4 64 bit\python.exe" setup.py build_ext --inplace
del core.html
del core.c
rd /s /q build
ren core_35_64.cp35-win_amd64.pyd core_35_64.pyd

"C:\Program Project\Python 3.7.2 64 bit\python.exe" setup.py build_ext --inplace
del core.html
del core.c
rd /s /q build
ren core_37_64.cp37-win_amd64.pyd core_37_64.pyd

"C:\Program Project\Python 3.5.4 32 bit\python.exe" setup.py build_ext --inplace
del core.html
del core.c
rd /s /q build
ren core_35_32.cp35-win_amd32.pyd core_35_32.pyd

"C:\Program Project\Python 3.7.2 32 bit\python.exe" setup.py build_ext --inplace
del core.html
del core.c
rd /s /q build
ren core_37_32.cp37-win_amd32.pyd core_37_32.pyd

pause