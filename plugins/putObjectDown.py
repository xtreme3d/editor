def putObjectDown(app, event):
    if app.keyComboPressed(app.keycodes.KEY_LCTRL, app.keycodes.KEY_DOWN):
        if app.selectedObject != 0:
            obj = app.selectedObject
            app.x3d.ObjectHide(obj)
            x = app.x3d.ObjectGetAbsolutePosition(obj, 0)
            y = app.x3d.ObjectGetGroundHeight(obj, app.map)
            z = app.x3d.ObjectGetAbsolutePosition(obj, 2)
            app.x3d.ObjectShow(obj)
            app.x3d.ObjectSetAbsolutePosition(obj, x, y, z)
            app.updateBoundingBox(obj)
    
def setup(app):
    app.registerAction('keyDown', putObjectDown)

