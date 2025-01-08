from coins_and_dices.constants import RUNEBOUND_FACES, RUNEBOUND_INITIAL_DICE, RUNEBOUND_MAX_DICE, RUNEBOUND_MIN_DICE
from coins_and_dices.custom_dice_frame import CustomDiceFrame
from coins_and_dices.runebound_frame import DiceButtonHandler, FaceButtonHandler, RuneboundFrame
from coins_and_dices.standard_dice_frame import StandardDiceFrame
import wx
import pytest
from coins_and_dices.coin_frame import CoinFrame, MIN_COINS, MAX_COINS, INITIAL_COINS
from datetime import datetime
from project import (
    track_game_history,
    calculate_odds,
    generate_game_report,
    calculate_session_duration,
    calculate_win_loss_ratio,
    analyze_trends
)

@pytest.fixture
def runebound_frame(app):
    frame = RuneboundFrame()
    yield frame
    frame.Destroy()

def test_runebound_frame_initialization(runebound_frame):
    """Test initial state of RuneboundFrame"""
    assert runebound_frame.GetTitle() == 'Dés Runebound'
    assert isinstance(runebound_frame.dice_count, wx.SpinCtrl)
    assert runebound_frame.dice_count.GetValue() == RUNEBOUND_INITIAL_DICE
    assert runebound_frame.dice_count.GetMin() == RUNEBOUND_MIN_DICE
    assert runebound_frame.dice_count.GetMax() == RUNEBOUND_MAX_DICE
    assert len(runebound_frame.rerolls_used) == 0
    assert len(runebound_frame.dice_panels) == 0

def test_runebound_dice_roll(runebound_frame):
    """Test dice rolling functionality"""
    runebound_frame.dice_count.SetValue(3)
    event = wx.CommandEvent(wx.EVT_BUTTON.typeId)
    runebound_frame.on_roll_dice(event)
    
    assert len(runebound_frame.dice_panels) == 3
    for panel in runebound_frame.dice_panels:
        assert hasattr(panel, 'current_face')
        assert panel.current_face in RUNEBOUND_FACES

def test_runebound_reroll_mechanics(runebound_frame):
    """Test reroll functionality"""
    # Initial roll
    runebound_frame.dice_count.SetValue(1)
    roll_event = wx.CommandEvent(wx.EVT_BUTTON.typeId)
    runebound_frame.on_roll_dice(roll_event)
    
    # Get initial face and reroll button
    initial_face = runebound_frame.dice_panels[0].current_face
    reroll_button = [child for child in runebound_frame.dice_panels[0].GetChildren() 
                    if isinstance(child, wx.Button) and child.GetLabel() == "↻"][0]
    
    # Store the button index
    button_index = reroll_button.dice_index
    
    # Trigger reroll via button event
    reroll_event = wx.CommandEvent(wx.EVT_BUTTON.typeId)
    reroll_event.SetEventObject(reroll_button)
    runebound_frame._on_reroll(reroll_event)
    
    # Verify reroll was tracked
    assert button_index in runebound_frame.rerolls_used
    
    # Get the new reroll button after panel recreation
    new_reroll_button = [child for child in runebound_frame.dice_panels[0].GetChildren() 
                        if isinstance(child, wx.Button) and child.GetLabel() == "↻"][0]
    
    # Verify new button state
    assert new_reroll_button.GetBackgroundColour() == wx.LIGHT_GREY
    assert not new_reroll_button.IsEnabled()

def test_dice_button_handler(app):
    """Test DiceButtonHandler functionality"""
    parent = wx.Frame(None)
    button = wx.Button(parent)
    face_buttons = [wx.Button(parent) for _ in range(3)]
    
    DiceButtonHandler.handle_click(button, face_buttons)
    assert button.GetBackgroundColour() == wx.RED
    for btn in face_buttons:
        assert not btn.IsEnabled()
    
    parent.Destroy()

def test_face_button_handler(app):
    """Test FaceButtonHandler functionality"""
    parent = wx.Frame(None)
    dice_button = wx.Button(parent)
    face_buttons = [wx.Button(parent) for _ in range(3)]
    clicked_button = face_buttons[0]
    
    FaceButtonHandler.handle_click(face_buttons, clicked_button, dice_button)
    assert clicked_button.GetBackgroundColour() == wx.GREEN
    
    parent.Destroy()

@pytest.fixture
def standard_dice_frame(app):
    frame = StandardDiceFrame()
    yield frame
    frame.Destroy()

