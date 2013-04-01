'''
    Scene Graph implementation
'''
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree
import pyglet
from pyglet.graphics import OrderedGroup
from pyglet.gl import glColor3f, glColor4f, glLineWidth, glBegin, glVertex3i,\
    glVertex3f, glEnd, glPushMatrix, glPopMatrix, glTranslatef,\
    GL_QUADS, glColorMask, GL_FALSE, GL_TRUE

'''
    z position of layers.
'''
class DrawZPos(object):
    TERRAIN_LINES = 7 #for debug
    FRONT = 6
    SPRITES = 5
    FOREGROUND = 4


''' 
    class BaseLayer
'''
class BaseLayer(object):
    def __init__(self):
        self.viewportWidth
        self.viewportHeight
        self.name = ""
        
    def setView(self, sceneGraph, x, y):
        self.group.setView(x, y)
        self.viewportWidth = sceneGraph.viewportWidth
        self.viewportHeight = sceneGraph.viewportHeight
    
    def update(self, dt):
        pass
        
'''  
    Aesthetic Layer 
'''
class AestheticGroup(OrderedGroup):
    focusX = 0
    focusY = 0
    visible = True
    def __init__(self, z_order):
        super(AestheticGroup, self).__init__(z_order)
        
    def setView(self, x, y):
        self.focusX = x
        self.focusY = y

    def set_state(self):
        glTranslatef(self.focusX, self.focusY, 0)
        if self.visible == False:
            glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
        
    def unset_state(self):
        glTranslatef(-self.focusX, -self.focusY, 0)
        if self.visible == False:
            glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
        
class Visual(object):
    def __init__(self, name, sprite, (x,y), scale, rot, layerOpacity):
        self.name = name
        self.sprite = sprite
        self.x = y
        self.y = x
        self.scale = scale
        self.rot = rot
        self.absOpacity = 255
        self.opacity = self.absOpacity * layerOpacity
        
    def _set_opacity(self, opacity):
        self._opacity = opacity
        self.sprite.opacity = opacity
    def _get_opacity(self):
        return self._opacity
    opacity = property(_get_opacity, _set_opacity)
        
    def setOpacity(self, layerOpacity, value):
        self.absOpacity = value
        self.opacity = layerOpacity * self.absOpacity
        self.sprite.opacity = self.opacity
        
class AestheticLayer(BaseLayer):
    dir = 'visuals'
    visible = True
    opacity = 1.0
    
    def __init__(self, name, batch, z_order):
        self.batch = batch
        self.name = name
        self.group = AestheticGroup(z_order)
        self.z_order = z_order
        self.items = []
        
    def teardown(self):
        for item in self.items:
            item.sprite.delete()
        
    def setVisible(self, value):
        self.visible = value
        self.group.visible = value
        
    def setZOrder(self, value):
        self.z_order = value
        self.group = AestheticGroup(value)
        for item in self.items:
            item.sprite.group = self.group
        
    def setOpacity(self, value):
        self.opacity = value
        for item in self.items:
            item.opacity = item.absOpacity * self.opacity
        
    def addItem(self, path, item, (x,y), scale, rot):
        file = item + ".png"
        img = pyglet.image.load(os.path.join(path, self.dir, file))
        sprite = pyglet.sprite.Sprite(img, batch=self.batch, group=self.group)
        sprite.x = x
        sprite.y = y
        sprite.scale = scale
        sprite.rotation = rot
        self.items.append(Visual(item, sprite, (x,y), scale, rot, self.opacity))
        
        
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
class ObjectGroup(OrderedGroup):
    focusX = 0
    focusY = 0
    def __init__(self):
        super(ObjectGroup, self).__init__(DrawZPos.SPRITES)
        
    def setView(self, x, y):
        self.focusX = x
        self.focusY = y

    def set_state(self):
        glTranslatef(self.focusX, self.focusY, 0)
        
    def unset_state(self):
        glTranslatef(-self.focusX, -self.focusY, 0)
        
class Object(object):
    def __init__(self, name, sprite, (x,y), scale, rot):
        self.name = name
        self.sprite = sprite
        self.x = y
        self.y = x
        self.scale = scale
        self.rot = rot
        
    '''
        doesPointIntersect()
        returns boolean based on whether point is over line
        given threshold of width
    '''
    def doesPointIntersect(self, point, threshold):
        pass
class ObjectLayer(BaseLayer):
    items = list()
    group = ObjectGroup()
    dir = 'objects'
    name = 'object'
    
    def __init__(self, batch):
        self.batch = batch
        
    def addItem(self, path, item, (x,y), scale, rot):
        file = item + ".png"
        img = pyglet.image.load(os.path.join(path, self.dir, file))
        sprite = pyglet.sprite.Sprite(img, batch=self.batch, group=self.group)
        sprite.x = x
        sprite.y = y
        sprite.scale = scale
        sprite.rotation = rot
        self.items.append(Object(item, sprite, (x,y), scale, rot))
        
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
    focusX = 0
    focusY = 0
    def __init__(self):
        super(TerrainGroup, self).__init__(DrawZPos.TERRAIN_LINES)
        
    def setView(self, x, y):
        self.focusX = x
        self.focusY = y

    def set_state(self):
        glLineWidth(2)
        glTranslatef(self.focusX, self.focusY, 0)
        
    def unset_state(self):
        glTranslatef(-self.focusX, -self.focusY, 0)
        
