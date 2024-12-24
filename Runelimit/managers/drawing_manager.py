import wx
import math
import random
from typing import List, Tuple, Dict

class DrawingManager:
    LINE_PATTERN_WIDTH = 2

    def __init__(self, hex_manager):
        self.hex_manager = hex_manager
        self.biome_manager = None
        self.use_double_buffering = True  # Nouvelle propriété

    def set_biome_manager(self, biome_manager):
        self.biome_manager = biome_manager

    def draw_grid(self, dc):
        buffer = wx.Bitmap(self.hex_manager.canvas_width, self.hex_manager.canvas_height)
        memory_dc = wx.MemoryDC(buffer)
    
        memory_dc.SetBackground(wx.Brush(wx.WHITE))
        memory_dc.Clear()
    
        # Dessiner la grille hexagonale
        for row in range(self.hex_manager.grid_height):
            for col in range(self.hex_manager.grid_width):
                center = self.hex_manager.get_hex_center(col, row)
                points = self.hex_manager.get_hex_points(*center)
                pos = (col, row)
                biome = self.biome_manager.get_biome(pos)
                biome_data = self.biome_manager.get_biome_data(biome)
                self.draw_hex(memory_dc, points, biome_data, pos)
    
        # Ajouter les événements
        self.draw_events(memory_dc)
    
        # Copier le buffer vers le DC principal
        dc.Blit(0, 0, buffer.GetWidth(), buffer.GetHeight(), memory_dc, 0, 0)
    
    def draw_hex(self, dc, points, biome_data, pos):
        if not biome_data or "primary" not in biome_data:
            dc.SetBrush(wx.Brush(wx.Colour(200, 200, 200)))
        else:
            dc.SetBrush(wx.Brush(biome_data["primary"]))

        if pos == self.hex_manager.selected_hex:
            dc.SetPen(wx.Pen(wx.YELLOW, 2))
        elif pos in self.hex_manager.highlighted_hexes:
            dc.SetPen(wx.Pen(wx.YELLOW, 4))
        else:
            dc.SetPen(wx.Pen(wx.BLACK, 1))

        dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])

        current_biome = self.hex_manager.biome_manager.get_biome(pos)
        center = self.hex_manager.get_hex_center(*pos)

        if current_biome == "Ville":
            self._draw_city(dc, center)
        elif current_biome == "Riviere":
            self._draw_river_tile(dc, pos, center)
        elif current_biome == "Route":
            self._draw_route_tile(dc, pos, center)
        elif current_biome == "Marais":
            self._draw_swamp(dc, center)
            
    def _draw_pattern_overlay(self, dc: wx.DC, points: List[Tuple[float, float]], pattern: Dict, pos: Tuple[int, int]):
        if pattern["type"] == "line":
            dc.SetPen(wx.Pen(pattern["color"], self.LINE_PATTERN_WIDTH))
            for i in range(0, 6, 2):
                start_x = points[i][0]
                start_y = points[i][1]
                end_x = points[(i + 3) % 6][0]
                end_y = points[(i + 3) % 6][1]
                dc.DrawLine(int(start_x), int(start_y), int(end_x), int(end_y))

    def _draw_city(self, dc: wx.DC, center: Tuple[float, float]):
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            radius = self.hex_manager.hex_size * 0.3
            gc.SetBrush(wx.Brush(wx.Colour(200, 200, 200)))
            gc.SetPen(wx.Pen(wx.BLACK, 2))
            gc.DrawEllipse(center[0] - radius, center[1] - radius, radius * 2, radius * 2)

    def _draw_river_tile(self, dc: wx.DC, current_pos: tuple, center: tuple):
        river_tile = self.hex_manager.biome_manager.river_path.get_tile(current_pos)
        if river_tile:
            if not river_tile['connections']:
                self._draw_lake(dc, center, wx.BLUE)
            else:
                for next_pos in river_tile['connections']:
                    next_center = self.hex_manager.get_hex_center(*next_pos)
                    next_biome = self.hex_manager.biome_manager.get_biome(next_pos)
                    self._draw_connection_line(dc, center, next_center, next_biome, wx.BLUE)

    def _draw_route_tile(self, dc: wx.DC, current_pos: tuple, center: tuple):
        route_tile = self.hex_manager.biome_manager.river_path.get_route_tile(current_pos)
        if route_tile:
            for next_pos in route_tile['connections']:
                next_center = self.hex_manager.get_hex_center(*next_pos)
                next_biome = self.hex_manager.biome_manager.get_biome(next_pos)
                self._draw_route_line(dc, center, next_center, next_biome, wx.Colour(139, 69, 19))

    def _draw_lake(self, dc: wx.DC, center: Tuple[float, float], color: str):
        x, y = center
        base_radius = self.hex_manager.hex_size * 0.3
        points = self._generate_lake_points(x, y, base_radius)
        dc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
        dc.SetBrush(wx.Brush(color))
        dc.DrawPolygon([wx.Point(int(px), int(py)) for px, py in points])

    def _generate_lake_points(self, x: float, y: float, base_radius: float) -> List[Tuple[float, float]]:
        points = []
        num_points = 16
        prev_radius = base_radius
        
        for i in range(num_points):
            angle = (i * 360 / num_points) * math.pi / 180
            radius = (prev_radius + base_radius * random.uniform(0.7, 1.3)) / 2
            prev_radius = radius
            points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
        
        points.append(points[0])
        return points

    def _draw_connection_line(self, dc: wx.DC, start_center: Tuple[float, float], 
                            end_center: Tuple[float, float], end_biome: str, color: str):
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            start_point = self._find_optimal_connection_point(start_center, end_center,
                            self.hex_manager.get_hex_points(*start_center))
            end_point = self._find_optimal_connection_point(end_center, start_center,
                            self.hex_manager.get_hex_points(*end_center))
            
            path = gc.CreatePath()
            path.MoveToPoint(*start_point)
            path.AddLineToPoint(*end_point)
            
            gc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
            gc.DrawPath(path)

    def _find_optimal_connection_point(self, from_center: Tuple[float, float], 
                                    to_center: Tuple[float, float],
                                    hex_points: List[Tuple[float, float]]) -> Tuple[float, float]:
        # Calculer le vecteur de direction
        dx = to_center[0] - from_center[0]
        dy = to_center[1] - from_center[1]
        
        # Normaliser le vecteur
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length
        
        # Utiliser directement le centre comme point de départ
        return (from_center[0], from_center[1])

    def _draw_route_line(self, dc: wx.DC, start_center: Tuple[float, float], 
                        end_center: Tuple[float, float], end_biome: str, color: str):
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            start_point = self._find_optimal_connection_point(start_center, end_center,
                            self.hex_manager.get_hex_points(*start_center))
            end_point = self._find_optimal_connection_point(end_center, start_center,
                            self.hex_manager.get_hex_points(*end_center))
            
            path = gc.CreatePath()
            path.MoveToPoint(*start_point)
            path.AddLineToPoint(*end_point)
            
            dashed_pen = wx.Pen(color, self.LINE_PATTERN_WIDTH)
            dashed_pen.SetStyle(wx.PENSTYLE_SHORT_DASH)
            gc.SetPen(dashed_pen)
            gc.DrawPath(path)

    def _draw_swamp(self, dc: wx.DC, center: Tuple[float, float]):
        base_radius = self.hex_manager.hex_size * 0.7
        swamp_points = self._generate_lake_points(center[0], center[1], base_radius)
        swamp_color = wx.Colour(100, 170, 220)
        vegetation_color = wx.Colour(80, 160, 70)

        dc.SetPen(wx.Pen(swamp_color, self.LINE_PATTERN_WIDTH))
        dc.SetBrush(wx.Brush(swamp_color))
        dc.DrawPolygon([wx.Point(int(px), int(py)) for px, py in swamp_points])

        self._draw_vegetation(dc, center, base_radius, vegetation_color)

    def _draw_vegetation(self, dc: wx.DC, center: Tuple[float, float], base_radius: float, color: str):
        num_dots = random.randint(8, 12)
        for _ in range(num_dots):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, base_radius * 0.6)
            dot_x = center[0] + radius * math.cos(angle)
            dot_y = center[1] + radius * math.sin(angle)
            dot_size = random.uniform(3, 6)
        
            dc.SetBrush(wx.Brush(color))
            dc.SetPen(wx.Pen(color))
            dc.DrawCircle(int(dot_x), int(dot_y), int(dot_size))

    def draw_diamond_marker(self, dc, center, color):
        x, y = center
        size = self.hex_manager.hex_size * 0.3  # Taille du diamant proportionnelle à l'hexagone
        
        points = [
            (x, y - size),  # Haut
            (x + size, y),  # Droite
            (x, y + size),  # Bas
            (x - size, y)   # Gauche
        ]
        
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        dc.DrawPolygon([wx.Point(int(px), int(py)) for px, py in points])

    def draw_events(self, dc):
        # Définition des couleurs par tier
        tier_colors = {
            "Tier1": wx.Colour(0, 255, 0),    # Vert
            "Tier2": wx.Colour(0, 0, 255),    # Bleu
            "Tier3": wx.Colour(255, 255, 0),  # Jaune
            "Tier4": wx.Colour(255, 0, 0)     # Rouge
        }
        
        for pos, event_data in self.biome_manager.events.items():
            if event_data["type"] in tier_colors:
                center = self.hex_manager.get_hex_center(*pos)
                self.draw_diamond_marker(dc, center, tier_colors[event_data["type"]])
