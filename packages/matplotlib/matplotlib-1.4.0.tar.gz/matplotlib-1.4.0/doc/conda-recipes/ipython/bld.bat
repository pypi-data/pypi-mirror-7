copy "%RECIPE_DIR%\IPython.ico" %MENU_DIR%
if errorlevel 1 exit 1

python setup.py install
if errorlevel 1 exit 1

rd /s /q %SP_DIR%\ipython-0.13.2-py%PY_VER%.egg\share
