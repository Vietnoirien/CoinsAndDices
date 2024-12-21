import math

class HexManager:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.hex_size = 0
        
    def calculate_hex_size(self, window_width, window_height):
        available_width = window_width * 0.6
        max_width = (available_width - 50) / (self.grid_width * 1.5)
        max_height = (window_height - 50) / (self.grid_height * math.sqrt(3))
        self.hex_size = min(max_width, max_height)
        
    def get_hex_center(self, col, row):
        width = self.hex_size * 2
        height = self.hex_size * math.sqrt(3)
        x = width * 0.75 * col
        y = height * row
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
