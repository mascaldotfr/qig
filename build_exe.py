import PyInstaller.__main__
import platform

PyInstaller.__main__.run([
    'qig.py',
    '--onefile',
    '--console'
])
