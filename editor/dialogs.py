'''
MainDialog control panel for leveleditor.

'''
import os
import pyglet
import kytten
from kytten.dialog import Dialog
from kytten.button import Button
import widgets
import levelview
import py2d.scenegraph as scenegraph


theme = kytten.Theme(os.path.join(os.getcwd(), 'theme'), override={
"gui_color": [64, 128, 255, 255],
"font_size": 16
})


'''
    tears down specified dialog
'''
def on_escape(dialog):
    dialog.teardown()
    
'''
    NewLevelDialog
    allows user to create new level specifying properties
'''
class NewLevelDialog(Dialog):
    def __init__(self, parentDialog, window, batch, scene):
        self.scene = scene
        self.pDialog = parentDialog
        super(NewLevelDialog, self).__init__(
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
                             on_click=self.on_submit),
                         kytten.Button("Cancel",
                             on_click=self.on_cancel)
                     ])
                ])),
            window=window, batch=batch,
            anchor=kytten.ANCHOR_CENTER, theme=theme,
            on_enter=self.on_enter, on_escape=on_escape)   
            
    def on_submit(self):
        values = self.get_values()
        width = int(values["width"])
        height = int(values["height"])
        self.scene.newLevel(width, height)
        self.pDialog.syncLayerMenu()
        on_escape(self)
    def on_enter(self, dialog):
        self.on_submit()
    def on_cancel(self):
        on_escape(self)
    
'''
    class EditLayerDialog
    allows user to edit the properties of the current layer
'''
#TODO configure the dialog according to current layer and change properties correctly.
class EditLayerDialog(Dialog):
    def __init__(self, window, batch, scene):
        self.scene = scene
        self.visible = kytten.Checkbox("Visible", id="visible")
        super(EditLayerDialog, self).__init__(
            kytten.Frame(
                kytten.VerticalLayout([
                    kytten.GridLayout([
                        [visible, kytten.Button("Delete",
                                         on_click=self.on_click_delete_button)],
                        [kytten.VerticalLayout([
                            kytten.Label("Opacity"),
                            kytten.Slider(self.scene.scale, 0.0, 1.0, steps=10, on_set=self.opacity_on_set)]
                            ),
                             kytten.Button("Entity List", on_click=self.entity_list)]
                    ]),
                    kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
                     kytten.HorizontalLayout([
                         kytten.Button("Ok",
                             on_click=self.on_submit),
                         kytten.Button("Cancel",
                             on_click=self.on_cancel)
                     ])
                ])
            ),
            window=window, batch=batch,
            anchor=kytten.ANCHOR_CENTER, theme=theme,
            on_enter=self.on_enter, on_escape=on_escape)
    
    def entity_list(self):
        pass
    
    def opacity_on_set(self):
        pass
    
    def on_click_delete_button(self):
        pass
    
    def on_submit(self):
        #TODO change layer properties here.
        layer = self.scene.currentLayer
        layer.visble = self.visible.is_checked
        
        on_escape(self)
    def on_enter(self):
        on_submit()
    def on_cancel(self):
        on_escape(self)

