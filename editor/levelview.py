'''
Works with scenemap implementation to allow
editing, saving and loading of scenemaps

'''
from pyglet.window import mouse, key
from pyglet.gl import *
from py2d.scenemap import SceneMap

FILE_EXT = 'lvl'

class Keys(key.KeyStateHandler):
    def __init__(self, levelView):
        self.levelView = levelView

    def on_key_press(self, symbol, modifiers):
        self.levelView.mode.key_press(symbol, modifiers)
        super(Keys, self).on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.levelView.mode.key_release(symbol, modifiers)
        super(Keys, self).on_key_release(symbol, modifiers)

class BaseController(object):
    name = "base"
    tool = None
    PAN_TOOL = 'pan'
    
    def __init__(self, levelView, window):
        self.levelView = levelView
        self.tool = self.PAN_TOOL
        self.window = window
        self.keys = Keys(self)
        
        
    def translateMouseClick(self, x=0, y=0, point=None):
        if point != None:
            x = point[0] - self.levelView.sceneMap.focusX
            y = point[1] - self.levelView.sceneMap.focusY
            return (x,y)
        else:
            x = x - self.levelView.sceneMap.focusX
            y = y - self.levelView.sceneMap.focusY
            return (x,y)
        
        
    def on_mouse_motion(self, x, y, dx, dy):
        pass
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.tool == self.PAN_TOOL:
            if self.levelView.sceneMap != None:
                self.levelView.sceneMap.moveFocus(dx, dy)
        
    def on_mouse_press(self,x, y, button, modifiers):
        pass
    
    def on_mouse_scdfroll(self,x, y, scroll_x, scroll_y):
        pass
        
    def on_mouse_release(self, x, y, button, modifiers):
        pass
    
    def key_press(self, symbol, modifiers):
        if symbol == key.HOME:
            self.levelView.sceneMap.setFocus(0,0)
        # scale movement keys:
        if symbol == key.MINUS:
            self.levelView.scale -= round((self.levelView.scale / 10), 2)
            self.window.dispatch_event('on_dialog_update')
        if symbol == key.EQUAL:
            self.levelView.scale += round((self.levelView.scale / 10), 2)
            self.window.dispatch_event('on_dialog_update')
        if symbol == key._0 or key.NUM_9:
            self.levelView.scale = 1.0
            self.window.dispatch_event('on_dialog_update')
            
    def key_release(self, symbol, modifiers):
        pass
        
    def pollPanKeys(self, dt):
        moveRate = dt * 400
        if self.keys[key.UP]:
            self.levelView.sceneMap.moveFocus(y=-moveRate)
        if self.keys[key.DOWN]:
            self.levelView.sceneMap.moveFocus(y=moveRate)
        if self.keys[key.LEFT]:
            self.levelView.sceneMap.moveFocus(moveRate)
        if self.keys[key.RIGHT]:
            self.levelView.sceneMap.moveFocus(-moveRate)
        
    def update(self, dt):
        self.pollPanKeys(dt)
        
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class TerrainController(BaseController):
    name = "terrain"
    LINE_TOOL = 'line'
    lineStart = (0,0)
    linePreview = None
    mousePoint = (0,0)
    snapMode = False

    def __init__(self, levelView, window):
        super(TerrainController, self).__init__(levelView, window)
        self.tool = self.PAN_TOOL
        
    def preview(self, x, y):
        if self.tool == self.LINE_TOOL:
            if self.linePreview:
                self.linePreview.vl.delete()
            layer = self.levelView.sceneMap.layers[self.name]
            mousePos = self.translateMouseClick(x,y)
            self.linePreview = layer.addLine(mousePos[0],mousePos[1],self.lineStart[0],self.lineStart[1], True)
            
    def closestPointToMouse(self):
        lines = self.levelView.sceneMap.layers[self.name].lines
        mousePos = self.translateMouseClick(self.mousePoint[0],self.mousePoint[1])
        closestPoint = None
        points = list()
        
        for line in lines:
            #create list of points
            points.append(Point(line.x1, line.y1))
            points.append(Point(line.x2, line.y2))
        for point in points:
            # calcuate distance between mouse and point
            xDist = abs(mousePos[0] - point.x)
            yDist = abs(mousePos[1] - point.y)
            dist = xDist + yDist
            if closestPoint == None:
                closestDist = dist
                closestPoint = point
            if dist < closestDist:
                closestDist = dist
                closestPoint = point
        return (closestPoint.x,closestPoint.y)
        
    '''
    keyboard and mouse input handlers
    
    '''    
    def key_press(self, symbol, modifiers):
        super(TerrainController, self).key_press(symbol, modifiers)
        
    def key_release(self, symbol, modifiers):
        if modifiers & key.MOD_CTRL and symbol == key.S:
            if self.snapMode == True:
                print "snap off!"
                self.snapMode = False
            else:
                print "snap!"
                self.snapMode = True
            
        super(TerrainController, self).key_release(symbol, modifiers)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super(TerrainController, self).on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self.preview(x,y)
   
    def on_mouse_press(self, x, y, button, modifiers):
        if self.tool == self.LINE_TOOL:
            if button == mouse.LEFT:
                if self.snapMode == True:
                    ''' snap mode causes line start 
                        to snap to nearest point '''
                    self.lineStart = self.closestPointToMouse()
                else:
                    translatedCoords = self.translateMouseClick(x,y)
                    self.lineStart = translatedCoords
        
    def on_mouse_motion(self, x, y, dx, dy):
        self.mousePoint = (x, y)
        
    def on_mouse_scdfroll(self,x, y, scroll_x, scroll_y):
        pass
        
    def on_mouse_release(self, x, y, button, modifiers):
        if self.tool == self.LINE_TOOL:
            if button == mouse.LEFT:
                terrain = self.levelView.sceneMap.layers['terrain']
                if self.linePreview:
                    self.linePreview.vl.delete()
                mousePos = self.translateMouseClick(x,y)
                terrain.addLine(self.lineStart[0], self.lineStart[1], mousePos[0], mousePos[1])
                self.linePreview = None
                


