import math
import wx
from typing import List, Tuple, Optional, Dict

class HexManager:
    # Class-level constants
    HEX_ANGLE_DEG = 60
    HEX_ANGLE_RAD = math.pi / 180 * HEX_ANGLE_DEG
    CANVAS_WIDTH_RATIO = 0.6  # 60% of window width
    GRID_MARGIN = 50
    LINE_PATTERN_WIDTH = 2

    def __init__(self, grid_width: int, grid_height: int):
        if grid_width <= 0 or grid_height <= 0:
            raise ValueError("Grid dimensions must be positive")
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.hex_size = 0
        self.biome_manager = None
        self.canvas = None
        self.last_clicked_hex = None
        self.canvas_width = 0
        self.canvas_height = 0
        
    def set_biome_manager(self, biome_manager) -> None:
        self.biome_manager = biome_manager
        
    def calculate_hex_size(self, window_width: int, window_height: int) -> None:
        self.canvas_width = window_width
        self.canvas_height = window_height
        available_width = window_width * self.CANVAS_WIDTH_RATIO
        max_width = (available_width - self.GRID_MARGIN) / (self.grid_width * 1.5)
        max_height = (window_height - self.GRID_MARGIN) / (self.grid_height * math.sqrt(3))
        self.hex_size = min(max_width, max_height)

    def get_hex_center(self, col: int, row: int) -> Tuple[float, float]:
        margin = 40
        horiz_spacing = self.hex_size * 1.5
        vert_spacing = self.hex_size * 1.732
        
        x = col * horiz_spacing + margin
        y = row * vert_spacing + margin
        
        if col % 2:
            y += vert_spacing / 2
            
        return (x + self.hex_size * 2, y + self.hex_size)
    
    def get_hex_points(self, x: float, y: float) -> List[Tuple[float, float]]:
        points = []
        for i in range(6):
            angle = (i * 60) * math.pi / 180
            px = x + self.hex_size * math.cos(angle)
            py = y + self.hex_size * math.sin(angle)
            points.append((px, py))
        return points
        
    def point_in_hex(self, px: float, py: float, center: Tuple[float, float]) -> bool:
        cx, cy = center
        dx = abs(px - cx)
        dy = abs(py - cy)
        hex_width = self.hex_size * math.sqrt(3) / 2
        hex_height = self.hex_size
        if dx > hex_width or dy > hex_height:
            return False
        return (hex_width * hex_height - hex_width * dy - hex_height * dx / 2) >= 0
        
    def get_clicked_hex(self, mouse_x: float, mouse_y: float) -> Optional[Tuple[int, int]]:
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                center = self.get_hex_center(col, row)
                if self.point_in_hex(mouse_x, mouse_y, center):
                    return (col, row)
        return None

    def get_neighbors(self, col: int, row: int) -> List[Tuple[int, int]]:
        neighbors = []
        # Different neighbor patterns for even/odd columns
        if col % 2 == 0:  # Even columns
            offsets = [
                (-1, 0),   # Left
                (1, 0),    # Right
                (0, -1),   # Top
                (0, 1),    # Bottom
                (-1, -1),  # Top-left
                (1, -1)    # Top-right
            ]
        else:  # Odd columns
            offsets = [
                (-1, 0),   # Left
                (1, 0),    # Right
                (-1, 1),   # Bottom-left
                (1, 1),    # Bottom-right
                (0, -1),   # Top
                (0, 1)     # Bottom
            ]
        
        for dx, dy in offsets:
            new_col, new_row = col + dx, row + dy
            if 0 <= new_col < self.grid_width and 0 <= new_row < self.grid_height:
                neighbors.append((new_col, new_row))
    
        return neighbors

    def draw_hex(self, dc: wx.DC, points: List[Tuple[float, float]], biome_data: Dict, col: int, row: int) -> None:
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        dc.SetBrush(wx.Brush(biome_data["primary"]))
        dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])

        current_pos = (col, row)
        current_biome = self.biome_manager.get_biome(current_pos)
        
        if biome_data["pattern"] and current_biome not in ["Marais", "Ville"]:
            if biome_data["pattern"]["type"] == "line":
                self.draw_path_lines(dc, points, col, row, biome_data["pattern"]["color"])

    def draw_path_lines(self, dc: wx.DC, points: List[Tuple[float, float]], col: int, row: int, color: str) -> None:
        current_pos = (col, row)
        current_biome = self.biome_manager.get_biome(current_pos)
        center = self.get_hex_center(col, row)

        if current_biome == "Riviere":
            river_tile = self.biome_manager.river_path.get_tile(current_pos)
            if river_tile:
                for next_pos in river_tile['connections']:
                    next_center = self.get_hex_center(*next_pos)
                    next_biome = self.biome_manager.get_biome(next_pos)
                    self._draw_connection_line(dc, center, next_center, next_biome, color)
        elif current_biome == "Route":
            route_tile = self.biome_manager.river_path.get_tile(current_pos)
            if route_tile:
                for next_pos in route_tile['connections']:
                    next_center = self.get_hex_center(*next_pos)
                    next_biome = self.biome_manager.get_biome(next_pos)
                    self._draw_connection_line(dc, center, next_center, next_biome, color)

    def _draw_connection_line(self, dc: wx.DC, start_center: Tuple[float, float], 
                            end_center: Tuple[float, float], end_biome: str, color: str) -> None:
        if end_biome in ["Marais", "Ville"]:
            mid_x = (start_center[0] + end_center[0]) / 2
            mid_y = (start_center[1] + end_center[1]) / 2
            dc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
            dc.DrawLine(int(start_center[0]), int(start_center[1]), int(mid_x), int(mid_y))
        else:
            dc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
            dc.DrawLine(int(start_center[0]), int(start_center[1]), 
                       int(end_center[0]), int(end_center[1]))

    def find_river_connections(self, col: int, row: int) -> List[Tuple[int, int]]:
        valid_connections = []
        current_pos = (col, row)
        neighbors = self.get_neighbors(col, row)

        # First prioritize connecting to existing river tiles
        for neighbor in neighbors:
            if (self.biome_manager.get_biome(neighbor) == "Riviere" and
                len(self.biome_manager.river_path.get_tile(neighbor)['connections']) < 2):
                valid_connections.append(neighbor)
                if len(valid_connections) >= 2:
                    return valid_connections

        # Then check cities/swamps if we still need connections
        for neighbor in neighbors:
            if (self.biome_manager.get_biome(neighbor) in ["Ville", "Marais"] and
                neighbor not in valid_connections):
                valid_connections.append(neighbor)
                if len(valid_connections) >= 2:
                    return valid_connections

        return valid_connections