'''
    class EditorDialog
    main dialog for application. allows layer navigation and map loading/saving
'''
class EditorDialog(Dialog):
    lastLayerChoice = None
    def __init__(self, editor):
        self.scene = editor.sceneController
        frame = self.createLayout()
        super(EditorDialog, self).__init__(frame,
            window=editor, batch=editor.dialogBatch, 
            anchor=kytten.ANCHOR_TOP_RIGHT, theme=theme)
        
    def syncLayerMenu(self):
        options = list()
        keys = self.scene.graph.layers.by_name.iterkeys()
        for key in keys:
            options.append(key)
        self.layerMenu.set_options(options)
        
    def layerMenuSelect(self, choice):
        # unselect active layer if clicked
        if choice == self.lastLayerChoice:
            self.layerMenu.options[choice].unselect()
            self.scene.setActiveLayer("none")
            self.lastLayerChoice = None
        else:
            self.scene.setActiveLayer(choice)
            self.lastLayerChoice = choice
        self.window.dispatch_event('on_layer_update')
        if self.window.selectedItemDialog.dialog != None:
            self.window.selectedItemDialog.dialog.teardown()
    
    def metaLayerMenuSelect(self, choice):
        if choice == "add layer":
            print "add"
            '''# add layer to LevelView
            self.scene.addAestheticLayer("layer" + str(self.scene.layers))
            self.syncLayerMenu()
            # unselect new layer button
            if self.layerMenu.selected is not None:
                self.layerMenu.options[self.layerMenu.selected].unselect()'''
        elif choice == "edit layer":
            EditLayerDialog(self.window, self.batch, self.scene)
             
    def createLayout(self):
        # layers section
        self.layerMenu = kytten.Menu(options=[], on_select=self.layerMenuSelect)
        layersSection = kytten.FoldingSection("Layers", kytten.VerticalLayout([self.layerMenu]))
        #
        # layers section
        self.metaLayerMenu = widgets.ClickMenu(['add layer', 'edit layer'], on_select=self.metaLayerMenuSelect)
        
        # map section
        mapSection = kytten.FoldingSection("Map", 
            widgets.ClickMenu(
                options=["New Level", "Load Level", "Save Level", "Quit"], 
                on_select=self.mapMenuSelect),
                )
        return kytten.Frame(kytten.VerticalLayout([layersSection, self.metaLayerMenu, mapSection]))
   
    def mapMenuSelect(self, choice):
        if choice == "New Level":
            NewLevelDialog(self, self.window, self.batch, self.scene)
        elif choice == "Load Level":
            def on_select(filename):
                self.scene.loadMap(filename)
                on_escape(dialog)
            dialog = kytten.FileLoadDialog(
                        extensions=[levelview.FILE_EXT], window=self.window, 
                        theme=self.theme,
                        on_select=on_select, batch=self.batch,
                        on_escape=on_escape,)
        elif choice == "Save Level":
            def on_select(filename):
                self.scene.saveMap(filename)
                on_escape(dialog)
            dialog = kytten.FileSaveDialog(
                extensions=[levelview.FILE_EXT], window=self.window,
                batch=self.batch, anchor=kytten.ANCHOR_CENTER,
                theme=self.theme, on_escape=on_escape, on_select=on_select)   
        elif choice == "Quit":
            pyglet.app.exit()
            
            
'''
    class LayerDialog
    controls dialog that allows user to manipulate layers
    by dynamically while current type of layer is selected
    showing given controls for type of layer.
'''   
class LayerDialog(object):
    def __init__(self, editor):
        self.layouts = {
            "terrain" : self.terrainLayout,
            "aesthetic" : self.itemLayout,
            "object" : self.itemLayout
        }
        editor.push_handlers(self)
        self.scene = editor.sceneController
        self.dialog = None
        self.window = editor
        self.previousChoice = None
    
    def delete(self):
        if self.dialog is not None:
            self.dialog.teardown()
            self.dialog = None
            
    def on_layer_update(self):
        layer = self.scene.currentLayer
        if layer == None:
            self.delete()
            return
        if self.dialog != None:
            self.dialog.teardown()
        # create layout according to editor mode
        if layer.name == "terrain" or layer.name == "object":
            name = layer.name
        else:
            name = "aesthetic"
        self.layout = self.layouts[name]()
        self.dialog = kytten.Dialog(kytten.Frame(kytten.VerticalLayout([self.layout])),
            window=self.window, batch=self.window.dialogBatch,
            anchor=kytten.ANCHOR_TOP_LEFT, theme=theme)
            
    def on_tool_select(self, id):
        self.active_tool = id
        self.scene.setCurrentTool(id)
        # reset the selected item dialog
        if self.window.selectedItemDialog.dialog != None:
            self.window.selectedItemDialog.dialog.teardown()
            
            
    def on_item_select(self, item):
        self.selectedItemLabel.set_text(item)
        #TODO correct this path.
        path = os.path.join("graphics/scene/visuals/", item)
        self.selectedItemImage.setImage(pyglet.image.load(path))
        
        self.scene.tools['placeitem'].setSelectedItem(path)

    '''
    creates terrain layer manip dialog.
    syncing with current options
    '''
    def terrainLayout(self):
        def on_snapmode_click(is_checked):
            self.scene.tools['plotline'].snapMode = is_checked

        def on_colour_select(choice):
            self.scene.graph.layers['terrain'].setLineColor(choice)
        
        toolSet = []
        toolSet.append(('pan', pyglet.image.load(
            os.path.join('theme', 'tools', 'pan.png'))))
        toolSet.append(('plotline', pyglet.image.load(
            os.path.join('theme', 'tools', 'plotline.png'))))
        toolSet.append(('select',pyglet.image.load(
            os.path.join('theme', 'tools', 'select.png'))))
            
        # Create options from images to pass to Palette
        palette_options = [[]]
        palette_options.append([])
        palette_options.append([])
        for i, pair in enumerate(toolSet):
            option = widgets.PaletteOption(id=pair[0], image=pair[1], padding=4)
            # Build column down, 3 rows
            palette_options[i%2].append(option)
        toolSection = widgets.PaletteMenu(palette_options, on_select=self.on_tool_select)
        
        '''
        sync dropdown colour selection
        '''
        keys = self.scene.currentLayer.colors.items()
        for key in keys:
            if key[1] == self.scene.currentLayer.curColor:
                colour = key[0]
                break
        
        return kytten.VerticalLayout([
            toolSection,
            kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
            kytten.Label("Line Colour"),
            kytten.Dropdown(["White", "Black", "Blue", "Green", "Red"], selected=colour, on_select=on_colour_select),
            kytten.Checkbox("Point Snap", is_checked=self.scene.tools["plotline"].snapMode, on_click=on_snapmode_click)
        ])
    
    '''
    
    '''
    def itemLayout(self):
        def on_select_item():
            SelectItemDialog(self.window, self.scene.currentLayer, self)
            
        toolSet = []
        toolSet.append(('pan', pyglet.image.load(
            os.path.join('theme', 'tools', 'pan.png'))))
        toolSet.append(('placeitem', pyglet.image.load(
            os.path.join('theme', 'tools', 'object.png'))))
        toolSet.append(('select',pyglet.image.load(
            os.path.join('theme', 'tools', 'select.png'))))
            
        # Create options from images to pass to Palette
        palette_options = [[]]
        palette_options.append([])
        palette_options.append([])
        for i, pair in enumerate(toolSet):
            option = widgets.PaletteOption(id=pair[0], image=pair[1], padding=4)
            # Build column down, 3 rows
            palette_options[i%2].append(option)
        toolSection = widgets.PaletteMenu(palette_options, on_select=self.on_tool_select)
        
        '''
        selected item display
        '''
        self.selectedItemLabel = kytten.Label("")
        self.selectedItemImage = widgets.Image(None,  maxWidth=128, maxHeight=164)
        
        '''
        sync layer
        '''
        
        
        return kytten.VerticalLayout([
            toolSection,
            kytten.SectionHeader("Selected Item", align=kytten.HALIGN_LEFT),
            self.selectedItemLabel,
            self.selectedItemImage,
            kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
            kytten.Button("Select Item", on_click=on_select_item)
        ])
        
