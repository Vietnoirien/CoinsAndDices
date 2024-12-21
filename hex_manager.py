import math
import wx
from typing import List, Tuple, Optional, Dict

class HexManager:
    # Class-level constants
    HEX_ANGLE_DEG = 60
    HEX_ANGLE_RAD = math.pi / 180 * HEX_ANGLE_DEG
    CANVAS_WIDTH_RATIO = 0.6  # 60% of window width
    GRID_MARGIN = 50
    
    NEIGHBOR_DIRECTIONS = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),           (1, 0),
        (-1, 1),  (0, 1),  (1, 1)
    ]
    
    FLOW_PRIORITIES = {
        (0, 1): 1,     # South
        (1, 0): 2,     # East
        (-1, 0): 2,    # West
        (0, -1): 3,    # North
    }
    
    MAX_RIVER_CONNECTIONS = 2
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

    def get_hex_center(self, col, row):
        # Add margin offset to starting position
        margin = 40
        
        # Horizontal spacing between hex centers
        horiz_spacing = self.hex_size * 1.5
        # Vertical spacing between hex centers
        vert_spacing = self.hex_size * 1.732
        
        x = col * horiz_spacing + margin
        y = row * vert_spacing + margin
        
        # Offset odd columns
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
        odd_col = col % 2
        
        # These are the only valid adjacent positions in a hex grid
        adjacent_offsets = [
            (-1, 0),  # Left
            (1, 0),   # Right
            (0, -1),  # Up
            (0, 1),   # Down
            (-1, odd_col - 1),  # Upper left
            (1, odd_col - 1),   # Upper right
        ]
        
        for dx, dy in adjacent_offsets:
            new_col, new_row = col + dx, row + dy
            if 0 <= new_col < self.grid_width and 0 <= new_row < self.grid_height:
                neighbors.append((new_col, new_row))
        
        return neighbors

    def draw_hex(self, dc: wx.DC, points: List[Tuple[float, float]], biome_data: Dict, col: int, row: int) -> None:
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        dc.SetBrush(wx.Brush(biome_data["primary"]))
        dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])

        current_biome = self.biome_manager.get_biome((col, row))
        if biome_data["pattern"] and current_biome not in ["Marais", "Ville"]:
            if biome_data["pattern"]["type"] == "line":
                self.draw_connected_lines(dc, points, col, row, biome_data["pattern"]["color"])

    def get_position_priority(self, position: Tuple[int, int]) -> int:
        return self.FLOW_PRIORITIES.get(position, 4)

    def draw_connected_lines(self, dc: wx.DC, points: List[Tuple[float, float]], col: int, row: int, color: str) -> None:
        current_pos = (col, row)
        current_biome = self.biome_manager.get_biome(current_pos)
        center = self.get_hex_center(col, row)

        if current_biome == "Riviere":
            connected_hexes = self.biome_manager.get_connected_biomes(current_pos)
            for next_pos in connected_hexes:
                next_center = self.get_hex_center(*next_pos)
                next_biome = self.biome_manager.get_biome(next_pos)
                self._draw_connection_line(dc, center, next_center, next_biome, color)

        elif current_biome == "Route":
            for adj_col, adj_row in self.get_neighbors(col, row):
                adj_biome = self.biome_manager.get_biome((adj_col, adj_row))
                if self.biome_manager.should_connect(current_biome, adj_biome):
                    adj_center = self.get_hex_center(adj_col, adj_row)
                    self._draw_connection_line(dc, center, adj_center, adj_biome, color)

    def _draw_connection_line(self, dc: wx.DC, start_center: Tuple[float, float], end_center: Tuple[float, float], end_biome: str, color: str) -> None:
        if end_biome in ["Marais", "Ville"]:
            mid_x = (start_center[0] + end_center[0]) / 2
            mid_y = (start_center[1] + end_center[1]) / 2
            dc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
            dc.DrawLine(int(start_center[0]), int(start_center[1]), int(mid_x), int(mid_y))
        else:
            dc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
            dc.DrawLine(int(start_center[0]), int(start_center[1]), 
                    int(end_center[0]), int(end_center[1]))

    def is_edge_tile(self, col: int, row: int) -> bool:
        return col == 0 or col == self.grid_width - 1 or row == 0 or row == self.grid_height - 1

    def get_edge_sides(self, col: int, row: int) -> List[str]:
        edges = []
        if col == 0:
            edges.append("west")
        if col == self.grid_width - 1:
            edges.append("east")
        if row == 0:
            edges.append("north")
        if row == self.grid_height - 1:
            edges.append("south")
        return edges

    def find_river_connections(self, col: int, row: int) -> List[Tuple[int, int]]:
        valid_neighbors = []
        current_pos = (col, row)
    
        # Check if this hex is on the edge
        if self.is_edge_tile(col, row):
            # Check if any adjacent river already connects to this edge
            edge_sides = self.get_edge_sides(col, row)
            for adj_pos in self.get_neighbors(col, row):
                adj_col, adj_row = adj_pos
                adj_biome = self.biome_manager.get_biome(adj_pos)
                if adj_biome == "Riviere":
                    # If adjacent river is on same edge, skip this hex's edge connection
                    if any(side in self.get_edge_sides(adj_col, adj_row) for side in edge_sides):
                        edge_sides = []  # Remove edge connection possibility
                        break
    
        # Rest of the connection logic...
        for adj_pos in self.get_neighbors(col, row):
            adj_col, adj_row = adj_pos
            adj_biome = self.biome_manager.get_biome(adj_pos)
        
            if adj_biome in ["Marais", "Riviere", "Ville"]:
                if self.biome_manager.get_connection_count(adj_pos) < self.MAX_RIVER_CONNECTIONS:
                    position = self.get_relative_position(col, row, adj_col, adj_row)
                    # Only allow edge connection if we still have valid edge_sides
                    if self.is_edge_tile(col, row):
                        relative_side = self.get_position_side(position)
                        if relative_side in edge_sides:
                            priority = 1  # Give edge connection high priority
                            valid_neighbors.append((adj_pos, priority))
                            continue
                
                    priority = self.get_position_priority(position)
                    valid_neighbors.append((adj_pos, priority))

        valid_neighbors.sort(key=lambda x: x[1])
        return [pos for pos, _ in valid_neighbors[:self.MAX_RIVER_CONNECTIONS]]

    def get_position_side(self, position: Tuple[int, int]) -> str:
        dx, dy = position
        if dy < 0:
            return "north"
        elif dy > 0:
            return "south"
        elif dx < 0:
            return "west"
        elif dx > 0:
            return "east"
        return ""

    def get_relative_position(self, current_col: int, current_row: int, adj_col: int, adj_row: int) -> Tuple[int, int]:
        return (adj_col - current_col, adj_row - current_row)
