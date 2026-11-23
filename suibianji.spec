# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/run_suibianji.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cryptography', 'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
        'PyQt6.QtNetwork', 'logging.handlers',
        'suibianji', 'suibianji.core', 'suibianji.core.data_manager',
        'suibianji.core.models', 'suibianji.core.paths', 'suibianji.core.settings',
        'suibianji.core.single_instance', 'suibianji.ui', 'suibianji.ui.app_icon',
        'suibianji.ui.main_window', 'suibianji.ui.theme',
    ],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='随便记',
    icon='assets/app.ico',
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
    uac_admin=False,
)
