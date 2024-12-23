import json
import os
import wx
from .river_path import RiverPath

class BiomeManager:
    def __init__(self, hex_manager):
        self.hex_manager = hex_manager
        self.hex_biomes = {}
        self.biomes = {
            "Marais": {"primary": wx.Colour(120, 200, 110), "pattern": None},
            "Plaine": {"primary": wx.Colour(120, 200, 110), "pattern": None},
            "Riviere": {
                "primary": wx.Colour(120, 200, 110),
                "pattern": {"color": wx.Colour(0, 0, 255), "type": "line"}
            },
            "Colline": {"primary": wx.Colour(165, 113, 78), "pattern": None},
            "Route": {
                "primary": wx.Colour(120, 200, 110),
                "pattern": {"color": wx.Colour(139, 69, 19), "type": "line"}
            },
            "Montagne": {"primary": wx.Colour(101, 67, 33), "pattern": None},
            "Ville": {"primary": wx.Colour(128, 128, 128), "pattern": None},
            "Foret": {"primary": wx.Colour(0, 100, 0), "pattern": None}
        }
        self.river_path = RiverPath(self.hex_manager)
        self.drawing_manager = None

    def set_drawing_manager(self, drawing_manager):
        self.drawing_manager = drawing_manager
        self.river_path.set_drawing_manager(drawing_manager)

    def get_biome(self, hex_pos):
        pos_str = f"({hex_pos[0]}, {hex_pos[1]})"
        return self.hex_biomes.get(pos_str, "Plaine")

    def get_biome_data(self, biome_name):
        return self.biomes.get(biome_name)

    def load_biomes(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(project_root, 'biomes.json')
    
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                if 'biomes' in data:
                    self.hex_biomes = data['biomes']
                if 'river_paths' in data:
                    self.river_path.load_paths(data['river_paths'])

    def initialize(self):
        self.drawing_manager = self.hex_manager.drawing_manager
        self.river_path.set_drawing_manager(self.drawing_manager)
        self.load_biomes()

    def get_connected_biomes(self, hex_pos):
        if self.get_biome(hex_pos) == "Riviere":
            river_tile = self.river_path.get_tile(hex_pos)
            return river_tile['connections'] if river_tile else []
        
        col, row = hex_pos
        neighbors = self.hex_manager.get_neighbors(col, row)
        current_biome = self.get_biome(hex_pos)
        
        connected = []
        for neighbor in neighbors:
            neighbor_biome = self.get_biome(neighbor)
            if self.should_connect(current_biome, neighbor_biome):
                connected.append(neighbor)
        return connected

    def should_connect(self, biome1, biome2):
        if not biome1 or not biome2:
            return False
            
        if biome1 == "Riviere" and biome2 in ["Riviere", "Ville", "Marais"]:
            return True
        if biome1 == "Marais" and biome2 == "Riviere":
            return True
        if biome1 == "Route" and biome2 in ["Route", "Ville"]:
            return True
        
        return False

    def get_city_connections(self, hex_pos):
        river_connections = []
        route_connections = []
        
        col, row = hex_pos
        neighbors = self.hex_manager.get_neighbors(col, row)
        
        for neighbor in neighbors:
            neighbor_biome = self.get_biome(neighbor)
            if neighbor_biome == "Riviere":
                river_connections.append(neighbor)
            elif neighbor_biome == "Route":
                route_connections.append(neighbor)
                
        return {
            'river': river_connections[:2],
            'route': route_connections[:2]
        }
