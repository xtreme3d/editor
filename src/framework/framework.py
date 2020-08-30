import time
import ctypes
import sdl2
from keycodes import *

def messageBox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, unicode(text), unicode(title), style)

def windowHandle(sdlwnd):    
    info = sdl2.SDL_SysWMinfo()
    sdl2.SDL_GetWindowWMInfo(sdlwnd, ctypes.byref(info)) 
    return info.info.win.window
    
def textRead(filename):
    f = open(filename, 'r')
    return f.read()

class Framework:    
    windowWidth = 640
    windowHeight = 480
    window = None
    
    _keyPressed = [False] * 512
    _mouseButtonPressed = [False] * 255
    _mouseButtonClickTime = [False] * 255
    mouseX = 0
    mouseY = 0
    
    halfWindowWidth = 0
    halfWindowHeight = 0

    running = True
    fixedTimeStep = 1.0 / 60.0
    timer = 0
    lastTime = 0
    
    clickTime = 300

    def __init__(self, w, h, title):
        self.windowWidth = w
        self.windowHeight = h
        self.windowTitle = title
        
        self.halfWindowWidth = self.windowWidth / 2
        self.halfWindowHeight = self.windowHeight / 2
        
        self.sdl2 = sdl2
    
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.window = sdl2.SDL_CreateWindow(self.windowTitle,
                      sdl2.SDL_WINDOWPOS_CENTERED,
                      sdl2.SDL_WINDOWPOS_CENTERED, 
                      self.windowWidth, self.windowHeight,
                      sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_RESIZABLE)
        sdl2.SDL_ShowCursor(1)
        self.start()
        
    def maximizeWindow(self):
        sdl2.SDL_MaximizeWindow(self.window)
        
    def start(self):
        pass

    def update(self, dt):
        pass
    
    def render(self):
        pass
    
    def onKeyDown(self, key):
        pass
            
    def onKeyUp(self, key):
        pass
    
    def onMouseButtonDown(self, button):
        pass
        
    def onMouseButtonUp(self, button):
        pass
    
    def onClick(self, button):
        pass
    
    def setMouse(self, x, y):
        sdl2.SDL_WarpMouseInWindow(self.window, x, y)
    
    def setMouseToCenter(self):
        self.setMouse(self.halfWindowWidth, self.halfWindowHeight)
    
    def onWindowResize(self, width, height):
        pass
    
    def onDropFile(self, filename):
        pass
    
    def keyPressed(self, key):
        return self._keyPressed[key]
    
    def mouseButtonPressed(self, mb):
        return self._mouseButtonPressed[mb]
    
    def keyComboPressed(self, key1, key2):
        return self.keyPressed(key1) and self.keyPressed(key2)
        
    def mouseComboPressed(self, button, key):
        return self.mouseButtonPressed(button) and self.keyPressed(key)
    
    def run(self):
        event = sdl2.SDL_Event()
        while self.running:
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False
                elif event.type == sdl2.SDL_KEYDOWN:
                    self._keyPressed[event.key.keysym.scancode] = True
                    self.onKeyDown(event.key.keysym.scancode)
                elif event.type == sdl2.SDL_KEYUP:
                    self._keyPressed[event.key.keysym.scancode] = False
                    self.onKeyUp(event.key.keysym.scancode)
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mb = event.button.button
                    self._mouseButtonPressed[mb] = True
                    self._mouseButtonClickTime[mb] = self.currentTime
                    self.onMouseButtonDown(mb)
                elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                    mb = event.button.button
                    self._mouseButtonPressed[mb] = False
                    self.onMouseButtonUp(mb)
                    clickElapsedTime = self.currentTime - self._mouseButtonClickTime[mb]
                    if clickElapsedTime < self.clickTime:
                        self._mouseButtonClickTime[mb] = 0
                        self.onClick(mb)
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    self.mouseX = event.motion.x
                    self.mouseY = event.motion.y
                elif event.type == sdl2.SDL_WINDOWEVENT:
                    if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                        self.windowWidth = event.window.data1
                        self.windowHeight = event.window.data2
                        self.halfWindowWidth = self.windowWidth / 2
                        self.halfWindowHeight = self.windowHeight / 2
                        self.onWindowResize(event.window.data1, event.window.data2)
                    elif event.window.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
                        self.windowWidth = event.window.data1
                        self.windowHeight = event.window.data2
                        self.halfWindowWidth = self.windowWidth / 2
                        self.halfWindowHeight = self.windowHeight / 2
                        self.onWindowResize(event.window.data1, event.window.data2)
                elif event.type == sdl2.SDL_DROPFILE:
                    self.onDropFile(event.drop.file)
            self.currentTime = sdl2.SDL_GetTicks()
            elapsedTime = self.currentTime - self.lastTime
            self.lastTime = self.currentTime
            dt = elapsedTime * 0.001

            self.timer += dt
            if (self.timer >= self.fixedTimeStep):
                self.timer -= self.fixedTimeStep
                self.update(self.fixedTimeStep)
                
            self.render()

        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()
