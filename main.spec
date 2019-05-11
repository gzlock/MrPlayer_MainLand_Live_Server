# -*- mode: python -*-

from sys import platform

block_cipher = None

if platform == 'win32':
    path = 'E:\\'
else:
    path = '/Users/lock/Desktop/hls_downloader/'


a = Analysis(['main.py'],
             pathex=[path],
             binaries=[],
             datas=[(path + 'icon.ico','.'),(path + 'index.html','.')],
             hiddenimports=['engineio.async_drivers.sanic'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt5'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          icon=path+'icon.ico',
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
