# Xtreme3D Editor

Scene editor for Xtreme3D 3.8+. Work in progress!

## Prerequisites
- Python 2.7 32-bit

## Run
```
python src/main.py
```

## Build standalone
```
python setup.py build
```

## Controls
- Right mouse button + WASD - navigate through the scene
- Left mouse button - select object
- Arrow keys, PgUp, PgDn - move selected object by a small increment
- Ctrl+O - open scene (WIP)
- Ctrl+S - save scene (WIP)
- Ctrl+I - import model
- Ctrl+Down - put selected object on ground
- Ctrl+G - align selected object to grid

## License
Copyright (c) 2020 Timur Gafarov. Distributed under the Boost Software License, Version 1.0.
Contains source code from the following projects:
- [PySDL2](https://pypi.org/project/PySDL2/) - Public Domain
- [Pluginbase](https://pypi.org/project/pluginbase/) - BSD license
- [cx_Freeze 5](https://pypi.org/project/cx-Freeze/) - PSFL-derived license
