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
    
    for mat in app.materials:
        if len(mat.name) == 0:
            self.logError('Invalid material')
        if not mat.name in data['materials']:
            materialData = {}
            textures = []
            for i in range(len(mat.textures)):
                tex = mat.textures[i]
                if len(tex) > 0:
                    if app.fileExists(tex):
                        app.copyFile(tex, texturesDir)
                        newTextureFilename = 'textures/' + app.baseName(tex)
                        textures.append(newTextureFilename)
                    else:
                        msg = 'Cannot find texture file: %s' % tex
                        self.showMessage('Warning', msg)
                        self.logWarning(msg)
                        textures.append('')
            if len(textures) > 0:
                materialData['textures'] = textures
            data['materials'][mat.name] = materialData
    
    for obj in app.objects:
        id = obj.id
        if id == 0:
            self.logError('Invalid object: null id')
        
        objData = {
            'index': obj.index,
            'position': obj.getPosition(),
            'rotation': obj.getRotation(),
            'scale': obj.getScale()
        }
        
        if len(obj.name) > 0:
            objData['name'] = obj.name
        
        className = obj.className
        if len(obj.className) == 0:
            className = 'TGLDummyCube'
        objData['class'] = className
        
        parentObj = obj.getParent()
        if not parentObj is None:
            objData['parentIndex'] = parentObj.index
        
        if not obj.material == None:
            objData['material'] = obj.material.name
        
        if obj.className == 'TGLLightSource':
            objData['light'] = obj.lightProperties
        
        if len(obj.filename) > 0:
            if app.fileExists(obj.filename):
                app.copyFile(obj.filename, modelsDir)
                objData['filename'] = 'models/' + app.baseName(obj.filename)
            else:
                msg = 'Cannot find model file: %s' % obj.filename
                self.showMessage('Warning', msg)
                self.logWarning(msg)
        
        if obj.properties:
            objData['properties'] = obj.properties
        
        data['objects'].append(objData)
    
    app.saveJSON(filename, data)

def importX3D(app, filename):
    app.logMessage('Import %s...' % filename)
    dir = app.dirName(filename)
    data = app.loadJSON(filename)
    app.mapName = data.get('name', '')
    app.mapAuthor = data.get('author', '')
    app.mapCopyright = data.get('copyright', '')
    
    # Create materials
    for matName, matData in data['materials'].iteritems():
        textures = [''] * 16
        texture0 = ''
        if 'textures' in matData:
            textures = matData['textures']
            if len(textures) > 0:
                texture0 = dir + '/' + matData['textures'][0]
                if not app.fileExists(texture0):
                    msg = 'Cannot find texture file: %s' % texture0
                    self.showMessage('Warning', msg)
                    self.logWarning(msg)
                    texture0 = ''
        
        material = app.addMaterialOfName(matName, texture0)
        #TODO: load other textures
    
    # Create objects
    for objData in data['objects']:
        if not 'index' in objData:
            self.logError('Invalid object: no index')
        index = objData['index']
        className = objData.get('class', 'TGLDummyCube')
        name = objData.get('name', '')
        parentIndex = objData.get('parentIndex', 0)
        objFilename = ''
        if 'filename' in objData:
            filename = objData['filename']
            if len(filename) > 0:
                objFilename = dir + '/' + filename
                if not app.fileExists(objFilename):
                    msg = 'Cannot find model file: %s' % objFilename
                    self.showMessage('Warning', msg)
                    self.logWarning(msg)
                    objFilename = ''
        
        position = objData.get('position', [0, 0, 0])
        rotation = objData.get('rotation', [0, 0, 0])
        scale = objData.get('scale', [0, 0, 0])
        matName = objData.get('material', '')
        obj = app.addObject(className, objFilename)
        obj.index = index
        obj.parentIndex = parentIndex
        obj.setName(name)
        obj.setPosition(position[0], position[1], position[2])
        obj.setRotation(rotation[0], rotation[1], rotation[2])
        obj.setScale(scale[0], scale[1], scale[2])
        if len(matName) > 0:
            mat = app.getMaterialByName(matName)
            if mat != None:
                obj.setMaterial(mat)
        if 'light' in objData:
            light = objData['light']
            obj.setLightDiffuseColor(light.get('diffuseColor', app.constants.c_white))
            obj.setLightSpecularColor(light.get('specularColor', app.constants.c_white))
            obj.setLightAmbientColor(light.get('ambientColor', app.constants.c_black))
            #TODO: other light props
        obj.properties = objData.get('properties', {})
    
    # Assign parents to created objects
    for obj in app.objects:
        id = obj.id
        if id == 0:
            self.logError('Invalid object: null id')
        obj.setParentByIndex(obj.parentIndex)

def setup(app):
    description = 'Xtreme3D Editor Scene'
    extension = 'x3d'
    app.registerExporter(description, extension, exportX3D)
    app.registerImporter(description, extension, importX3D)
