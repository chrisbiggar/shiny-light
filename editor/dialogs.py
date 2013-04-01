'''
Editor Dialogs

'''
import os
import pyglet
import kytten
from kytten.dialog import Dialog
from kytten.button import Button
from kytten.layout import VerticalLayout, HorizontalLayout, GridLayout

import widgets
import py2d.scenegraph as scenegraph


theme = kytten.Theme(os.path.join(os.getcwd(), 'theme'), override={
"gui_color": [64, 128, 255, 255],
"font_size": 16
})

def genOkCancelLayout(on_submit, on_cancel):
    return HorizontalLayout([
         Button("Ok", on_click=on_submit),
         Button("Cancel", on_click=on_cancel)
        ], align=kytten.HALIGN_RIGHT)


def on_escape(dialog):
    '''
        tears down specified dialog
    '''
    dialog.teardown()


class MainDialog(Dialog):
    '''
        class MainDialog
        main dialog for application. allows layer navigation and map loading/saving
    '''
    lastLayerChoice = None
    def __init__(self, editor):
        self.scene = editor.sceneController
        frame = self.createLayout()
        super(MainDialog, self).__init__(frame,
            window=editor, batch=editor.dialogBatch, 
            anchor=kytten.ANCHOR_TOP_RIGHT, theme=theme)
        
    def syncLayerMenu(self):
        options = list()
        keys = self.scene.graph.layers.by_name.iterkeys()
        for key in keys:
            options.append(key)
        self.layerMenu.set_options(options)
        self.metaLayerMenu.set_options(['add layer', 'edit layer', 'source dir', 'bg color'])
        
        
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
            # add layer to LevelView
            NewLayerDialog(self, self.window, self.batch, self.scene)
            # unselect new layer button
            if self.layerMenu.selected is not None:
                self.layerMenu.options[self.layerMenu.selected].unselect()
        elif choice == "edit layer":
            EditLayerDialog(self.window, self.batch, self.scene)
        elif choice == "source dir":
            SourceDirectoryDialog(self.window, self.batch, self.scene)
        elif choice == "bg color":
            BackgroundColorDialog(self.window, self.batch, self.scene)

             
    def createLayout(self):
        # layers section
        self.layerMenu = kytten.Menu(options=[], on_select=self.layerMenuSelect)
        layersSection = kytten.FoldingSection("Layers", kytten.VerticalLayout([self.layerMenu]))
        #
        # layers section
        self.metaLayerMenu = widgets.ClickMenu(['-add layer', '-edit layer', '-source dir', '-bg color'], on_select=self.metaLayerMenuSelect)

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
                self.scene.loadLevel(filename)
                on_escape(dialog)
            dialog = kytten.FileLoadDialog(
                        extensions=[self.scene.graph.FILE_EXT], window=self.window, 
                        theme=self.theme,
                        on_select=on_select, batch=self.batch,
                        on_escape=on_escape,)
        elif choice == "Save Level":
            def on_select(filename):
                if filename.endswith('.lvl') == False:
                    filename += '.lvl'
                self.scene.graph.saveMapToFile(filename)
                on_escape(dialog)
            dialog = kytten.FileSaveDialog(
                extensions=[self.scene.graph.FILE_EXT], window=self.window,
                batch=self.batch, anchor=kytten.ANCHOR_CENTER,
                theme=self.theme, on_escape=on_escape, on_select=on_select)
        elif choice == "Quit":
            pyglet.app.exit()
            

class NewLevelDialog(Dialog):
    '''
        allows user to create new level specifying properties
    '''
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
                    genOkCancelLayout(self.on_submit, self.on_cancel)
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
    
