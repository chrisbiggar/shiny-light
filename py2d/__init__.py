'''
py2d. a 2d game engine for pyglet.
author: chris biggar
version 0.1
'''
version = 0.1

import pyglet
graphicsLoader = pyglet.resource.Loader(["graphics"])


'''
jolt = False
def keyRelease(symbol, modifiers):
	global jolt
	if symbol == key.HOME:
		jolt = True

z = 800
ascend = False
def update(dt):
	global jolt
	if jolt:
		global z, ascend
		if ascend:
			z += 1200 * dt
		else:
			z -= 1200 * dt
		if z <= 750:
			ascend = True
		if z > 800:
			ascend = False
			jolt = False
			z = 800
	
	if keys[key.PAGEUP]:
		z += 50 * dt
		print z
	if keys[key.PAGEDOWN]:
		z -= 50 * dt
		print z
'''




