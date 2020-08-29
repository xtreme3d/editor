import sys
from cx_Freeze import setup, Executable

sys.path.append('src')

executable = Executable(
    script = 'src/main.py',
    targetName = 'editor.exe',
    icon = 'assets/editor.ico',
    base = 'Win32GUI')

packages = [
    'os', 'sys', 'time', 'math', 'random', 
    'ctypes', 'json', 'logging'
]

include = [
    'data',
    'plugins',
    'sample_scene',
    'freetype.dll',
    'SDL2.dll',
    'xtreme3d.dll'
]

setup(
    name = 'Xtreme3D Editor',
    version = '0.1.0',
    description = 'Xtreme3D Editor',
    options = {
        'build_exe': {
            'packages': packages,
            'include_files': include,
            'include_msvcr': True,
            'excludes': ['sqlite3'],
            'optimize': 2
        }
    },
    executables = [executable]
)
