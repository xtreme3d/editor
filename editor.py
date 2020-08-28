# -*- coding: utf-8 -*-

import os.path
import math
import time
import ctypes
import sdl2
from framework import *
from framework import keycodes
from pluginbase import PluginBase

pluginBase = PluginBase(package = 'editorPlugins')

class EditorApplication(Framework):
    selectedObject = 0
    mouseSensibility = 0.3
    previousMouseX = 0
    previousMouseY = 0
    dragAxis = -1
    actions = {
        'keyDown': [],
        'keyUp': [],
        'mouseButtonDown': [],
        'mouseButtonUp': [],
        'mouseClick': [],
        'selectObject': [],
        'unselectObject': []
    }

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

        self.matlib = MaterialLibraryCreate()
        MaterialLibraryActivate(self.matlib)

        self.objects = DummycubeCreate(0)
        self.back = DummycubeCreate(self.objects)
        self.scene = DummycubeCreate(self.objects)
        self.front = DummycubeCreate(self.objects)
        
        ObjectShowAxes(self.scene, True)
        
        self.light = LightCreate(lsOmni, self.scene)
        LightSetAmbientColor(self.light, c_gray);
        LightSetDiffuseColor(self.light, c_white);
        LightSetSpecularColor(self.light, c_white);
        ObjectSetPosition(self.light, 2, 4, 2)

        self.camera = CameraCreate(self.scene)
        ObjectSetPosition(self.camera, 0, 1, 5)
        CameraSetViewDepth(self.camera, 500)
        CameraSetFocal(self.camera, 120)
        CameraSetSceneScale(self.camera, 1.1)
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
        
        # Objects that should be saved to file
        self.map = DummycubeCreate(self.scene)
        
        self.sphere0 = SphereCreate(0.25, 16, 8, self.map)
        ObjectSetPosition(self.sphere0, 1, 0.25, 1)
        ObjectSetName(self.sphere0, 'sphere0')
        
        self.cube0 = CubeCreate(0.5, 0.5, 0.5, self.map)
        ObjectSetPosition(self.cube0, 2, 0.25, 1)
        ObjectSetName(self.cube0, 'cube0')
        
        matlib2 = MaterialLibraryCreate();
        MaterialLibrarySetTexturePaths(matlib2, 'data/hellknight')
        MaterialLibraryActivate(matlib2)
        bump = BumpShaderCreate();
        BumpShaderSetDiffuseTexture(bump, '')
        BumpShaderSetNormalTexture(bump, '')
        BumpShaderSetMaxLights(bump, 3)
        BumpShaderUseAutoTangentSpace(bump, True)
        MaterialCreate('mHellknight', 'diffuse.png')
        MaterialCreate('mHellknightNormal', 'normal.png')
        MaterialSetSecondTexture('mHellknight', 'mHellknightNormal')
        MaterialSetShininess('mHellknight', 32)
        MaterialSetAmbientColor('mHellknight', c_gray, 1)
        MaterialSetDiffuseColor('mHellknight', c_white, 1)
        MaterialSetSpecularColor('mHellknight', c_ltgray, 1)
        MaterialSetShader('mHellknight', bump)

        hk = ActorCreate('data/hellknight/hellknight.md5mesh', matlib2, self.map)
        ActorAddObject(hk, 'data/hellknight/idle.md5anim')
        ActorAddObject(hk, 'data/hellknight/attack.md5anim')
        ActorSwitchToAnimation(hk, 0, True)
        ObjectSetScale(hk, 0.012, 0.012, 0.012)
        ObjectSetPosition(hk, 0, 0, 0)
        ObjectSetMaterial(hk, 'mHellknight')
            
        MaterialLibraryActivate(self.matlib);
        
        # GUI widgets
        self.boundingBox = DummycubeCreate(self.scene)
        DummycubeSetVisible(self.boundingBox, True)
        DummycubeSetEdgeColor(self.boundingBox, c_white)
        ObjectHide(self.boundingBox)
        
        self.gizmo = DummycubeCreate(self.scene)
        ObjectSetScale(self.gizmo, 0.75, 0.75, 0.75)
        ObjectHide(self.gizmo)
        
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
        ObjectIgnoreDepthBuffer(self.gizmoX, True)
        ObjectIgnoreDepthBuffer(self.gizmoArrowX, True)
        
        self.gizmoY = CylinderCreate(0.04, 0.04, 1.0, 6, 1, 1, self.gizmo)
        ObjectSetPositionY(self.gizmoY, 0.5)
        self.gizmoArrowY = ConeCreate(0.1, 0.25, 8, 1, 1, self.gizmoY)
        ObjectSetPositionY(self.gizmoArrowY, 0.5)
        MaterialCreate('gizmoGreen', '')
        MaterialSetDiffuseColor('gizmoGreen', c_lime, 1.0)
        MaterialSetOptions('gizmoGreen', True, True)
        ObjectSetMaterial(self.gizmoY, 'gizmoGreen')
        ObjectSetMaterial(self.gizmoArrowY, 'gizmoGreen')
        ObjectIgnoreDepthBuffer(self.gizmoY, True)
        ObjectIgnoreDepthBuffer(self.gizmoArrowY, True)
        
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
        ObjectIgnoreDepthBuffer(self.gizmoZ, True)
        ObjectIgnoreDepthBuffer(self.gizmoArrowZ, True)
        
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
        
        self.setMouseToCenter()
    
    def message(self, title, text, style):
        messageBox(title, text, style)
    
    def registerAction(self, event, func):
        if event in self.actions:
            self.actions[event].append(func)
        else:
            print("Unsupported event: \"%s\"" % (event))
    
    def callActions(self, event, params):
        if event in self.actions:
            for action in self.actions[event]:
                action(self, params)
    
    def onKeyDown(self, key):
        self.callActions('keyDown', { 'key': key })
            
    def onKeyUp(self, key):
        self.callActions('keyUp', { 'key': key })
            
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
        self.callActions('mouseButtonDown', { 'button': button })
        
    def onMouseButtonUp(self, button):
        self.callActions('mouseButtonUp', { 'button': button })
    
    def onClick(self, button):
        if button == MB_LEFT:
            self.unselectObjects()
            ObjectHide(self.plane)
            ObjectHide(self.front)
            pickedObj = ViewerGetPickedObject(self.viewer, self.mouseX, self.mouseY)
            ObjectShow(self.front)
            ObjectShow(self.plane)
            if pickedObj != 0:
                self.selectObject(pickedObj)
            else:
                self.unselectObjects()
        self.callActions('mouseClick', { 'button': button })
    
    def selectObject(self, obj):
        self.selectedObject = obj
        self.updateBoundingBox(obj)
        ObjectShow(self.boundingBox)
        ObjectShow(self.gizmo)
        self.callActions('selectObject', { 'object': obj })
    
    def unselectObjects(self):
        if self.selectedObject != 0:
            obj = self.selectedObject
            ObjectHide(self.boundingBox)
            ObjectHide(self.gizmo)
            self.callActions('unselectObject', { 'object': obj })
            self.selectedObject = 0
    
    def updateBoundingBox(self, obj):
        ObjectSetPositionOfObject(self.gizmo, obj)
        ObjectSetPositionOfObject(self.boundingBox, obj)
        ObjectAlignWithObject(self.boundingBox, obj)
        sx = ObjectGetScale(obj, 0)
        sy = ObjectGetScale(obj, 1)
        sz = ObjectGetScale(obj, 2)
        bsr = ObjectGetBoundingSphereRadius(obj)
        ObjectSetScale(self.boundingBox, max(bsr, sx * 0.5), max(bsr, sy * 0.5), max(bsr, sz * 0.5))
    
    def onWindowResize(self, width, height):
        ViewerResize(self.viewer, 0, 0, width, height)
    
    def update(self, dt):
        if self.mouseButtonPressed(MB_LEFT):
            dx = (self.mouseX - self.previousMouseX);
            dy = (self.mouseY - self.previousMouseY);
            self.previousMouseX = self.mouseX
            self.previousMouseY = self.mouseY
            if self.selectedObject != 0:
                obj = self.selectedObject
                
                dirx = ObjectGetAbsoluteDirection(obj, 0)
                diry = ObjectGetAbsoluteDirection(obj, 1)
                dirz = ObjectGetAbsoluteDirection(obj, 2)
                ux = ObjectGetAbsoluteUp(obj, 0)
                uy = ObjectGetAbsoluteUp(obj, 1)
                uz = ObjectGetAbsoluteUp(obj, 2)
                rx = ObjectGetAbsoluteRight(obj, 0)
                ry = ObjectGetAbsoluteRight(obj, 1)
                rz = ObjectGetAbsoluteRight(obj, 2)
                
                if self.dragAxis == 0:
                    vx = CameraScreenDeltaToVector(self.camera, dx, -dy, 0.01, 0, 1, 0, 0)
                    vz = CameraScreenDeltaToVector(self.camera, dx, -dy, 0.01, 0, 1, 0, 2)
                    strafe = rx * vx + rz * vz
                    ObjectTranslate(obj, strafe, 0, 0)
                elif self.dragAxis == 1:
                    lift = -(uy * dy * 0.01)
                    ObjectTranslate(obj, 0, lift, 0)
                elif self.dragAxis == 2:
                    vx = CameraScreenDeltaToVector(self.camera, dx, -dy, 0.01, 0, 1, 0, 0)
                    vz = CameraScreenDeltaToVector(self.camera, dx, -dy, 0.01, 0, 1, 0, 2)
                    move = dirx * vx + dirz * vz
                    ObjectTranslate(obj, 0, 0, move)
                self.updateBoundingBox(obj)
                
        if self.mouseButtonPressed(MB_RIGHT):
            dx = (self.mouseX - self.dragOriginX) * self.mouseSensibility;
            dy = (self.mouseY - self.dragOriginY) * self.mouseSensibility;
            self.setMouse(self.dragOriginX, self.dragOriginY);
            NavigatorTurnHorizontal(self.navigator, dx)
            NavigatorTurnVertical(self.navigator, -dy)
            if self.keyPressed(KEY_W): NavigatorFlyForward(self.navigator, 5 * dt)
            if self.keyPressed(KEY_A): NavigatorStrafeHorizontal(self.navigator, -5 * dt)
            if self.keyPressed(KEY_D): NavigatorStrafeHorizontal(self.navigator, 5 * dt)
            if self.keyPressed(KEY_S): NavigatorFlyForward(self.navigator, -5 * dt)
        
        if self.selectedObject != 0:
            obj = self.selectedObject
            if not self.keyPressed(KEY_LCTRL):
                if self.keyPressed(KEY_LEFT): 
                    ObjectTranslate(obj, 0.1, 0, 0)
                    self.updateBoundingBox(obj)
                if self.keyPressed(KEY_RIGHT):
                    ObjectTranslate(obj, -0.1, 0, 0)
                    self.updateBoundingBox(obj)
                if self.keyPressed(KEY_UP):
                    ObjectTranslate(obj, 0, 0, 0.1)
                    self.updateBoundingBox(obj)
                if self.keyPressed(KEY_DOWN):
                    ObjectTranslate(obj, 0, 0, -0.1)
                    self.updateBoundingBox(obj)
        
            x = ObjectGetPosition(obj, 0)
            y = ObjectGetPosition(obj, 1)
            z = ObjectGetPosition(obj, 2)
            HUDTextSetText(self.text, 'X: %.2f\rY: %.2f\rZ: %.2f' % (x, y, z));
        
        Update(dt)
    
    def render(self):
        ViewerRender(self.viewer)

app = EditorApplication(1280, 720, 'Xtreme3D Editor')
app.run()
