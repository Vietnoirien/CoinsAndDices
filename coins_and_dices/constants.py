from typing import Tuple, List

# Window dimensions
WINDOW_SIZE: Tuple[int, int] = (1024, 768)
BUTTON_SIZE: Tuple[int, int] = (300, 60)
QUIT_BUTTON_SIZE: Tuple[int, int] = (200, 40)

# Font sizes
TITLE_FONT_SIZE: int = 24
BUTTON_FONT_SIZE: int = 12
DESCRIPTION_FONT_SIZE: int = 10

# Padding values
TITLE_PADDING: int = 20
BUTTON_PADDING: int = 10
DESCRIPTION_PADDING: int = 5

# Adding new constants for CustomDiceFrame
CUSTOM_DICE_FRAME_SIZE: Tuple[int, int] = (800, 600)
CUSTOM_DICE_RESULT_AREA_SIZE: Tuple[int, int] = (700, 400)
CUSTOM_DICE_MAX_COUNT: int = 100
CUSTOM_DICE_MIN_COUNT: int = 1

# Add these new constants for Runebound_frame
RUNEBOUND_FRAME_SIZE: Tuple[int, int] = (800, 600)
RUNEBOUND_MAX_DICE: int = 5
RUNEBOUND_MIN_DICE: int = 1
RUNEBOUND_INITIAL_DICE: int = 5


RUNEBOUND_FACES: List[List[str]] = [
    ["Marais", "Riviere"],
    ["Montagne", "Plaine", "Route"],
    ["Riviere", "Foret"],
    ["Route", "Plaine", "Colline"],
    ["Route", "Riviere"],
    ["Route", "Plaine", "Colline"]
]
