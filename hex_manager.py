import wx
import math
from typing import List, Tuple, Optional
from drawing_manager import DrawingManager

class HexManager:
    HEX_ANGLE_DEG = 60
    HEX_ANGLE_RAD = math.pi / 180 * HEX_ANGLE_DEG
    CANVAS_WIDTH_RATIO = 0.6
    GRID_MARGIN = 50

    def __init__(self, grid_width: int, grid_height: int):
        if grid_width <= 0 or grid_height <= 0:
            raise ValueError("Grid dimensions must be positive")
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.hex_size = 0
        self.biome_manager = None
        self.canvas = None
        self.last_clicked_hex = None
        self.highlighted_hex = None
        self.canvas_width = 0
        self.canvas_height = 0
        self.drawing_manager = DrawingManager(self)
    
    def set_biome_manager(self, biome_manager) -> None:
        self.biome_manager = biome_manager
    
    def calculate_hex_size(self, window_width: int, window_height: int) -> None:
        self.canvas_width = window_width
        self.canvas_height = window_height
        available_width = window_width * self.CANVAS_WIDTH_RATIO
        max_width = (available_width - self.GRID_MARGIN) / (self.grid_width * 1.5)
        max_height = (window_height - self.GRID_MARGIN) / (self.grid_height * math.sqrt(3))
        self.hex_size = min(max_width, max_height)
        self.drawing_manager.invalidate_buffer()

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
        if col % 2 == 0:
            offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1)]
        else:
            offsets = [(-1, 0), (1, 0), (-1, 1), (1, 1), (0, -1), (0, 1)]
        
        for dx, dy in offsets:
            new_col, new_row = col + dx, row + dy
            if 0 <= new_col < self.grid_width and 0 <= new_row < self.grid_height:
                neighbors.append((new_col, new_row))
    
        return neighbors

    def find_river_connections(self, col: int, row: int) -> List[Tuple[int, int]]:
        valid_connections = []
        current_pos = (col, row)
        neighbors = self.get_neighbors(col, row)

        for neighbor in neighbors:
            if (self.biome_manager.get_biome(neighbor) == "Riviere" and
                len(self.biome_manager.river_path.get_tile(neighbor)['connections']) < 2):
                valid_connections.append(neighbor)
                if len(valid_connections) >= 2:
                    return valid_connections

        for neighbor in neighbors:
            if (self.biome_manager.get_biome(neighbor) in ["Ville", "Marais"] and
                neighbor not in valid_connections):
                valid_connections.append(neighbor)
                if len(valid_connections) >= 2:
                    return valid_connections

        return valid_connections

    def find_route_connections(self, col: int, row: int) -> List[Tuple[int, int]]:
        valid_connections = []
        neighbors = self.get_neighbors(col, row)

        for neighbor in neighbors:
            if (self.biome_manager.get_biome(neighbor) == "Route" and
                len(self.biome_manager.river_path.get_route_tile(neighbor)['connections']) < 2):
                valid_connections.append(neighbor)
                if len(valid_connections) >= 2:
                    return valid_connections

        for neighbor in neighbors:
            if (self.biome_manager.get_biome(neighbor) == "Ville" and
                neighbor not in valid_connections):
                valid_connections.append(neighbor)
                if len(valid_connections) >= 2:
                    return valid_connections

        return valid_connections

    def set_highlighted_hex(self, hex_pos):
        self.highlighted_hex = hex_pos
        if self.canvas:
            self.canvas.Refresh()
