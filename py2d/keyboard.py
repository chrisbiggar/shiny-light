'lack of better place: find place for this class.'

import pyglet
from pyglet.window import key

class Keyboard(key.KeyStateHandler):
	def __init__(self):
		super(Keyboard, self).__init__()
		self.keyPressHandler = None
		self.keyReleaseHandler = None
		
	def on_key_press(self, symbol, modifiers):
		super(Keyboard, self).on_key_press(symbol, modifiers)
		if self.keyPressHandler:
			self.keyPressHandler(symbol, modifiers)
		
	def on_key_release(self, symbol, modifiers):
		super(Keyboard, self).on_key_release(symbol, modifiers)
		if self.keyReleaseHandler:
			self.keyReleaseHandler(symbol, modifiers)
