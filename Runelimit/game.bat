@echo off
pythonw -c "import wx" 2>NUL || pip install wxPython
start pythonw game.py
