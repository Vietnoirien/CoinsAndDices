import wx
import math
import json
from char_edit import CharacterEditor
from monster_edit import MonsterEditor
import os
from biome_manager import BiomeManager
from hex_manager import HexManager
from panel_manager import PanelManager
from companion_edit import CompanionEditor
from drawing_manager import DrawingManager

class HexagonalGrid(wx.Frame):
    def __init__(self):
        screen = wx.Display().GetGeometry()
        window_width = int(screen.width * 0.8)
        window_height = int(screen.height * 0.8)

        super().__init__(parent=None, title='Grille Hexagonale', size=(window_width, window_height))

        self.grid_width = 13
        self.grid_height = 14
    
        self.hex_manager = HexManager(self.grid_width, self.grid_height)
        self.drawing_manager = self.hex_manager.drawing_manager
        self.calculate_hex_size()

        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.canvas = wx.Panel(self.panel)
        self.canvas.SetBackgroundColour(wx.WHITE)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

        right_panel = wx.Panel(self.panel)
    
        self.char_editor = CharacterEditor(right_panel)
        self.monster_editor = MonsterEditor(right_panel)
        self.buttons_panel = wx.Panel(right_panel)
        self.panel_manager = PanelManager(self)
        self.companion_editor = CompanionEditor(right_panel)

        self.panel_manager.register_panels(
            self.buttons_panel,
            self.char_editor,
            self.monster_editor,
            self.companion_editor,
            right_panel
        )

        main_sizer.Add(self.canvas, 3, wx.EXPAND|wx.ALL|wx.GROW, 5)
        main_sizer.Add(right_panel, 2, wx.EXPAND|wx.ALL|wx.GROW, 5)
        self.panel.SetSizer(main_sizer)
    
        self.char_editor.Hide()
        self.monster_editor.Hide()
        self.companion_editor.Hide()

        self.right_panel = right_panel
        self.hex_manager.canvas = self.canvas
        self.biome_manager = BiomeManager(self.hex_manager)
        self.hex_manager.set_biome_manager(self.biome_manager)
        self.last_clicked_hex = None
    
        self.Bind(wx.EVT_SIZE, self.on_resize)        
        self.ensure_directory_structure()
        self.Center()
        self.Show()

    def on_paint(self, event):
        dc = wx.PaintDC(self.canvas)
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                center = self.hex_manager.get_hex_center(col, row)
                points = self.hex_manager.get_hex_points(*center)
                pos = (col, row)
                biome_name = self.biome_manager.get_biome(pos)
                biome_data = self.biome_manager.get_biome_data(biome_name)
                self.drawing_manager.draw_hex(dc, points, biome_data, col, row)

    def calculate_hex_size(self):
        width, height = self.GetSize()
        canvas_width = width * 0.6
        canvas_height = height - 40
        
        margin = 40
        usable_width = canvas_width - (2 * margin)
        usable_height = canvas_height - (2 * margin)
        
        width_based_size = usable_width / (self.grid_width * 1.5)
        height_based_size = usable_height / ((self.grid_height + 0.5) * math.sqrt(3))
        
        self.hex_manager.hex_size = min(width_based_size, height_based_size)
                 
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
            self.hex_manager.last_clicked_hex = hex_pos
            self.canvas.Refresh()

    def on_right_click(self, event):
        pos = event.GetPosition()
        hex_pos = self.hex_manager.get_clicked_hex(pos.x, pos.y)
        if hex_pos:
            self.hex_manager.last_clicked_hex = hex_pos
            menu = self.biome_manager.create_context_menu(self)
            self.canvas.PopupMenu(menu)
            menu.Destroy()
