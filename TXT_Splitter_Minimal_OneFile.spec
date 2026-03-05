# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files


datas = []
# Required for themed widgets and drag-drop runtime assets.
datas += collect_data_files("customtkinter")
datas += collect_data_files("tkinterdnd2")

hiddenimports = [
    # Optional readers loaded at runtime in core/document_loader.py
    "pdfplumber",
    "pypdf",
    "pdfminer.high_level",
    "ebooklib",
    "bs4",
    "lxml",
    "docx",
    "mobi",
]

# Keep environment-only heavy stacks out of the bundle.
excludes = [
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "sklearn",
    "IPython",
    "ipykernel",
    "jupyter",
    "jupyter_client",
    "jupyter_core",
    "nbformat",
    "nbconvert",
    "notebook",
    "traitlets",
    "comm",
    "debugpy",
    "zmq",
    "pyzmq",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "qtpy",
    "paramiko",
    "bcrypt",
    "nacl",
    "pynacl",
    "trio",
    "anyio",
    "ptyprocess",
    "psutil",
    "cloudpickle",
    "dill",
    "pygments",
    "jedi",
    "prompt_toolkit",
    "pypdfium2",
    "pypdfium2_raw",
    "pytest",
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TXT_Splitter_Minimal",
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
    icon=["app_icon.ico"],
)
