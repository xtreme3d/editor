# Plugins
Put your plugins here. Plugins are Python 2.7 scripts.

## Usage
Each plugin should contain `setup` function and can register actions and scene exporters/importers:

```python
def actionFunction(app, event):
    # ...
    pass

def exporterFunction(app, map, filename):
    f = open(filename, 'w')
    f.write('SomeData')
    f.close()

def importerFunction(app, map, filename):
    f = open(filename, 'r')
    # ...
    f.close()

def setup(app):
    app.registerAction('eventName', actionFunction)
    app.registerExporter('My Scene Format', 'msf', exporterFunction)
    app.registerImporter('My Scene Format', 'msf', importerFunction)
```

Instead of `'eventName'` use the following:
- `'keyDown'` - action is called when key is pressed
- `'keyUp'` - action is called when key is released
- `'mouseButtonDown'` - action is called when mouse button is pressed
- `'mouseButtonUp'` - action is called when mouse button is released
- `'mouseClick'` - action is called when mouse button is pressed and immediately released
- `'selectObject'` - action is called when user selects an object
- `'unselectObject'` - action is called when user unselects an object

`app` parameter is an application object (see `editor.py`). You can access any of its properties and methods, and even directly modify anything with Xtreme3D functions, so be careful!

Useful properties:
- `app.x3d` - namespace for Xtreme3D functions (e.g. `app.x3d.ObjectSetPosition(obj, 0, 1, 4)`)
- `app.objects` - editable objects
- `app.selectedObject` - currently selected object id (or 0 if nothing selected)
- `app.camera` - editor camera id
- `app.navigator` - default navigator id of the `app.camera`
- `app.matlib` - default MaterialLibrary id
- `app.boundingBox` - bounding box Dummycube to highlight selected object
- `app.gizmo` - parent Dummycube for the 3D manipulator widgets
- `app.font` - default font
- `app.keycodes` - keyboard and mouse button codes (e.g. `app.keycodes.KEY_W`, `app.keycodes.MB_LEFT`). See `framework/keycodes.py` for a full list of codes.
- `app.mouseX`, `app.mouseY` - mouse coordinates in a window

Useful methods:
- `app.registerAction(eventName, func)` - register action for an event
- `app.registerExporter(description, extension, func)` - register exporter for a given format
- `app.registerImporter(description, extension, func)` - register importer for a given format
- `app.logMessage(msg)` - print a message to `editor.log`
- `app.logWarning(msg)` - print a warning message to `editor.log`
- `app.logError(msg)` - print an error message to `editor.log`, then exit
- `app.showMessage(title, msg)` - show a message box
- `app.keyPressed(key)` - if key is pressed
- `app.keyComboPressed(key1, key2)` - if two keys are pressed
- `app.mouseButtonPressed(button)` - if mouse button is pressed
- `app.mouseComboPressed(button, key)` - if mouse button and a key are pressed
- `app.addObject(className, filename, matlib, parent)` - add Xtreme3D object by className
- `app.getObjectById(id)` - select object by Xtreme3D id
- `app.getObjectByIndex(index)` - select object by editor index
- `app.selectObject(obj)` - select an object
- `app.unselectObjects()` - clear selection

`event` parameter has the following properties:
- `event.key` - a key that is pressed or released
- `event.button` - a mouse button that is pressed or released
- `event.object` - an id of the object that is selected or unselected