'''
    class SelectItemDialog
    allows user to select aesthetic or object item
'''
class SelectItemDialog(Dialog):
    def __init__(self, window, currentLayer, layerDialog):
        self.layerDialog = layerDialog
        layout = self.createLayout(currentLayer)
        super(SelectItemDialog, self).__init__(
            kytten.Frame(layout),
                window=window, batch=window.dialogBatch,
                anchor=kytten.ANCHOR_CENTER, theme=theme,
                on_enter=self.on_enter, on_escape=on_escape)
                
    def createLayout(self, currentLayer):
        folderName = None
        if(isinstance(currentLayer,scenegraph.ObjectLayer)):
            folderName = "objects"
        elif(isinstance(currentLayer,scenegraph.AestheticLayer)):
            folderName = "visuals"
        '''
        build list of items with name and image
        '''
        path = os.path.join("graphics/scene",folderName)
        items = list()
        for (path, dirs, files) in os.walk(path):
            for file in files:
                if file.endswith(".png"):
                    items.append([file, pyglet.image.load(os.path.join(path, file))])
                
        return kytten.VerticalLayout([
            kytten.Scrollable(
                widgets.ItemMenu(items, on_select=self.layerDialog.on_item_select),
                height=600),
            kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
            kytten.HorizontalLayout([
                Button("Cancel", on_click=self.cancel),
                Button("Ok", on_click=lambda:self.on_enter(self))
            ], align=kytten.ANCHOR_BOTTOM_RIGHT)
        ])
    
    def cancel(self):
        on_escape(self)
                
    def on_enter(self, dialog):
        on_escape(self)



'''
    class SelectedItemDialog
    indicated currently selected and item and displays editable properties
'''
class SelectedItemDialog(object):
    currentItem = None

    def __init__(self, editor):
        self.dialog = None
        self.scene = editor.sceneController
        self.window = editor
        self.updateItem()
        
    def on_select_item(self):
        print "select"
        item = self.scene.tools["select"].selectedItem
        self.updateItem(item)
        
    def updateItem(self, item=None):
        if self.dialog != None:
            self.dialog.teardown()
        if item == None:
            self.currentItem = None
        else:
            self.currentItem = item
            if isinstance(item, scenegraph.Line):
                layout = kytten.GridLayout([
                    [kytten.Label("X1 Pos"), kytten.Input("x1_pos", str(item.x1), abs_width=50, max_length=5)],
                    [kytten.Label("Y1 Pos"), kytten.Input("y1_pos", str(item.y1), abs_width=50, max_length=5)],
                    [kytten.Label("X2 Pos"), kytten.Input("x2_pos", str(item.x2), abs_width=50, max_length=5)],
                    [kytten.Label("Y2 Pos"), kytten.Input("y2_pos", str(item.y2), abs_width=50, max_length=5)]
                ])
            else:
                layout = None
            self.dialog = kytten.Dialog(
                kytten.Frame(kytten.FoldingSection("Item",layout)),
                window=self.window, batch=self.window.dialogBatch,
                anchor=kytten.ANCHOR_BOTTOM_LEFT, theme=theme)
            
        
