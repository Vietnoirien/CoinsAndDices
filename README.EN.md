# Dice and Coins Roller

A complete desktop application to simulate dice and coin rolls, developed with wxPython.

## Features

### 1. Standard Dice
- Roll multiple dice simultaneously using NdX notation
- Detailed results display (total, average, min/max)
- Support for multiple dice groups

### 2. Coins
- Roll up to 100+ coins simultaneously
- Statistics display (heads/tails)
- Complete sequence visualization

### 3. Custom Dice
- Create dice with custom faces
- Permanent storage of created dice
- Edit and delete existing dice

### 4. Runebound Dice
- Simulation of special Runebound game dice
- Support for multiple rolls
- Display of obtained terrains

## Installation

1. Make sure you have Python 3.x installed
2. Install dependencies:
```bash
pip install wxPython
```

## Usage

1. Launch the application:
```bash
python wx_app.py
```

2. Navigation
- Use the main menu to access different features
- Each module has its dedicated interface with intuitive controls

## Project Structure

- `wx_app.py`: Main file containing all GUI classes
  - `HomePage`: Application main menu
  - `StandardDiceFrame`: Standard dice management
  - `CoinFrame`: Coin flip simulation
  - `CustomDiceFrame`: Custom dice interface
  - `RuneboundFrame`: Special module for Runebound

- `custom_dices.json`: Persistent storage for custom dice

## Architecture

The application is built using a modular architecture where each feature is encapsulated in its own Frame class. This allows:
- Easy maintenance
- Clear separation of responsibilities
- Simple extensibility to add new features

## Contact

For any questions or suggestions, feel free to open an issue on the project.
