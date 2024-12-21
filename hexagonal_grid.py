import wx
import math
import json
from char_edit import CharacterEditor
from monster_edit import MonsterEditor
import os
from biome_manager import BiomeManager
from hex_manager import HexManager
from panel_manager import PanelManager

class HexagonalGrid(wx.Frame):
    def __init__(self):
        screen = wx.Display().GetGeometry()
        window_width = int(screen.width * 0.8)
        window_height = int(screen.height * 0.8)
    
        super().__init__(parent=None, title='Grille Hexagonale', size=(window_width, window_height))

        self.grid_width = 13
        self.grid_height = 14
        
        self.hex_manager = HexManager(self.grid_width, self.grid_height)
        self.calculate_hex_size()

        # Main panel setup
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Canvas setup
        self.canvas = wx.Panel(self.panel)
        self.canvas.SetBackgroundColour(wx.WHITE)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

        # Right panel setup
        right_panel = wx.Panel(self.panel)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Editors setup
        self.char_editor = CharacterEditor(right_panel)
        self.monster_editor = MonsterEditor(right_panel)

        # Buttons panel setup
        self.buttons_panel = wx.Panel(right_panel)
        
        # Initialize PanelManager
        self.panel_manager = PanelManager(self)
        self.panel_manager.register_panels(
            self.buttons_panel,
            self.char_editor,
            self.monster_editor,
            right_panel
        )

        # Right panel sizer setup
        right_sizer.Add(self.buttons_panel, 0, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_sizer.Add(self.char_editor, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_sizer.Add(self.monster_editor, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_panel.SetSizer(right_sizer)

        # Main sizer setup
        main_sizer.Add(self.canvas, 3, wx.EXPAND|wx.ALL|wx.GROW, 5)
        main_sizer.Add(right_panel, 2, wx.EXPAND|wx.ALL|wx.GROW, 5)
        self.panel.SetSizer(main_sizer)

        # Initial panel states
        self.char_editor.Hide()
        self.monster_editor.Hide()

        # Initialize managers and bindings
        self.right_panel = right_panel
        self.biome_manager = BiomeManager(self.hex_manager)
        self.hex_manager.set_biome_manager(self.biome_manager)
        self.last_clicked_hex = None
        
        self.Bind(wx.EVT_SIZE, self.on_resize)        
        self.ensure_directory_structure()
        self.Center()
        self.Show()

    def calculate_hex_size(self):
        width, height = self.GetSize()
        self.hex_manager.calculate_hex_size(width, height)

    def should_connect(self, biome1, biome2):
        return self.biome_manager.should_connect(biome1, biome2)

    def create_context_menu(self):
        menu = wx.Menu()
        for biome in self.biome_manager.biomes.keys():
            item = menu.Append(-1, biome)
            self.Bind(wx.EVT_MENU, lambda evt, b=biome: self.set_biome(evt, b), item)
        return menu

    def set_biome(self, event, biome_name):
        if self.last_clicked_hex:
            self.biome_manager.set_biome(self.last_clicked_hex, biome_name)
            self.canvas.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self.canvas)
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                center = self.hex_manager.get_hex_center(col, row)
                points = self.hex_manager.get_hex_points(*center)
                pos = (col, row)
            
                biome_name = self.biome_manager.get_biome(pos)
                biome_data = self.biome_manager.get_biome_data(biome_name)
                self.hex_manager.draw_hex(dc, points, biome_data, col, row)
                   
    def on_resize(self, event):
        self.calculate_hex_size()
        self.canvas.Refresh()
        event.Skip()

    def ensure_directory_structure(self):
        base_dirs = [
            'Runelimit',
            'Runelimit/characters',
            'Runelimit/monsters',
            'Runelimit/monsters/class_1',
            'Runelimit/monsters/class_2',
            'Runelimit/monsters/class_3',
            'Runelimit/monsters/class_4'
        ]
        for directory in base_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def on_click(self, event):
        pos = event.GetPosition()
        hex_pos = self.hex_manager.get_clicked_hex(pos.x, pos.y)
        if hex_pos:
            self.last_clicked_hex = hex_pos
            self.canvas.Refresh()

    def on_right_click(self, event):
        pos = event.GetPosition()
        hex_pos = self.hex_manager.get_clicked_hex(pos.x, pos.y)
        if hex_pos:
            self.last_clicked_hex = hex_pos
            menu = self.create_context_menu()
            self.canvas.PopupMenu(menu)
            menu.Destroy()
