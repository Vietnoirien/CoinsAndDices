class RiverPath:
    def __init__(self, hex_manager=None):
        self.river_tiles = []
        self.route_tiles = []
        self.hex_manager = hex_manager      
          
    def get_tile(self, position: tuple) -> dict:
        """Get river tile data for a specific position"""
        for tile in self.river_tiles:
            if tile['position'] == position:
                return tile
        return None
        
    def add_river_tile(self, pos, connections):
        hex_manager = self.hex_manager
        valid_neighbors = hex_manager.get_neighbors(*pos)
        
        # Prioritize maintaining existing river connections
        existing_river_connections = []
        for neighbor in valid_neighbors:
            neighbor_tile = self.get_tile(neighbor)
            if neighbor_tile and pos in neighbor_tile['connections']:
                existing_river_connections.append(neighbor)
        
        # Add new connections up to limit
        remaining_slots = 2 - len(existing_river_connections)
        new_connections = [c for c in connections if c not in existing_river_connections][:remaining_slots]
        
        all_connections = existing_river_connections + new_connections
        
        new_tile = {
            'position': pos,
            'connections': all_connections
        }
        
        self.river_tiles = [tile for tile in self.river_tiles if tile['position'] != pos]
        self.river_tiles.append(new_tile)
        
        # Ensure bidirectional connections
        for conn_pos in all_connections:
            self._ensure_bidirectional_connection(pos, conn_pos)
        
        self._sort_river_path()
        self.validate_river_network()
        
    def _ensure_bidirectional_connection(self, pos1, pos2):
        """Ensures both tiles reference each other in their connections"""
        tile1 = self.get_tile(pos1)
        tile2 = self.get_tile(pos2)
    
        if not tile2:
            tile2 = {
                'position': pos2,
                'connections': [pos1]
            }
            self.river_tiles.append(tile2)
        elif pos1 not in tile2['connections'] and len(tile2['connections']) < 2:
            tile2['connections'].append(pos1)
        
        if pos2 not in tile1['connections'] and len(tile1['connections']) < 2:
            tile1['connections'].append(pos2)

    def validate_river_network(self):
        """Enhanced validation to ensure proper river flow"""
        if not self.river_tiles:
            return
        
        # Find all endpoints (tiles with 1 connection)
        endpoints = [tile for tile in self.river_tiles if len(tile['connections']) == 1]
    
        if not endpoints:
            # If no endpoints, find a tile to start from
            start_tile = self.river_tiles[0]
        else:
            start_tile = endpoints[0]
    
        # Trace the network and validate connections
        visited = set()
        to_visit = [(start_tile, None)]  # (tile, previous_tile)
    
        while to_visit:
            current_tile, previous = to_visit.pop(0)
            current_pos = current_tile['position']
        
            if str(current_pos) in visited:
                continue
            
            visited.add(str(current_pos))
        
            # Check each connection
            for conn_pos in current_tile['connections']:
                next_tile = self.get_tile(conn_pos)
                if next_tile and str(conn_pos) not in visited:
                    to_visit.append((next_tile, current_tile))
                
                    # Validate bidirectional connection
                    if current_pos not in next_tile['connections']:
                        next_tile['connections'].append(current_pos)
                        if len(next_tile['connections']) > 2:
                            next_tile['connections'] = next_tile['connections'][:2]
                            
    def remove_tile(self, position: tuple) -> None:
        # Remove from river tiles and update their connections
        self.river_tiles = [tile for tile in self.river_tiles 
                       if tile['position'] != position]
        for tile in self.river_tiles:
            if position in tile['connections']:
                tile['connections'].remove(position)
    
        # Remove from route tiles and update their connections
        self.route_tiles = [tile for tile in self.route_tiles 
                       if tile['position'] != position]
        for tile in self.route_tiles:
            if position in tile['connections']:
                tile['connections'].remove(position)
        
    def get_route_tile(self, position: tuple) -> dict:
        """Get route tile data for a specific position"""
        for tile in self.route_tiles:
            if tile['position'] == position:
                return tile
        return None

    def add_route_tile(self, pos, connections):
        hex_manager = self.hex_manager
        valid_neighbors = hex_manager.get_neighbors(*pos)
        
        # Prioritize maintaining existing route connections
        existing_route_connections = []
        for neighbor in valid_neighbors:
            neighbor_tile = self.get_route_tile(neighbor)
            if neighbor_tile and pos in neighbor_tile['connections']:
                existing_route_connections.append(neighbor)
        
        # Add new connections up to limit
        remaining_slots = 2 - len(existing_route_connections)
        new_connections = [c for c in connections if c not in existing_route_connections][:remaining_slots]
        
        all_connections = existing_route_connections + new_connections
        
        new_tile = {
            'position': pos,
            'connections': all_connections
        }
        
        self.route_tiles = [tile for tile in self.route_tiles if tile['position'] != pos]
        self.route_tiles.append(new_tile)
        
        # Ensure bidirectional connections for routes
        for conn_pos in all_connections:
            self._ensure_bidirectional_route_connection(pos, conn_pos)
        
        self._sort_route_path()
        
    def _sort_river_path(self):
        """Sort river tiles to maintain continuous path order"""
        if not self.river_tiles:
            return
            
        sorted_tiles = []
        remaining_tiles = self.river_tiles.copy()
        
        # Find endpoints (tiles with 1 connection) to start path
        start_tiles = [tile for tile in remaining_tiles 
                      if len(tile['connections']) == 1]
        
        # If no endpoints found, use any tile as starting point
        if not start_tiles and remaining_tiles:
            start_tiles = [remaining_tiles[0]]
            
        # Build continuous path
        while start_tiles and remaining_tiles:
            current = start_tiles.pop(0)
            if current in remaining_tiles:
                sorted_tiles.append(current)
                remaining_tiles.remove(current)
                
                # Find next connected tile
                for conn_pos in current['connections']:
                    next_tiles = [tile for tile in remaining_tiles 
                                if tile['position'] == conn_pos]
                    if next_tiles:
                        start_tiles.append(next_tiles[0])
        
        # Add any remaining disconnected tiles
        sorted_tiles.extend(remaining_tiles)
        self.river_tiles = sorted_tiles
        
    def _sort_route_path(self):
        """Sort route tiles for consistent rendering"""
        if self.route_tiles:
            self.route_tiles.sort(key=lambda x: (x['position'][0], x['position'][1]))
            
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
            if not current_tile:
                break
                
            segment.append(current_tile)
            # Find next unvisited connection
            next_pos = None
            for conn_pos in current_tile['connections']:
                conn_key = self._pos_to_key(conn_pos)
                if conn_key not in visited:
                    next_pos = conn_pos
                    break
            current_pos = next_pos
                
        return segment
        
    def _pos_to_key(self, position):
        """Convert position tuple to string key"""
        return str(position)

    def _ensure_bidirectional_route_connection(self, pos1, pos2):
        """Ensures both route tiles reference each other in their connections"""
        tile1 = self.get_route_tile(pos1)
        tile2 = self.get_route_tile(pos2)

        if not tile2:
            tile2 = {
                'position': pos2,
                'connections': [pos1]
            }
            self.route_tiles.append(tile2)
        elif pos1 not in tile2['connections'] and len(tile2['connections']) < 2:
            tile2['connections'].append(pos1)
        
        if pos2 not in tile1['connections'] and len(tile1['connections']) < 2:
            tile1['connections'].append(pos2)

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
            # Find next unvisited connection
            next_pos = None
            for conn_pos in current_tile['connections']:
                conn_key = self._pos_to_key(conn_pos)
                if conn_key not in visited:
                    next_pos = conn_pos
                    break
            current_pos = next_pos
                
        return segment
