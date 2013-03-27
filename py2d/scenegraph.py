'''
    Scene Graph implementation
'''
import os
import pyglet
from pyglet.graphics import OrderedGroup
from pyglet.gl import glColor3f, glLineWidth, glBegin, glVertex3i,\
    glVertex3f, glEnd, glPushMatrix, glPopMatrix, glTranslatef, GL_QUADS

'''
    z position of layers.
'''
class DrawZPos(object):
    TERRAIN_LINES = 4 #for debug
    FRONT = 3
    SPRITES = 2
    FOREGROUND = 1


''' 
    class BaseLayer
'''
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
        self.name = ""
        self.batch = pyglet.graphics.Batch()
        
    def setView(self, sceneGraph, x, y):
        self.focusX = x
        self.focusY = y
        self.viewportWidth = sceneGraph.viewportWidth
        self.viewportHeight = sceneGraph.viewportHeight
    
    def update(self, dt):
        pass
        
'''  
    Aesthetic Layer 
'''
class Visual(object):
    def __init__(self, name, sprite, (x,y)):
        self.name = name
        self.sprite = sprite
        self.x = y
        self.y = x
        
class AestheticLayer(BaseLayer):
    items = list()
    group = OrderedGroup(DrawZPos.FOREGROUND)
    dir = 'visuals'
    sources = list()
    
    def __init__(self, batch):
        self.batch = batch
        
    def addItem(self, path, item, (x,y)):
        file = item + ".png"
        img = pyglet.image.load(os.path.join(path, self.dir, file))
        sprite = pyglet.sprite.Sprite(img, batch=self.batch, group=self.group)
        sprite.x = x
        sprite.y = y
        self.items.append(Visual(item, sprite, (x,y)))
        
        
    '''
        doesPointIntersect()
        returns boolean based on whether point is over line
        given threshold of width
    '''
    def isPointOverItem(self, point, threshold):
        pass


'''
    Object Layer
'''
class Object(object):
    
    def __init__(self, name, sprite, (x,y)):
        self.name = name
        self.sprite = sprite
        self.x = y
        self.y = x
        
    '''
        doesPointIntersect()
        returns boolean based on whether point is over line
        given threshold of width
    '''
    def doesPointIntersect(self, point, threshold):
        pass
class ObjectLayer(BaseLayer):
    items = list()
    group = OrderedGroup(DrawZPos.FOREGROUND)
    dir = 'objects'
    
    def __init__(self, batch):
        self.batch = batch
        
    def addItem(self, path, item, (x,y)):
        file = item + ".png"
        img = pyglet.image.load(os.path.join(path, self.dir, file))
        sprite = pyglet.sprite.Sprite(img, batch=self.batch, group=self.group)
        sprite.x = x
        sprite.y = y
        self.items.append(Object(item, sprite, (x,y)))
        
    def isPointOverItem(self, point, threshold):
        pass
        

''' 
    Terrain Layer
    manages the terrain line of sim
'''
''' Class Line
    stores a current terrain layer line and its vertex list 
'''
class Line(object):
    def __init__(self, x1, y1, x2, y2, vl=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.vl = vl # gl vertex list
    
    '''
        function doesPointIntersect()
        returns boolean based on whether point is over line
        given threshold of width
    '''
    def doesPointIntersect(self, point, threshold):
        pass
        
class TerrainGroup(OrderedGroup):
    def __init__(self):
        super(TerrainGroup, self).__init__(DrawZPos.TERRAIN_LINES)

    def set_state(self):
        glLineWidth(2)
        
    def unset_state(self):
        pass
class TerrainLayer(BaseLayer):
    ''' initial variables
    '''
    lines = list()
    group = TerrainGroup()
    colors = dict()
    
    def __init__(self, batch=None, dl=False):
        self.drawLines = dl
        self.batch = batch
        self.initColors()
        
        
    def initColors(self):
        self.colors['Blue'] = (0.,0.,255.)
        self.colors['Red'] = (255.,0.,0.)
        self.colors['Green'] = (0.,255.,.0)
        self.colors['White'] = (255.,255.,255.)
        self.colors['Black'] = (0.,0.,0.)
        self.curColor = self.colors['White']
    
    '''
        sets the color of all lines in layer
    '''
    def setLineColor(self, color):
        try:
            color = self.colors[color]
            self.curColor = color
            for line in self.lines:
                line.vl.colors = [color[0],color[1],color[2],color[0],color[1],color[2]]
        except KeyError:
            print "Line Colour Key Error"
    
    '''
        adds a line to the terrain layer upon preview being false,
        while preview is true, line is not stored permanetely and just
        temporarly added to batch
    '''
    def addLine(self, x1, y1, x2, y2):
        vl = None
        if self.drawLines:
            vl = self.batch.add(2, pyglet.gl.GL_LINES, self.group,
                ('v2i', (x1, y1, x2, y2)),
                ('c3f', (self.curColor[0],self.curColor[1],self.curColor[2])*2))
        line = Line(x1, y1, x2, y2, vl)
        self.lines.append(line)
    
    
    '''
        returns the line that click is over
    '''
    def isPointOverItem(self, point, threshold):
        for line in self.lines:
            if line.doesPointIntersect(point, threshold) == True:
                return line
        return None
            
'''
    Layers
    expands upon list container for named retrievel of items
'''
class Layers(list):
    def __init__(self):
        self.by_name = {}
    
    def addNamed(self, layer, name):
        self.append(layer)
        self.by_name[name] = layer
        self.by_name[name].name = name
    
    def __getitem__(self, item):
        if isinstance(item, int):
            return self[item]
        return self.by_name[item]

'''
    sceneGraph
'''
class SceneGraph(object):
    FILE_EXT = 'lvl'

    def __init__(self, viewportSize, width=0, height=0, editorMode=False):
        self.batch = pyglet.graphics.Batch()
        #
        self.width = width
        self.height = height
        self.focusX, self.focusY = 0, 0
        self.viewportWidth, self.viewportHeight = viewportSize
        self.backColour = [0.,0.,0.]
        self.sourcePath = 'assets'
        # layers:
        self.layers = Layers()
        self.layers.addNamed(AestheticLayer(self.batch), "foreground")
        self.layers.addNamed(ObjectLayer(self.batch), "object")
        self.layers.addNamed(TerrainLayer(self.batch, dl=editorMode), "terrain")
        
    @classmethod
    def fromMapFile(cls, fileName, viewportSize):
        pass
     
    def saveMapToFile(self, fileName):
        print "save: " + fileName
        
        
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
    
    '''
        drawBackground()
        draws background colour or image of scene.
    '''
    def drawBackground(self):
        glColor3f(self.backColour[0],self.backColour[1],self.backColour[2])
        glBegin(GL_QUADS)
        glVertex3i(0, 0, 0)
        glVertex3f(0, float(self.height), 0)
        glVertex3f(float(self.width), float(self.height), 0)
        glVertex3f(float(self.width), 0, 0)
        glEnd()
    
    '''
        draw()
        draws whole scene.
    '''
    def draw(self):
        glPushMatrix()
        glTranslatef(self.focusX, self.focusY, 0) #move this to individual layers
        self.drawBackground()
        self.batch.draw()
        glPopMatrix()
        
        
        










