def exportX3D(app, map, filename):
    print('Export %s...' % filename)
    modelsDir = app.dirName(filename) + '/models'
    texturesDir = app.dirName(filename) + '/textures'
    app.makeDir(modelsDir)
    app.makeDir(texturesDir)
    data = app.getMapProps()
    for obj in data['objects']:
        objFilename = obj['filename']
        if len(objFilename) > 0:
            app.copyFile(objFilename, modelsDir)
            obj['filename'] = 'models/' + app.baseName(objFilename)
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
