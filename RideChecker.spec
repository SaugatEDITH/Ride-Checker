# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

# Collect everything inside assets and maps
datas = collect_data_files('assets', include_py_files=False)
datas += collect_data_files('maps', include_py_files=False)

# Include the database explicitly
datas += [('database/ride_hailing.db', 'database')]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],  # make sure current dir is included
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RideChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # True if you want console for debugging
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RideChecker'
)
