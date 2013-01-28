'''

'''
import math
from loggable import Loggable
import pyglet
from pyglet import window
from pyglet.gl import *
import pymunk
import py2d
from py2d.director import Director


class DuplicateActor(Exception): """actor is already in the world"""
class Scene(window.key.KeyStateHandler, pyglet.event.EventDispatcher, Loggable):
	actors = set()
	batch = pyglet.graphics.Batch()
	space = pymunk.Space()

	def __init__(self, name):
		self.loaded = False
		self.name = name
		self.initLogging()

	
	def load(self):
		self.loaded = True
		
		#physics
		self.space.gravity = 0, -1000
		
		self.platformSegs = [
		    pymunk.Segment(self.space.static_body, (0, 100), (400, 100), 5),
		    pymunk.Segment(self.space.static_body, (400, 100), (1000, 500), 5),
		    pymunk.Segment(self.space.static_body, (1000, 500), (1000, 780), 5),
		    pymunk.Segment(self.space.static_body, (320, 360), (545, 340), 5)
		    ]
		
		for seg in self.platformSegs:
		    seg.friction = 1.
		    seg.group = 1
		
		self.space.add(self.platformSegs)

	def addActor(self, actor, isKeyHandler=False):
		if actor in self.actors:
			raise DuplicateActor("Actor is already in world")
		else:
			self.actors.add(actor)
			actor.addedToScene(self)


	def hasActor(self, actor):
		return actor in self.actors


	def removeActor(self):
		pass


	def clearActors(self):
		self.actors = set()


	def update(self, dt):
		if self[window.key.H]:
			self.group.rotation += 45 * dt
		
		if self[window.key.S]:
			self.group.scaleX += 100 * dt
		if self[window.key.X]:
			self.group.scaleX -= 100 * dt
		
		
	
		for actor in self.actors:
			actor.update(dt)
			
		self.space.step(1./60)
	

	def draw(self):
	    for segment in self.platformSegs:
	        drawSegment(segment)
	
		self.batch.draw()

## seems that you can just use 
## the segment coords to draw with..
def drawSegment(seg):
    body = seg.body
    
    pv1 = body.position + seg.a.rotated(body.angle)
    pv2 = body.position + seg.b.rotated(body.angle)
    glLineWidth(5.0)
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2f', (pv1.x,pv1.y+25,pv2.x,pv2.y+25)),
                ('c3f', (.8,.8,.8)*2)
                )
                
class SceneMap(object):
	pass
            



















