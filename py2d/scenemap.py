'''
Scene Map implementation

'''
import pyglet
from pyglet.graphics import Batch
from pyglet.gl import *

class DrawZPos(object):
	TERRAIN_LINES = 1 #for debug
	FRONT = 2
	SPRITES = 3
	FOREGROUND = 4

class BaseLayer(object):
    def __init__(self):
        self.focusX = 0
        self.focusY = 0
        self.viewportWidth
        self.viewportHeight
        #self.width = tileMap.width
        #self.height = tileMap.height
        self.objects = list()
        self.visible = True
        
    def setView(self, sceneMap, x, y):
        self.focusX = x
        self.focusY = y
        self.viewportWidth = sceneMap.viewportWidth
        self.viewportHeight = sceneMap.viewportHeight
    
    def update(self, dt):
        pass
    
class AestheticLayer(BaseLayer):
    def __init__(self, name):
        self.name = name

class ObjectLayer(BaseLayer):
    name = "object"
    def __init__(self):
        pass

''' Terrain Layer
'''
class TerrainGroup(pyglet.graphics.OrderedGroup):
    def __init__(self):
        super(TerrainGroup, self).__init__(DrawZPos.TERRAIN_LINES)    

    def set_state(self):
    	glColor3f(0.5,0.0,0.6)
    	glLineWidth(3)
        pass
        
    def unset_state(self):
        pass
    
class Line(object):
    def __init__(self, x1, y1, x2, y2, vl=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.vl = vl # gl vertex list
    
    def checkClick():
        #depending, bring up dialog or delete line.
        #self.vl.delete()
        pass
       
class TerrainLayer(BaseLayer):
    ''' initial variables
    '''
    name = "terrain"
    lines = list()
    group = TerrainGroup()
    visible = True
    
    def __init__(self, batch=None, dl=True):
        self.drawLines = dl
        self.batch = batch
        
    def addLine(self, x1, y1, x2, y2, preview=False):
        vl = None
        if self.drawLines:
            vl = self.batch.add(2, pyglet.gl.GL_LINES, self.group,
                ('v2i', (x1, y1, x2, y2)),
                ('c3f', (.8,.8,.8)*2))
        line = Line(x1, y1, x2, y2, vl)
        if not preview:
        	self.lines.append(line)
        return line
        

class Layers(list):
    def __init__(self):
        self.by_name = {}
    
    def addNamed(self, layer, name):
        self.append(layer)
        self.by_name[name] = layer
    
    def __getitem__(self, item):
        if isinstance(item, int):
            return self[item]
        return self.by_name[item]

class SceneMap(object):
    def __init__(self, viewportSize):
        self.batch = pyglet.graphics.Batch()
        #
        self.width = 0
        self.height = 0
        self.focusX, self.focusY = 0, 0
        self.viewportWidth, self.viewportHeight = viewportSize
        self.backColour = [0.,0.,0.]
        # layers:
        self.layers = Layers()
        self.layers.addNamed(AestheticLayer("foreground"), "foreground")
        self.layers.addNamed(ObjectLayer(), "object")
        self.layers.addNamed(TerrainLayer(self.batch, dl=True), "terrain")
        
    @classmethod
    def fromMapFile(cls, filename, viewportSize):
        pass
        
    def moveFocus(self, x=0, y=0):
        self.setFocus(self.focusX + x, self.focusY + y)
        
    previousFocus = None
    forceFocus = False
    def setFocus(self, x, y):
        newFocus = (x, y)
        
        # check for redundant arg
        if self.previousFocus == newFocus:
            return
        self.previousFocus = newFocus
        
        x = int(x)
        y = int(y)
        
        #restrict view to within map size
        if self.forceFocus == False:
            if -x >= self.width - self.viewportWidth:
                x = -(self.width - self.viewportWidth)
            elif -x < 0:
                x = 0
            if -y >= self.height - self.viewportHeight:
                y = -(self.height - self.viewportHeight)
            elif -y < 0:
                y = 0
        
        self.focusX = x
        self.focusY = y
        # update layers
        for layer in self.layers:
            layer.setView(self, x, y)
        
    def update(self, dt):
        for layer in self.layers:
            layer.update(dt)
            
    def drawBackground(self):
        glColor3f(self.backColour[0],self.backColour[1],self.backColour[2])
        glBegin(GL_QUADS)
        glVertex3i(0, 0, 0)
        glVertex3f(0, float(self.height), 0)
        glVertex3f(float(self.width), float(self.height), 0)
        glVertex3f(float(self.width), 0, 0)
        glEnd()
       
    def draw(self):
        glPushMatrix()
        glTranslatef(self.focusX, self.focusY, 0) #move this to individual layers
        self.drawBackground()
        self.batch.draw()
        glPopMatrix()
        
        
        











