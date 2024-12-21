import math
import wx

class HexManager:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.hex_size = 0
        self.biome_manager = None  # Will need to be set after initialization
        
    def set_biome_manager(self, biome_manager):
        self.biome_manager = biome_manager
        
    def calculate_hex_size(self, window_width, window_height):
        self.canvas_width = window_width
        self.canvas_height = window_height
        available_width = window_width * 0.6
        max_width = (available_width - 50) / (self.grid_width * 1.5)
        max_height = (window_height - 50) / (self.grid_height * math.sqrt(3))
        self.hex_size = min(max_width, max_height)

    def get_hex_center(self, col, row):
        width = self.hex_size * 2
        height = self.hex_size * math.sqrt(3)
    
        # Calculate total grid dimensions
        total_width = width * 0.75 * self.grid_width + width * 0.25
        total_height = height * self.grid_height + (height * 0.5 if self.grid_width % 2 else 0)
    
        # Calculate offsets to center within the 60% width area
        available_width = self.canvas_width * 0.6
        x_offset = (available_width - total_width) / 2
        y_offset = (self.canvas_height - total_height) / 2
    
        # Calculate hex position with offset
        x = width * 0.75 * col + x_offset
        y = height * row + y_offset
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
        
    def point_in_hex(self, px, py, center):
        cx, cy = center
        dx = abs(px - cx)
        dy = abs(py - cy)
        hex_width = self.hex_size * math.sqrt(3) / 2
        hex_height = self.hex_size
        if dx > hex_width or dy > hex_height:
            return False
        return (hex_width * hex_height - hex_width * dy - hex_height * dx / 2) >= 0
        
    def get_clicked_hex(self, mouse_x, mouse_y):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                center = self.get_hex_center(col, row)
                if self.point_in_hex(mouse_x, mouse_y, center):
                    return (col, row)
        return None

    def get_neighbors(self, col, row):
        neighbors = []
        odd_col = col % 2
        directions = [
            (-1, -1 + odd_col), (0, -1),  (1, -1 + odd_col),
            (-1, 0 + odd_col),            (1, 0 + odd_col),
            (-1, 1 + odd_col), (0, 1),   (1, 1 + odd_col)
        ]
        
        for dx, dy in directions:
            new_col, new_row = col + dx, row + dy
            if 0 <= new_col < self.grid_width and 0 <= new_row < self.grid_height:
                neighbors.append((new_col, new_row))
        return neighbors

    def draw_hex(self, dc, points, biome_data, col, row):
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        dc.SetBrush(wx.Brush(biome_data["primary"]))
        dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])

        current_biome = self.biome_manager.get_biome((col, row))
        if biome_data["pattern"] and current_biome not in ["Marais", "Ville"]:
            if biome_data["pattern"]["type"] == "line":
                self.draw_connected_lines(dc, points, col, row, biome_data["pattern"]["color"])

    def draw_connected_lines(self, dc, points, col, row, color):
        current_biome = self.biome_manager.get_biome((col, row))
        center = self.get_hex_center(col, row)
    
        if current_biome == "Riviere":
            connections = self.find_river_connections(col, row)
            for next_col, next_row in connections:
                next_biome = self.biome_manager.get_biome((next_col, next_row))
                next_center = self.get_hex_center(next_col, next_row)
                self._draw_connection_line(dc, center, next_center, next_biome, color)
    
        elif current_biome == "Route":
            for adj_col, adj_row in self.get_neighbors(col, row):
                adj_biome = self.biome_manager.get_biome((adj_col, adj_row))
                if self.biome_manager.should_connect(current_biome, adj_biome):
                    adj_center = self.get_hex_center(adj_col, adj_row)
                    self._draw_connection_line(dc, center, adj_center, adj_biome, color)

    def _draw_connection_line(self, dc, start_center, end_center, end_biome, color):
        if end_biome in ["Marais", "Ville"]:
            mid_x = (start_center[0] + end_center[0]) / 2
            mid_y = (start_center[1] + end_center[1]) / 2
            dc.SetPen(wx.Pen(color, 2))
            dc.DrawLine(int(start_center[0]), int(start_center[1]), int(mid_x), int(mid_y))
        else:
            dc.SetPen(wx.Pen(color, 2))
            dc.DrawLine(int(start_center[0]), int(start_center[1]), 
                    int(end_center[0]), int(end_center[1]))

    def find_river_connections(self, col, row):
        all_neighbors = []
    
        # Group neighbors by type
        for adj_col, adj_row in self.get_neighbors(col, row):
            adj_biome = self.biome_manager.get_biome((adj_col, adj_row))
            if adj_biome in ["Marais", "Riviere", "Ville"]:
                # Store tuple of (col, row, biome_type)
                all_neighbors.append((adj_col, adj_row, adj_biome))
    
        # If we have more than 2 water neighbors, select the best connections
        if len(all_neighbors) > 2:
            # Prioritize creating continuous flow
            # First, look for opposite pairs to create straight flows
            for i, (col1, row1, biome1) in enumerate(all_neighbors):
                for col2, row2, biome2 in all_neighbors[i+1:]:
                    # Check if points are roughly opposite to each other
                    if abs(col1 - col2) == 2 or abs(row1 - row2) == 2:
                        return [(col1, row1), (col2, row2)]
    
        # If no optimal pairs found, return up to 2 neighbors
        return [(n[0], n[1]) for n in all_neighbors[:2]]
