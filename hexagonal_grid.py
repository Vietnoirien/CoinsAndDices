import wx
import math
import json
from char_edit import CharacterEditor
from monster_edit import MonsterEditor
import os

class HexagonalGrid(wx.Frame):
    def __init__(self):
        # Calcul de la taille de la fenêtre basée sur l'écran
        screen = wx.Display().GetGeometry()
        window_width = int(screen.width * 0.8)
        window_height = int(screen.height * 0.8)
    
        super().__init__(parent=None, title='Grille Hexagonale', size=(window_width, window_height))

        # Définition des dimensions de la grille
        self.grid_width = 13
        self.grid_height = 14

        # Calcul initial de la taille des hexagones
        self.calculate_hex_size()

        # Création du panneau principal avec un sizer horizontal
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Canvas pour la grille hexagonale (partie gauche)
        self.canvas = wx.Panel(self.panel)
        self.canvas.SetBackgroundColour(wx.WHITE)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

        # Panneau droit avec gestion proportionnelle
        right_panel = wx.Panel(self.panel)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Création des éditeurs
        self.char_editor = CharacterEditor(right_panel)
        self.monster_editor = MonsterEditor(right_panel)

        # Panneau de boutons
        self.buttons_panel = wx.Panel(right_panel)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Création et configuration des boutons
        self.char_button = wx.Button(self.buttons_panel, label="Créer un personnage")
        self.monster_button = wx.Button(self.buttons_panel, label="Créer un monstre")
        self.char_button.Enable(True)
        self.monster_button.Enable(True)        
        self.char_button.Bind(wx.EVT_BUTTON, self.show_char_editor)
        self.monster_button.Bind(wx.EVT_BUTTON, self.show_monster_editor)


        # Ajout des boutons avec expansion
        buttons_sizer.Add(self.char_button, 1, wx.ALL|wx.EXPAND, 5)
        buttons_sizer.Add(self.monster_button, 1, wx.ALL|wx.EXPAND, 5)
        self.buttons_panel.SetSizer(buttons_sizer)

        # Configuration du panneau droit avec proportions
        right_sizer.Add(self.buttons_panel, 0, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_sizer.Add(self.char_editor, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_sizer.Add(self.monster_editor, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)
        right_panel.SetSizer(right_sizer)

        # Configuration du sizer principal avec ratio 60/40
        main_sizer.Add(self.canvas, 3, wx.EXPAND|wx.ALL|wx.GROW, 5)
        main_sizer.Add(right_panel, 2, wx.EXPAND|wx.ALL|wx.GROW, 5)
        self.panel.SetSizer(main_sizer)

        # État initial des éditeurs
        self.char_editor.Hide()
        self.monster_editor.Hide()

        # Stockage de la référence au panneau droit
        self.right_panel = right_panel

        self.biomes = {
        "Marais": {"primary": wx.Colour(0, 100, 100), "pattern": None},
        "Plaine": {"primary": wx.Colour(144, 238, 144), "pattern": None},
        "Riviere": {
            "primary": wx.Colour(144, 238, 144),
            "pattern": {"color": wx.Colour(0, 0, 255), "type": "line"}
        },
        "Colline": {"primary": wx.Colour(165, 113, 78), "pattern": None},
        "Route": {
            "primary": wx.Colour(144, 238, 144),
            "pattern": {"color": wx.Colour(139, 69, 19), "type": "line"}
        },
        "Montagne": {"primary": wx.Colour(101, 67, 33), "pattern": None},
        "Ville": {"primary": wx.Colour(128, 128, 128), "pattern": None},
        "Foret": {"primary": wx.Colour(0, 100, 0), "pattern": None}
        }

        self.hex_biomes = {}
        self.last_clicked_hex = None
        self.Bind(wx.EVT_SIZE, self.on_resize)        
        self.ensure_directory_structure()
        self.load_biomes()
        self.Center()
        self.Show()

    def show_char_editor(self, event):
        self.buttons_panel.Hide()
        self.char_editor.Show()
        self.buttons_panel.Disable()  # Désactive les boutons pendant l'édition
        self.char_editor.init_panel.Hide()
        self.char_editor.editor_panel.Show()
        self.monster_editor.Hide()
        self.Layout()
        self.force_layout()

    def show_monster_editor(self, event):
        self.buttons_panel.Hide()
        self.buttons_panel.Disable()  # Désactive les boutons pendant l'édition
        self.monster_editor.Show()
        self.monster_editor.init_panel.Hide()
        self.monster_editor.editor_panel.Show()
        self.char_editor.Hide()
        self.Layout()
        self.force_layout()

    def rebind_buttons(self):
        self.char_button.Bind(wx.EVT_BUTTON, self.show_char_editor)
        self.monster_button.Bind(wx.EVT_BUTTON, self.show_monster_editor)

    def force_layout(self):
            self.panel.Layout()
            self.panel.GetChildren()[1].Layout()  # Accès au panneau droit via les enfants
            self.char_editor.Layout()
            self.monster_editor.Layout()
            self.Refresh()
        
    def calculate_hex_size(self):
        width, height = self.GetSize()
        # Ajuster la largeur disponible en tenant compte du ratio 60/40
        available_width = width * 0.6  # 60% de la largeur pour la grille
        
        # Calcul des dimensions maximales possibles pour un hexagone
        max_width = (available_width - 50) / (self.grid_width * 1.5)
        max_height = (height - 50) / (self.grid_height * math.sqrt(3))
        
        # Prendre la plus petite valeur pour garantir que les hexagones rentrent dans l'espace
        self.hex_size = min(max_width, max_height)

    def get_hex_center(self, col, row):
        width = self.hex_size * 2
        height = self.hex_size * math.sqrt(3)
        
        x = width * 0.75 * col
        y = height * row
        
        if col % 2:
            y += height / 2
            
        return (x + width/2, y + height/2)

    def get_hex_points(self, x, y):
        points = []
        for i in range(6):
            angle = (i * 60) * math.pi / 180
            px = x + self.hex_size * math.cos(angle)
            py = y + self.hex_size * math.sin(angle)
            points.append((px, py))
        return points

    def get_adjacent_hexes(self, col, row):
        adjacents = []
        if col % 2 == 0:
            directions = [
                (0, -1), (1, -1), (1, 0),
                (0, 1), (-1, 0), (-1, -1)
            ]
        else:
            directions = [
                (0, -1), (1, 0), (1, 1),
                (0, 1), (-1, 1), (-1, 0)
            ]
        
        for dx, dy in directions:
            new_col, new_row = col + dx, row + dy
            if 0 <= new_col < self.grid_width and 0 <= new_row < self.grid_height:
                adjacents.append((new_col, new_row))
        return adjacents

    def get_clicked_hex(self, mouse_x, mouse_y):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                center = self.get_hex_center(col, row)
                if self.point_in_hex(mouse_x, mouse_y, center):
                    return (col, row)
        return None

    def point_in_hex(self, px, py, center):
        cx, cy = center
        dx = abs(px - cx)
        dy = abs(py - cy)
        
        hex_width = self.hex_size * math.sqrt(3) / 2
        hex_height = self.hex_size
        
        if dx > hex_width or dy > hex_height:
            return False
            
        return (hex_width * hex_height - hex_width * dy - hex_height * dx / 2) >= 0

    def create_context_menu(self):
        menu = wx.Menu()
        for biome in self.biomes.keys():
            item = menu.Append(-1, biome)
            self.Bind(wx.EVT_MENU, lambda evt, b=biome: self.set_biome(evt, b), item)
        return menu

    def on_right_click(self, event):
        pos = event.GetPosition()
        hex_pos = self.get_clicked_hex(pos.x, pos.y)
        if hex_pos:
            self.last_clicked_hex = hex_pos
            menu = self.create_context_menu()
            self.canvas.PopupMenu(menu)
            menu.Destroy()

    def set_biome(self, event, biome):
        if self.last_clicked_hex:
            self.hex_biomes[str(self.last_clicked_hex)] = biome
            self.save_biomes()
            self.canvas.Refresh()

    def save_biomes(self):
        os.makedirs('Runelimit', exist_ok=True)
        with open('Runelimit/biomes.json', 'w') as f:
            json.dump(self.hex_biomes, f)

    def load_biomes(self):
        try:
            with open('Runelimit/biomes.json', 'r') as f:
                self.hex_biomes = json.load(f)
        except FileNotFoundError:
            self.hex_biomes = {}

    def on_click(self, event):
        pos = event.GetPosition()
        hex_pos = self.get_clicked_hex(pos.x, pos.y)
        self.last_clicked_hex = hex_pos
        if hex_pos:
            self.canvas.Refresh()

    def should_connect(self, biome1, biome2):
        if not biome1 or not biome2:
            return False
            
        if biome1 == "Riviere" and biome2 in ["Riviere", "Ville", "Marais"]:
            return True
        
        if biome1 == "Route" and biome2 in ["Route", "Ville"]:
            return True
        
        return False

    def find_river_connections(self, col, row):
        # Separate neighbors by type
        marsh_neighbors = []
        other_water_neighbors = []
    
        for adj_col, adj_row in self.get_adjacent_hexes(col, row):
            adj_biome = self.hex_biomes.get(str((adj_col, adj_row)))
            if adj_biome == "Marais":
                marsh_neighbors.append((adj_col, adj_row))
            elif adj_biome in ["Riviere", "Ville"]:
                other_water_neighbors.append((adj_col, adj_row))
    
        connections = []
        # Add marsh connections first
        connections.extend(marsh_neighbors)
    
        # If we still have room for connections, add other water tiles
        remaining_slots = 2 - len(connections)
        if remaining_slots > 0:
            connections.extend(other_water_neighbors[:remaining_slots])
    
        return connections[:2]  # Ensure we never return more than 2 connections

    def draw_connected_lines(self, dc, points, col, row, color):
        current_biome = self.hex_biomes.get(str((col, row)))
        center = self.get_hex_center(col, row)
        
        if current_biome == "Riviere":
            connections = self.find_river_connections(col, row)
            for next_col, next_row in connections:
                next_biome = self.hex_biomes.get(str((next_col, next_row)))
                next_center = self.get_hex_center(next_col, next_row)
                
                if next_biome in ["Marais", "Ville"]:
                    # Dessine une demi-ligne vers le marais ou la ville
                    mid_x = (center[0] + next_center[0]) / 2
                    mid_y = (center[1] + next_center[1]) / 2
                    dc.SetPen(wx.Pen(color, 2))
                    dc.DrawLine(int(center[0]), int(center[1]), int(mid_x), int(mid_y))
                else:
                    # Dessine une ligne complète pour les autres connexions
                    dc.SetPen(wx.Pen(color, 2))
                    dc.DrawLine(int(center[0]), int(center[1]), 
                               int(next_center[0]), int(next_center[1]))
        
        elif current_biome == "Route":
            for adj_col, adj_row in self.get_adjacent_hexes(col, row):
                adj_biome = self.hex_biomes.get(str((adj_col, adj_row)))
                if self.should_connect(current_biome, adj_biome):
                    adj_center = self.get_hex_center(adj_col, adj_row)
                    
                    if adj_biome in ["Marais", "Ville"]:
                        # Demi-ligne pour les connexions vers ville
                        mid_x = (center[0] + adj_center[0]) / 2
                        mid_y = (center[1] + adj_center[1]) / 2
                        dc.SetPen(wx.Pen(color, 2))
                        dc.DrawLine(int(center[0]), int(center[1]), int(mid_x), int(mid_y))
                    else:
                        # Ligne complète pour les autres connexions
                        dc.SetPen(wx.Pen(color, 2))
                        dc.DrawLine(int(center[0]), int(center[1]), 
                                   int(adj_center[0]), int(adj_center[1]))
                        
    def draw_hex(self, dc, points, biome_data, col, row):
        # Dessine l'hexagone de base
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        
        # Vérifie si la position a un biome assigné
        pos = str((col, row))
        if pos not in self.hex_biomes:
            dc.SetBrush(wx.Brush(wx.WHITE))
        else:
            dc.SetBrush(wx.Brush(biome_data["primary"]))
            
        dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])

        # Dessine les motifs uniquement si ce n'est pas un Marais ou une Ville
        current_biome = self.hex_biomes.get(str((col, row)))
        if biome_data["pattern"] and current_biome not in ["Marais", "Ville"]:
            if biome_data["pattern"]["type"] == "line":
                self.draw_connected_lines(dc, points, col, row, biome_data["pattern"]["color"])

    def on_paint(self, event):
        dc = wx.PaintDC(self.canvas)
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                center = self.get_hex_center(col, row)
                points = self.get_hex_points(*center)
                pos = (col, row)
                
                biome_name = self.hex_biomes.get(str(pos), "Plaine")
                biome_data = self.biomes[biome_name]
                self.draw_hex(dc, points, biome_data, col, row)

    def on_resize(self, event):
        self.calculate_hex_size()
        self.canvas.Refresh()
        event.Skip()

    def ensure_directory_structure(self):
        """
        Assure que tous les répertoires nécessaires existent
        """
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