class EditLayerDialog(object):
    '''
        allows user to edit the properties of the current layer
    '''
    def __init__(self, window, batch, scene):
        self.layouts = {
            "aesthetic" : self.aestheticLayout,
            "entitylist" : self.entityLayout,
            "switchingentitylist" : self.switchingEntityLayout
        }
        self.scene = scene
        self.dialog = None
        self.window = window
        self.sync()
        
    def sync(self, switch=""):
        if self.dialog != None:
            self.dialog.teardown()
        if switch == "entitylist":
            layout = self.layouts["switchingentitylist"]()
        else:
            currentLayer = self.scene.currentLayer
            if currentLayer is not None:
                '''setup the correct layout'''
                if currentLayer.name == "terrain" or \
                    currentLayer.name == "object":
                    layout = self.layouts["entitylist"]()
                else:
                    layout = self.layouts["aesthetic"]()
                layout.add(genOkCancelLayout(self.on_submit, self.on_cancel))
            else:
                #dont show dialog while no layer is selected
                return
        self.dialog = kytten.Dialog(kytten.Frame(layout),
            window=self.window, batch=self.window.dialogBatch,
            anchor=kytten.ANCHOR_CENTER, theme=theme)
        
    def aestheticLayout(self):
        def entitylist_click():
            self.sync(switch="entitylist")
        def delete_click():
            self.scene.graph.deleteAestheticLayer(self.scene.currentLayer.name)
            self.scene.currentLayer = None
            self.window.dispatch_event('on_layer_update')
        def visible_click(value):
            self.scene.currentLayer.setVisible(value)
        def opacity_on_set(value):
            self.scene.currentLayer.setOpacity(value)
            
        layer = self.scene.currentLayer
        if layer.name == "foreground":
            disableInputs = True
        else:
            disableInputs = False
        properties = GridLayout([
            [kytten.Label("Name"), kytten.Input("name", layer.name, max_length=20, abs_width=140, disabled=disableInputs)],
            [kytten.Label("Opacity"), kytten.Slider(layer.opacity, 0.0, 1.0, steps=10, on_set=opacity_on_set)],
            [kytten.Label("Visible"), kytten.Checkbox(is_checked=layer.visible, on_click=visible_click)],
            [kytten.Label("Z Order"), kytten.Input("z_order", str(layer.z_order), max_length=1, abs_width=35, disabled=disableInputs)],
            [kytten.Button("Entity List", on_click=entitylist_click), kytten.Button("Delete", on_click=delete_click, disabled=disableInputs)]
        ], padding=10)
        return VerticalLayout([
            kytten.SectionHeader("Aesthetic Layer", align=kytten.HALIGN_LEFT),
            properties,
            kytten.SectionHeader("", align=kytten.HALIGN_LEFT)
        ])
    
    def entityLayout(self):
        return VerticalLayout([
            kytten.SectionHeader("Entity List", align=kytten.HALIGN_LEFT),
            kytten.SectionHeader("", align=kytten.HALIGN_LEFT)
        ])
    
    def switchingEntityLayout(self):
        def on_cancel():
            pass
        def on_ok():
            pass
        def on_edit_layer():
            self.sync()
        if self.dialog != None:
            self.dialog.teardown()
        return VerticalLayout([
            self.entityLayout(),
            HorizontalLayout([
                Button("Edit Layer", on_click=on_edit_layer), 
                Button("Ok", on_click=on_ok), 
                Button("Cancel", on_click=on_cancel)
            ])
        ])
    
    def on_submit(self):
        layer = self.scene.currentLayer
        values = self.dialog.get_values()
        name = values["name"]
        if layer.name != name:
            self.scene.graph.layers.delete(layer.name)
            layer.name = name
            self.scene.graph.layers.addNamed(layer, layer.name)
            self.window.dispatch_event('on_layer_update')
        layer.setZOrder(int(values["z_order"]))
        self.dialog.teardown()
    def on_enter(self):
        on_submit()
    def on_cancel(self):
        self.dialog.teardown()
            
            
class SourceDirectoryDialog(Dialog):
    '''
        allows the source directory to be chosen.
    '''
    def __init__(self, window, batch, scene):
        self.scene = scene
        currentPath = self.scene.graph.sourcePath
        super(SourceDirectoryDialog, self).__init__(
            kytten.Frame(kytten.VerticalLayout([
                kytten.Label("Source"),
                kytten.HorizontalLayout([
                    kytten.Input("source", currentPath,  max_length=20)
                ]),
                kytten.Spacer(height=20),
                genOkCancelLayout(self.on_submit, self.on_cancel)
            ])),
            window=window, batch=batch,
            anchor=kytten.ANCHOR_CENTER, theme=theme,
            on_enter=self.on_enter, on_escape=on_escape)
                
    def on_submit(self):
        values = self.get_values()
        self.scene.graph.sourcePath = values['source']
        on_escape(self)
    
    def on_enter(self, dialog):
        self.on_submit()
    
    def on_cancel(self):
        on_escape(self)
        
        
