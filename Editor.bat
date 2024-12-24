@echo off
pythonw -c "import wx" 2>NUL || pip install wxPython
start pythonw main_hexgrid.py
