# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_all

debug_build = os.environ.get('AUTOMATIZADOR_DEBUG_BUILD') == '1'

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
datas += [('assets/app-icon.ico', 'assets')]

# PyInstaller 6.21 não reconhece o Tcl/Tk desta instalação do Python 3.12,
# embora tkinter funcione normalmente. Incluímos os componentes explicitamente
# para evitar que o hook padrão exclua o tkinter do executável.
python_dir = os.path.dirname(sys.executable)
hiddenimports += [
    'tkinter',
    'tkinter.constants',
    'tkinter.dialog',
    'tkinter.filedialog',
    'tkinter.font',
    'tkinter.messagebox',
    'tkinter.ttk',
    '_tkinter',
]
for destino, origem, _tipo in Tree(
    os.path.join(python_dir, 'tcl', 'tcl8.6'), prefix='_tcl_data'
):
    datas.append((origem, str(Path(destino).parent)))
for destino, origem, _tipo in Tree(
    os.path.join(python_dir, 'tcl', 'tk8.6'), prefix='_tk_data'
):
    datas.append((origem, str(Path(destino).parent)))
tkinter_dir = Path(python_dir) / 'Lib' / 'tkinter'
for arquivo in tkinter_dir.rglob('*.py'):
    destino = Path('tkinter') / arquivo.relative_to(tkinter_dir)
    datas.append((str(arquivo), str(destino.parent)))
binaries += [
    (os.path.join(python_dir, 'DLLs', '_tkinter.pyd'), '.'),
    (os.path.join(python_dir, 'DLLs', 'tcl86t.dll'), '.'),
    (os.path.join(python_dir, 'DLLs', 'tk86t.dll'), '.'),
]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hooks/pyi_rth_tkinter.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='automatizador_holerites diagnostico' if debug_build else 'automatizador_holerites 2.0',
    console=debug_build,
    icon='assets/app-icon.ico',
    debug=debug_build,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
