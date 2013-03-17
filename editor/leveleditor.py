'''
map editor for py2d.

'''
import pyglet
from pyglet.window import key
from pyglet.gl import glViewport, glMatrixMode, glLoadIdentity,\
	gluPerspective, gluLookAt, GL_PROJECTION, GL_MODELVIEW
import scenecontroller
import dialogs


'''
Main Application Class for level editor

'''
class LevelEditor(pyglet.window.Window):
    fpsDisplay = pyglet.clock.ClockDisplay()
    WINDOW_CAPTION = "Map Editor"
    
    def __init__(self, options):
        for display in pyglet.app.displays:
            screen = display.get_default_screen()    
        super(LevelEditor, self).__init__(screen.width, screen.height, self.WINDOW_CAPTION, resizable=True)
        self.set_location(screen.x, screen.y)
        self.dialogBatch = pyglet.graphics.Batch()
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.sceneController = scenecontroller.SceneController(self)
        self.createDialogs()
        # time since program started.
        self.time = 0
        #self.el = pyglet.window.event.WindowEventLogger()
        #self.push_handlers(self.el)
    
    
    def createDialogs(self):
        self.register_event_type('on_update') # kytten dialogs get updated with this event
        self.register_event_type('on_layer_update') # update layer info
        self.editorDialog = dialogs.EditorDialog(self)
        self.statusPane = dialogs.StatusPane(self, self.dialogBatch, self.sceneController)
        self.layerDialog = dialogs.LayerDialog(self)
        self.selectedItemDialog = dialogs.SelectedItemDialog(self)
        self.register_event_type('on_select_item')
        self.push_handlers(self.selectedItemDialog)


    def on_close(self):
        if self.sceneController.map != None and self.sceneController.edited == True:
            ''' if map is open and not saved prompt user
            '''
            dialogs.ConfirmExitDialog(self, self.dialogBatch, self.sceneController)
        else:
            super(LevelEditor, self).on_close()
        
    def on_resize(self, width, height):
        ''' calculate perspective matrix
        '''
        v_ar = width/float(height)
        usableWidth = int(min(width, height*v_ar))
        usableHeight = int(min(height, width/v_ar))
        ox = (width - usableWidth) // 2
        oy = (height - usableHeight) // 2
        glViewport(ox, oy, usableWidth, usableHeight)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, usableWidth/float(usableHeight), 0.1, 3000.0)
        ''' set camera position on modelview matrix
        '''
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(width/2.0, height/2.0, height/1.1566,
            width/2.0, height/2.0, 0,
            0.0, 1.0, 0.0)
        ''' update LevelView with size
        '''
        self.sceneController.resize(width, height)
        return pyglet.event.EVENT_HANDLED
    
    lastClick = 0
    def on_mouse_press(self, x, y, button, modifiers):
        #super(LevelEditor, self).on_mouse_press(x, y, button, modifiers)
        pass
            
    def on_key_release(self, symbol, modifiers):
        #super(LevelEditor, self).on_mouse_release(x, y, button, modifiers)
       	pass
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER and modifiers & key.MOD_ALT:
            ''' toggle fullscreen
            '''
            self.set_fullscreen(not self.fullscreen)
        
    def update(self, dt):
        self.time += (dt * 1000)
        self.sceneController.update(dt)
        
    def updateKytten(self, dt):
    	self.dispatch_event('on_update', dt)
        
    def on_draw(self):
        self.clear()
        self.sceneController.draw()
        self.dialogBatch.draw()
        #self.fpsDisplay.draw()
    
    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60.)
        pyglet.clock.schedule_interval(self.updateKytten, 1/60.)
        pyglet.app.run()

            

    
    
    
    
    
    
    
    
    
