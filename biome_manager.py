import json
import os
import wx
import logging
from datetime import datetime

class BiomeManager:
    def __init__(self, hex_manager):
        self.setup_logger()
        self.hex_manager = hex_manager
        self.hex_biomes = {}
        self.connection_counts = {}
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
        
    def setup_logger(self):
        os.makedirs('Runelimit/logs', exist_ok=True)
        self.logger = logging.getLogger('BiomeManager')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('Runelimit/logs/biome.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

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

    def get_connection_count(self, hex_pos):
        return self.connection_counts.get(str(hex_pos), 0)

    def update_connection_count(self, hex_pos):
        self.logger.info(f"Updating connections for hex {hex_pos}")
        pos_str = str(hex_pos)
        
        connected_positions = self.get_connected_biomes(hex_pos)
        self.logger.debug(f"Connected positions: {connected_positions}")
        
        # Garantir au moins une connexion
        self.connection_counts[pos_str] = max(1, len(connected_positions))
        
        for connected_pos in connected_positions:
            connected_str = str(connected_pos)
            if connected_str not in self.connection_counts:
                self.connection_counts[connected_str] = 1
            else:
                self.connection_counts[connected_str] = min(2, self.connection_counts[connected_str] + 1)
        
        self.save_biomes()

    def save_biomes(self):
        os.makedirs('Runelimit', exist_ok=True)
        data = {
            'biomes': self.hex_biomes,
            'connections': self.connection_counts
        }
        self.logger.debug(f"Saving biome state: {json.dumps(data, indent=2)}")
        with open('Runelimit/biomes.json', 'w') as f:
            json.dump(data, f)

    def load_biomes(self):
        try:
            with open('Runelimit/biomes.json', 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.hex_biomes = data.get('biomes', {})
                    self.verify_connection_counts()
                else:
                    self.hex_biomes = {}
                    self.connection_counts = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.hex_biomes = {}
            self.connection_counts = {}
            self.save_biomes()

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
                if current_biome == "Riviere" and self.get_connection_count(neighbor) >= 2:
                    continue
                connected.append(neighbor)
        return connected

    def create_context_menu(self, parent):
        menu = wx.Menu()
        for biome in self.biomes.keys():
            item = menu.Append(-1, biome)
            parent.Bind(wx.EVT_MENU, lambda evt, b=biome: self.set_biome_with_refresh(evt, b), item)
        return menu

    def set_biome_with_refresh(self, event, biome_name):
        if self.hex_manager.last_clicked_hex:
            current_pos = self.hex_manager.last_clicked_hex
            old_biome = self.get_biome(current_pos)
            
            self.clear_connections(current_pos)
            self.set_biome(current_pos, biome_name)
            
            # Forcer la mise à jour des connexions pour tous les voisins
            if biome_name in ["Riviere", "Route"]:
                # Obtenir et connecter les voisins valides
                valid_connections = self.hex_manager.find_river_connections(*current_pos)
                self.establish_connections(current_pos, valid_connections)
                
                # Mettre à jour les connexions des voisins
                neighbors = self.hex_manager.get_neighbors(*current_pos)
                for neighbor in neighbors:
                    if self.get_biome(neighbor) in ["Riviere", "Route"]:
                        neighbor_connections = self.hex_manager.find_river_connections(*neighbor)
                        self.establish_connections(neighbor, neighbor_connections)
            
            self.hex_manager.canvas.Refresh()

    def clear_connections(self, hex_pos):
        connected = self.get_connected_biomes(hex_pos)
        self.connection_counts[str(hex_pos)] = 0
        for connected_pos in connected:
            conn_str = str(connected_pos)
            if conn_str in self.connection_counts:
                self.connection_counts[conn_str] = max(0, self.connection_counts[conn_str] - 1)

    def establish_connections(self, source_pos, target_positions):
        source_str = str(source_pos)
        # Initialiser la connexion source à 1 pour chaque connexion
        self.connection_counts[source_str] = 1
        
        for target_pos in target_positions:
            target_str = str(target_pos)
            if target_str not in self.connection_counts:
                self.connection_counts[target_str] = 1
            else:
                self.connection_counts[target_str] = min(2, self.connection_counts[target_str] + 1)

    def verify_connection_counts(self):
        self.connection_counts = {}
        for hex_pos_str, biome in self.hex_biomes.items():
            if biome == "Riviere":
                hex_pos = eval(hex_pos_str)
                self.update_connection_count(hex_pos)
        self.save_biomes()

    def set_connection_count(self, hex_pos, count):
        """
        Définit le nombre de connexions pour une position donnée
        Args:
            hex_pos: Tuple (col, row) représentant la position
            count: Nombre de connexions à définir
        """
        pos_str = str(hex_pos)
        self.connection_counts[pos_str] = count
        self.logger.debug(f"Set connection count for {pos_str} to {count}")
        self.save_biomes()