class TerrainLayer(BaseLayer):
    ''' initial variables
    '''
    lines = list()
    group = TerrainGroup()
    colors = dict()
    name = 'terrain'
    
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
    expands upon list container for named retrieval of items
'''
class Layers(list):
    def __init__(self):
        self.by_name = {}
    
    def addNamed(self, layer, name):
        self.append(layer)
        self.by_name[name] = layer
        self.by_name[name].name = name
        
    def delete(self, name):
        item = self.by_name[name]
        self.by_name.pop(name)
        self.remove(item)
    
    def __getitem__(self, item):
        if isinstance(item, int):
            return self[item]
        return self.by_name[item]

'''
    sceneGraph
    
'''
class SceneGraph(object):
    FILE_EXT = 'lvl'

    def __init__(self, viewportSize, width=0, height=0, debugMode=False):
        self.batch = pyglet.graphics.Batch()
        #
        self.width = width
        self.height = height
        self.focusX, self.focusY = 0, 0
        self.viewportWidth, self.viewportHeight = viewportSize
        self.backColour = [0.,0.,0.]
        self.sourcePath = 'assets'
        self.name = 'default'
        # layers:
        self.layers = Layers()
        self.layers.addNamed(AestheticLayer("foreground", self.batch, DrawZPos.FOREGROUND), "foreground")
        self.layers.addNamed(ObjectLayer(self.batch), "object")
        self.layers.addNamed(TerrainLayer(self.batch, dl=debugMode), "terrain")
        
    def addAestheticLayer(self, name, z_order):
        self.layers.addNamed(AestheticLayer(name, self.batch, z_order), name)
        
    def deleteAestheticLayer(self, name):
        self.layers[name].teardown()
        self.layers.delete(name)
        
    @classmethod
    def fromMapFile(cls, fileName, viewportSize, debugMode=False):
        #TODO load xml file and parse to create graph from file
        graph = cls(viewportSize, width, height, debugMode)
        return graph
     
     
    '''
        saves map to xml file
    '''
    def saveMapToFile(self, fileName):
        root = Element('map')
        root.set('width', str(self.width))
        root.set('height', str(self.height))
        head = SubElement(root, 'head')
        name = SubElement(head, 'name')
        name.text = self.name
        source = SubElement(head, 'source')
        source.text = self.sourcePath
        layers = SubElement(root, 'layers')
        
        terrainLayer = self.layers["terrain"]
        if len(terrainLayer.lines) > 0:
            terrain_layer = SubElement(layers, 'terrainLayer')
            #print "terrain" + " items:"
            for line in terrainLayer.lines:
                #print line
                e = SubElement(terrain_layer, 'line')
                e.set('x1', str(line.x1))
                e.set('y1', str(line.y1))
                e.set('x2', str(line.x2))
                e.set('y2', str(line.y2))
    
        objectLayer = self.layers["object"]
        if len(objectLayer.items) > 0:
            object_layer = SubElement(layers, 'objectLayer')
            #print "object" + " items:"
            for item in objectLayer.items:
                #print item
                e = SubElement(object_layer, 'item')
                e.set('name', item.name)
                e.set('x', str(item.x))
                e.set('y', str(item.y))
                if item.scale != 1.0:
                    es = SubElement(e, 'scale')
                    es.text = str(item.scale)
                if item.rot != 0:
                    er = SubElement(e, 'rotation')
                    er.text = str(item.rot)
        
        for layer in self.layers:
            if layer.name != "terrain" and \
                layer.name != "object" and \
                len(layer.items) > 0:
                aesthetic_layer = SubElement(layers, 'aestheticLayer')
                aesthetic_layer.set('name', layer.name)
                aesthetic_layer.set('visible', str(layer.visible))
                aesthetic_layer.set('opacity', str(layer.opacity))
                for item in layer.items:
                    print item.name
                    e = SubElement(aesthetic_layer, 'item')
                    e.set('name', item.name)
                    e.set('x', str(item.x))
                    e.set('y', str(item.y))
                    if item.scale != 1.0:
                        es = SubElement(e, 'scale')
                        es.text = str(item.scale)
                    if item.rot != 0:
                        er = SubElement(e, 'rotation')
                        er.text = str(item.rot)
        tree = ElementTree(root)
        tree.write(fileName)
        
        
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
        glTranslatef(self.focusX, self.focusY, 0)
        glBegin(GL_QUADS)
        glVertex3i(0, 0, 0)
        glVertex3f(0, float(self.height), 0)
        glVertex3f(float(self.width), float(self.height), 0)
        glVertex3f(float(self.width), 0, 0)
        glEnd()
        glTranslatef(-self.focusX, -self.focusY, 0)
    
    '''
        draw()
        draws whole scene.
    '''
    def draw(self):
        glPushMatrix()
        self.drawBackground()
        self.batch.draw()
        glPopMatrix()
        
        
        










