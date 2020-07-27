pip uninstall -y commodplot
python setup.py bdist_wheel
pip install dist\commodplot-1.0.15-py2.py3-none-any.whl
REM pip install git+https://github.com/aeorxc/commodplotl#egg=commodplot