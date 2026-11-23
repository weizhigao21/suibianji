# -*- mode: python ; coding: utf-8 -*-
# onedir 打包:启动时无需把整个包解压到临时目录,冷启动明显快于 onefile

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
        'suibianji.core.hotkey', 'suibianji.core.models', 'suibianji.core.paths',
        'suibianji.core.settings', 'suibianji.core.single_instance',
        'suibianji.core.totp', 'suibianji.ui', 'suibianji.ui.app_icon',
        'suibianji.ui.main_window', 'suibianji.ui.search_dialog', 'suibianji.ui.theme',
    ],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 用不到的 Qt 模块,剔除以缩小体积
        'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtQml',
        'PyQt6.QtQuick', 'PyQt6.QtPdf', 'PyQt6.QtMultimedia', 'PyQt6.QtBluetooth',
        'PyQt6.QtPositioning', 'PyQt6.QtSerialPort', 'PyQt6.QtTest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 本程序是纯 widgets 界面,不需要 Qt 的软件 OpenGL 回退库(约 20MB)
a.binaries = [b for b in a.binaries if 'opengl32sw' not in b[0].lower()]

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='随便记',
    icon='assets/app.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='随便记',
)
