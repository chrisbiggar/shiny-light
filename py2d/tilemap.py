'''
tmx loader and tilemap system

'''
import sys
import struct
import collections
from xml.etree import ElementTree
import pyglet
from pyglet import image
from pyglet.gl import *


        
class Cell(pyglet.sprite.Sprite):
    def __init__(self, indexX, indexY, x, y, tile, b):
        super(Cell, self).__init__(tile.image, x, y, batch=b)
        self.indexX, self.indexY = indexX, indexY
        self.bottomLeft = (x, y)
        self.left = x
        self.right = x + tile.tileWidth
        self.top = y
        self.bottom = y + tile.tileHeight
        self.center = (x + tile.tileWidth // 2, \
            y + tile.tileHeight // 2)
            
class TileLayer(object):
    def __init__(self, name, tileMap, visible=True):
        self.viewportWidth = tileMap.viewportWidth
        self.viewportHeight = tileMap.viewportHeight
        self.focusX = 0
        self.focusY = 0
        self.width = tileMap.width
        self.height = tileMap.height
        self.tileWidth = tileMap.tileWidth
        self.tileHeight = tileMap.tileHeight
        self.widthPixels = self.width * self.tileWidth
        self.heightPixels = self.height * self.tileHeight
        self.name = None
        self.opacity = -1
        self.visible = visible
        self.properties = {}
        self.cells = {}
        self.batch = pyglet.graphics.Batch()
    
    @classmethod
    def fromElement(cls, tag, tileMap):
        layer = cls(tag.attrib['name'], tileMap, int(tag.attrib.get('visible', 1)))
        
        dataE = tag.find('data')
        if dataE is None:
            raise ValueError('layer %s does not contain <data>' % layer.name)
        
        dataE = dataE.text.strip()
        tileData = dataE.decode('base64').decode('zlib')
        tileData = struct.unpack('<%di' % (len(tileData)/4,), tileData)
        assert len(tileData) == layer.width * layer.height
        
        for i, gid in enumerate(tileData):
            if gid < 1:
                continue # not set
            tile = tileMap.tileSets[gid]
            x = i % layer.width
            y = i // layer.width
            px = x * tileMap.tileWidth
            py = layer.heightPixels - (y * tileMap.tileHeight) - tileMap.tileHeight
            layer.cells[x, y] = Cell(x, y, px,
                py, tile, layer.batch)
        
        return layer
        
    def setView(self, tileMap, x, y):
        self.focusX = x
        self.focusY = y
   
    def update(self, dt):
       pass

    def draw(self):
        glPushMatrix()
        glTranslatef(self.focusX, self.focusY, 0 )
        self.batch.draw()
        glPopMatrix()
                
class Layers(list):
    def __init__(self):
        self.by_name = {}
    
    def addNamed(self, layer, name):
        self.append(layer)
        self.by_name[name] = layer
    
    def __getitem__(self, item):
        if isinstance(item, int):
            return self[item]
        return self.byName[item]
        
class Tile(object):
    def __init__(self, gid, image, tileSet):
        self.gid = gid
        self.tileWidth = tileSet.tileWidth
        self.tileHeight = tileSet.tileHeight
        self.image = image
        self.properties = {} 
        
    def loadXml(self, tag):
        props = tag.find('properties')
        if props is None:
            return
        for c in props.findall('property'):
            pass
            #store additional properties

class TileSet(object):
    def __init__(self, name, tileWidth, tileHeight, firstGid):
        self.firstGid = firstGid
        self.name = name
        self.images = []
        self.tiles = []
        self.indexed_images = {}
        self.spacing = 0
        self.margin = 0
        self.properties = {}
        self.tileHeight = tileHeight
        self.tileWidth = tileWidth
        
    def getTile(self, gid):
        return self.tiles[gid - self.firstGid]

    def addTileSheet(self, imageFile):
        ''' adds all the tiles from an image based
            on tileset tile size.
        
            Reverses the tile sheet row-wise, due to tiled
            rows being reverse of pyglet imagegrid rows.
        '''
        origImage = image.load(imageFile)
        if not origImage:
            print "Error creating new Tileset: file %s not found" % imageFile
        
        rows = origImage.height / self.tileHeight
        columns = origImage.width / self.tileWidth
        
        imageGrid = pyglet.image.ImageGrid(origImage, rows, columns)
        
        tsRows = list()
        finalSheet = pyglet.image.Texture.create(origImage.width, origImage.height)
        
        gridIndex = 0
        for r in range(rows):
            tsRows.append(imageGrid[gridIndex:gridIndex+columns])
            gridIndex += columns
            
        #reverse the rows
        tsRows = reversed(tsRows)
            
        rowNum = 0
        columnNum = 0
        for row in tsRows:
            for tile in row:
                finalSheet.blit_into(tile, columnNum * self.tileWidth, rowNum * self.tileHeight, 1)
                columnNum += 1
            rowNum += 1
            columnNum = 0
        
        imageGrid = pyglet.image.ImageGrid(finalSheet, rows, columns)
        textureGrid = pyglet.image.TextureGrid(imageGrid)
        
        tileId = self.firstGid
        for tile in textureGrid:
            self.tiles.append(Tile(tileId, tile, self))
            tileId += 1
            
            
    @classmethod
    def fromElement(cls, element, firstGid=None):
        if 'source' in element.attrib:
            firstGid = int(element.attrib['firstgid'])
            with open(element.attrib['source']) as f:
                tilesetElements = ElementTree.fromstring(f.read())
            return cls.fromElement(tilesetElements, firstGid)
        
        name = element.attrib['name']
        if firstGid is None:
            firstGid = int(element.attrib['firstgid'])
        tileWidth = int(element.attrib['tilewidth'])
        tileHeight = int(element.attrib['tileheight'])
        
        tileSet = TileSet(name, tileWidth, tileHeight, firstGid)
        
        for c in element.getchildren():
            if c.tag == "image":
                tileSet.addTileSheet(c.attrib['source'])
            elif c.tag == 'tile':
                gid = tileSet.firstGid + int(c.attrib['id'])
                tileSet.getTile(gid).loadXml(c)
        return tileSet

class TileSets(dict):
    def add(self, tileSet):
        for i, tile in enumerate(tileSet.tiles):
            i += tileSet.firstGid
            self[i] = tile
        
        
class TileMap(object):
    def __init__(self, size):
        self.tileHeight = 0
        self.tileWidth = 0
        self.width = 0
        self.height = 0
        self.widthPixels = 0
        self.heightPixels = 0
        self.focusX, self.focusY = 0, 0 # viewport focus point
        self.viewportWidth, self.viewportHeight = size # viewport size
        self.tileSets = TileSets()
        self.layers = Layers()
        self.properties = {}
        self.mapFileName = ""
    
    @classmethod
    def fromTmx(cls, fileName, viewportSize):
        with open(fileName) as f:
            mapE = ElementTree.fromstring(f.read())
            
        tileMap = TileMap(viewportSize)
        tileMap.width = int(mapE.attrib['width'])
        tileMap.height = int(mapE.attrib['height'])
        tileMap.tileWidth = int(mapE.attrib['tilewidth'])
        tileMap.tileHeight = int(mapE.attrib['tileheight'])
        tileMap.widthPixels = tileMap.width * tileMap.tileWidth
        tileMap.heightPixels = tileMap.height * tileMap.tileHeight
        
        for element in mapE.findall('tileset'):
            tileMap.tileSets.add(TileSet.fromElement(element))

        for element in mapE.findall('layer'):
            layer = TileLayer.fromElement(element, tileMap)
            tileMap.layers.addNamed(layer, layer.name)
            
        return tileMap
        
    def moveFocus(self, x, y):
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
		    if -x >= self.widthPixels - self.viewportWidth:
		        x = -(self.widthPixels - self.viewportWidth)
		    elif -x < 0:
		        x = 0
		    if -y >= self.heightPixels - self.viewportHeight:
		        y = -(self.heightPixels - self.viewportHeight)
		    elif -y < 0:
		        y = 0
        
        self.focusX = x
        self.focusY = y
        print x,y
        
        for layer in self.layers:
            layer.setView(self, x, y)
            layer.viewportWidth = self.viewportWidth
            layer.viewportHeight = self.viewportHeight
            
    
    def update(self, dt):
        for layer in self.layers:
            layer.update(dt)
       
    def draw(self):
        for layer in self.layers:
            if layer.visible == True:
                layer.draw()
               
               
               
               
