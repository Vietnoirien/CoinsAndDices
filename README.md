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
3. **Custom Dice Creator** - Design your own fate with customizable dice faces
4. **Runebound Adventure** - Experience the thrill of the Runebound board game system

## 🌟 Perfect For

- 📚 **Students** exploring probability and statistics
- 🎲 **Game Masters** seeking a reliable digital companion
- 🎮 **Board Game Enthusiasts** enhancing their gaming experience

## 💫 Features That Amaze

- **Intelligent Display Systems** that handle millions of results with grace
- **Stunning Visual Feedback** with color-coded status indicators
- **Persistent History Tracking** to analyze your probability journey
- **Seamless GPU Integration** for mind-bending performance

## 🚀 Ready to Roll?

Transform your understanding of probability with CoinsAndDices. Whether you're a casual gamer or a serious statistician, our platform offers the perfect blend of power and elegance.

[Get Started Now](#installation)

[![CoinsAndDices: A Harvard CS50P Final Project](https://img.youtube.com/vi/MWD90OtE2IA/maxresdefault.jpg)](https://www.youtube.com/watch?v=MWD90OtE2IA)

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
  - Batch processing of 100K flips per iteration

2. **Adaptive Display System**
  - Virtual mode for datasets > 1M flips
  - Progressive loading with sequence batching
  - Memory-efficient sequence formatting (12 items per line)
  - Real-time statistical tracking

3. **Performance Optimizations**
  - 50ms throttled UI updates
  - Batched result processing
  - Three view modes: Full, Sample, Statistics
  - Efficient memory management with GPU cache clearing
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
- Batch size: 100,000 for GPU processing
- Update interval: 50ms for UI refresh
- Display threshold: 1M results for virtual mode
- Sample size: 1000 results for quick view
- Items per line: 12
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

## 🎲 Custom Dice Deep Dive

### Architecture Overview

The custom dice module provides a flexible system for creating and managing user-defined dice with GPU-accelerated rolling capabilities and persistent storage.

#### Core Components
1. **Custom Dice Engine**
  - JSON-based configuration storage
  - Dynamic face value management
  - GPU-accelerated random generation
  - Batch processing optimization

2. **Configuration System**
  - Persistent dice definitions
  - Real-time configuration updates
  - Face value validation
  - Dynamic UI adaptation

3. **Performance Architecture**
  - Batch processing (1M dice per iteration)
  - Memory-efficient face storage
  - Optimized result handling
  - Throttled display updates

#### Key Features

1. **Dice Management**
  - Create/Edit/Delete custom dice
  - Dynamic face configuration
  - Value validation system
  - Real-time updates

2. **Rolling System**
  - GPU-accelerated batch rolling
  - Progressive result loading
  - Virtual mode for large datasets
  - Statistical tracking

3. **Progress Tracking**
  - Visual progress indication
  - Batch processing feedback
  - Memory usage monitoring
  - Operation cancellation

4. **Data Management**
  - JSON configuration persistence
  - Automatic saving/loading
  - Error recovery
  - Version control

#### Technical Specifications

- Maximum dice: 1 million per roll
- Face count: Unlimited per die
- Batch size: 1 million for GPU processing
- Display threshold: 1M results for virtual mode
- Update interval: 100ms for UI refresh

## 🎲 Runebound Dice Deep Dive

### Architecture Overview

The Runebound dice module implements a specialized board game system with interactive reroll mechanics and state tracking, providing an immersive gaming experience.

#### Core Components
1. **State Management Engine**
  - Per-die state tracking
  - Reroll availability monitoring
  - Face selection validation
  - Color-coded status system

2. **Interactive Display System**
  - Dynamic button states
  - Real-time visual feedback
  - Color-based state indication
  - Responsive UI updates

3. **Game Logic Architecture**
  - Custom face value handling
  - Reroll limitation enforcement
  - Selection state management
  - Event-driven updates

#### Key Features

1. **Dice Management**
  - Individual die state tracking
  - Face selection system
  - Reroll availability indicators
  - Dynamic face updates

2. **Visual Feedback System**
  - Red: Locked dice states
  - Green: Selected face values
  - Blue: Available rerolls
  - Grey: Used reroll states

3. **Game Controls**
  - Interactive dice selection
  - Face value choosing
  - Reroll management
  - State persistence

4. **Event Handling**
  - Click event management
  - State change tracking
  - Selection validation
  - History recording

#### Technical Specifications

- Maximum dice: 5 per game
- Face configurations: 6 unique sets
- Rerolls: One per die
- Update interval: Real-time
- Display mode: Interactive UI

### Supporting Systems

1. **Game History Tracking**
   - Singleton pattern implementation for global state
   - Event-based architecture with metadata capture
   - Session-wide statistics aggregation
   - Comprehensive event logging with timestamps
   - Performance metrics collection

2. **User Interface Features**
   - Centralized UI configuration management
   - Dynamic frame switching with state preservation
   - Consistent styling across all components
   - Event handler delegation pattern
   - Automated resource cleanup
   - Responsive layout management

3. **Data Management**
   - JSON-based configuration persistence
   - Real-time statistics calculation
   - Session state preservation
   - Error recovery mechanisms
   - Event metadata enrichment

4. **Analytics Engine**
   - Win/loss ratio tracking
   - Trend analysis with pattern detection
   - Session duration monitoring
   - Game type distribution analysis
   - Streak calculation system
   - Hourly activity tracking

5. **Frame Management**
   - Parent-child relationship handling
   - Resource lifecycle management
   - Event propagation system
   - State preservation between transitions
   - Memory optimization

6. **Configuration System**
   - Centralized constants management
   - Dynamic UI element configuration
   - Localization support
   - Feature toggles
   - Environment-aware settings

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

for windows you will need to install the following packages:
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```
then install the requirements:
```
pip install -r requirements.txt
```

## Usage
- Launch the application:
```
python -m project.py
```
