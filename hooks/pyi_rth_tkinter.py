"""Configura as bibliotecas Tcl/Tk incluídas no executável one-file."""

import os
import sys


_base = sys._MEIPASS
os.environ.setdefault("TCL_LIBRARY", os.path.join(_base, "_tcl_data"))
os.environ.setdefault("TK_LIBRARY", os.path.join(_base, "_tk_data"))
