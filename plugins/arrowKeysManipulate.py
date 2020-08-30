def putObjectDown(app, event):
    obj = app.selectedObject
    if obj == None:
        return
    id = app.selectedObject.id
    if app.keyComboPressed(app.keycodes.KEY_LCTRL, app.keycodes.KEY_DOWN):
        app.x3d.ObjectHide(id)
        x = app.x3d.ObjectGetAbsolutePosition(id, 0)
        y = app.x3d.ObjectGetGroundHeight(id, app.map)
        z = app.x3d.ObjectGetAbsolutePosition(id, 2)
        app.x3d.ObjectShow(id)
        app.x3d.ObjectSetAbsolutePosition(id, x, y, z)
        app.updateBoundingBox(obj)
    elif app.keyPressed(app.keycodes.KEY_LEFT): 
        app.x3d.ObjectTranslate(id, app.increment, 0, 0)
        app.updateBoundingBox(obj)
    elif app.keyPressed(app.keycodes.KEY_RIGHT):
        app.x3d.ObjectTranslate(id, -app.increment, 0, 0)
        app.updateBoundingBox(obj)
    elif app.keyPressed(app.keycodes.KEY_UP):
        app.x3d.ObjectTranslate(id, 0, 0, app.increment)
        app.updateBoundingBox(obj)
    elif app.keyPressed(app.keycodes.KEY_DOWN):
        app.x3d.ObjectTranslate(id, 0, 0, -app.increment)
        app.updateBoundingBox(obj)
    elif app.keyPressed(app.keycodes.KEY_PAGEUP):
        app.x3d.ObjectTranslate(id, 0, app.increment, 0)
        app.updateBoundingBox(obj)
    elif app.keyPressed(app.keycodes.KEY_PAGEDOWN):
        app.x3d.ObjectTranslate(id, 0, -app.increment, 0)
        app.updateBoundingBox(obj)
    
def setup(app):
    app.registerAction('keyDown', putObjectDown)

