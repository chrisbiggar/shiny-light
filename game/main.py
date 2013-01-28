'''

'''

import py2d
from py2d import director
from py2d import actor
from py2d import scene
import pyglet
import player


class Game(object):
	def __init__(self, options):
		self.director = director.Director(options.showfps)
		thePlayer = player.Player(self.director)
		thePlayer.set_position(100,800)

		scene = py2d.scene.Scene("level")
		scene.addActor(thePlayer)
		self.director.push_handlers(scene)
		
		self.director.registerScene(scene)
		self.director.setScene("level")

	def run(self):
	    self.director.run()
