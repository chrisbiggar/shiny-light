'''
Implementation of scene controller and scene manipulation tools.
'''
import pyglet
from pyglet.window import mouse, key
from pyglet.gl import glPopMatrix, glPushMatrix, \
    glScalef, glClearColor, glLineWidth
import py2d.scenegraph as scenegraph
from py2d.scenegraph import SceneGraph


'''
    BaseTool
    abstract. base for all scene tools.
'''
class BaseTool(object):
    NAME = "Base"
    def __init__(self, scene):
    	self.scene = scene
    	
    def activate(self):
        return self
        
    def deactivate(self):
        pass
    
    def translateMouseClick(self, x=0, y=0, point=None):
        if point != None:
            x = point[0] - self.scene.graph.focusX
            y = point[1] - self.scene.graph.focusY
            return (x,y)
        else:
            x = x - self.scene.graph.focusX
            y = y - self.scene.graph.focusY
            return (x,y)
            
    # input event handlers 
    def on_mouse_motion(self, x, y, dx, dy):
        pass
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass
    def on_mouse_press(self,x, y, button, modifiers):
        pass
    def on_mouse_scdfroll(self,x, y, scroll_x, scroll_y):
        pass
    def on_mouse_release(self, x, y, button, modifiers):
        pass
    def key_press(self, symbol, modifiers):
        pass
    def key_release(self, symbol, modifiers):
        pass
        

'''
    PanTool
    allows user to pan scene using mouse.
'''
class PanTool(BaseTool):
    NAME = "Pan"
    def __init__(self, scene):
    	super(PanTool, self).__init__(scene)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.scene.graph != None:
            self.scene.graph.moveFocus(dx, dy)
            

          
'''
    PlotLineTool
    allows user to place a line in the terrain layer. 
'''
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
class PlotLineTool(BaseTool):
    NAME = "Line"
    lineStart = (0,0)
    mousePoint = (0,0)
    snapMode = False
    preview = None
    
    def __init__(self, scene):
    	super(PlotLineTool, self).__init__(scene)
    
    def doPreview(self, x2, y2):
        if self.lineStart is None:
            return
        if self.preview is not None:
            self.preview.delete()
            self.preview = None
        x1,y1 = self.lineStart
        x2,y2 = self.translateMouseClick(x2,y2)
        # create vl of line preview
        batch = self.scene.graph.batch
        group = self.scene.currentLayer.group
        curColor = self.scene.currentLayer.curColor
        self.preview = batch.add(2, pyglet.gl.GL_LINES, group,
                ('v2i', (x1, y1, x2, y2)),
                ('c3f', (curColor[0],curColor[1],curColor[2])*2))
            
    def closestPointToMouse(self):
        lines = self.scene.graph.layers["terrain"].lines
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
        return (closestPoint.x, closestPoint.y)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.doPreview(x,y)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if self.snapMode == True:
                ''' snap mode causes line start
                    to snap to nearest point '''
                self.mousePoint = (x,y)
                self.lineStart = self.closestPointToMouse()
            else:
                translatedCoords = self.translateMouseClick(x,y)
                self.lineStart = translatedCoords

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            terrain = self.scene.graph.layers['terrain']
            if self.preview is not None:
                self.preview.delete()
                self.preview = None
            mousePos = self.translateMouseClick(x,y)
            terrain.addLine(self.lineStart[0], self.lineStart[1], mousePos[0], mousePos[1])
            self.linePreview = None
            
