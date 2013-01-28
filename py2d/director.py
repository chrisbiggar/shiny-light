''' 
Director class is the main pyglet window, and manages scenes
and other general stuff.

'''
from loggable import Loggable
import pyglet
from pyglet.window import key
from pyglet.gl import *
import actor


class Director(pyglet.window.Window):
	currentScene = None
	scenes = dict()

	def __init__(self, showFps=False, windowCaption="Py2d"):
		super(Director, self).__init__(1280, 720, windowCaption)
		self.keys = key.KeyStateHandler()
		self.push_handlers(self.keys)
		self.fpsDisplay = pyglet.clock.ClockDisplay()
		self.showFps = showFps
	
	def registerScene(self, scene):
	    self.scenes[scene.name] = scene

	def setScene(self, sceneName):
		if sceneName in self.scenes:
			self.currentScene = self.scenes[sceneName]
			if self.currentScene.loaded == False:
				self.currentScene.load()
	
	def update(self, dt):
		self.currentScene.update(dt)
		
	def on_draw(self):
		self.clear()
		self.currentScene.draw()
		if self.showFps == True:
			self.fpsDisplay.draw()
			
	def on_resize(self, width, height):
		v_ar = width/float(height)
		usableWidth = int(min(width, height*v_ar))
		usableHeight = int(min(height, width/v_ar))
		ox = (width - usableWidth) // 2
		oy = (height - usableHeight) // 2
		
		glViewport(ox, oy, usableWidth, usableHeight)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(60, usableWidth/float(usableHeight), 0.1, 3000.0)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		''' alternative is:
		    glTranslatef(-width/2, -height/2, -height*1.21)
		    but i guess it produces the same matrix..
		'''
		gluLookAt(width/2.0, height/2.0, height/1.1566,
		    width/2.0, height/2.0, 0,
		    0.0, 1.0, 0.0)
		#glRotatef(45, 1.0, 0.0, 0.0)
		return pyglet.event.EVENT_HANDLED
		
	def run(self, updateFreq=1/60.0):
		pyglet.clock.schedule_interval(self.update, updateFreq)
		pyglet.app.run()
