def exportX3D(app, map, filename):
    print('Export %s...' % filename)
    data = app.getMapProps()
    f = open(filename, 'w')
    f.write(app.jsonString(data))
    f.close()
    
def importX3D(app, map, filename):
    print('Import %s...' % filename)
    
def setup(app):
    description = 'Xtreme3D Editor Scene'
    extension = 'x3d'
    app.registerExporter(description, extension, exportX3D)
    app.registerImporter(description, extension, importX3D)