'''
    PlaceItemTool
    allows user to place aesthetic or object items into correct layer
'''
class PlaceItemTool(BaseTool):
    NAME="PlaceItem"
    selectedName = None
    selectedItem = None
    preview = None
    active = False
    
    def __init__(self, scene):
        super(PlaceItemTool, self).__init__(scene)
        
    def activate(self):
        self.active = True
        if self.preview is not None:
            self.preview.visible = True
        return self
        
    def deactivate(self):
        self.active = False
        if self.preview is not None:
            self.preview.visible = False
    
    def setSelectedItem(self, path):
        if path is None:
            self.selectedName = None
            self.selectedItem = None 
        # extracts the file name without extention
        f = path.__getslice__(path.rfind("/") + 1, len(path))
        self.selectedName = f.__getslice__(0, f.find("."))
        self.selectedItem = pyglet.image.load(path)
        self.preview = pyglet.sprite.Sprite(
                self.selectedItem, batch=self.scene.graph.batch, 
                group=self.scene.currentLayer.group)
        if self.active == False:
            self.preview.visible = False
            
    def key_press(self, symbol, modifiers):
        if self.preview is not None:
            if modifiers & key.MOD_CTRL:
                if symbol == key.MINUS:
                    self.preview.scale -= 0.05
                elif symbol == key.EQUAL:
                    self.preview.scale += 0.05
                elif symbol == key.S:
                    self.preview.rotation += 5
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self.preview is not None and self.active is True:
            self.preview.x, self.preview.y = self.translateMouseClick(x,y)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.preview is not None and self.active is True:
            x,y = self.translateMouseClick(x,y)
            self.scene.currentLayer.addItem(self.scene.graph.sourcePath, self.selectedName, (x,y), self.preview.scale, self.preview.rotation)
        
        
'''
    SelectTool
    allows user to select an object.
'''
class SelectTool(BaseTool):
    NAME = "Select"
    def __init__(self, scene, window):
    	super(SelectTool, self).__init__(scene)
    	self.window = window
    	self.selectedItem = None
    	
    def on_mouse_motion(self, x, y, dx, dy):
        self.mousePoint = (x, y)
        if self.scene.currentLayer.isPointOverItem(self.mousePoint, 5) != None:
            # change cursor
            pass
        else:
            # change back
            pass
        
    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        # self.selectedItem = self.scene.currentLayer.isPointOverItem(self.mousePoint, 5)
        # self.window.dispatch_event('on_select_item')
        # fake.
        self.selectedItem = scenegraph.Line(24,24,24,24)
        self.window.dispatch_event('on_select_item')
        


'''
    class Keys
    responds to keypresses, notifying an event handler 
    while storing the current state of the keys for querying
'''
class Keys(key.KeyStateHandler):
    def __init__(self, parent):
        self.parent = parent

    def on_key_press(self, symbol, modifiers):
        self.parent.key_press(symbol, modifiers)
        super(Keys, self).on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.parent.key_release(symbol, modifiers)
        super(Keys, self).on_key_release(symbol, modifiers)

class GridGroup(pyglet.graphics.OrderedGroup):
    focusX = 0
    focusY = 0
    def __init__(self, scene):
        super(GridGroup, self).__init__(8)
        self.scene = scene
        
    def set_state(self):
        glLineWidth(1)
        '''if self.scene.graph is not None:
            glTranslatef(self.scene.graph.focusX, self.scene.graph.focusY, 0)'''
        
    def unset_state(self):
        '''if self.scene.graph is not None:
            glTranslatef(-self.scene.graph.focusX, -self.scene.graph.focusY, 0)'''
        pass
        
class Grid(object):
    def __init__(self, scene, window):
        self.visible = False
        self.snap = False
        self.hSpacing = 50
        self.vSpacing = 50
        self.hOffset = 0
        self.vOffset = 0
        self.batch = pyglet.graphics.Batch()
        self.group = GridGroup(scene)
        self.lines = list()
        self.window = window
        
    def update(self):
        for line in self.lines:
            line.delete()
        self.lines = []
        if self.visible == True:
            hCount = self.window.width / self.hSpacing
            i = 1
            while i <= hCount:
                x = (self.hSpacing * i) + self.hOffset
                y1 = 0
                y2 = self.window.height
                self.lines.append(self.batch.add(2, pyglet.gl.GL_LINES, self.group,
                    ('v2i', (x, y1, x, y2)),
                    ('c3f', (1.0,1.0,1.0)*2)))
                i = i + 1
            vCount = self.window.height / self.vSpacing
            i = 1
            while i <= vCount:
                y = (self.vSpacing * i) + self.vOffset
                x1 = 0
                x2 = self.window.width
                self.lines.append(self.batch.add(2, pyglet.gl.GL_LINES, self.group,
                    ('v2i', (x1, y, x2, y)),
                    ('c3f', (1.0,1.0,1.0)*2)))
                i = i + 1

