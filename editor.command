#!/bin/bash
python3 -c "import wx" 2>/dev/null || pip3 install wxPython
python3 main_hexgrid.py