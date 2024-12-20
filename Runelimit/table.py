import wx
import math
import json
from dataclasses import dataclass
import os
from map_design import get_biomes, should_connect, find_river_connections
from mov_dice import MovementPhase
from events import TerrainHoverEvent, EVT_TERRAIN_HOVER

@dataclass
class PlayerToken:
    position: tuple
    color: wx.Colour
    name: str

class GameTable(wx.Frame):
    def __init__(self, players):
        screen = wx.Display().GetGeometry()
        window_width = int(screen.width * 0.8)
        window_height = int(screen.height * 0.8)
        
        super().__init__(parent=None, title='Table de jeu', size=(window_width, window_height))
        
        self.grid_width = 13
        self.grid_height = 14
        self.players = []
        self.biomes = get_biomes()
        
        colors = [wx.Colour(255, 0, 0), wx.Colour(0, 255, 0), 
                 wx.Colour(0, 0, 255), wx.Colour(255, 255, 0),
                 wx.Colour(255, 0, 255), wx.Colour(0, 255, 255)]
                 
        for i, player in enumerate(players):
            self.players.append(PlayerToken(
                position=player.position,
                color=colors[i],
                name=player.name
            ))
        
        self.calculate_hex_size()
        self.panel = wx.Panel(self)
        
        # Création du sizer horizontal principal
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Panneau gauche pour la grille
        left_panel = wx.Panel(self.panel)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.load_biomes()
        
        self.canvas = wx.Panel(left_panel)
        self.canvas.SetBackgroundColour(wx.WHITE)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        
        left_sizer.Add(self.canvas, 1, wx.EXPAND)
        left_panel.SetSizer(left_sizer)
        
        # Panneau droit pour les phases
        self.movement_phase = MovementPhase(self.panel, self.players[0].name)
        
        # Ajout des panneaux au sizer principal
        main_sizer.Add(left_panel, 2, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(self.movement_phase, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(main_sizer)
        
        self.Bind(wx.EVT_SIZE, self.on_resize)
        
        self.Center()
        self.Show()

        self.highlighted_hexes = set()
        self.selected_hex = None  # Pour stocker la case sélectionnée
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_hex_click)  # Ajout de l'événement de clic
        self.Bind(EVT_TERRAIN_HOVER, self.on_terrain_hover)
        self.selected_terrain = None  # Ajout d'un attribut pour stocker le terrain sélectionné

    def on_hex_click(self, event):
        x, y = event.GetPosition()
        clicked_hex = self.get_hex_from_pixel(x, y)
        
        if clicked_hex in self.highlighted_hexes:
            self.selected_hex = clicked_hex
            self.players[0].position = clicked_hex  # Met à jour la position du joueur
            self.highlighted_hexes.clear()
            self.canvas.Refresh()

    def on_terrain_hover(self, event):
        if event.terrain:
            self.selected_terrain = event.terrain
            player = self.players[0]
            self.highlighted_hexes.clear()
            adjacent_hexes = self.get_adjacent_hexes(*player.position)
            for hex_pos in adjacent_hexes:
                biome = self.hex_biomes.get(str(hex_pos))
                if biome == self.selected_terrain:
                    self.highlighted_hexes.add(hex_pos)
    
        self.canvas.Refresh()
        print(f"Position joueur: {player.position}")
        adjacent_hexes = self.get_adjacent_hexes(*player.position)
        print(f"Cases adjacentes: {adjacent_hexes}")
        for hex_pos in adjacent_hexes:
            biome = self.hex_biomes.get(str(hex_pos))
            print(f"Position {hex_pos} -> biome {biome}")
            if biome == event.terrain:
                print(f"Match trouvé: {hex_pos}")
                self.highlighted_hexes.add(hex_pos)
        print(f"Cases à surligner: {self.highlighted_hexes}")
        
        self.canvas.Refresh()
        
    def draw_hex(self, dc, points, biome_data, col, row):
        if (col, row) == self.selected_hex:
            # Case sélectionnée en jaune plein
            dc.SetPen(wx.Pen(wx.YELLOW, 2))
            dc.SetBrush(wx.Brush(wx.YELLOW))
            dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])
        elif (col, row) in self.highlighted_hexes:
            # Cases surlignées avec hachures
            dc.SetPen(wx.Pen(wx.YELLOW, 4))
            dc.SetBrush(wx.Brush(wx.YELLOW, wx.BRUSHSTYLE_CROSSDIAG_HATCH))
            dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])
            dc.SetBrush(wx.Brush(biome_data["primary"]))
            dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])
        else:
            # Affichage normal
            dc.SetPen(wx.Pen(wx.BLACK, 1))
            dc.SetBrush(wx.Brush(biome_data["primary"]))
            dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])

        current_biome = self.hex_biomes.get(str((col, row)))
        if biome_data["pattern"] and current_biome not in ["Marais", "Ville"]:
            if biome_data["pattern"]["type"] == "line":
                self.draw_connected_lines(dc, points, col, row, biome_data["pattern"]["color"])

    def get_hex_from_pixel(self, px, py):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                center = self.get_hex_center(col, row)
                points = self.get_hex_points(*center)
                if self.point_in_polygon(px, py, points):
                    return (col, row)
        return None

    def calculate_hex_size(self):
        width, height = self.GetSize()
        max_width = (width * 0.66 - 50) / (self.grid_width * 1.5)  # Ajusté pour tenir compte du panneau droit
        max_height = (height - 50) / (self.grid_height * math.sqrt(3))
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

    def load_biomes(self):
        try:
            with open('Runelimit/biomes.json', 'r') as f:
                self.hex_biomes = json.load(f)
        except FileNotFoundError:
            self.hex_biomes = {}

    def draw_token(self, dc, center, color, size):
        x, y = center
        token_size = self.hex_size * 0.4
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(wx.BLACK, 2))
        dc.DrawCircle(int(x), int(y), int(token_size))

    def draw_connected_lines(self, dc, points, col, row, color):
        current_biome = self.hex_biomes.get(str((col, row)))
        center = self.get_hex_center(col, row)
        
        if current_biome == "Riviere":
            connections = find_river_connections(self.hex_biomes, col, row, self.get_adjacent_hexes)
            for next_col, next_row in connections:
                next_biome = self.hex_biomes.get(str((next_col, next_row)))
                next_center = self.get_hex_center(next_col, next_row)
                
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
            for adj_col, adj_row in self.get_adjacent_hexes(col, row):
                adj_biome = self.hex_biomes.get(str((adj_col, adj_row)))
                if should_connect(current_biome, adj_biome):
                    adj_center = self.get_hex_center(adj_col, adj_row)
                    
                    if adj_biome in ["Marais", "Ville"]:
                        mid_x = (center[0] + adj_center[0]) / 2
                        mid_y = (center[1] + adj_center[1]) / 2
                        dc.SetPen(wx.Pen(color, 2))
                        dc.DrawLine(int(center[0]), int(center[1]), int(mid_x), int(mid_y))
                    else:
                        dc.SetPen(wx.Pen(color, 2))
                        dc.DrawLine(int(center[0]), int(center[1]), 
                                   int(adj_center[0]), int(adj_center[1]))

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

        for player in self.players:
            center = self.get_hex_center(*player.position)
            self.draw_token(dc, center, player.color, self.hex_size * 0.4)

    def on_resize(self, event):
        self.calculate_hex_size()
        self.canvas.Refresh()
        event.Skip()
        
    def point_in_polygon(self, x, y, points):
        n = len(points)
        inside = False
        
        p1x, p1y = points[0]
        for i in range(n + 1):
            p2x, p2y = points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
