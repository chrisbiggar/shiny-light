'''

'''

import math
from loggable import Loggable
import pyglet
import pymunk
import py2d

def centerImgAnchor(img):
	img.anchor_x = img.width // 2
	img.anchor_y = img.height // 2


class Actor(object):
	Scene = None

	def __init__(self):
		pass

	def update(self, dt):
		pass

	def addedToScene(self, scene):
		self.scene = scene
		
	def removedFromScene(self, scene):
		self.scene = None
	

class VisualActor(pyglet.sprite.Sprite, Actor):
	def __init__(self, img, batch=None):
		super(VisualActor, self).__init__(img, batch=batch)

	def update(self, dt):
		pass
		
	def addedToScene(self, scene):
		super(VisualActor, self).addedToScene(scene)
		self.batch = scene.batch
		
	def loadAnimation(self, imageName, rows, columns, animFreq, loop=False, centerAnchor=False):
		animImg = py2d.graphicsLoader.image(imageName)
		animGrid = pyglet.image.ImageGrid(animImg, rows, columns)
		animGrid = animGrid.get_texture_sequence()
		if centerAnchor == True:
			map(centerImgAnchor, animGrid)
		return \
			pyglet.image.Animation.from_image_sequence(animGrid,
				animFreq, loop=loop)
				
# PhysicalActor - Comprises a pymunk body and the common
# calculations..
#			
class PhysicalActor(VisualActor):
	def __init__(self, img, batch=None, mass=5, moment=pymunk.inf):
		super(PhysicalActor, self).__init__(img, batch=batch)
		self.body = pymunk.Body(mass, moment)
		
	def update(self, dt):
		self.position = self.body.position
		self.x = self.position[0] + (self.image.get_max_width()/4)
		self.y = self.position[1] + (self.image.get_max_height()/4)
		self.rotation = math.degrees(self.body.angle)
		
	def addedToScene(self, scene):
		super(PhysicalActor, self).addedToScene(scene)
		scene.space.add(self.body)


class CompositeActor():
	pass
	
class EffectActor():
	pass
	
	
	
	
	
	
	