class BackgroundColorDialog(Dialog):
    '''
        Allows the background colour of current map
        to be changed.
    '''
    def __init__(self, window, batch, scene):
        self.scene = scene
        bgcolor = self.scene.graph.backColour
        super(BackgroundColorDialog, self).__init__(
            kytten.Frame(kytten.VerticalLayout([
                kytten.Label("RGB Selector"),
                kytten.HorizontalLayout([
                    kytten.Input("r", str(bgcolor[0]),  max_length=4, abs_width=60),
                    kytten.Input("g", str(bgcolor[1]),  max_length=4, abs_width=60),
                    kytten.Input("b", str(bgcolor[2]),  max_length=4, abs_width=60)
                    
                ]),
                kytten.Spacer(height=20),
                genOkCancelLayout(self.on_submit, self.on_cancel)
            ])),
            window=window, batch=batch,
            anchor=kytten.ANCHOR_CENTER, theme=theme,
            on_enter=self.on_enter, on_escape=on_escape)
                
    def on_submit(self):
        values = self.get_values()
        r = float(values['r'])
        g = float(values['g'])
        b = float(values['b'])
        self.scene.graph.backColour = [r,g,b]
        on_escape(self)
    
    def on_enter(self, dialog):
        self.on_submit()
    
    def on_cancel(self):
        on_escape(self)

 
class NewLayerDialog(Dialog):
    '''
        allows user to create new level specifying properties
    '''
    def __init__(self, parentDialog, window, batch, scene):
        self.scene = scene
        self.pDialog = parentDialog
        super(NewLayerDialog, self).__init__(
            kytten.Frame(
                kytten.VerticalLayout([
                    kytten.SectionHeader("New Aesthetic Layer", align=kytten.HALIGN_LEFT),
                    kytten.GridLayout([
                        [kytten.Label("Name"), kytten.Input("name", "untitled",
                                                max_length=20)],
                        [kytten.Label("Z Order"), kytten.Input("z_order", "3",
                                                max_length=1)]                                            
                    ]),
                    kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
                    genOkCancelLayout(self.on_submit, self.on_cancel)
                ])),
            window=window, batch=batch,
            anchor=kytten.ANCHOR_CENTER, theme=theme,
            on_enter=self.on_enter, on_escape=on_escape)   
            
    def on_submit(self):
        values = self.get_values()
        name = values["name"]
        z_order = values["z_order"]
        self.scene.graph.addAestheticLayer(name, z_order)
        self.pDialog.syncLayerMenu()
        on_escape(self)
        
    def on_enter(self, dialog):
        self.on_submit()
        
    def on_cancel(self):
        on_escape(self)
            
            
class LayerDialog(object):
    '''
        controls dialog that allows user to manipulate layers
        by dynamically while current type of layer is selected
        showing given controls for type of layer.
    '''   
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
            
    def sync(self):
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
        path = os.path.join(self.scene.graph.sourcePath, self.scene.currentLayer.dir, item)
        self.selectedItemImage.setImage(pyglet.image.load(path))
        
        self.scene.tools['placeitem'].setSelectedItem(path)

    def terrainLayout(self):
        '''
        creates terrain layer manip dialog.
        syncing with current options
        '''
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
            kytten.Checkbox("Point Snap", is_checked=self.scene.tools["plotline"].snapMode, on_click=on_snapmode_click),
            kytten.Checkbox("Grid Snap", id="snap_to", is_checked=True)
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
        
        return kytten.VerticalLayout([
            kytten.Label(self.scene.currentLayer.name),
            toolSection,
            kytten.SectionHeader("Selected Item", align=kytten.HALIGN_LEFT),
            self.selectedItemLabel,
            self.selectedItemImage,
            kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
            kytten.Checkbox("Grid Snap", id="snap_to", is_checked=True),
            kytten.Checkbox("Sticky Mode", id="sticky_mode", is_checked=True),
            kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
            kytten.Button("Select Item", on_click=on_select_item)
        ])
        

class SelectItemDialog(Dialog):
    '''
        allows user to select aesthetic or object item
    '''
    def __init__(self, window, currentLayer, layerDialog):
        self.scene = window.sceneController
        self.layerDialog = layerDialog
        layout = self.createLayout(currentLayer)
        super(SelectItemDialog, self).__init__(
            kytten.Frame(layout),
                window=window, batch=window.dialogBatch,
                anchor=kytten.ANCHOR_CENTER, theme=theme,
                on_enter=self.on_enter, on_escape=on_escape)
                
    def createLayout(self, currentLayer):
        '''
        build list of items with name and image
        '''
        path = os.path.join(self.scene.graph.sourcePath, currentLayer.dir)
        items = list()
        for (path, dirs, files) in os.walk(path):
            for file in files:
                if file.endswith(".png"):
                    items.append([file, pyglet.image.load(os.path.join(path, file))])
        
        if len(items) == 0:
            itemsMenu = kytten.Label("No Items Found")
        else:
             itemsMenu = kytten.Scrollable(widgets.ItemMenu(items, on_select=self.layerDialog.on_item_select),
                    height=600)
                
        return kytten.VerticalLayout([
            itemsMenu,
            kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
            genOkCancelLayout(self.on_submit, self.on_cancel)
        ])
    
    def on_cancel(self):
        on_escape(self)
    def on_submit(self):
        self.on_enter(self)
    def on_enter(self, dialog):
        on_escape(self)


