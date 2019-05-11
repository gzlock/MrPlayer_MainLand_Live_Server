# -*- mode: python -*-

from sys import platform

datas = ['index.html', 'icon.ico', 'icon.icns']
if platform == 'win32':
    path = 'E:\\'
    icon = 'icon.ico'
else:
    path = '/Users/lock/Desktop/hls_downloader/'
    icon = 'icon.icns'

datas = [(path + item,'.') for item in datas]

print('datas', datas)

block_cipher = None


a = Analysis(['main.py'],
             pathex=[path],
             binaries=[],
             datas=datas,
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
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon=icon)
app = BUNDLE(exe,
             name='main.app',
             icon=icon,
             bundle_identifier=None)
