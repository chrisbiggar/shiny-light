'''
Implementation of scene controller and scene manipulation tools.
'''
import pyglet
from pyglet.window import mouse, key
from pyglet.gl import glPopMatrix, glPushMatrix, \
    glScalef, glClearColor
import py2d.scenegraph as scenegraph
from py2d.scenegraph import SceneGraph


MAP_FILE_EXT = 'lvl'

'''
    BaseTool
    abstract. base for all scene tools.
'''
class BaseTool(object):
    NAME = "Base"
    def __init__(self, scene):
    	self.scene = scene
    
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
    	
    def activate(self):
        return self
        
    def deactivate(self):
        pass
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.scene.graph != None:
            self.scene.graph.moveFocus(dx, dy)
            

          
'''
    PlotLineTool
    allows user to place a line in the terrain layer. 
'''      
#TODO recode this removing "line preview" and adding to batch in tool itself.
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
class PlotLineTool(BaseTool):
    NAME = "Line"
    lineStart = (0,0)
    linePreview = None
    mousePoint = (0,0)
    snapMode = False
    
    def __init__(self, scene):
    	super(PlotLineTool, self).__init__(scene)
    	
    def activate(self):
        return self
        
    def deactivate(self):
        pass
    
    def preview(self, x, y):
        if self.linePreview:
            self.linePreview.vl.delete()
        layer = self.scene.currentLayer
        mousePos = self.translateMouseClick(x,y)
        if self.lineStart == None:
            self.lineStart = mousePos
        self.linePreview = layer.addLine(mousePos[0], mousePos[1], self.lineStart[0], self.lineStart[1], True)
            
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
        if closestPoint == None:
            return None
        return (closestPoint.x, closestPoint.y)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.preview(x,y)
    
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
            if self.linePreview:
                self.linePreview.vl.delete()
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
        
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self.preview is not None and self.active is True:
            self.preview.x = x
            self.preview.y = y
        
    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        if self.preview is not None and self.active is True:
            self.scene.currentLayer.addItem(self.scene.graph.sourcePath, self.selectedName, (x,y))
        
        
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
    
    def activate(self):
        return self
        
    def deactivate(self):
        pass
    	
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
        
        ''' these hold references.
        '''
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
        self.graph = SceneGraph(self.size, editorMode=True)
        self.graph.width = width
        self.graph.height = height
        self.graph.forceFocus = True
    
    def loadLevel(self, fileName):
        print "graph loaded"
        self.graph = SceneGraph.fromMapFile(fileName)
    
    def saveLevel(self,  fileName):
        print "graph saved"
            
    def resize(self, width, height):
        self.size = (width, height)
        if self.graph:
            self.graph.viewportWidth = width
            self.graph.viewportHeight = height
            
    def updateGrid(self, values):
        pass
    
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
    

            
