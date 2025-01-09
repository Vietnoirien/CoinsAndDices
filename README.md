# 🎲 CoinsAndDices: Where Chance Meets Innovation

> "Fortune favors the prepared mind" - Louis Pasteur

Dive into the fascinating world of probability with CoinsAndDices, a state-of-the-art simulation platform that brings ancient games of chance into the digital age. Powered by cutting-edge GPU acceleration and an elegant interface, this Python masterpiece transforms simple probability into an engaging experience.

## ✨ What Makes It Special

🚀 **Lightning-Fast Performance**
- Harness the power of CUDA-enabled GPUs to simulate up to 10 million coin flips in seconds
- Optimized algorithms that make probability calculations feel like magic

🎮 **Four Unique Gaming Experiences**
1. **Coin Master** - Push the boundaries with millions of simultaneous coin flips
2. **Dice Virtuoso** - Master the classic dice notation with stunning visualizations
3. **Runebound Adventure** - Experience the thrill of the Runebound board game system
4. **Custom Dice Creator** - Design your own fate with customizable dice faces

🔍 **Deep Statistical Insights**
- Real-time tracking of probabilities
- Beautiful data visualizations
- Comprehensive statistical analysis at your fingertips

## 🌟 Perfect For

- 📚 **Students** exploring probability and statistics
- 🎲 **Game Masters** seeking a reliable digital companion
- 🔬 **Data Scientists** analyzing random distributions
- 🎮 **Board Game Enthusiasts** enhancing their gaming experience

## 💫 Features That Amaze

- **Intelligent Display Systems** that handle millions of results with grace
- **Stunning Visual Feedback** with color-coded status indicators
- **Persistent History Tracking** to analyze your probability journey
- **Seamless GPU Integration** for mind-bending performance

## 🚀 Ready to Roll?

Transform your understanding of probability with CoinsAndDices. Whether you're a casual gamer or a serious statistician, our platform offers the perfect blend of power and elegance.

[Get Started Now](#installation)

---

*CoinsAndDices: Where every roll tells a story, and every flip writes history.*

## Detailed Components

## 🎲 Coin Simulation Deep Dive

### Architecture Overview

The coin simulation module leverages PyTorch's GPU acceleration to deliver exceptional performance while maintaining memory efficiency. Here's how it works:

#### Core Components
1. **GPU-Accelerated Engine**
  - PyTorch tensor operations for parallel coin flips
  - Automatic device selection (CUDA/CPU)
  - Batch processing of 1M flips per iteration

2. **Adaptive Display System**
  - Virtual mode for datasets > 1M flips
  - Progressive loading with 10K batch updates
  - Memory-efficient sequence formatting
  - Real-time statistical tracking

3. **Performance Optimizations**
  - 100ms throttled UI updates
  - Batched result processing
  - Lazy loading for large datasets
  - Efficient memory management

#### Key Features

1. **Smart Display Modes**
  - Quick view: Summary with first/last 1000 results
  - Full view: Complete sequence with progress tracking
  - Virtual mode: For datasets exceeding 1M flips

2. **Real-time Statistics**
  - Running totals for heads/tails
  - Percentage calculations
  - Sequence formatting (15-30 items per line)

3. **Progress Tracking**
  - Visual progress bars for large operations
  - Time remaining estimates
  - Cancellable operations

4. **Memory Management**
  - Efficient result storage
  - Batch processing to prevent memory overflow
  - Garbage collection optimization

#### Technical Specifications

- Maximum coins: 10 million per simulation
- Batch size: 1 million for GPU processing
- Update interval: 100ms for UI refresh
- Display threshold: 1M results for virtual mode
- Sample size: 1000 results for quick view

## 🎲 Standard Dice Deep Dive

### Architecture Overview

The standard dice module combines powerful GPU computation with flexible dice notation parsing to create a versatile and high-performance dice rolling system.

#### Core Components
1. **Advanced Dice Engine**
  - Support for standard (XdY) and scientific notation
  - Multi-dice batch processing
  - Parallel GPU computation for massive rolls
  - Automatic float/int handling for large numbers

2. **Multi-Mode Display System**
  - Full Mode: Complete result visualization
  - Sample Mode: Statistical sampling for large datasets
  - Statistics Mode: Comprehensive analysis view
  - Virtual mode with progressive loading

3. **Performance Architecture**
  - Batch processing (10K dice per iteration)
  - Memory-efficient result handling
  - Throttled display updates
  - Dynamic UI scaling

#### Key Features

1. **Intelligent Display Modes**
  - Full sequence viewing with progress tracking
  - Statistical sampling for massive datasets
  - Real-time calculation updates
  - Adaptive formatting based on result size

2. **Statistical Analysis**
  - Sum totals and averages
  - Standard deviation calculation
  - Min/Max tracking
  - Distribution analysis

3. **Progress Management**
  - Visual progress indication
  - Batch-based updates
  - Cancellable operations
  - Memory usage optimization

4. **Export Capabilities**
  - CSV export for large datasets
  - Formatted result saving
  - Statistical summary export
  - Raw data extraction

#### Technical Specifications

- Maximum dice: 1 million per roll
- Maximum sides: 1 billion (scientific notation)
- Batch size: 10,000 for GPU processing
- Display threshold: 10,000 results for virtual mode
- Update interval: 100ms for UI refresh

### 3. Custom Dice System (CustomDiceFrame)
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
  
### 4. Runebound Game System (RuneboundFrame)
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


## Installation
1. Clone the repository and switch to the optimization branch:

git clone https://github.com/Vietnoirien/CoinsAndDices.git
cd CoinsAndDices
git checkout feature/torch-optimization

2. Install the required packages:

pip install -r requirements.txt


## Usage
- Launch the application:

python -m project.py

