'''
MainDialog control panel for leveleditor.

'''
import os
import pyglet
import kytten
from kytten.dialog import Dialog
import widgets
import string
import leveleditor
import levelview

def on_escape(dialog):
    dialog.teardown()

class EditorDialog(Dialog):
    lastLayerChoice = None
    def __init__(self, editor):
        self.levelView = editor.levelView
        frame = self.createLayout()
        super(EditorDialog, self).__init__(frame,
            window=editor, batch=editor.dialogBatch, 
            anchor=kytten.ANCHOR_TOP_RIGHT, theme=leveleditor.theme)
        
    def on_dialog_update(self):
        self.syncZoom()
        
    def syncZoom(self):
        self.zoomSlider.set_pos((self.levelView.scale / self.zoomSlider.max_value) 
            - self.zoomSlider.min_value)
        self.zoomText.set_text("Zoom: " + str(self.levelView.scale))
        
    def syncLayerMenu(self):
        options = list()
        for layer in self.levelView.sceneMap.layers:
            options.append(layer.name)
        options.append("add layer")
        self.layerMenu.set_options(options)
             
                
    def newLevelDialog(self):
        dialog = None
        def on_enter(dialog):
            values = dialog.get_values()
            self.levelView.newLevel(values)
            self.levelView.setActiveLayer("base", self.window)
            self.syncLayerMenu()
            on_escape(dialog)
        def on_submit():
            on_enter(dialog)
        def on_cancel():
            on_escape(dialog)
        dialog = kytten.Dialog(
            kytten.Frame(
                kytten.VerticalLayout([
                    kytten.SectionHeader("New Level", align=kytten.HALIGN_LEFT),
                    kytten.GridLayout([
                        [kytten.Label("Name"), kytten.Input("name", "untitled",
                                                max_length=20)],
                        [kytten.Label("Height"), kytten.Input("height", "1200",
                                                max_length=5)],
                        [kytten.Label("Width"), kytten.Input("width", "5000",
                                                max_length=5)]                                                
                    ]),
                    kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
                     kytten.HorizontalLayout([
                         kytten.Button("Ok",
                             on_click=on_submit),
                         kytten.Button("Cancel",
                             on_click=on_cancel)
                     ])
                ])),
            window=self.window, batch=self.batch,
            anchor=kytten.ANCHOR_CENTER, theme=self.theme,
            on_enter=on_enter, on_escape=on_escape)          

    def gridOptionsDialog(self):
        dialog = None
        def on_enter(dialog):
            values = dialog.get_values()
            self.levelView.updateGrid(values)
            on_escape(dialog)
        def on_submit():
            on_enter(dialog)
        def on_cancel():
            on_escape(dialog)
        dialog = kytten.Dialog(
            kytten.Frame(
                    kytten.VerticalLayout([
                        kytten.SectionHeader("Grid Options", align=kytten.HALIGN_LEFT),
                        kytten.Checkbox("Show Grid", id="show_grid"),
                        kytten.Checkbox("Snap To Grid", id="snap_to"),
                        kytten.GridLayout([
                            [kytten.Label("H Spacing"), kytten.Input("h_spacing", "50", max_length=3)],
                            [kytten.Label("V Spacing"), kytten.Input("v_spacing", "50", max_length=3)]]),
                        kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
                        kytten.HorizontalLayout([
                             kytten.Button("Ok",
                                 on_click=on_submit),
                             kytten.Button("Cancel",
                                 on_click=on_cancel)]),
                                 ])),
                window=self.window, batch=self.batch,
                anchor=kytten.ANCHOR_CENTER, theme=self.theme,
                on_enter=on_enter, on_escape=on_escape) 
            
    def createLayout(self):
        # layers section
        self.layerMenu = kytten.Menu(options=[], on_select=self.layerMenuSelect)
        layersSection = kytten.FoldingSection("Layers", kytten.VerticalLayout([self.layerMenu]))
        # view section
        def gridOptionsSelect(choice):
            self.gridOptionsDialog()
        def zoom_on_set(value):
            self.levelView.setScale(value)
            self.zoomText.set_text("Zoom: " + str(self.levelView.scale))
        self.zoomSlider = kytten.Slider(self.levelView.scale, 0.2, 2.0, steps=9, on_set=zoom_on_set)
        self.zoomText = kytten.Label("Zoom: 1.0")
        viewSection = kytten.FoldingSection("View", 
            kytten.VerticalLayout([
                self.zoomText,
                self.zoomSlider,
                widgets.ClickMenu(options=["Grid Options"],on_select=gridOptionsSelect)]))
        # map section
        mapSection = kytten.FoldingSection("Map", 
            widgets.ClickMenu(
                options=["New Level", "Load Level", "Save Level", "Quit"], 
                on_select=self.mapMenuSelect))
        return kytten.Frame(kytten.VerticalLayout([layersSection, viewSection, mapSection]))
           
    
    def layerMenuSelect(self, choice):
    	# unselect active layer if clicked
        if choice == self.lastLayerChoice:
            self.layerMenu.options[choice].unselect()
            choice = "base"
        if choice == "add layer":
            # add layer to LevelView
            self.levelView.addAestheticLayer("layer" + str(self.levelView.layers))
            self.syncLayerMenu()
            # unselect new layer button
            if self.layerMenu.selected is not None:
                self.layerMenu.options[self.layerMenu.selected].unselect()
        else:
            self.levelView.setActiveLayer(choice, self.window)
            self.lastLayerChoice = choice
        self.window.dispatch_event('on_dialog_update')
            
   
    def mapMenuSelect(self, choice):
        if choice == "New Level":
            self.newLevelDialog()
        elif choice == "Load Level":
            def on_select(filename):
                self.levelView.loadMap(filename)
                on_escape(dialog)
            dialog = kytten.FileLoadDialog(
                        extensions=[levelview.FILE_EXT], window=self.window, 
                        theme=self.theme,
                        on_select=on_select, batch=self.batch,
                        on_escape=on_escape,)
        elif choice == "Save Level":
            def on_select(filename):
                self.levelView.saveMap(filename)
                on_escape(dialog)
            dialog = kytten.FileSaveDialog(
                extensions=[levelview.FILE_EXT], window=self.window,
                batch=self.batch, anchor=kytten.ANCHOR_CENTER,
                theme=self.theme, on_escape=on_escape, on_select=on_select)   
        elif choice == "Quit":
            pyglet.app.exit()
            
   
    
