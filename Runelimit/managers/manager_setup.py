from .hex_manager import HexManager
from .drawing_manager import DrawingManager
from .biome_manager import BiomeManager

def setup_managers(grid_width, grid_height):
    hex_manager = HexManager(grid_width, grid_height)
    drawing_manager = DrawingManager(hex_manager)
    biome_manager = BiomeManager(hex_manager)
    
    # Configuration des références croisées
    hex_manager.drawing_manager = drawing_manager
    hex_manager.biome_manager = biome_manager
    drawing_manager.biome_manager = biome_manager  # Ajout crucial
    biome_manager.drawing_manager = drawing_manager
    
    return hex_manager, drawing_manager, biome_manager    
