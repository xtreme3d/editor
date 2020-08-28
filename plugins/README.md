# Plugins
Put your plugins here. Plugins are Python 2.7 scripts.

## Usage
Each plugin should contain `setup` function and can register one or more action:

```python
def pluginActionFunction(app, event):
    # ...
    pass

def setup(app):
    app.registerAction('eventName', pluginActionFunction)
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
- `app.x3d` - a namespace for Xtreme3D functions (e.g. `app.x3d.ObjectSetPosition(obj, 0, 1, 4)`)
- `app.objects` - a root Dummycube of the editor
- `app.back` - root Dummycube for background objects
- `app.scene` - root Dummycube for spatial objects
- `app.front` - root Dummycube for HUD objects
- `app.map` - root Dummycube for editable objects
- `app.selectedObject` - currently selected object (or 0 if nothing selected)
- `app.camera` - editor camera
- `app.navigator` - default Navigator of the `app.camera`
- `app.matlib` - default MaterialLibrary of the editor
- `app.plane` - ground plane
- `app.boundingBox` - bounding box Dummycube to highlight selected object
- `app.gizmo` - parent Dummycube for the 3D manipulator widgets
- `app.font` - default font

Useful methods:
- TODO

`event` parameter has the following properties depending on event type:
- `event["key"]` - a key that is pressed or released
- `event["button"]` - a mouse button that is pressed or released
- `event["object"]` - an object that is selected or unselected