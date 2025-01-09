# CoinsAndDices

A comprehensive Python application for simulating various dice games and coin flips, featuring an intuitive wxPython GUI with specialized frames for different game mechanics.

## Detailed Components

### 1. Coin Simulation (CoinFrame)
- GPU-accelerated coin flipping using PyTorch
- Supports up to 10 million coins per flip
- Advanced display strategies:
  - Virtual mode for datasets > 1M flips with "Show All" capability
  - Progressive loading with progress tracking
  - Direct display for small datasets
  - Full sequence viewing with memory-efficient loading
- Real-time statistical tracking:
  - Individual flip results (Heads/Tails)
  - Running totals and percentages
  - Formatted sequence display with configurable items per line
- Performance optimizations:
  - Batched processing (10,000 coins per batch)
  - Memory-efficient result handling
  - Throttled UI updates (100ms interval)
  - Progress tracking for large operations
- Hardware acceleration features:
  - CUDA GPU support when available
  - Automatic CPU fallback
  - Batch size optimization
  - Memory-efficient processing

### 2. Standard Dice (StandardDiceFrame)
- Full support for standard dice notation (e.g., "2d6", "3d1e6")
- Advanced display modes:
  - Full Mode: Complete detailed results with progressive loading
  - Sample Mode: Representative sample with summary
  - Statistics Mode: Comprehensive statistical analysis
  - Virtual mode for large datasets with full view option
- Performance features:
  - Virtual display mode for >1M results
  - Progressive loading with progress tracking
  - Optimized batch processing (10,000 dice per batch)
  - Memory-efficient result handling
- Statistical Analysis:
  - Individual roll results
  - Sum totals
  - Mean and median
  - Standard deviation
  - Min/Max values
- Display optimizations:
  - Batched updates with progress indication
  - Throttled UI refresh (100ms interval)
  - Adaptive display modes
  - Full sequence access for any dataset size

### 3. Runebound Game System (RuneboundFrame)
- Specialized implementation of Runebound board game dice mechanics
- Features:
  - Custom face values and symbols
  - Dynamic reroll system:
    - Per-die reroll tracking
    - Visual state indicators
    - Reroll limitations
  - Interactive dice selection
  - Color-coded status indicators:
    - Red: Locked dice
    - Green: Selected faces
    - Blue: Available rerolls
    - Grey: Used rerolls

### 4. Custom Dice System (CustomDiceFrame)
- Complete custom dice creation and management:
  - Persistent storage of custom dice configurations
  - JSON-based saving/loading system
  - Dynamic face value configuration
- Features:
  - Create/Edit/Delete custom dice
  - Multiple dice rolls (1-100 per roll)
  - Custom face values and probabilities
  - Result history tracking
  - Detailed roll statistics

### Supporting Systems

1. **Game History Tracking**
- Comprehensive event logging
- Statistical analysis capabilities
- Session persistence
- Event metadata storage

2. **User Interface Features**
- Consistent design across all frames
- Responsive layouts
- Error handling and validation
- Interactive controls
- Automatic sizing and scrolling

3. **Data Management**
- JSON configuration storage
- Session state management
- Result caching
- Error recovery

## Technical Specifications

### Constraints
- Coin flips: 1-100 coins
- Standard dice: 1-1000 sides
- Custom dice: 1-100 dice per roll
- Runebound dice: Configurable face count
- Result display: 15-30 items per line (configurable)

### File Organization
```
project_root/
 ├── project.py # Main application entry point
 ├── test_project.py # Test suite 
 ├── requirements.txt # Project dependencies 
 ├── README.md # Project documentation 
 └── coins_and_dices/ # Main package directory 
      ├── init.py # Package initialization 
      ├── main.py # Package entry point 
      ├── config.py # Configuration settings 
      ├── constants.py # Shared constants 
      ├── handlers.py # Event handlers 
      ├── home_page.py # Main application homepage 
      ├── stats_frame.py # Statistics display frame 
      ├── coin_frame.py # Coin flipping simulation 
      ├── standard_dice_frame.py # Standard dice rolling 
      ├── runebound_frame.py # Runebound dice game 
      ├── custom_dice_frame.py # Custom dice interface 
      ├── custom_dice_dialog.py # Custom dice creation dialog 
      ├── game_history.py # Game event tracking 
      └── custom_dices.json # Custom dice configurations
```

## Installation
1. Clone the repository and switch to the optimization branch:
```
git clone https://github.com/Vietnoirien/CoinsAndDices.git
cd CoinsAndDices
git checkout feature/torch-optimization
```
2. Install the required packages:
```
pip install -r requirements.txt
```

## Usage
- Launch the application:
```
python -m project.py
```

