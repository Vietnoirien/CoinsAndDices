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
        # Validate connections against hex grid topology
        hex_manager = self.hex_manager
        valid_neighbors = hex_manager.get_neighbors(*pos)
        
        # Filter out neighbors that already have 2 connections
        available_connections = []
        for conn in connections:
            if conn in valid_neighbors:
                existing_tile = self.get_tile(conn)
                if not existing_tile or len(existing_tile['connections']) < 2:
                    available_connections.append(conn)
        
        # Create new tile with validated connections
        new_tile = {
            'position': pos,
            'connections': available_connections[:2]  # Max 2 connections
        }
        
        # Remove existing tile if present
        self.river_tiles = [tile for tile in self.river_tiles 
                           if tile['position'] != pos]
        
        # Add new tile and ensure bidirectional connections
        self.river_tiles.append(new_tile)
        
        # Update neighbor connections
        for conn_pos in available_connections:
            found = False
            for tile in self.river_tiles:
                if tile['position'] == conn_pos:
                    if pos not in tile['connections'] and len(tile['connections']) < 2:
                        tile['connections'].append(pos)
                    found = True
                    break
            if not found:
                self.river_tiles.append({
                    'position': conn_pos,
                    'connections': [pos]
                })
        
        self._sort_river_path()
        self.validate_river_network()
        
    def validate_river_network(self):
        """Ensures river network follows valid flow patterns"""
        # Find all endpoints (tiles with 1 connection)
        endpoints = [tile for tile in self.river_tiles 
                    if len(tile['connections']) == 1]
        
        if not endpoints:
            return
            
        # Start from first endpoint
        visited = set()
        current = endpoints[0]
        
        while current:
            pos_key = str(current['position'])
            if pos_key in visited:
                # Found a cycle, break it
                current['connections'] = current['connections'][:1]
                break
                
            visited.add(pos_key)
            
            # Find next unvisited connection
            next_tile = None
            for conn_pos in current['connections']:
                next_key = str(conn_pos)
                if next_key not in visited:
                    next_tile = self.get_tile(conn_pos)
                    break
                    
            current = next_tile

    def remove_tile(self, position: tuple) -> None:
        """Remove a tile and update affected connections"""
        # Remove from river tiles
        self.river_tiles = [tile for tile in self.river_tiles 
                           if tile['position'] != position]
        
        # Update connections that referenced this tile
        for tile in self.river_tiles:
            if position in tile['connections']:
                tile['connections'].remove(position)
        
        # Remove from route tiles
        self.route_tiles = [tile for tile in self.route_tiles 
                           if tile['position'] != position]
        
    def add_route_tile(self, pos, connections):
        """Add a route tile with its connections"""
        self.route_tiles.append({
            'position': pos,
            'connections': connections
        })
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
