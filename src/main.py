# -*- coding: utf-8 -*-

import io
import os.path
import shutil
import getpass
import math
import time
import datetime
import ctypes
import Tkinter, tkFileDialog
import logging
import sdl2
import json
from framework import *
from framework import keycodes
from pluginbase import PluginBase

now = datetime.datetime.now()
userName = getpass.getuser()

root = Tkinter.Tk()
root.withdraw()

supportedMeshExtensions = [
    '.bsp', '.b3d', '.lod', '.x', '.csm',
    '.lmts', '.dxs', '.3ds', '.ase', '.obj',
    '.lwo', '.ms3d', '.oct', '.nmf', '.wrl',
    '.ply', '.gts', '.tin', '.stl', '.glsm',
    '.md2', '.md3', '.md5', '.smd', '.mdc'
]

supportedAnimatedMeshExtensions = [
    '.md2', '.md3', '.md5', '.smd', '.mdc'
]

supportedImageExtensions = [
    '.png', '.jpg', '.jpeg', '.bmp', '.tga', '.dds'
]

supportedMeshFormats = [
    ('All files', '*.*'),
    ('Quake 3 BSP', '*.bsp'),
    ('Blitz3D B3D', '*.b3d'),
    ('LODka3D LOD', '*.lod'),
    ('Direct3D X', '*.x'),
    ('Cartography Shop 4 CSM', '*.csm'),
    ('Pulsar LMTools LMTS', '*.lmts'),
    ('DeleD DXS', '*.dxs'),
    ('Autodesk 3DS', '*.3ds'),
    ('Autodesk ASE', '*.ase'),
    ('Wavefront OBJ', '*.obj'),
    ('Lightwave LWO', '*.lwo'),
    ('Milkshape MS3D', '*.ms3d'),
    ('FSRad OCT', '*.oct'),
    ('AMD NormalMapper NMF', '*.nmf'),
    ('VRML 1.0 WRL', '*.wrl'),
    ('Stanford PLY', '*.ply'),
    ('GNU GTS', '*.gts'),
    ('Triangular Irregular Network TIN', '*.tin'),
    ('Stereolithography STL', '*.stl'),
    ('GLScene GLSM', '*.glsm'),
    ('Quake 2 MD2', '*.md2'),
    ('Quake 3 MD3', '*.md3'),
    ('Doom 3 MD5', '*.md5'),
    ('Half-Life SMD', '*.smd'),
    ('Return To Castle Wolfenstein MDC', '*.mdc')
]

logFilename = 'editor.log'
logging.basicConfig(
    format = '%(asctime)s %(levelname)-8s %(message)s', 
    datefmt = '%d-%m-%Y %H:%M:%S', 
    filename = logFilename,
    level = logging.INFO)
logging.FileHandler(logFilename, mode='w')
logging.getLogger().addHandler(logging.StreamHandler())

pluginBase = PluginBase(package = 'editorPlugins')

class Event:
    key = KEY_UNKNOWN
    button = KEY_UNKNOWN
    object = 0
    def __init__(self, *args, **kwargs):
        self.key = kwargs.get('key', KEY_UNKNOWN)
        self.button = kwargs.get('button', KEY_UNKNOWN)
        self.object = kwargs.get('object', 0)

lastIndex = 0
def uniqueIndex():
    global lastIndex
    lastIndex += 1
    return lastIndex

class X3DObject:
    app = None
    index = 0
    id = 0 #Xtreme3D id
    name = ''
    className = ''
    filename = ''
    material = None
    parentIndex = 0
    
    def __init__(self, app, id, className):
        self.app = app
        self.id = id
        self.className = className
        self.index = uniqueIndex()
    
    def setName(self, name):
        self.name = name
        ObjectSetName(self.id, name)
    
    def setMaterial(self, material):
        self.material = material
        ObjectSetMaterial(self.id, material.name)
    
    def setParentByIndex(self, parentIndex):
        parent = self.app.getObjectByIndex(parentIndex)
        if not parent is None:
            ObjectSetParent(self.id, parent.id)
    
    def getParent(self):
        parentId = ObjectGetParent(self.id)
        for obj in self.app.objects:
            if obj.id == parentId:
                return obj
        return None

    def setPosition(self, x, y, z):
        ObjectSetPosition(self.id, x, y, z)

    def getPosition(self):
        return [
            ObjectGetPositionX(self.id),
            ObjectGetPositionY(self.id),
            ObjectGetPositionZ(self.id)
        ]
    
    def setRotation(self, p, t, r):
        ObjectSetRotation(self.id, p, t, r)
    
    def getRotation(self):
        return [
            ObjectGetPitch(self.id),
            ObjectGetTurn(self.id),
            ObjectGetRoll(self.id)
        ]
    
    def setScale(self, x, y, z):
        ObjectSetScale(self.id, x, y, z)
    
    def getScale(self):
        return [
            ObjectGetScale(self.id, 0),
            ObjectGetScale(self.id, 1),
            ObjectGetScale(self.id, 2)
        ]

