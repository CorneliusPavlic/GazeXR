# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gaze_xr_main_GUI.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/corne/anaconda3/envs/paddleocr-inference/Lib/site-packages/ultralytics/cfg/default.yaml', 'ultralytics/cfg')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5'],
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
    name='gaze_xr_main_GUI',
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
)
