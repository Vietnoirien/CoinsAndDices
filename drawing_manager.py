import wx
import math
import random
from typing import List, Tuple, Dict

class DrawingManager:
    LINE_PATTERN_WIDTH = 2

    def __init__(self, hex_manager):
        self.hex_manager = hex_manager
        self.river_buffer = None
        self.river_dirty = True

    def invalidate_buffer(self):
        """Mark the buffer as needing redraw"""
        if self.hex_manager.canvas_width > 0 and self.hex_manager.canvas_height > 0:
            self.river_buffer = wx.Bitmap(self.hex_manager.canvas_width, 
                                        self.hex_manager.canvas_height)
        self.river_dirty = True
        
    def draw_hex(self, dc: wx.DC, points: List[Tuple[float, float]], biome_data: Dict, col: int, row: int) -> None:
        current_pos = (col, row)
    
        # Définir l'épaisseur du contour en fonction de la sélection
        line_width = 3 if current_pos == self.hex_manager.highlighted_hex else 1
        dc.SetPen(wx.Pen(wx.BLACK, line_width))
    
        # Si l'hexagone est surligné, ajouter un effet de surbrillance
        if current_pos == self.hex_manager.highlighted_hex:
            # Dessiner un contour de surbrillance
            highlight_pen = wx.Pen(wx.Colour(255, 255, 0), 2)  # Jaune
            dc.SetPen(highlight_pen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])
        
            # Revenir au style normal pour le reste du dessin
            dc.SetPen(wx.Pen(wx.BLACK, line_width))
        
        # Continuer avec le dessin normal de l'hexagone
        dc.SetBrush(wx.Brush(biome_data["primary"]))
        dc.DrawPolygon([wx.Point(int(x), int(y)) for x, y in points])
    
        current_biome = self.hex_manager.biome_manager.get_biome(current_pos)
        center = self.hex_manager.get_hex_center(col, row)
    
        # Handle specific biome types
        if current_biome == "Ville":
            self._draw_city(dc, center)
        elif current_biome == "Riviere":
            self._draw_river_tile(dc, current_pos, center)
        elif current_biome == "Route":
            self._draw_route_tile(dc, current_pos, center)
        elif current_biome == "Marais":
            self._draw_swamp(dc, center)
        elif biome_data["pattern"]:
            self._draw_pattern_overlay(dc, points, biome_data["pattern"])

    def _draw_city(self, dc: wx.DC, center: Tuple[float, float]) -> None:
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            radius = self.hex_manager.hex_size * 0.3
            gc.SetBrush(wx.Brush(wx.Colour(200, 200, 200)))
            gc.SetPen(wx.Pen(wx.BLACK, 2))
            gc.DrawEllipse(center[0] - radius, center[1] - radius, radius * 2, radius * 2)

    def _draw_river_tile(self, dc: wx.DC, current_pos: tuple, center: tuple) -> None:
        river_tile = self.hex_manager.biome_manager.river_path.get_tile(current_pos)
        if river_tile:
            if not river_tile['connections']:
                self._draw_lake(dc, center, wx.BLUE)
            else:
                for next_pos in river_tile['connections']:
                    next_center = self.hex_manager.get_hex_center(*next_pos)
                    next_biome = self.hex_manager.biome_manager.get_biome(next_pos)
                    self._draw_connection_line(dc, center, next_center, next_biome, wx.BLUE)

    def _draw_route_tile(self, dc: wx.DC, current_pos: tuple, center: tuple) -> None:
        route_tile = self.hex_manager.biome_manager.river_path.get_route_tile(current_pos)
        if route_tile:
            for next_pos in route_tile['connections']:
                next_center = self.hex_manager.get_hex_center(*next_pos)
                next_biome = self.hex_manager.biome_manager.get_biome(next_pos)
                self._draw_route_line(dc, center, next_center, next_biome, wx.Colour(139, 69, 19))

    def _draw_pattern_overlay(self, dc: wx.DC, points: List[Tuple[float, float]], pattern: Dict) -> None:
        if pattern["type"] == "line":
            dc.SetPen(wx.Pen(pattern["color"], self.LINE_PATTERN_WIDTH))
            for i in range(0, 6, 2):
                start_x = points[i][0]
                start_y = points[i][1]
                end_x = points[(i + 3) % 6][0]
                end_y = points[(i + 3) % 6][1]
                dc.DrawLine(int(start_x), int(start_y), int(end_x), int(end_y))

    def _draw_lake(self, dc: wx.DC, center: Tuple[float, float], color: str) -> None:
        x, y = center
        base_radius = self.hex_manager.hex_size * 0.3
        num_points = 16
        points = []
    
        prev_radius = base_radius
        for i in range(num_points):
            angle = (i * 360 / num_points) * math.pi / 180
            radius = (prev_radius + base_radius * random.uniform(0.7, 1.3)) / 2
            prev_radius = radius
            
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
    
        points.append(points[0])
    
        dc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
        dc.SetBrush(wx.Brush(color))
        dc.DrawPolygon([wx.Point(int(px), int(py)) for px, py in points])

    def _draw_connection_line(self, dc: wx.DC, start_center: Tuple[float, float], 
                            end_center: Tuple[float, float], end_biome: str, color: str) -> None:
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            if end_biome == "Marais":
                base_radius = self.hex_manager.hex_size * 0.7
                swamp_points = self._generate_swamp_shape(end_center, base_radius)
                
                dx = start_center[0] - end_center[0]
                dy = start_center[1] - end_center[1]
                angle_to_river = math.atan2(dy, dx)
                
                # Trouver le meilleur point d'intersection avec la forme du marais
                best_point = swamp_points[0]
                min_angle_diff = float('inf')
                
                for point in swamp_points:
                    test_angle_diff = abs(math.atan2(point[1] - end_center[1], 
                                                point[0] - end_center[0]) - angle_to_river)
                    if test_angle_diff < min_angle_diff:
                        min_angle_diff = test_angle_diff
                        best_point = point
                
                path = gc.CreatePath()
                path.MoveToPoint(best_point[0], best_point[1])
                path.AddLineToPoint(start_center[0], start_center[1])
                
                gc.SetPen(wx.Pen(color, self.LINE_PATTERN_WIDTH))
                gc.DrawPath(path)
                return
                
            elif end_biome == "Ville":
                hex_points = self.hex_manager.get_hex_points(*end_center)
                hex_sides = list(zip(hex_points, hex_points[1:] + [hex_points[0]]))
                
                closest_side = min(hex_sides, 
                                key=lambda side: ((side[0][0] + side[1][0])/2 - start_center[0])**2 + 
                                                ((side[0][1] + side[1][1])/2 - start_center[1])**2)
                
                end_center = ((closest_side[0][0] + closest_side[1][0])/2,
                            (closest_side[0][1] + closest_side[1][1])/2)
            
            path = gc.CreatePath()
            base_width = self.LINE_PATTERN_WIDTH
            width_variation = random.uniform(1.5, 2.2)
            current_width = int(base_width * width_variation)
            
            dx = end_center[0] - start_center[0]
            dy = end_center[1] - start_center[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            points = self._generate_curve_points(start_center, end_center, distance)
            self._draw_curved_path(gc, points, color, current_width)

    def _generate_curve_points(self, start: Tuple[float, float], end: Tuple[float, float], 
                             distance: float) -> List[Tuple[float, float]]:
        points = [start]
        num_points = 3
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        for i in range(1, num_points):
            t = i / (num_points + 1)
            max_offset = min(distance * 0.15, self.hex_manager.hex_size/6)
            rand_offset_x = random.uniform(-max_offset, max_offset)
            rand_offset_y = random.uniform(-max_offset, max_offset)
            
            x = start[0] + dx * t + rand_offset_x
            y = start[1] + dy * t + rand_offset_y
            points.append((x, y))
            
        points.append(end)
        return points

    def _draw_curved_path(self, gc: wx.GraphicsContext, points: List[Tuple[float, float]], 
                         color: str, width: int) -> None:
        path = gc.CreatePath()
        path.MoveToPoint(points[0][0], points[0][1])
        
        for i in range(len(points) - 1):
            if i == 0:
                ctrl_x, ctrl_y = points[1]
                end_x = (points[1][0] + points[2][0]) / 2
                end_y = (points[1][1] + points[2][1]) / 2
            elif i == len(points) - 2:
                ctrl_x, ctrl_y = points[-2]
                end_x, end_y = points[-1]
            else:
                ctrl_x, ctrl_y = points[i]
                end_x = (points[i][0] + points[i+1][0]) / 2
                end_y = (points[i][1] + points[i+1][1]) / 2
                
            path.AddQuadCurveToPoint(ctrl_x, ctrl_y, end_x, end_y)
        
        gc.SetPen(wx.Pen(color, width))
        gc.DrawPath(path)

    def _draw_route_line(self, dc: wx.DC, start_center: Tuple[float, float], 
                        end_center: Tuple[float, float], end_biome: str, color: str) -> None:
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            if end_biome == "Ville":
                city_points = self.hex_manager.get_hex_points(*end_center)
                hex_sides = list(zip(city_points, city_points[1:] + [city_points[0]]))
                
                closest_side = min(hex_sides, 
                                 key=lambda side: ((side[0][0] + side[1][0])/2 - start_center[0])**2 + 
                                                ((side[0][1] + side[1][1])/2 - start_center[1])**2)
                
                end_center = ((closest_side[0][0] + closest_side[1][0])/2,
                             (closest_side[0][1] + closest_side[1][1])/2)
            
            dashed_pen = wx.Pen(color, self.LINE_PATTERN_WIDTH)
            dashed_pen.SetStyle(wx.PENSTYLE_SHORT_DASH)
            gc.SetPen(dashed_pen)

            path = gc.CreatePath()
            path.MoveToPoint(start_center[0], start_center[1])
            path.AddLineToPoint(end_center[0], end_center[1])

            gc.DrawPath(path)

    def _generate_swamp_shape(self, center: Tuple[float, float], base_radius: float) -> List[Tuple[float, float]]:
        x, y = center
        num_points = 16
        points = []
    
        prev_radius = base_radius
        for i in range(num_points):
            angle = (i * 360 / num_points) * math.pi / 180
            radius = (prev_radius + base_radius * random.uniform(0.7, 1.3)) / 2
            prev_radius = radius
        
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
    
        points.append(points[0])  # Fermer la forme
        return points

    def _draw_swamp(self, dc: wx.DC, center: Tuple[float, float]) -> List[Tuple[float, float]]:
        base_radius = self.hex_manager.hex_size * 0.7
        swamp_points = self._generate_swamp_shape(center, base_radius)
        swamp_color = wx.Colour(100, 170, 220)
        vegetation_color = wx.Colour(80, 160, 70)

        # Dessiner la forme du marais
        dc.SetPen(wx.Pen(swamp_color, self.LINE_PATTERN_WIDTH))
        dc.SetBrush(wx.Brush(swamp_color))
        dc.DrawPolygon([wx.Point(int(px), int(py)) for px, py in swamp_points])

        # Ajouter les points de végétation
        num_dots = random.randint(8, 12)
        for _ in range(num_dots):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, base_radius * 0.6)
            dot_x = center[0] + radius * math.cos(angle)
            dot_y = center[1] + radius * math.sin(angle)
            dot_size = random.uniform(3, 6)
        
            dc.SetBrush(wx.Brush(vegetation_color))
            dc.SetPen(wx.Pen(vegetation_color))
            dc.DrawCircle(int(dot_x), int(dot_y), int(dot_size))

        return swamp_points
