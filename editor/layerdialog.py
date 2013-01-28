'''
Layer Editor Dialog

'''
import os
import pyglet
import kytten
from kytten.dialog import Dialog
import widgets
import levelview
import leveleditor


def on_escape(dialog):
    dialog.teardown()
    
class LayerDialog(object):
    def __init__(self, editor):
        self.layouts = {
            "terrain" : self.createTerrainLayout,
            "aesthetic" : self.createAestheticLayout,
            "object" : self.createObjectLayout
        }
        editor.push_handlers(self)
        self.levelView = editor.levelView
        self.dialog = None
        self.window = editor
        self.previousChoice = None
            
    def on_dialog_update(self):
        self.updateLayout()
        
    def updateLayout(self):
        modeName = self.levelView.mode.name
        if self.dialog != None:
            self.dialog.teardown()
        if modeName == "base":
            return
        # create layout according to editor mode
        self.layout = self.layouts[modeName]()
        self.commonSection =  self.createCommonSection()
        frame = kytten.Frame(kytten.HorizontalLayout([self.layout,
                kytten.Spacer(width=15),
                self.commonSection
            ])
        )
        self.dialog = kytten.Dialog(frame,
            window=self.window, batch=self.window.dialogBatch,
            anchor=kytten.ANCHOR_BOTTOM, theme=leveleditor.theme)
        # update all controls on dialog
        
        
    def createCommonSection(self):
        def opacity_on_set(value):
            pass
        def delete_button():
            pass
        def entity_list():
            pass
        commonLayout = kytten.FoldingSection("Layer",
            kytten.GridLayout([
                [kytten.Checkbox("Visible", id="visible"), kytten.Button("Delete",
                                 on_click=delete_button)],
                [kytten.VerticalLayout([
                    kytten.Label("Opacity"),
                    kytten.Slider(self.levelView.scale, 0.0, 1.0, steps=10, on_set=opacity_on_set)]
                    ),
                     kytten.Button("Entity List", on_click=entity_list)]
            ])
        )
        return commonLayout
        
    def createTerrainLayout(self):
        def on_select(choice):
            if choice == "Line Place":
                self.levelView.mode.tool = levelview.TerrainController.LINE_TOOL
            elif choice == "Pan":
                self.levelView.mode.tool = levelview.BaseController.PAN_TOOL
        self.toolMenu = kytten.Menu(
            options=["Line Place", "Pan"], on_select=on_select)
        return self.toolMenu
            
        
    
    def createAestheticLayout(self):
        pass
    
    def createObjectLayout(self):
        pass
        

        
        
        
        
        
        
        
        
        
        
