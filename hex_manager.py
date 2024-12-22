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
        self.river_buffer = None  # Initialize as None
        self.river_dirty = True
        
    def set_biome_manager(self, biome_manager) -> None:
        self.biome_manager = biome_manager
    
    def calculate_hex_size(self, window_width: int, window_height: int) -> None:
        self.canvas_width = window_width
        self.canvas_height = window_height
        available_width = window_width * self.CANVAS_WIDTH_RATIO
        max_width = (available_width - self.GRID_MARGIN) / (self.grid_width * 1.5)
        max_height = (window_height - self.GRID_MARGIN) / (self.grid_height * math.sqrt(3))
        self.hex_size = min(max_width, max_height)
    
        # Create buffer only after we have valid dimensions
        if window_width > 0 and window_height > 0:
            self.river_buffer = wx.Bitmap(window_width, window_height)
            self.river_dirty = True
        self.river_dirty = True

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
        # Draw the base hex
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        dc.SetBrush(wx.Brush(biome_data["primary"]))
        dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])

        # Draw patterns only if needed
        current_pos = (col, row)
        current_biome = self.biome_manager.get_biome(current_pos)
        
        if biome_data["pattern"] and current_biome in ["Riviere", "Route"]:
            self.draw_path_lines(dc, points, col, row, biome_data["pattern"]["color"])

    def draw_path_lines(self, dc: wx.DC, points: List[Tuple[float, float]], col: int, row: int, color: str) -> None:
        current_pos = (col, row)
        current_biome = self.biome_manager.get_biome(current_pos)
        center = self.get_hex_center(col, row)

        # Draw directly to DC for now, buffer will be used for optimization later
        if current_biome == "Riviere":
            river_tile = self.biome_manager.river_path.get_tile(current_pos)
            if river_tile:
                if not river_tile['connections']:
                    self._draw_lake(dc, center, color)
                else:
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
                    
    def _draw_lake(self, dc: wx.DC, center: Tuple[float, float], color: str) -> None:
        import random
        x, y = center
        base_radius = self.hex_size * 0.3
        num_points = 16  # Increased number of points for smoother shape
        points = []
    
        # Create Perlin noise-like effect
        prev_radius = base_radius
        for i in range(num_points):
            angle = (i * 360 / num_points) * math.pi / 180
            # Use previous radius to create more continuous variation
            radius = (prev_radius + base_radius * random.uniform(0.7, 1.3)) / 2
            prev_radius = radius
        
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
    
        # Close the shape by connecting back to first point
        points.append(points[0])
    
        # Draw with anti-aliasing
        dc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
        dc.SetBrush(wx.Brush(color))
        dc.DrawPolygon([wx.Point(int(px), int(py)) for px, py in points])

    def _draw_connection_line(self, dc: wx.DC, start_center: Tuple[float, float], 
                        end_center: Tuple[float, float], end_biome: str, color: str) -> None:
        import random
        
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return
            
        path = gc.CreatePath()
        
        # Base width with controlled variation
        base_width = self.LINE_PATTERN_WIDTH
        width_variation = random.uniform(1.5, 2.2)
        current_width = int(base_width * width_variation)
        
        # Calculate main direction vector
        dx = end_center[0] - start_center[0]
        dy = end_center[1] - start_center[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Create control points with constrained randomness
        num_points = 3
        points = []
        
        # Always include start and end points
        points.append(start_center)
        
        # Generate intermediate points with controlled offsets
        for i in range(1, num_points):
            t = i / (num_points + 1)
            # Limit random offset based on distance
            max_offset = min(distance * 0.15, self.hex_size/6)
            rand_offset_x = random.uniform(-max_offset, max_offset)
            rand_offset_y = random.uniform(-max_offset, max_offset)
            
            x = start_center[0] + dx * t + rand_offset_x
            y = start_center[1] + dy * t + rand_offset_y
            points.append((x, y))
        
        points.append(end_center)
        
        # Draw continuous curve
        path.MoveToPoint(points[0][0], points[0][1])
        
        # Use quadratic Bezier curves for smoother connection
        for i in range(len(points) - 1):
            if i == 0:  # First segment
                ctrl_x = points[1][0]
                ctrl_y = points[1][1]
                end_x = (points[1][0] + points[2][0]) / 2
                end_y = (points[1][1] + points[2][1]) / 2
            elif i == len(points) - 2:  # Last segment
                ctrl_x = points[-2][0]
                ctrl_y = points[-2][1]
                end_x = points[-1][0]
                end_y = points[-1][1]
            else:  # Middle segments
                ctrl_x = points[i][0]
                ctrl_y = points[i][1]
                end_x = (points[i][0] + points[i+1][0]) / 2
                end_y = (points[i][1] + points[i+1][1]) / 2
                
            path.AddQuadCurveToPoint(ctrl_x, ctrl_y, end_x, end_y)
        
        gc.SetPen(wx.Pen(color, current_width))
        gc.DrawPath(path)

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

    def invalidate_river_buffer(self):
        """Mark the river buffer as needing redraw"""
        self.river_dirty = True

    def _draw_path_to_buffer(self, mem_dc: wx.MemoryDC, current_pos: tuple, center: tuple, color: str) -> None:
        """Draw a single river/route segment to the buffer"""
        current_biome = self.biome_manager.get_biome(current_pos)
        
        if current_biome == "Riviere":
            river_tile = self.biome_manager.river_path.get_tile(current_pos)
            if river_tile:
                if not river_tile['connections']:
                    self._draw_lake(mem_dc, center, color)
                else:
                    for next_pos in river_tile['connections']:
                        next_center = self.get_hex_center(*next_pos)
                        next_biome = self.biome_manager.get_biome(next_pos)
                        self._draw_connection_line(mem_dc, center, next_center, next_biome, color)
                        
        elif current_biome == "Route":
            route_tile = self.biome_manager.river_path.get_tile(current_pos)
            if route_tile:
                for next_pos in route_tile['connections']:
                    next_center = self.get_hex_center(*next_pos)
                    next_biome = self.biome_manager.get_biome(next_pos)
                    self._draw_connection_line(mem_dc, center, next_center, next_biome, color)