def test_standard_dice_frame_initialization(standard_dice_frame):
    """Test initial state of StandardDiceFrame"""
    assert standard_dice_frame.GetTitle() == 'Lanceur de Dés Standards'
    assert isinstance(standard_dice_frame.dice_input, wx.TextCtrl)
    assert isinstance(standard_dice_frame.grid, wx.grid.Grid)
    assert standard_dice_frame.grid.GetNumberCols() == len(StandardDiceFrame.GRID_COLUMNS)

def test_validate_dice_input(standard_dice_frame):
    """Test dice notation validation"""
    # Valid cases
    assert standard_dice_frame.validate_dice_input("2d6")
    assert standard_dice_frame.validate_dice_input("1d20")
    assert standard_dice_frame.validate_dice_input("10d10")
    
    # Invalid cases
    assert not standard_dice_frame.validate_dice_input("")  # Empty
    assert not standard_dice_frame.validate_dice_input("d20")  # Missing count
    assert not standard_dice_frame.validate_dice_input("2d")  # Missing sides
    assert not standard_dice_frame.validate_dice_input("0d6")  # Zero dice
    assert not standard_dice_frame.validate_dice_input(f"{StandardDiceFrame.MAX_DICE + 1}d6")  # Exceeds max dice

def test_parse_dice_notation(standard_dice_frame):
    """Test parsing of dice notation"""
    # Valid parsing
    assert standard_dice_frame.parse_dice_notation("2d6") == (2, 6)
    assert standard_dice_frame.parse_dice_notation("1d20") == (1, 20)
    
    # Invalid parsing
    assert standard_dice_frame.parse_dice_notation("invalid") is None
    assert standard_dice_frame.parse_dice_notation("d20") is None
    assert standard_dice_frame.parse_dice_notation("2d") is None

def test_roll_dice(standard_dice_frame):
    """Test dice rolling functionality"""
    # Test single die
    results = standard_dice_frame.roll_dice(1, 6)
    assert len(results) == 1
    assert 1 <= results[0] <= 6
    
    # Test multiple dice
    results = standard_dice_frame.roll_dice(3, 20)
    assert len(results) == 3
    assert all(1 <= result <= 20 for result in results)

def test_format_rolls_display(standard_dice_frame):
    """Test formatting of roll results"""
    rolls = [1, 2, 3, 4, 5]
    formatted = standard_dice_frame.format_rolls_display(rolls)
    assert "[1, 2, 3, 4, 5]" in formatted
    
    # Test line breaking for large number of rolls
    many_rolls = list(range(1, StandardDiceFrame.MAX_ROLLS_PER_LINE + 5))
    formatted = standard_dice_frame.format_rolls_display(many_rolls)
    assert formatted.count('\n') == 1  # Should split into two lines

def test_handle_dice_roll(standard_dice_frame):
    """Test complete dice rolling process"""
    standard_dice_frame.dice_input.SetValue("2d6")
    event = wx.CommandEvent(wx.EVT_BUTTON.typeId)
    standard_dice_frame.on_roll_dice(event)
    
    # Verify grid has been populated
    assert standard_dice_frame.grid.GetNumberRows() == 1
    assert standard_dice_frame.grid.GetCellValue(0, StandardDiceFrame.GRID_COLUMNS['NOTATION']) == "2d6"
    
    # Verify numeric results
    total = int(standard_dice_frame.grid.GetCellValue(0, StandardDiceFrame.GRID_COLUMNS['TOTAL']))
    assert 2 <= total <= 12  # Valid range for 2d6

@pytest.fixture
def custom_dice_frame(app):
    frame = CustomDiceFrame()
    yield frame
    frame.Destroy()

def test_custom_dice_frame_initialization(custom_dice_frame):
    """Test initial state of CustomDiceFrame"""
    assert custom_dice_frame.GetTitle() == 'Dés Personnalisés'
    assert isinstance(custom_dice_frame.custom_dice_choice, wx.Choice)
    assert isinstance(custom_dice_frame.custom_dice_number, wx.SpinCtrl)
    assert custom_dice_frame.custom_dice_number.GetValue() == 1
    assert isinstance(custom_dice_frame.custom_result, wx.TextCtrl)

def test_save_and_load_custom_dice(custom_dice_frame):
    """Test saving and loading custom dice configurations"""
    test_dice_name = "Test Dice"
    test_values = ["1", "2", "3", "4"]
    
    custom_dice_frame.save_custom_dice(test_dice_name, test_values)
    loaded_dices = custom_dice_frame.load_custom_dices()
    
    assert test_dice_name in loaded_dices
    assert loaded_dices[test_dice_name]['faces'] == 4
    assert loaded_dices[test_dice_name]['values'] == test_values

