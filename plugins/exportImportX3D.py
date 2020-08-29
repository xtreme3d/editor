def exportX3D(app, map, filename):
    print(filename)
    f = open(filename, 'w')
    f.write('Test')
    f.close()
    
def importX3D(app, map, filename):
    print(filename)
    
def setup(app):
    description = 'Xtreme3D Editor Scene'
    mask = '*.x3d'
    app.registerExporter(description, mask, exportX3D)
    app.registerImporter(description, mask, importX3D)
