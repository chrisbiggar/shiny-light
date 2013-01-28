'''
Widgets for map editor

'''

import pyglet
import kytten
from kytten.menu import *


class ClickMenu(Menu):
    '''
    A menu that does not stay selected.
    
    '''
    def __init__(self, options=[], align=HALIGN_CENTER, padding=4,
                 on_select=None):
        Menu.__init__(self, options=options, align=align, 
                      padding=padding, on_select=on_select)

    def select(self, text):
        if not text in self.options:
            return

        if self.selected is not None:
            self.options[self.selected].unselect()
        self.selected = text
        menu_option = self.options[text]
        #menu_option.select()

        if self.on_select is not None:
            self.on_select(text)
