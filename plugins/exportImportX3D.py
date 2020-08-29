def exportX3D(app, filename):
    app.logMessage('Export %s...' % filename)
    modelsDir = app.dirName(filename) + '/models'
    texturesDir = app.dirName(filename) + '/textures'
    app.makeDir(modelsDir)
    app.makeDir(texturesDir)
    
    data = {
        'name': app.mapName,
        'author': app.mapAuthor,
        'copyright': app.mapCopyright, 
        'objects': [],
        'materials': {}
    }
    
    for obj in app.objects:
        id = obj.id
        if id == 0:
            self.logError('Invalid object')
        
        materialName = obj.material
        if len(materialName) > 0:
            if not materialName in data['materials']:
                materialData = {
                    'name': materialName
                }
                data['materials'][materialName] = materialData
        
        parentObj = obj.getParentObject()
        parentIndex = 0
        if not parentObj is None:
            parentIndex = parentObj.index
        
        objData = {
            'name': obj.name,
            'index': obj.index,
            'class': obj.className,
            'parentIndex': parentIndex,
            'position': obj.getPosition(),
            'rotation': obj.getRotation(),
            'scale': obj.getScale(),
            'material': obj.material,
            'filename': obj.filename
        }
        
        if len(obj.filename) > 0:
            app.copyFile(obj.filename, modelsDir)
            objData['filename'] = 'models/' + app.baseName(obj.filename)
        
        data['objects'].append(objData)
    
    app.saveJSON(filename, data)

def importX3D(app, filename):
    app.logMessage('Import %s...' % filename)
    dir = app.dirName(filename)
    data = app.loadJSON(filename)
    app.mapName = data['name']
    app.mapAuthor = data['author']
    app.mapCopyright = data['copyright']
    
    #TODO: load materials
    
    # Create objects
    for objData in data['objects']:
        index = objData['index']
        name = objData['name']
        className = objData['class']
        parentIndex = objData['parentIndex']
        objFilename = ''
        if len(objData['filename']) > 0:
            objFilename = dir + '/' + objData['filename']
        position = objData['position']
        rotation = objData['rotation']
        scale = objData['scale']
        obj = app.addObject(className, objFilename)
        obj.index = index
        obj.parentIndex = parentIndex
        obj.setName(name)
        obj.setPosition(position[0], position[1], position[2])
        obj.setRotation(rotation[0], rotation[1], rotation[2])
        obj.setScale(scale[0], scale[1], scale[2])
    
    # Assign parents to created objects
    for obj in app.objects:
        id = obj.id
        if id == 0:
            self.logError('Invalid object')
        obj.setParentByIndex(obj.parentIndex)

def setup(app):
    description = 'Xtreme3D Editor Scene'
    extension = 'x3d'
    app.registerExporter(description, extension, exportX3D)
    app.registerImporter(description, extension, importX3D)
