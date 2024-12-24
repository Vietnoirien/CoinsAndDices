import wx
from dataclasses import dataclass
import os
import json
from managers.hex_manager import HexManager
from managers.biome_manager import BiomeManager
from managers.drawing_manager import DrawingManager
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
        
        self.players = []
        self.grid_width = 13
        self.grid_height = 14        
        
        self._initialize_managers()
        self._setup_players(players)
        self._setup_ui()
        
        self.highlighted_hexes = set()
        self.selected_hex = None
        self.selected_terrain = None
        self.valid_moves = set()  # Pour stocker les positions valides
        
        self._bind_events()
        self.Center()
        self.Show()

    def _initialize_managers(self):
        self.hex_manager = HexManager(self.grid_width, self.grid_height)
        self.drawing_manager = DrawingManager(self.hex_manager)
        self.biome_manager = BiomeManager(self.hex_manager)
        
        self.hex_manager.drawing_manager = self.drawing_manager
        self.hex_manager.biome_manager = self.biome_manager
        self.drawing_manager.biome_manager = self.biome_manager
        self.biome_manager.drawing_manager = self.drawing_manager
        
        self.biome_manager.initialize()
        self.load_game_data()

    def _setup_players(self, players):
        colors = [
            wx.Colour(255, 0, 0), wx.Colour(0, 255, 0), 
            wx.Colour(0, 0, 255), wx.Colour(255, 255, 0),
            wx.Colour(255, 0, 255), wx.Colour(0, 255, 255)
        ]
        
        for i, player in enumerate(players):
            self.players.append(PlayerToken(
                position=player.position,
                color=colors[i],
                name=player.name
            ))

    def _setup_ui(self):
        self.hex_manager.calculate_hex_size(self.GetSize().width, self.GetSize().height)
        self.panel = wx.Panel(self)
        
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_panel = wx.Panel(self.panel)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.canvas = wx.Panel(left_panel)
        self.canvas.SetBackgroundColour(wx.WHITE)
        
        left_sizer.Add(self.canvas, 1, wx.EXPAND)
        left_panel.SetSizer(left_sizer)
        
        self.movement_phase = MovementPhase(self.panel, self.players[0].name)
        self.movement_phase.set_player(self.players[0])
        
        main_sizer.Add(left_panel, 2, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(self.movement_phase, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(main_sizer)

    def _bind_events(self):
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_hex_click)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(EVT_TERRAIN_HOVER, self.on_terrain_hover)

    def on_paint(self, event):
        dc = wx.PaintDC(self.canvas)
        self.drawing_manager.draw_grid(dc)
        self.draw_players(dc)

    def draw_players(self, dc):
        for player in self.players:
            center = self.hex_manager.get_hex_center(*player.position)
            self.draw_token(dc, center, player.color)

    def draw_token(self, dc, center, color):
        x, y = center
        token_size = self.hex_manager.hex_size * 0.4
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(wx.BLACK, 2))
        dc.DrawCircle(int(x), int(y), int(token_size))

    def on_resize(self, event):
        width, height = self.GetSize()
        self.hex_manager.calculate_hex_size(width, height)
        self.canvas.Refresh()
        event.Skip()

    def on_hex_click(self, event):
        x, y = event.GetPosition()
        clicked_hex = self.hex_manager.get_clicked_hex(x, y)
        
        if clicked_hex in self.valid_moves:
            self.selected_hex = clicked_hex
            self.players[0].position = clicked_hex
            # Mettre à jour uniquement l'hexagone sélectionné
            self.hex_manager.set_highlighted_hexes({clicked_hex})
            # Verrouiller le dé utilisé
            self.movement_phase.lock_selected_face()
            self.canvas.Refresh()
            
    def on_terrain_hover(self, event):
        if event.is_selected:
            player = self.players[0]
            self.valid_moves = set()
            adjacent_hexes = self.hex_manager.get_neighbors(*player.position)
            
            for hex_pos in adjacent_hexes:
                # Permettre l'entrée dans une ville avec n'importe quelle face
                if self.biome_manager.get_biome(hex_pos) == "Ville":
                    self.valid_moves.add(hex_pos)
                # Comportement normal pour les autres terrains
                elif self.biome_manager.get_biome(hex_pos) == event.terrain:
                    self.valid_moves.add(hex_pos)
                    
            self.hex_manager.set_highlighted_hexes(self.valid_moves)
        else:
            # Garder le comportement de survol existant
            if event.terrain:
                player = self.players[0]
                highlighted = set()
                adjacent_hexes = self.hex_manager.get_neighbors(*player.position)
                for hex_pos in adjacent_hexes:
                    if self.biome_manager.get_biome(hex_pos) == event.terrain:
                        highlighted.add(hex_pos)
                self.hex_manager.set_highlighted_hexes(highlighted)
            else:
                self.hex_manager.set_highlighted_hexes(set())
    
        self.canvas.Refresh()

    def load_game_data(self):
        try:
            # BiomeManager a déjà sa propre méthode de chargement
            self.biome_manager.load_biomes()
        except FileNotFoundError:
            print("Fichier biomes.json non trouvé")
        except json.JSONDecodeError:
            print("Erreur de format dans biomes.json")

    def get_player_position(self):
        return self.players[0].position
