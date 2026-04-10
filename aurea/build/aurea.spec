# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Aurea standalone distribution (Art. II Mode 3)

block_cipher = None

a = Analysis(
    ['../src/aurea/cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../src/aurea/vendor', 'aurea/vendor'),
        ('../src/aurea/themes', 'aurea/themes'),
        ('../src/aurea/agent_commands', 'aurea/agent_commands'),
        ('../src/aurea/templates', 'aurea/templates'),
    ],
    # pyyaml imports as 'yaml'; urllib.robotparser is stdlib but sometimes missed
    hiddenimports=[
        'typer',
        'jinja2',
        'mistune',
        'rich',
        'watchdog',
        'yaml',
        'urllib.robotparser',
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='aurea',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
