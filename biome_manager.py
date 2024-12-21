import json
import os
import wx

class BiomeManager:
    def __init__(self, hex_manager):
        self.hex_manager = hex_manager
        self.hex_biomes = {}
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
        self.load_biomes()
        
    def set_biome(self, hex_pos, biome):
        col, row = hex_pos
        if not (0 <= col < self.hex_manager.grid_width and 0 <= row < self.hex_manager.grid_height):
            return False
        if biome in self.biomes:
            self.hex_biomes[str(hex_pos)] = biome
            self.save_biomes()
            return True
        return False
    
    def get_biome(self, hex_pos):
        return self.hex_biomes.get(str(hex_pos), "Plaine")

    def get_biome_data(self, biome_name):
        return self.biomes.get(biome_name)

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

    def should_connect(self, biome1, biome2):
        if not biome1 or not biome2:
            return False
            
        if biome1 == "Riviere" and biome2 in ["Riviere", "Ville", "Marais"]:
            return True
        
        if biome1 == "Route" and biome2 in ["Route", "Ville"]:
            return True
        
        return False

    def get_connected_biomes(self, hex_pos):
        col, row = hex_pos
        neighbors = self.hex_manager.get_neighbors(col, row)
        current_biome = self.get_biome(hex_pos)
        
        connected = []
        for neighbor in neighbors:
            neighbor_biome = self.get_biome(neighbor)
            if self.should_connect(current_biome, neighbor_biome):
                connected.append(neighbor)
        return connected