'''
    GridOptionsDialog
    shows editable grid options.
'''
class GridOptionsDialog(Dialog):
    def __init__(self, window, batch, scene):
        self.scene = scene
        super(GridOptionsDialog, self).__init__(
            kytten.Frame(
                    kytten.VerticalLayout([
                        kytten.SectionHeader("Grid Options", align=kytten.HALIGN_LEFT),
                        kytten.Checkbox("Show Grid", id="show_grid"),
                        kytten.Checkbox("Snap To Grid", id="snap_to"),
                        kytten.GridLayout([
                            [kytten.Label("H Spacing"), kytten.Input("h_spacing", "50", max_length=3)],
                            [kytten.Label("V Spacing"), kytten.Input("v_spacing", "50", max_length=3)],
                            [kytten.Label("H Offset"), kytten.Input("h_offset", "50", max_length=3)],
                            [kytten.Label("V Offset"), kytten.Input("v_offset", "50", max_length=3)]
                            ]),
                        kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
                        kytten.HorizontalLayout([
                             kytten.Button("Ok",
                                 on_click=self.on_submit),
                             kytten.Button("Cancel",
                                 on_click=self.on_cancel)]),
                                 ])),
                window=window, batch=batch,
                anchor=kytten.ANCHOR_CENTER, theme=theme,
                on_enter=self.on_enter, on_escape=on_escape)
                
    def on_submit(self):
        values = self.get_values()
        self.scene.updateGrid(values)
        on_escape(self)
    
    def on_enter(self):
        on_submit()
    
    def on_cancel(self):
        on_escape(self)


       

'''
Class StatusPane
Controls a dialog that shows the user status information,
and allows one to change some relevent settings
'''
class StatusPane(Dialog):
    def __init__(self, window, batch, scene):
        frame = self.createLayout()
        super(StatusPane, self).__init__(
            frame, window=window, batch=batch, 
            anchor=kytten.ANCHOR_BOTTOM, theme=theme)
        self.scene = scene
    
    def updateCoords(self):
        x = self.scene.mouseCoord[0]
        y = self.scene.mouseCoord[1]
        if self.scene.graph is not None:
            x = x - self.scene.graph.focusX
            y = y - self.scene.graph.focusY
        strX = "X: " + str(x)
        self.xLabel.set_text(strX)
        strY = "Y: " + str(y)
        self.yLabel.set_text(strY)

    def createLayout(self):
        self.xLabel = kytten.Label("X:")
        self.yLabel = kytten.Label("Y:")
        coords = kytten.VerticalLayout([self.xLabel, self.yLabel])
        return kytten.Frame(kytten.HorizontalLayout([
            kytten.Spacer(200, 45),
            kytten.Button("Grid", on_click=self.gridDialog),
            kytten.Spacer(10, 0),
            coords, kytten.Spacer(10, 0)]),
             path=['pane'])
    
    def gridDialog(self):
        GridOptionsDialog(self.window, self.batch, self.scene)
    
    def on_update(self, dt):
        self.updateCoords()
        super(StatusPane, self).on_update(dt)

        
        
'''
    class ConfirmExitDialo
    Controls a Dialog prompts User to save the level if edited and not saved
'''    
class ConfirmExitDialog(Dialog):
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
        self.scene = levelView
    
    def save(self):
        def on_select(filename):
            self.scene.saveLevel(filename)
            self.exit()
        kytten.FileSaveDialog(
            extensions=[levelview.FILE_EXT], window=self.window,
            batch=self.batch, anchor=kytten.ANCHOR_CENTER,
            theme=theme, on_select=on_select)   
    
    def exitApp(self):
        self.scene.map = None
        pyglet.app.exit()
    
    def cancel(self):
        self.teardownDialog(self)
        
    def teardownDialog(self, dialog):
        super(ConfirmExitDialog, self).teardown()
    
'''        # detect double click and toggle fullscreen
        if self.time - self.lastClick <= 150:
            self.set_fullscreen(not self.fullscreen)
        self.lastClick = self.time'''
            
   
    
