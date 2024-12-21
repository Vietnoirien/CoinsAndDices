import wx
import math
import json
from char_edit import CharacterEditor
from monster_edit import MonsterEditor
import os
from biome_manager import BiomeManager
from hex_manager import HexManager

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

        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.canvas = wx.Panel(self.panel)
        self.canvas.SetBackgroundColour(wx.WHITE)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

        right_panel = wx.Panel(self.panel)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        self.char_editor = CharacterEditor(right_panel)
        self.monster_editor = MonsterEditor(right_panel)

        self.buttons_panel = wx.Panel(right_panel)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.char_button = wx.Button(self.buttons_panel, label="Créer un personnage")
        self.monster_button = wx.Button(self.buttons_panel, label="Créer un monstre")
        self.char_button.Enable(True)
        self.monster_button.Enable(True)        
        self.char_button.Bind(wx.EVT_BUTTON, self.show_char_editor)
        self.monster_button.Bind(wx.EVT_BUTTON, self.show_monster_editor)

        buttons_sizer.Add(self.char_button, 1, wx.ALL|wx.EXPAND, 5)
        buttons_sizer.Add(self.monster_button, 1, wx.ALL|wx.EXPAND, 5)
        self.buttons_panel.SetSizer(buttons_sizer)

        right_sizer.Add(self.buttons_panel, 0, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_sizer.Add(self.char_editor, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_sizer.Add(self.monster_editor, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_panel.SetSizer(right_sizer)

        main_sizer.Add(self.canvas, 3, wx.EXPAND|wx.ALL|wx.GROW, 5)
        main_sizer.Add(right_panel, 2, wx.EXPAND|wx.ALL|wx.GROW, 5)
        self.panel.SetSizer(main_sizer)

        self.char_editor.Hide()
        self.monster_editor.Hide()

        self.right_panel = right_panel
        self.biome_manager = BiomeManager(self.hex_manager)
        self.last_clicked_hex = None
        
        self.Bind(wx.EVT_SIZE, self.on_resize)        
        self.ensure_directory_structure()
        self.Center()
        self.Show()

    def show_char_editor(self, event):
        self.buttons_panel.Hide()
        self.char_editor.Show()
        self.buttons_panel.Disable()
        self.char_editor.init_panel.Hide()
        self.char_editor.editor_panel.Show()
        self.monster_editor.Hide()
        self.Layout()
        self.force_layout()

    def show_monster_editor(self, event):
        self.buttons_panel.Hide()
        self.buttons_panel.Disable()
        self.monster_editor.Show()
        self.monster_editor.init_panel.Hide()
        self.monster_editor.editor_panel.Show()
        self.char_editor.Hide()
        self.Layout()
        self.force_layout()

    def rebind_buttons(self):
        self.char_button.Bind(wx.EVT_BUTTON, self.show_char_editor)
        self.monster_button.Bind(wx.EVT_BUTTON, self.show_monster_editor)

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

    def find_river_connections(self, col, row):
        marsh_neighbors = []
        other_water_neighbors = []

        for adj_col, adj_row in self.hex_manager.get_neighbors(col, row):
            adj_biome = self.biome_manager.get_biome((adj_col, adj_row))
            if adj_biome == "Marais":
                marsh_neighbors.append((adj_col, adj_row))
            elif adj_biome in ["Riviere", "Ville"]:
                other_water_neighbors.append((adj_col, adj_row))

        connections = []
        connections.extend(marsh_neighbors)
        remaining_slots = 2 - len(connections)
        if remaining_slots > 0:
            connections.extend(other_water_neighbors[:remaining_slots])
        return connections[:2]

    def draw_connected_lines(self, dc, points, col, row, color):
        current_biome = self.biome_manager.get_biome((col, row))
        center = self.hex_manager.get_hex_center(col, row)
    
        if current_biome == "Riviere":
            connections = self.find_river_connections(col, row)
            for next_col, next_row in connections:
                next_biome = self.biome_manager.get_biome((next_col, next_row))
                next_center = self.hex_manager.get_hex_center(next_col, next_row)
            
                if next_biome in ["Marais", "Ville"]:
                    mid_x = (center[0] + next_center[0]) / 2
                    mid_y = (center[1] + next_center[1]) / 2
                    dc.SetPen(wx.Pen(color, 2))
                    dc.DrawLine(int(center[0]), int(center[1]), int(mid_x), int(mid_y))
                else:
                    dc.SetPen(wx.Pen(color, 2))
                    dc.DrawLine(int(center[0]), int(center[1]), 
                            int(next_center[0]), int(next_center[1]))
    
        elif current_biome == "Route":
            for adj_col, adj_row in self.hex_manager.get_neighbors(col, row):
                adj_biome = self.biome_manager.get_biome((adj_col, adj_row))
                if self.should_connect(current_biome, adj_biome):
                    adj_center = self.hex_manager.get_hex_center(adj_col, adj_row)
                
                    if adj_biome in ["Marais", "Ville"]:
                        mid_x = (center[0] + adj_center[0]) / 2
                        mid_y = (center[1] + adj_center[1]) / 2
                        dc.SetPen(wx.Pen(color, 2))
                        dc.DrawLine(int(center[0]), int(center[1]), int(mid_x), int(mid_y))
                    else:
                        dc.SetPen(wx.Pen(color, 2))
                        dc.DrawLine(int(center[0]), int(center[1]), 
                                int(adj_center[0]), int(adj_center[1]))

    def draw_hex(self, dc, points, biome_data, col, row):
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        dc.SetBrush(wx.Brush(biome_data["primary"]))
        dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])

        current_biome = self.biome_manager.get_biome((col, row))
        if biome_data["pattern"] and current_biome not in ["Marais", "Ville"]:
            if biome_data["pattern"]["type"] == "line":
                self.draw_connected_lines(dc, points, col, row, biome_data["pattern"]["color"])

    def on_paint(self, event):
        dc = wx.PaintDC(self.canvas)
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                center = self.hex_manager.get_hex_center(col, row)
                points = self.hex_manager.get_hex_points(*center)
                pos = (col, row)
            
                biome_name = self.biome_manager.get_biome(pos)
                biome_data = self.biome_manager.get_biome_data(biome_name)
                self.draw_hex(dc, points, biome_data, col, row) 
                   
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

    def force_layout(self):
        self.panel.Layout()
        self.right_panel.Layout()
        self.char_editor.Layout()
        self.monster_editor.Layout()
        self.Refresh()

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