class ObjectController(BaseController):
    name = "object"
    def __init__(self, levelView, window):
        super(ObjectController, self).__init__(levelView, window)
    
    def on_mouse_press(self, x, y, button, modifiers):
        print "object"
        
    def on_mouse_release(self, x, y, button, modifiers):
        print "release"


class AestheticController(BaseController):
    name = "aesthetic"
    def __init__(self, levelView, window):
        super(AestheticController, self).__init__(levelView, window)


class LevelView(object):
    modes = list()
    def __init__(self, window):
        #clears to a grey.
        glClearColor(0.4,0.4,0.4,0.)
        self.sceneMap = None
        self.edited = False
        self.size = (0,0)
        self.scale = 1.0
        self.layer = None
        self.mode = None
        self.layers = {
            "base" : BaseController(self, window),
            "terrain" : TerrainController(self, window),
            "object" : ObjectController(self, window),
            "foreground" : AestheticController(self, window)
        }
        self.keys = Keys(self)
        window.push_handlers(self)
        window.push_handlers(self.keys)
        
    def setActiveLayer(self, layer, window):
        window.remove_handlers(self.mode)
        self.layer = layer
        self.mode = self.layers[layer]
        window.push_handlers(self.mode)
        
    def newLevel(self, values):
        self.sceneMap = SceneMap(self.size)
        self.sceneMap.width = int(values["width"])
        self.sceneMap.height = int(values["height"])
        self.sceneMap.forceFocus = True
    
    def loadLevel(self, fileName):
        print "map loaded"
        self.sceneMap = SceneMap.fromMapFile(fileName)
    
    def saveLevel(self,  fileName):
        print "map saved"
            
    def resize(self, width, height):
        self.size = (width, height)
        if self.sceneMap:
            self.sceneMap.viewportWidth = width
            self.sceneMap.viewportHeight = height
            
    def updateGrid(self, values):
        pass
    
    def update(self, dt):
        if self.sceneMap:
            self.sceneMap.update(dt)
            self.mode.update(dt)
    
    def draw(self):
        if self.sceneMap:
            glPushMatrix()
            glScalef(self.scale, self.scale, 1.0)
            self.sceneMap.draw()
            glPopMatrix()
