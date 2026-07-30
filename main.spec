# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'customtkinter',
        'core',
        'core.events',
        'core.event_bus',
        'core.loop',
        'core.state',
        'core.sources',
        'core.sources.base',
        'core.sources.heartbeat',
        'core.sources.telemetry_file',
        'workers',
        'workers.executor',
        'ui',
        'ui.app_simple',
        'ui.panels',
        'ui.panels.telemetry_panel',
        'ui.panels.alerts_panel',
        'ui.panels.status_panel',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pulsedesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True para ver consola, False para ocultarla
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Agregar icono si se tiene: 'icon.ico'
)