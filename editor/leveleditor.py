'''
map editor for py2d.

'''
import os
import pyglet
from pyglet.window import key
from pyglet.gl import *
import kytten
import editordialog
import layerdialog
import levelview

theme = kytten.Theme(os.path.join(os.getcwd(), 'theme'), override={
"gui_color": [64, 128, 255, 255],
"font_size": 18
})

class LevelEditor(pyglet.window.Window):
    fpsDisplay = pyglet.clock.ClockDisplay()
    WINDOW_CAPTION = "Map Editor"
    
    def __init__(self, options):
        for display in pyglet.app.displays:
            screen = display.get_default_screen()    
        super(LevelEditor, self).__init__(screen.width, screen.height, self.WINDOW_CAPTION, resizable=True)
        self.set_location(screen.x, screen.y)
        self.levelView = levelview.LevelView(self)
        self.dialogBatch = pyglet.graphics.Batch()
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.createDialogs()
        # time since program started.
        self.time = 0
        #self.el = pyglet.window.event.WindowEventLogger()
        #self.push_handlers(self.el)
    
    
    def createDialogs(self):
        self.register_event_type('on_update') # kytten dialogs get updated with this event
        self.register_event_type('on_dialog_update') # update dialog info
        self.editorDialog = editordialog.EditorDialog(self)
        self.layerDialog = layerdialog.LayerDialog(self)


    def on_close(self):
        if self.levelView.sceneMap != None and self.levelView.edited == True:
            ''' if map is open and not saved prompt user
            '''
            ConfirmExitDialog(self, self.dialogBatch, self.levelView)
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
        self.levelView.resize(width, height)
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
        self.levelView.update(dt)
        
    def updateKytten(self, dt):
    	self.dispatch_event('on_update', dt)
        
    def on_draw(self):
        self.clear()
        self.levelView.draw()
        self.dialogBatch.draw()
        self.fpsDisplay.draw()
    
    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60.)
        pyglet.clock.schedule_interval(self.updateKytten, 1/60.)
        pyglet.app.run()

            
'''
    Dialog prompts User to save the level if edited and not saved
    
'''    
class ConfirmExitDialog(kytten.Dialog):
    def __init__(self, window, batch, levelView):
        super(ConfirmExitDialog, self).__init__(
            kytten.Frame(
                kytten.VerticalLayout([
                    kytten.SectionHeader("Map Not Saved:", align=kytten.HALIGN_LEFT),
                    kytten.Spacer(height=60),
                    kytten.HorizontalLayout([
                        kytten.Button("Save", on_click=self.save),
                        kytten.Button("Dont Save", on_click=self.exitApp),
                        kytten.Button("Cancel", on_click=self.cancel)
                    ])
                ])
            ), window=window, batch=batch,
                anchor=kytten.ANCHOR_CENTER, theme=theme,
                on_escape=self.teardownDialog
        )
        self.levelView = levelView
    
    def save(self):
        def on_select(filename):
            self.levelView.saveLevel(filename)
            self.exit()
        kytten.FileSaveDialog(
            extensions=[levelview.FILE_EXT], window=self.window,
            batch=self.batch, anchor=kytten.ANCHOR_CENTER,
            theme=theme, on_select=on_select)   
    
    def exitApp(self):
        self.levelView.sceneMap = None
        pyglet.app.exit()
    
    def cancel(self):
        self.teardownDialog(self)
        
    def teardownDialog(self, dialog):
        super(ConfirmExitDialog, self).teardown()
    
'''        # detect double click and toggle fullscreen
        if self.time - self.lastClick <= 150:
            self.set_fullscreen(not self.fullscreen)
        self.lastClick = self.time'''
    
    
    
    
    
    
    
    
    