class SelectedItemDialog(object):
    '''
        indicated currently selected and item and displays editable properties
    '''
    currentItem = None
    def __init__(self, editor):
        self.dialog = None
        self.scene = editor.sceneController
        self.window = editor
        self.updateItem()
        
    def on_select_item(self):
        item = self.scene.tools["select"].selectedItem
        self.updateItem(item)
        
    def updateItem(self, item=None):
        if self.dialog != None:
            self.dialog.teardown()
        if item == None:
            self.currentItem = None
        else:
            self.currentItem = item
            if self.scene.currentLayer.name == "terrain":
                layout = kytten.GridLayout([
                    [kytten.Label("X1 Pos"), kytten.Input("x1_pos", str(item.x1), abs_width=50, max_length=5)],
                    [kytten.Label("Y1 Pos"), kytten.Input("y1_pos", str(item.y1), abs_width=50, max_length=5)],
                    [kytten.Label("X2 Pos"), kytten.Input("x2_pos", str(item.x2), abs_width=50, max_length=5)],
                    [kytten.Label("Y2 Pos"), kytten.Input("y2_pos", str(item.y2), abs_width=50, max_length=5)]
                ])
            elif self.scene.currentLayer.name == "object":
                pass
            else:
                pass
            self.dialog = kytten.Dialog(
                kytten.Frame(kytten.FoldingSection("Item",layout)),
                window=self.window, batch=self.window.dialogBatch,
                anchor=kytten.ANCHOR_BOTTOM_LEFT, theme=theme)
    
    def genObjectLayout(self):
        pass
    
    def genVisualLayout(self):
        pass
    
    def genLineLayout(self):
        pass
            
       

class StatusPane(Dialog):
    '''
    Controls a dialog that shows the user status information,
    and allows one to change some relevent settings
    '''
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
        GridOptionsDialog(self.window, self.batch, self.scene.grid)
    
    def on_update(self, dt):
        self.updateCoords()
        super(StatusPane, self).on_update(dt)


class GridOptionsDialog(Dialog):
    '''
        shows editable grid options.
    '''
    def __init__(self, window, batch, grid):
        self.grid = grid
        super(GridOptionsDialog, self).__init__(
            kytten.Frame(
                    kytten.VerticalLayout([
                        kytten.SectionHeader("Grid Options", align=kytten.HALIGN_LEFT),
                        kytten.Checkbox("Show Grid", id="show_grid", is_checked=grid.visible),
                        kytten.GridLayout([
                            [kytten.Label("H Spacing"), kytten.Input("h_spacing", str(grid.hSpacing), max_length=3)],
                            [kytten.Label("V Spacing"), kytten.Input("v_spacing", str(grid.vSpacing), max_length=3)],
                            [kytten.Label("H Offset"), kytten.Input("h_offset", str(grid.hOffset), max_length=3)],
                            [kytten.Label("V Offset"), kytten.Input("v_offset", str(grid.vOffset), max_length=3)]
                            ]),
                        kytten.SectionHeader("", align=kytten.HALIGN_LEFT),
                        genOkCancelLayout(self.on_submit, self.on_cancel),
                                 ])),
                window=window, batch=batch,
                anchor=kytten.ANCHOR_CENTER, theme=theme,
                on_enter=self.on_enter, on_escape=on_escape)
                
    def on_submit(self):
        values = self.get_values()
        self.grid.visible = values["show_grid"]
        self.grid.hSpacing = int(values["h_spacing"])
        self.grid.vSpacing = int(values["v_spacing"])
        self.grid.hOffset = int(values["h_offset"])
        self.grid.vOffset = int(values["v_offset"])
        self.grid.update()
        on_escape(self)
    
    def on_enter(self):
        on_submit()
    
    def on_cancel(self):
        on_escape(self)

        
        
class ConfirmExitDialog(Dialog):
    '''
    Controls a Dialog prompts User to save the level if edited and not saved
    '''    
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
            
   
    