'''
    class SceneController
    manages editing of the level scene.
'''
class SceneController(object):
    def __init__(self, window):
        self.tools = {
            "pan" : PanTool(self),
            "plotline" : PlotLineTool(self),
            "placeitem" : PlaceItemTool(self),
            "select" : SelectTool(self, window)
        }
        #clears to a grey.
        glClearColor(0.4,0.4,0.4,0.)
        self.graph = None
        self.edited = False
        self.size = (0,0)
        self.scale = 1.0
        self.keys = Keys(self)
        self.mouseCoord = (0,0)
        self.grid = Grid(self, window)
        self.currentLayer = None
        self.currentTool = None
        self.keys = Keys(self)
        window.push_handlers(self)
        window.push_handlers(self.keys)
        
    def setActiveLayer(self, name):
        # sets the reference to the current layer
        if name == "none":
            self.currentLayer = None
            self.currentTool = None
            return
        try:
            self.currentLayer = self.graph.layers[name]
        except KeyError:
            print "Set Active Layer Key Error"
                    
        
    def setCurrentTool(self, tool):
        for t in self.tools:
            self.tools[t].deactivate()
        # search tool list for name and set
        # tool with given name to current tool.
        try:
            self.currentTool = self.tools[tool].activate()
        except KeyError:
            print "Set Current Tool Key Error"
        
        
    def newLevel(self, width, height):
        self.graph = SceneGraph(self.size, width, height, debugMode=True)
        self.graph.forceFocus = True
    
    def loadLevel(self, fileName):
        print "graph loaded"
        #TODO delete old graph and assets
        #self.graph = SceneGraph.fromMapFile(fileName, self.size)
        #self.graph.forceFocus = True
            
    def resize(self, width, height):
        self.size = (width, height)
        if self.graph:
            self.graph.viewportWidth = width
            self.graph.viewportHeight = height
            
    def update(self, dt):
        if self.graph:
            self.pollPanKeys(dt)
            self.graph.update(dt)
    
    def draw(self):
        if self.graph:
            glPushMatrix()
            glScalef(self.scale, self.scale, 1.0)
            self.graph.draw()
            glPopMatrix()
        self.grid.batch.draw()
            
    
    # input event handlers      
    def pollPanKeys(self, dt):
        moveRate = dt * 400
        if self.keys[key.UP]:
            self.graph.moveFocus(y=-moveRate)
        if self.keys[key.DOWN]:
            self.graph.moveFocus(y=moveRate)
        if self.keys[key.LEFT]:
            self.graph.moveFocus(moveRate)
        if self.keys[key.RIGHT]:
            self.graph.moveFocus(-moveRate)
            
    def key_press(self, symbol, modifiers):
        if symbol == key.HOME:
            if self.graph != None:
                self.graph.setFocus(0,0)
        if self.currentTool is not None:
        	self.currentTool.key_press(symbol, modifiers)
    
    def key_release(self, symbol, modifiers):
        if self.currentTool is not None:
        	self.currentTool.key_release(symbol, modifiers)
               
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouseCoord = (x,y)
        if self.currentTool is not None:
        	self.currentTool.on_mouse_motion(x, y, dx, dy)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.currentTool == None:
            if self.graph != None:
                self.graph.moveFocus(dx, dy)
        if self.currentTool is not None:
        	self.currentTool.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        
    def on_mouse_press(self,x, y, button, modifiers):
        if self.currentTool is not None:
        	self.currentTool.on_mouse_press(x, y, button , modifiers)
    
    def on_mouse_scdfroll(self,x, y, scroll_x, scroll_y):
        if self.currentTool is not None:
        	self.currentTool.on_mouse_scdfroll(x, y, scroll_x, scroll_y)
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.currentTool is not None:
        	self.currentTool.on_mouse_release(x, y, button, modifiers)
    

            