def test_roll_custom_dice(custom_dice_frame):
    """Test custom dice rolling functionality"""
    test_dice_name = "Test Dice"
    test_values = ["A", "B", "C"]
    custom_dice_frame.save_custom_dice(test_dice_name, test_values)
    
    # Test single roll
    results = custom_dice_frame.roll_custom_dice(test_dice_name, 1)
    assert len(results) == 1
    assert results[0] in test_values
    
    # Test multiple rolls
    results = custom_dice_frame.roll_custom_dice(test_dice_name, 3)
    assert len(results) == 3
    assert all(result in test_values for result in results)

def test_invalid_dice_operations(custom_dice_frame):
    """Test handling of invalid dice operations"""
    # Test rolling non-existent dice
    results = custom_dice_frame.roll_custom_dice("NonExistentDice", 1)
    assert results == []
    
    # Test saving invalid dice
    with pytest.raises(ValueError):
        custom_dice_frame.save_custom_dice("", [])

@pytest.fixture
def app():
    app = wx.App()
    yield app
    app.Destroy()

@pytest.fixture
def coin_frame(app):
    frame = CoinFrame()
    yield frame
    frame.Destroy()

def test_coin_frame_initialization(coin_frame):
    """Test initial state of CoinFrame"""
    assert coin_frame.GetTitle() == 'Lanceur de Pièces'
    assert isinstance(coin_frame.coin_input, wx.SpinCtrl)
    assert coin_frame.coin_input.GetMin() == MIN_COINS
    assert coin_frame.coin_input.GetMax() == MAX_COINS
    assert coin_frame.coin_input.GetValue() == INITIAL_COINS

def test_format_sequence(coin_frame):
    """Test the sequence formatting logic"""
    results = ['Pile', 'Face', 'Pile', 'Face']
    formatted = coin_frame.format_sequence(results, items_per_line=2)
    expected = 'Pile → Face\nPile → Face'
    assert formatted == expected

def test_handle_flip_coins(coin_frame):
    """Test coin flipping functionality"""
    coin_frame.coin_input.SetValue(10)
    # Simulate button click
    event = wx.CommandEvent(wx.EVT_BUTTON.typeId)
    coin_frame.handle_flip_coins(event)
    
    # Verify grid has been populated
    assert coin_frame.grid.GetCellValue(0, 0) == 'Pile'
    assert coin_frame.grid.GetCellValue(1, 0) == 'Face'
    
    # Verify counts are numeric and make sense
    piles = int(coin_frame.grid.GetCellValue(0, 1))
    faces = int(coin_frame.grid.GetCellValue(1, 1))
    assert piles + faces == 10

def test_coin_input_limits(coin_frame):
    """Test spin control limits"""
    coin_frame.coin_input.SetValue(MIN_COINS)
    assert coin_frame.coin_input.GetValue() == MIN_COINS
    
    coin_frame.coin_input.SetValue(MAX_COINS)
    assert coin_frame.coin_input.GetValue() == MAX_COINS
    
    # Test value clamping
    coin_frame.coin_input.SetValue(MAX_COINS + 1)
    assert coin_frame.coin_input.GetValue() == MAX_COINS

def test_track_game_history():
    result = track_game_history('dice', 6, {'bet_amount': 10})
    assert isinstance(result, dict)
    assert result['game_type'] == 'dice'
    assert result['result'] == 6
    assert isinstance(result['timestamp'], datetime)
    assert result['metadata']['bet_amount'] == 10

def test_calculate_odds():
    # Test dice odds
    assert calculate_odds('dice', {'target': 1, 'sides': 6}) == 1/6
    # Test coin odds
    assert calculate_odds('coin', {}) == 0.5
    # Test invalid game type
    assert calculate_odds('invalid', {}) == 0.0

@pytest.fixture
def sample_session_data():
    return [
        {
            'timestamp': datetime(2024, 1, 1, 10, 0),
            'game_type': 'dice',
            'result': 6,
            'metadata': {'won': True}
        },
        {
            'timestamp': datetime(2024, 1, 1, 10, 30),
            'game_type': 'coin',
            'result': 'heads',
            'metadata': {'won': False}
        }
    ]

def test_generate_game_report(sample_session_data):
    report = generate_game_report(sample_session_data)
    assert report['total_games'] == 2
    assert report['games_by_type']['dice'] == 1
    assert report['games_by_type']['coin'] == 1

def test_calculate_session_duration(sample_session_data):
    duration = calculate_session_duration(sample_session_data)
    assert duration == 30.0  # 30 minutes between games

def test_calculate_win_loss_ratio(sample_session_data):
    ratio = calculate_win_loss_ratio(sample_session_data)
    assert ratio['wins'] == 1
    assert ratio['losses'] == 1
    assert ratio['ratio'] == 0.5

def test_empty_session():
    empty_data = []
    duration = calculate_session_duration(empty_data)
    assert duration == 0.0