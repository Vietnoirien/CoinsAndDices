import json
import os
import wx
import logging
from datetime import datetime
from river_path import RiverPath

class BiomeManager:
    def __init__(self, hex_manager):
        self.setup_logger()
        self.hex_manager = hex_manager
        self.drawing_manager = hex_manager.drawing_manager
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
            old_biome = self.get_biome(hex_pos)
            self.hex_biomes[str(hex_pos)] = biome
            
            # Get all neighbors before making changes
            neighbors = self.hex_manager.get_neighbors(col, row)
            
            # Remove current tile from river path
            self.river_path.remove_tile(hex_pos)
            
            # If new tile is river, add it with connections
            if biome == "Riviere":
                connections = self.hex_manager.find_river_connections(col, row)
                self.river_path.add_river_tile(hex_pos, connections)
            
            # Refresh all neighboring river tiles
            for neighbor in neighbors:
                if self.get_biome(neighbor) == "Riviere":
                    n_col, n_row = neighbor
                    neighbor_connections = self.hex_manager.find_river_connections(n_col, n_row)
                    self.river_path.add_river_tile(neighbor, neighbor_connections)
            
            self.save_biomes()
            return True
        return False
    
    def get_biome(self, hex_pos):
        return self.hex_biomes.get(str(hex_pos), "Plaine")

    def get_biome_data(self, biome_name):
        return self.biomes.get(biome_name)

    def save_biomes(self):
        os.makedirs('Runelimit', exist_ok=True)
        data = {
            'biomes': self.hex_biomes,
            'river_paths': {
                'rivers': self.river_path.river_tiles,
                'routes': self.river_path.route_tiles
            }
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
                    
                    river_data = data.get('river_paths', {})
                    for river_tile in river_data.get('rivers', []):
                        self.river_path.add_river_tile(
                            tuple(river_tile['position']), 
                            [tuple(conn) for conn in river_tile['connections']]
                        )
                    for route_tile in river_data.get('routes', []):
                        self.river_path.add_route_tile(
                            tuple(route_tile['position']),
                            [tuple(conn) for conn in route_tile['connections']]
                        )
                else:
                    self._initialize_empty_state()
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_empty_state()
            
    def _initialize_empty_state(self):
        self.hex_biomes = {}
        self.river_path = RiverPath(self.hex_manager)  # <-- Pass hex_manager here too
        self.save_biomes()

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
    
    def create_context_menu(self, parent):
        menu = wx.Menu()
        for biome in self.biomes.keys():
            item = menu.Append(-1, biome)
            parent.Bind(wx.EVT_MENU, lambda evt, b=biome: self.set_biome_with_refresh(evt, b), item)
        return menu

    def set_biome_with_refresh(self, event, biome_name):
        if self.hex_manager.last_clicked_hex:
            current_pos = self.hex_manager.last_clicked_hex
            
            self.river_path.remove_tile(current_pos)
            self.set_biome(current_pos, biome_name)
            
            if biome_name == "Riviere":
                valid_connections = self.hex_manager.find_river_connections(*current_pos)
                self.river_path.add_river_tile(current_pos, valid_connections)
            elif biome_name == "Route":
                valid_connections = self.hex_manager.find_route_connections(*current_pos)
                self.river_path.add_route_tile(current_pos, valid_connections)
                
            self._update_neighbor_connections(current_pos)
            self.drawing_manager.invalidate_buffer()
            self.hex_manager.canvas.Refresh()
    
    def _update_neighbor_connections(self, current_pos):
        neighbors = self.hex_manager.get_neighbors(*current_pos)
        for neighbor in neighbors:
            neighbor_biome = self.get_biome(neighbor)
            if neighbor_biome == "Riviere":
                neighbor_connections = self.hex_manager.find_river_connections(*neighbor)
                self.river_path.add_river_tile(neighbor, neighbor_connections)
            elif neighbor_biome == "Route":
                neighbor_connections = self.hex_manager.find_route_connections(*neighbor)
                self.river_path.add_route_tile(neighbor, neighbor_connections)

    def validate_path_connections(self):
        """Validate both river and route connections"""
        self.river_path.validate_river_network()
        self.validate_route_network()

    def validate_route_network(self):
        """Validate route connections and ensure proper network flow"""
        for route_tile in self.river_path.route_tiles:
            pos = route_tile['position']
            connections = route_tile['connections']
            
            # Validate each connection
            valid_connections = []
            for conn_pos in connections:
                conn_biome = self.get_biome(conn_pos)
                if conn_biome in ["Route", "Ville"]:
                    valid_connections.append(conn_pos)
            
            # Update connections if needed
            if len(valid_connections) != len(connections):
                route_tile['connections'] = valid_connections[:2]  # Maximum 2 connections

    def get_city_connections(self, hex_pos):
        """Separate handling for city connections"""
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
            'river': river_connections[:2],  # Limit to 2 connections
            'route': route_connections[:2]
        }

