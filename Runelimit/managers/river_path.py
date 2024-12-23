class RiverPath:
    def __init__(self, hex_manager):
        self.hex_manager = hex_manager
        self.drawing_manager = None
        self.river_tiles = []
        self.route_tiles = []
          
    def get_tile(self, position):
        """Get river tile data for a specific position"""
        for tile in self.river_tiles:
            if tile['position'] == list(position):  # Convertir le tuple en liste pour la comparaison
                return tile
        return None
        
    def get_route_tile(self, position):
        """Get route tile data for a specific position"""
        for tile in self.route_tiles:
            if tile['position'] == list(position):  # Convertir le tuple en liste pour la comparaison
                return tile
        return None
    
    def get_connected_segments(self) -> list:
        """Get list of connected river segments for rendering"""
        segments = []
        visited = set()
        
        for tile in self.river_tiles:
            pos_key = self._pos_to_key(tile['position'])
            if pos_key not in visited:
                segment = self._trace_segment(tile['position'], visited)
                if segment:
                    segments.append(segment)
        return segments
    
    def _trace_segment(self, start_pos: tuple, visited: set) -> list:
        """Trace a continuous segment starting from given position"""
        segment = []
        current_pos = start_pos
        
        while current_pos:
            pos_key = self._pos_to_key(current_pos)
            if pos_key in visited:
                break
                
            visited.add(pos_key)
            current_tile = self.get_tile(current_pos)
            
            current_biome = self.hex_manager.biome_manager.get_biome(current_pos)
            if current_biome in ["Ville", "Marais"]:
                segment.append(current_tile)
                break
                
            if not current_tile:
                break
                
            segment.append(current_tile)
            next_pos = None
            for conn_pos in current_tile['connections']:
                conn_key = self._pos_to_key(conn_pos)
                if conn_key not in visited:
                    next_pos = conn_pos
                    break
            current_pos = next_pos
                
        return segment

    def get_connected_route_segments(self) -> list:
        """Get list of connected route segments for rendering"""
        segments = []
        visited = set()
        
        for tile in self.route_tiles:
            pos_key = self._pos_to_key(tile['position'])
            if pos_key not in visited:
                segment = self._trace_route_segment(tile['position'], visited)
                if segment:
                    segments.append(segment)
        return segments

    def _trace_route_segment(self, start_pos: tuple, visited: set) -> list:
        """Trace a continuous route segment starting from given position"""
        segment = []
        current_pos = start_pos
        
        while current_pos:
            pos_key = self._pos_to_key(current_pos)
            if pos_key in visited:
                break
                
            visited.add(pos_key)
            current_tile = self.get_route_tile(current_pos)
            if not current_tile:
                break
                
            segment.append(current_tile)
            next_pos = None
            for conn_pos in current_tile['connections']:
                conn_key = self._pos_to_key(conn_pos)
                if conn_key not in visited:
                    next_pos = conn_pos
                    break
            current_pos = next_pos
                
        return segment

    def load_paths(self, path_data):
        """Load path data from configuration"""
        self.river_tiles = path_data.get("rivers", [])
        self.route_tiles = path_data.get("routes", [])

    def _pos_to_key(self, position):
        """Convert position tuple to string key"""
        return str(position)

    def set_drawing_manager(self, drawing_manager):
        self.drawing_manager = drawing_manager