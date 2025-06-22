# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_with_gui.py'],
    pathex=['src/py', 'src/py/utils', 'src/py/utils/gui', 'src/py/utils/auto_answer'],
    binaries=[],
    datas=[('src/data/static', 'data/static'), ('src/js', 'js')],
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
    a.binaries,
    a.datas,
    [],
    name='main_with_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['the_icon.ico'],
)
