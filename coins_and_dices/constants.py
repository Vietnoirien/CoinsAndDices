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
CUSTOM_DICE_MAX_COUNT: int = 1_000_000
CUSTOM_DICE_MIN_COUNT: int = 1

# Standard Dice Constants
MAX_DICE: int = 1_000_000
MAX_SIDES: float = 1e9  # Support for billion-sided dice
MAX_ROLLS_PER_LINE: int = 30
DICE_BATCH_SIZE: int = 1_000_000  # GPU processing batch size
STANDARD_DICE_FRAME_SIZE: Tuple[int, int] = (1024, 768)

GRID_COLUMNS = {
    'NOTATION': 0,
    'DETAILS': 1,
    'TOTAL': 2,
    'AVERAGE': 3,
    'MINMAX': 4
}

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

# Coin display constants
ITEMS_PER_LINE: int = 15
BATCH_SIZE: int = 5_000_000  # Increased for better GPU utilization
COIN_UPDATE_INTERVAL: float = 0.1  # seconds
COIN_VIRTUAL_THRESHOLD: int = 1_000_000
COIN_BATCH_DISPLAY: int = 50000
COIN_BATCH_SIZE: int = 100000
COIN_SAMPLE_SIZE: int = 1000
COIN_CACHE_SIZE: int = 1_000_000  # Results caching threshold
WORKER_THREAD_SLEEP: float = 0.01  # Thread sleep interval

# Add these performance-related constants
COIN_MAX_COUNT: int = 10_000_000  # Maximum number of coins
COIN_MIN_COUNT: int = 1  # Minimum number of coins
COIN_PROGRESS_UPDATE: int = 100  # Progress dialog update interval
