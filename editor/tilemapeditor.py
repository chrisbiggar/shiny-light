'''
tilemap editor for py2d.

'''

import pyglet
from pyglet.window import key
from pyglet.gl import *
import pymunk
from py2d import tileMap

import sys
#sys.stdout = open('log','w')

PROGRAM_CAPTION = "Map Vectorizer"
MOVE_SPEED = 400

''' initilize window to maximum size
'''
for display in pyglet.app.displays:
    screen = display.get_default_screen()
window = pyglet.window.Window(screen.width,screen.height, PROGRAM_CAPTION, resizable=True)
window.set_location(screen.x, screen.y)
 
#toolbarWindow = pyglet.window.Window(200, 500, "ToolBar")

keys = key.KeyStateHandler()
window.push_handlers(keys)
theTileMap = None

fpsDisplay = pyglet.clock.ClockDisplay()

def init():
    global theTileMap
    theTileMap = tileMap.TileMap.fromTmx("untitled2.tmx", (window.width,window.height))
    

@window.event
def on_mouse_press(x, y, button, modifiers):
    pass
    
@window.event
def on_mouse_release(x, y, button, modifiers):
    pass
    
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    theTileMap.moveFocus(dx,dy)


def update(dt):
    theTileMap.viewportWidth = window.width
    theTileMap.viewportHeight = window.height
    theTileMap.moveFocus(0,0)
    if keys[key.LEFT]:
        theTileMap.moveFocus(MOVE_SPEED * dt, 0)
    if keys[key.RIGHT]:
        theTileMap.moveFocus(-MOVE_SPEED * dt, 0)
    if keys[key.UP]:
        theTileMap.moveFocus(0, -MOVE_SPEED * dt)
    if keys[key.DOWN]:
        theTileMap.moveFocus(0, MOVE_SPEED * dt)
    if keys[key.END]:
        theTileMap.forceFocus = True
        
    theTileMap.update(dt)

@window.event
def on_resize(width, height):
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
    return pyglet.event.EVENT_HANDLED

@window.event
def on_draw():
    window.clear()
    glPushMatrix()
    theTileMap.draw()
    fpsDisplay.draw()
    glPopMatrix()
    
init()
pyglet.clock.schedule_interval(update, 1/60.)
pyglet.app.run()
