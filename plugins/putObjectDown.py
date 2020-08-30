def putObjectDown(app, event):
    if app.keyComboPressed(app.keycodes.KEY_LCTRL, app.keycodes.KEY_DOWN):
        if app.selectedObject != None:
            id = app.selectedObject.id
            app.x3d.ObjectHide(id)
            x = app.x3d.ObjectGetAbsolutePosition(id, 0)
            y = app.x3d.ObjectGetGroundHeight(id, app.map)
            z = app.x3d.ObjectGetAbsolutePosition(id, 2)
            app.x3d.ObjectShow(id)
            app.x3d.ObjectSetAbsolutePosition(id, x, y, z)
            app.updateBoundingBox(app.selectedObject)
    
def setup(app):
    app.registerAction('keyDown', putObjectDown)