class X3DMaterial:
    name = ''
    textures = None
    
    def __init__(self, name, filename):
        self.name = name
        MaterialCreate(self.name, filename)
        self.textures = [''] * 16
        if filename != '':
            self.textures[0] = filename
    
    def setTexture(self, layer, filename):
        self.textures[layer] = filename
        MaterialLoadTextureEx(self.name, filename, layer)

class EditorApplication(Framework):
    mapName = 'My Map'
    mapAuthor = userName
    mapCopyright = 'Copyright (C) %s %s' % (now.year, userName)

    selectedObject = None
    mouseSensibility = 0.3
    previousMouseX = 0
    previousMouseY = 0
    dragAxis = -1
    
    increment = 1
    
    lastMaterialIndex = 0
    
    actions = {
        'keyDown': [],
        'keyUp': [],
        'mouseButtonDown': [],
        'mouseButtonUp': [],
        'mouseClick': [],
        'selectObject': [],
        'unselectObject': []
    }
    
    supportedExportFormats = [
        ('All files', '*.*')
    ]
    
    exporters = {
    }
    
    supportedImportFormats = [
        ('All files', '*.*')
    ]
    
    importers = {
    }
    
    objects = []
    materials = []

    def start(self):
        self.keycodes = keycodes
        self.x3d = x3d
    
        EngineCreate()
        self.viewer = ViewerCreate(0, 0, self.windowWidth, self.windowHeight, windowHandle(self.window))
        ViewerSetBackgroundColor(self.viewer, c_dkgray)
        ViewerSetAntiAliasing(self.viewer, aa4xHQ)
        ViewerSetLighting(self.viewer, True)
        ViewerEnableFog(self.viewer, True)
        ViewerSetFogColor(self.viewer, c_dkgray)
        ViewerSetFogDistance(self.viewer, 50, 100)
        ViewerEnableVSync(self.viewer, vsmSync)
        ViewerSetAutoRender(self.viewer, False)
        
        self.internalMatlib = MaterialLibraryCreate()
        MaterialLibrarySetTexturePaths(self.internalMatlib, 'data')
        
        self.matlib = MaterialLibraryCreate()

        self.root = DummycubeCreate(0)
        self.back = DummycubeCreate(self.root)
        self.map = DummycubeCreate(self.root)
        self.scene = DummycubeCreate(self.root)
        self.front = DummycubeCreate(self.root)
        
        ObjectShowAxes(self.scene, True)
        ObjectSetName(self.map, 'map')
        
        # Internal objects
        MaterialLibraryActivate(self.internalMatlib)
        
        self.light = LightCreate(lsOmni, self.scene)
        LightSetAmbientColor(self.light, c_gray);
        LightSetDiffuseColor(self.light, c_white);
        LightSetSpecularColor(self.light, c_white);
        ObjectSetPosition(self.light, 2, 4, 2)

        self.camera = CameraCreate(self.scene)
        ObjectSetPosition(self.camera, 0, 1, 5)
        CameraSetViewDepth(self.camera, 500)
        CameraSetFocal(self.camera, 120)
        CameraSetNearPlaneBias(self.camera, 0.1)
        ViewerSetCamera(self.viewer, self.camera)
        self.navigator = NavigatorCreate()
        NavigatorSetObject(self.navigator, self.camera)
        NavigatorSetUseVirtualUp(self.navigator, True)
        NavigatorSetVirtualUp(self.navigator, 0, 1, 0)
        
        self.plane = PlaneCreate(0, 100, 100, 100, 100, self.scene)
        MaterialCreate('mGround', 'data/tiles.png')
        MaterialSetOptions('mGround', 1, 1)
        MaterialSetTextureWrap('mGround', True)
        ObjectSetMaterial(self.plane, 'mGround')
        ObjectPitch(self.plane, 90)
        
        self.boundingBox = DummycubeCreate(self.scene)
        DummycubeSetVisible(self.boundingBox, True)
        DummycubeSetEdgeColor(self.boundingBox, c_white)
        ObjectHide(self.boundingBox)
        
        self.gizmo = DummycubeCreate(self.scene)
        ObjectSetScale(self.gizmo, 0.75, 0.75, 0.75)
        ObjectHide(self.gizmo)
        ObjectIgnoreDepthBuffer(self.gizmo, True)
        
        self.gizmoX = CylinderCreate(0.04, 0.04, 1.0, 6, 1, 1, self.gizmo)
        ObjectSetPositionX(self.gizmoX, 0.5)
        ObjectRotate(self.gizmoX, 90, 90, 0)
        self.gizmoArrowX = ConeCreate(0.1, 0.25, 8, 1, 1, self.gizmoX)
        ObjectSetPositionY(self.gizmoArrowX, 0.5)
        MaterialCreate('gizmoRed', '')
        MaterialSetDiffuseColor('gizmoRed', c_red, 1.0)
        MaterialSetOptions('gizmoRed', True, True)
        ObjectSetMaterial(self.gizmoX, 'gizmoRed')
        ObjectSetMaterial(self.gizmoArrowX, 'gizmoRed')
        
        self.gizmoY = CylinderCreate(0.04, 0.04, 1.0, 6, 1, 1, self.gizmo)
        ObjectSetPositionY(self.gizmoY, 0.5)
        self.gizmoArrowY = ConeCreate(0.1, 0.25, 8, 1, 1, self.gizmoY)
        ObjectSetPositionY(self.gizmoArrowY, 0.5)
        MaterialCreate('gizmoGreen', '')
        MaterialSetDiffuseColor('gizmoGreen', c_lime, 1.0)
        MaterialSetOptions('gizmoGreen', True, True)
        ObjectSetMaterial(self.gizmoY, 'gizmoGreen')
        ObjectSetMaterial(self.gizmoArrowY, 'gizmoGreen')
        
        self.gizmoZ = CylinderCreate(0.04, 0.04, 1.0, 6, 1, 1, self.gizmo)
        ObjectSetPositionZ(self.gizmoZ, 0.5)
        ObjectRotate(self.gizmoZ, 90, 0, 0)
        self.gizmoArrowZ = ConeCreate(0.1, 0.25, 8, 1, 1, self.gizmoZ)
        ObjectSetPositionY(self.gizmoArrowZ, -0.5)
        ObjectPitch(self.gizmoArrowZ, 180)
        MaterialCreate('gizmoBlue', '')
        MaterialSetDiffuseColor('gizmoBlue', c_blue, 1.0)
        MaterialSetOptions('gizmoBlue', True, True)
        ObjectSetMaterial(self.gizmoZ, 'gizmoBlue')
        ObjectSetMaterial(self.gizmoArrowZ, 'gizmoBlue')
        
        MaterialLibraryActivate(self.matlib)
        
        self.font = TTFontCreate('data/fonts/NotoSans-Regular.ttf', 14)
        
        self.text = HUDTextCreate(self.font, '', self.front)
        HUDTextSetColor(self.text, c_white, 1.0)
        ObjectSetPosition(self.text, 20, 20, 0)
        
        self.pluginSource = pluginBase.make_plugin_source(
            searchpath = ['./plugins'],
            identifier = 'editor')
        for pluginName in self.pluginSource.list_plugins():
            plugin = self.pluginSource.load_plugin(pluginName)
            plugin.setup(self)
            
        self.importMap('sample_scene/scene.x3d')
    
    def logMessage(self, msg):
        logging.info(msg)
        
    def logWarning(self, msg):
        logging.warning(msg)
        
    def logError(self, msg):
        logging.error(msg)
        self.showMessage('Error', msg)
        self.running = False
    
    def showMessage(self, title, text):
        messageBox(title, text, 0)
    
    def registerAction(self, event, func):
        if event in self.actions:
            self.actions[event].append(func)
        else:
            self.logWarning("Unsupported event: \"%s\"" % (event))
    
    def registerExporter(self, format, ext, func):
        self.supportedExportFormats.append((format, '*.%s' % ext))
        self.exporters['.%s' % ext] = func
        
    def registerImporter(self, format, ext, func):
        self.supportedImportFormats.append((format, '*.%s' % ext))
        self.importers['.%s' % ext] = func
    
    def callActions(self, event, params):
        if event in self.actions:
            for action in self.actions[event]:
                action(self, params)
    
    def exportMap(self, filename):
        name, ext = os.path.splitext(filename)
        if ext in self.exporters:
            self.exporters[ext](self, filename)
        else:
            msg = 'Unsupported scene format: ' + ext
            self.logWarning(msg)
            self.showMessage('Warning', 'Unsupported scene format')
    
    def importMap(self, filename):
        name, ext = os.path.splitext(filename)
        if ext in self.importers:
            self.unselectObjects()
            ObjectDestroyChildren(self.map)
            MaterialLibraryClear(self.matlib)
            self.objects = []
            self.materials = []
            lastIndex = 0
            self.lastTag = 0
            self.lastMaterialIndex = 0
            self.importers[ext](self, filename)
            lastIndex = len(self.objects)
            self.lastMaterialIndex = len(self.materials)
        else:
            msg = 'Unsupported file format: ' + ext
            self.logWarning(msg)
            self.showMessage('Warning', 'Unsupported scene format')
    
    def importModel(self, filename):
        name, ext = os.path.splitext(filename)
        if ext in supportedMeshExtensions:
            self.logMessage('Importing model %s...' % filename)
            if ext in supportedAnimatedMeshExtensions:
                obj = self.addObject('TGLActor', filename)
            else:
                obj = self.addObject('TGLFreeform', filename)
        else:
            msg = 'Unsupported mesh format: ' + ext
            self.logWarning(msg)
            self.showMessage('Warning', 'Unsupported mesh format')
    
    def importTexture(self, filename):
        name, ext = os.path.splitext(filename)
        if ext in supportedImageExtensions:
            self.logMessage('Importing texture %s...' % filename)
            material = self.addMaterial(filename)
            if not material == None:
                pickedObj = self.pickObject()
                if pickedObj != None:
                    print(material.name)
                    pickedObj.setMaterial(material)
            else:
                logError('Failed to create material %s' % material.name)
        else:
            msg = 'Unsupported texture format: ' + ext
            self.logWarning(msg)
            self.showMessage('Warning', 'Unsupported texture format')
    
    def pickObject(self):
        ObjectHide(self.plane)
        ObjectHide(self.front)
        pickedObjId = ViewerGetPickedObject(self.viewer, self.mouseX, self.mouseY)
        ObjectShow(self.front)
        ObjectShow(self.plane)
        if pickedObjId != 0:
            return self.getObjectById(pickedObjId)
        else:
            return None
    
    def importFile(self, filename):
        name, ext = os.path.splitext(filename)
        if ext in self.importers:
            self.importMap(filename)
        elif ext in supportedMeshExtensions:
            self.importModel(filename)
        elif ext in supportedImageExtensions:
            self.importTexture(filename)
    
    def onDropFile(self, filename):
        self.importFile(filename)
    
    def onKeyDown(self, key):
        if self.keyComboPressed(KEY_I, KEY_LCTRL) or self.keyComboPressed(KEY_I, KEY_RCTRL):
            filePath = tkFileDialog.askopenfilename(filetypes = supportedMeshFormats)
            if len(filePath) > 0:
                self.importModel(filePath)
        if self.keyComboPressed(KEY_S, KEY_LCTRL) or self.keyComboPressed(KEY_S, KEY_RCTRL):
            filePath = tkFileDialog.asksaveasfilename(filetypes = self.supportedExportFormats, defaultextension = '*.*')
            if len(filePath) > 0:
                self.exportMap(filePath)
        if self.keyComboPressed(KEY_O, KEY_LCTRL) or self.keyComboPressed(KEY_O, KEY_RCTRL):
            filePath = tkFileDialog.askopenfilename(filetypes = self.supportedImportFormats)
            if len(filePath) > 0:
                self.importMap(filePath)
        
        self.callActions('keyDown', Event(key = key))
    
    def onKeyUp(self, key):
        self.callActions('keyUp', Event(key = key))
            
    def onMouseButtonDown(self, button):
        self.dragOriginX = self.mouseX
        self.dragOriginY = self.mouseY
        self.previousMouseX = self.mouseX
        self.previousMouseY = self.mouseY
        if button == MB_LEFT:
            if ObjectIsPicked(self.gizmoX, self.viewer, self.mouseX, self.mouseY):
                self.dragAxis = 0
            elif ObjectIsPicked(self.gizmoY, self.viewer, self.mouseX, self.mouseY):
                self.dragAxis = 1
            elif ObjectIsPicked(self.gizmoZ, self.viewer, self.mouseX, self.mouseY):
                self.dragAxis = 2
            else:
                self.dragAxis = -1
        self.callActions('mouseButtonDown', Event(button = button))
        
    def onMouseButtonUp(self, button):
        self.callActions('mouseButtonUp', Event(button = button))
    
    def onClick(self, button):
        if button == MB_LEFT:
            self.unselectObjects()
            pickedObj = self.pickObject()
            if pickedObj != None:
                self.selectObject(pickedObj)
        self.callActions('mouseClick', Event(button = button))
    
    def selectObject(self, obj):
        self.selectedObject = obj
        self.updateBoundingBox(self.selectedObject)
        ObjectShow(self.boundingBox)
        ObjectShow(self.gizmo)
        self.callActions('selectObject', Event(object = obj.id))
    
    def unselectObjects(self):
        if self.selectedObject != None:
            obj = self.selectedObject
            ObjectHide(self.boundingBox)
            ObjectHide(self.gizmo)
            self.callActions('unselectObject', Event(object = obj.id))
            self.selectedObject = None
    
    def updateBoundingBox(self, obj):
        ObjectSetPositionOfObject(self.gizmo, obj.id)
        ObjectSetPositionOfObject(self.boundingBox, obj.id)
        ObjectAlignWithObject(self.boundingBox, obj.id)
        sx = ObjectGetScale(obj.id, 0)
        sy = ObjectGetScale(obj.id, 1)
        sz = ObjectGetScale(obj.id, 2)
        bsr = ObjectGetBoundingSphereRadius(obj.id)
        ObjectSetScale(self.boundingBox, max(bsr, sx * 0.5), max(bsr, sy * 0.5), max(bsr, sz * 0.5))
    
    def onWindowResize(self, width, height):
        ViewerResize(self.viewer, 0, 0, width, height)
    
    def dragSelectedObject(self):
        dx = (self.mouseX - self.previousMouseX);
        dy = (self.mouseY - self.previousMouseY);
        self.previousMouseX = self.mouseX
        self.previousMouseY = self.mouseY
        if self.selectedObject != None:
            id = self.selectedObject.id
            dirx = ObjectGetAbsoluteDirection(id, 0)
            diry = ObjectGetAbsoluteDirection(id, 1)
            dirz = ObjectGetAbsoluteDirection(id, 2)
            ux = ObjectGetAbsoluteUp(id, 0)
            uy = ObjectGetAbsoluteUp(id, 1)
            uz = ObjectGetAbsoluteUp(id, 2)
            rx = ObjectGetAbsoluteRight(id, 0)
            ry = ObjectGetAbsoluteRight(id, 1)
            rz = ObjectGetAbsoluteRight(id, 2)
            
            if self.dragAxis == 0:
                vx = CameraScreenDeltaToVector(self.camera, dx, -dy, 0.01, 0, 1, 0, 0)
                vz = CameraScreenDeltaToVector(self.camera, dx, -dy, 0.01, 0, 1, 0, 2)
                strafe = rx * vx + rz * vz
                ObjectTranslate(id, strafe, 0, 0)
            elif self.dragAxis == 1:
                lift = -(uy * dy * 0.01)
                ObjectTranslate(id, 0, lift, 0)
            elif self.dragAxis == 2:
                vx = CameraScreenDeltaToVector(self.camera, dx, -dy, 0.01, 0, 1, 0, 0)
                vz = CameraScreenDeltaToVector(self.camera, dx, -dy, 0.01, 0, 1, 0, 2)
                move = dirx * vx + dirz * vz
                ObjectTranslate(id, 0, 0, move)
            self.updateBoundingBox(self.selectedObject)
    
    def controlNavigator(self, dt):
        dx = (self.mouseX - self.dragOriginX) * self.mouseSensibility;
        dy = (self.mouseY - self.dragOriginY) * self.mouseSensibility;
        self.setMouse(self.dragOriginX, self.dragOriginY);
        NavigatorTurnHorizontal(self.navigator, dx)
        NavigatorTurnVertical(self.navigator, -dy)
        if self.keyPressed(KEY_W):
            NavigatorFlyForward(self.navigator, 5 * dt)
        if self.keyPressed(KEY_A):
            NavigatorStrafeHorizontal(self.navigator, -5 * dt)
        if self.keyPressed(KEY_D):
            NavigatorStrafeHorizontal(self.navigator, 5 * dt)
        if self.keyPressed(KEY_S):
            NavigatorFlyForward(self.navigator, -5 * dt)
    
    def update(self, dt):
        if self.mouseButtonPressed(MB_LEFT):
            self.dragSelectedObject()
                
        if self.mouseButtonPressed(MB_RIGHT):
            self.controlNavigator(dt)
        
        if self.selectedObject != None:
            obj = self.selectedObject
            x = ObjectGetPosition(obj.id, 0)
            y = ObjectGetPosition(obj.id, 1)
            z = ObjectGetPosition(obj.id, 2)
            HUDTextSetText(self.text, 'Name: %s\rX: %.2f\rY: %.2f\rZ: %.2f' % (obj.name, x, y, z));
        
        Update(dt)
    
    def render(self):
        ViewerRender(self.viewer)

    # Map API
    
    def addObject(self, className, filename, parentId = 0):
        if parentId == 0:
            parentId = self.map
        className = unicode(className)
        creators = {
            'TGLPlane': lambda: PlaneCreate(1, 1, 1, 1, 1, parentId),
            'TGLCube': lambda: CubeCreate(1, 1, 1, parentId),
            'TGLSphere': lambda: SphereCreate(1, 16, 8, parentId),
            'TGLCylinder': lambda: CylinderCreate(1, 1, 1, 16, 1, 1, parentId),
            'TGLCone': lambda: ConeCreate(1, 1, 16, 1, 1, parentId),
            'TGLAnnulus': lambda: AnnulusCreate(0.5, 1, 1, 16, 1, 1, parentId),
            'TGLTorus': lambda: TorusCreate(0.5, 1, 16, 8, parentId),
            'TGLDisk': lambda: DiskCreate(0.5, 1, 0.0, 360.0, 1, 16, parentId),
            'TGLFrustum': lambda: FrustrumCreate(1, 1, 1, 0.5, parentId),
            'TGLDodecahedron': lambda: DodecahedronCreate(parentId),
            'TGLIcosahedron': lambda: IcosahedronCreate(parentId),
            'TGLTeapot': lambda: TeapotCreate(parentId),
            'TGLFreeform': lambda: FreeformCreate(filename, self.matlib, self.matlib, parentId),
            'TGLActor': lambda: ActorCreate(filename, self.matlib, parentId)
        }
        if className in creators:
            id = creators[className]()
            obj = X3DObject(self, id, className)
            obj.filename = filename
            parentObj = obj.getParent()
            obj.parentIndex = 0
            if not parentObj is None:
                obj.parentIndex = parentObj.index
            self.objects.append(obj)
            return obj
        else:
            self.logError('Unsupported object class: %s' % className)
            return 0

    def getObjectByIndex(self, index):
        for obj in self.objects:
            if obj.index == index:
                return obj
        return None

    def getObjectById(self, id):
        for obj in self.objects:
            if obj.id == id:
                return obj
        return None

    def addMaterial(self, filename):
        materialName = self.uniqueMaterialName()
        return self.addMaterialOfName(materialName, filename)

    def addMaterialOfName(self, name, filename):
        material = None
        #TODO: check if name already exists
        if not self.materialExists(name):
            if filename != '':
                material = X3DMaterial(name, filename)
            else:
                material = X3DMaterial(name, '')
            self.materials.append(material)
        else:
            return self.getMaterialByName(name)
        return material

    def materialExists(self, name):
        for mat in self.materials:
            if mat.name == name:
                return True
        return False

    def getMaterialByName(self, name):
        for mat in self.materials:
            if mat.name == name:
                return mat
        return None

    def uniqueMaterialName(self):
        name = 'material' + str(self.lastMaterialIndex)
        self.lastMaterialIndex += 1
        return name

    def saveJSON(self, filename, data):
        f = open(filename, 'w')
        jsonStr = json.dumps(data, indent = 4, separators = (',', ': '), ensure_ascii = False)
        f.write(unicode(jsonStr).encode('utf-8'))
        f.close()

    def loadJSON(self, filename):
        data = {}
        f = io.open(filename, 'r', encoding = 'utf8')
        data = json.loads(f.read())
        f.close()
        return data

    def dirName(self, path):
        return os.path.dirname(path)

    def baseName(self, path):
        return os.path.basename(path)

    def makeDir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def sameFile(self, file1, file2):
        p1 = os.path.normcase(os.path.abspath(os.path.normpath(file1)))
        p2 = os.path.normcase(os.path.abspath(os.path.normpath(file2)))
        return p1 == p2

    def copyFile(self, filename, dir):
        name = os.path.basename(filename)
        newFilename = dir + '/' + name
        if not self.sameFile(filename, newFilename):
            shutil.copy(filename, dir + '/')

app = EditorApplication(1280, 720, 'Xtreme3D Editor')
app.run()
