import torch
from coins_and_dices.constants import *
from coins_and_dices.custom_dice_frame import CustomDiceFrame
from coins_and_dices.game_history import GameHistory
from coins_and_dices.runebound_frame import DiceButtonHandler, FaceButtonHandler, RuneboundFrame
from coins_and_dices.standard_dice_frame import StandardDiceFrame
import wx
import pytest
from coins_and_dices.coin_frame import CoinFrame, ViewMode
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
    """Test initial state of StandardDiceFrame including GPU device"""
    # Existing assertions
    assert standard_dice_frame.GetTitle() == 'Lanceur de Dés Standards (GPU Edition)'
    assert isinstance(standard_dice_frame.dice_input, wx.TextCtrl)
    assert isinstance(standard_dice_frame.grid, wx.grid.Grid)
    
    # New GPU device assertions
    assert hasattr(standard_dice_frame, 'device')
    assert isinstance(standard_dice_frame.device, torch.device)
    if torch.cuda.is_available():
        assert standard_dice_frame.device.type == 'cuda'
    else:
        assert standard_dice_frame.device.type == 'cpu'

def test_dice_gpu_operations(standard_dice_frame):
    """Test GPU-accelerated dice rolling functionality"""
    # Test small batch
    results = standard_dice_frame.roll_dice_gpu(10, 6)
    assert len(results) == 10
    assert all(1 <= result <= 6 for result in results)
    
    # Test large batch
    large_roll = standard_dice_frame.roll_dice_gpu(1000, 20)
    assert len(large_roll) == 1000
    assert all(1 <= result <= 20 for result in large_roll)
    
    # Test float sides
    float_roll = standard_dice_frame.roll_dice_gpu(10, 6.5)
    assert len(float_roll) == 10
    assert all(isinstance(result, float) for result in float_roll)

def test_dice_view_modes(standard_dice_frame):
    """Test different view modes for dice results display"""
    test_rolls = [3, 4, 5, 6, 2, 1] * 10  # 60 rolls
    
    # Test Full mode
    standard_dice_frame.view_mode.SetSelection(0)  # FULL mode
    standard_dice_frame.update_display(test_rolls, 0)
    full_display = standard_dice_frame.grid.GetCellValue(0, GRID_COLUMNS['DETAILS'])
    assert '→' in full_display
    
    # Test Sample mode
    standard_dice_frame.LARGE_RESULT_THRESHOLD = 30  # Set threshold lower than test data
    standard_dice_frame.view_mode.SetSelection(1)  # SAMPLE mode
    standard_dice_frame.update_display(test_rolls, 0)
    sample_display = standard_dice_frame.grid.GetCellValue(0, GRID_COLUMNS['DETAILS'])
    
    # Verify either sample format or truncated display
    assert any([
        'Sample of first' in sample_display,
        '[...]' in sample_display,
        len(sample_display.split('→')) < len(test_rolls)
    ])
    
    # Test Statistics mode
    standard_dice_frame.view_mode.SetSelection(2)  # STATISTICS mode
    standard_dice_frame.update_display(test_rolls, 0)
    stats_display = standard_dice_frame.grid.GetCellValue(0, GRID_COLUMNS['DETAILS'])
    assert 'Average:' in stats_display
    assert 'Median:' in stats_display

def test_validate_dice_input(standard_dice_frame):
    """Test dice notation validation including scientific notation"""
    # Existing valid cases
    assert standard_dice_frame.validate_dice_notation("2d6")
    assert standard_dice_frame.validate_dice_notation("1d20")
    
    # New scientific notation cases
    assert standard_dice_frame.validate_dice_notation("1d1e6")  # Scientific notation
    assert standard_dice_frame.validate_dice_notation("2d1.5")  # Decimal notation
    
    # Invalid cases
    assert not standard_dice_frame.validate_dice_notation("")
    assert not standard_dice_frame.validate_dice_notation("d20")
    assert not standard_dice_frame.validate_dice_notation("2d")
    assert not standard_dice_frame.validate_dice_notation("0d6")

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
    results = standard_dice_frame.roll_dice_gpu(1, 6)
    assert len(results) == 1
    assert 1 <= results[0] <= 6
    
    # Test multiple dice
    results = standard_dice_frame.roll_dice_gpu(3, 20)
    assert all(1 <= result <= 20 for result in results)

def test_format_rolls_display(standard_dice_frame):
    """Test formatting of roll results"""
    rolls = [1, 2, 3, 4, 5]
    formatted = standard_dice_frame.format_rolls_display(rolls)
    assert "1 → 2 → 3 → 4 → 5" == formatted
    
    # Test line breaking for large number of rolls
    many_rolls = list(range(1, MAX_ROLLS_PER_LINE + 5))
    formatted = standard_dice_frame.format_rolls_display(many_rolls)
    assert formatted.count('\n') == 1  # Should split into two lines

def test_progressive_display_dice(standard_dice_frame):
    """Test progressive display functionality for large dice roll sets"""
    # Ensure grid has enough rows
    standard_dice_frame.grid.AppendRows(1)

    # Test with small dataset (below virtual threshold)
    small_rolls = list(range(1, 101))  # 100 rolls
    standard_dice_frame.display_results_progressively(small_rolls, 0)
    small_display = standard_dice_frame.grid.GetCellValue(0, GRID_COLUMNS['DETAILS'])

    # Account for line breaks in display formatting
    all_numbers = []
    for line in small_display.split('\n'):
        numbers = [int(n.strip()) for n in line.split('→')]
        all_numbers.extend(numbers)

    assert '→' in small_display
    assert len(all_numbers) == len(small_rolls)
    assert all_numbers == small_rolls

    # Test with dataset above virtual threshold
    large_rolls = list(range(1, 1_000_001))  # 1M rolls
    standard_dice_frame.display_results_progressively(large_rolls, 0, virtual_threshold=100_000)
    virtual_display = standard_dice_frame.grid.GetCellValue(0, GRID_COLUMNS['DETAILS'])

    # Verify first numbers are present
    assert '1 → 2' in virtual_display
    # Verify display is truncated (not showing all million numbers)
    assert len(virtual_display.split('→')) < len(large_rolls)
    
def test_handle_dice_roll(standard_dice_frame):
    """Test complete dice rolling process"""
    standard_dice_frame.dice_input.SetValue("2d6")
    event = wx.CommandEvent(wx.EVT_BUTTON.typeId)
    standard_dice_frame.on_roll_dice(event)
    
    # Verify grid has been populated
    assert standard_dice_frame.grid.GetNumberRows() == 1
    assert standard_dice_frame.grid.GetCellValue(0, GRID_COLUMNS['NOTATION']) == "2d6"
    
    # Verify numeric results - convert string to float first, then to int
    total = int(float(standard_dice_frame.grid.GetCellValue(0, GRID_COLUMNS['TOTAL'])))
    assert 2 <= total <= 12  # Valid range for 2d6

@pytest.fixture
def custom_dice_frame(app):
    frame = CustomDiceFrame()
    yield frame
    frame.Destroy()

def test_custom_dice_frame_initialization(custom_dice_frame):
    """Test initial state of CustomDiceFrame including GPU device"""
    # Basic initialization tests
    assert custom_dice_frame.GetTitle() == 'Dés Personnalisés'
    assert isinstance(custom_dice_frame.custom_dice_choice, wx.Choice)
    assert isinstance(custom_dice_frame.custom_dice_number, wx.SpinCtrl)
    
    # GPU device verification
    assert hasattr(custom_dice_frame, 'device')
    assert isinstance(custom_dice_frame.device, torch.device)
    if torch.cuda.is_available():
        assert custom_dice_frame.device.type == 'cuda'
    else:
        assert custom_dice_frame.device.type == 'cpu'

def test_custom_dice_gpu_operations(custom_dice_frame):
    """Test GPU-accelerated custom dice operations"""
    # Setup test dice
    test_dice = {
        'faces': 6,
        'values': ['A', 'B', 'C', 'D', 'E', 'F']
    }
    custom_dice_frame.custom_dices['test_dice'] = test_dice
    
    # Test small batch
    results = custom_dice_frame.roll_custom_dice('test_dice', 10)
    assert len(results) == 10
    assert all(result in test_dice['values'] for result in results)
    
    # Test large batch
    large_results = custom_dice_frame.roll_custom_dice('test_dice', 1000)
    assert len(large_results) == 1000
    assert all(result in test_dice['values'] for result in large_results)

def test_virtual_display_mode(custom_dice_frame):
    """Test virtual display mode for large result sets"""
    test_results = ['A', 'B', 'C'] * 1000  # 3000 results
    custom_dice_frame._display_virtual_results(test_results)
    
    display_text = custom_dice_frame.custom_result.GetValue()
    assert 'Total rolls: 3,000' in display_text
    assert 'First' in display_text
    assert 'Last' in display_text
    assert '[...' in display_text  # Changed to match actual implementation

def test_batch_processing_custom_dice(custom_dice_frame):
    """Test batch processing for large custom dice rolls"""
    test_dice = {
        'faces': 6,
        'values': ['1', '2', '3', '4', '5', '6']
    }
    custom_dice_frame.custom_dices['test_dice'] = test_dice
    
    # Test with batch size larger than BATCH_SIZE
    large_roll_count = BATCH_SIZE * 2 + 100
    results = custom_dice_frame.roll_custom_dice('test_dice', large_roll_count)
    
    assert len(results) == large_roll_count
    assert all(result in test_dice['values'] for result in results)

def test_statistical_display_custom(custom_dice_frame):
    """Test statistical display for custom dice results"""
    test_results = ['A'] * 60 + ['B'] * 40  # 60% A, 40% B
    custom_dice_frame.custom_result.SetValue("")
    
    # Display results with statistics
    custom_dice_frame._display_virtual_results(test_results)
    display_text = custom_dice_frame.custom_result.GetValue()
    
    assert 'Total rolls: 100' in display_text
    assert 'First' in display_text
    assert 'Last' in display_text
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
    """Test initial state of CoinFrame including GPU device and view modes"""
    # Existing assertions
    assert coin_frame.GetTitle() == 'Lanceur de Pièces'
    assert isinstance(coin_frame.coin_input, wx.SpinCtrl)
    assert coin_frame.coin_input.GetMin() == COIN_MIN_COUNT
    assert coin_frame.coin_input.GetMax() == COIN_MAX_COUNT
    assert coin_frame.coin_input.GetValue() == COIN_MIN_COUNT
    
    # New assertions for GPU device and view modes
    assert hasattr(coin_frame, 'device')
    assert isinstance(coin_frame.device, torch.device)
    assert isinstance(coin_frame.view_mode, wx.Choice)
    assert coin_frame.view_mode.GetCount() == len(ViewMode)
    assert coin_frame.view_mode.GetSelection() == 0

def test_coin_frame_gpu_operations(coin_frame):
    """Test GPU/CPU device selection and operations"""
    # Test device selection
    if torch.cuda.is_available():
        assert coin_frame.device.type == 'cuda'
    else:
        assert coin_frame.device.type == 'cpu'
    
    # Test GPU-accelerated flips
    results = coin_frame.flip_coins_gpu(100)
    assert len(results) == 100
    assert all(result in ['Pile', 'Face'] for result in results)

def test_coin_view_modes(coin_frame):
    """Test different view mode operations"""
    test_results = ['Pile', 'Face'] * 50  # 100 flips
    
    # Test Full mode
    coin_frame.view_mode.SetSelection(0)  # FULL mode
    coin_frame.update_display(test_results, 0)
    full_display = coin_frame.grid.GetCellValue(0, 1)
    assert '→' in full_display
    
    # Test Sample mode
    coin_frame.view_mode.SetSelection(1)  # SAMPLE mode
    coin_frame.update_display(test_results, 0)
    sample_display = coin_frame.grid.GetCellValue(0, 1)
    assert 'Sample of first' in sample_display
    
    # Test Statistics mode
    coin_frame.view_mode.SetSelection(2)  # STATISTICS mode
    coin_frame.update_display(test_results, 0)
    stats_display = coin_frame.grid.GetCellValue(0, 1)
    assert 'Total Flips:' in stats_display
    assert 'Ratio Pile/Face:' in stats_display

def test_batch_processing(standard_dice_frame):
    """Test batch processing for large dice rolls"""
    # Test with batch size larger than DICE_BATCH_SIZE
    large_roll_count = DICE_BATCH_SIZE * 2 + 100
    results = standard_dice_frame.roll_dice_gpu(large_roll_count, 6)
    assert len(results) == large_roll_count
    assert all(1 <= result <= 6 for result in results)

def test_format_sequence(coin_frame):
    """Test the sequence formatting logic"""
    results = ['Pile', 'Face', 'Pile', 'Face']
    
    # Ensure grid has a row
    if coin_frame.grid.GetNumberRows() == 0:
        coin_frame.grid.AppendRows(1)
    
    # Use handle_sequence_display which contains the formatting logic
    coin_frame.handle_sequence_display(results, 0)
    
    # Process pending events to allow CallAfter to complete
    wx.Yield()
    
    # Get the formatted display from the grid
    formatted_display = coin_frame.grid.GetCellValue(0, GRID_COLUMNS['DETAILS'])
    
    # Verify the formatting
    assert 'Pile → Face → Pile → Face' in formatted_display

def test_progressive_display(coin_frame):
    """Test progressive display functionality for large result sets"""
    # Ensure grid has enough rows
    coin_frame.grid.AppendRows(1)
    
    # Test with a small set first
    small_results = ['Pile', 'Face'] * 5
    
    # Process wx events to ensure display updates
    coin_frame.display_results_progressively(small_results, 0)
    wx.Yield()  # Allow UI to process pending events
    
    # Get display text after events are processed
    display_text = coin_frame.grid.GetCellValue(0, 1)
    
    # Verify display formatting
    assert '→' in display_text
    assert len(display_text.split('→')) == len(small_results)
    
    # Test with results above virtual threshold 
    large_results = ['Pile', 'Face'] * (COIN_VIRTUAL_THRESHOLD + 1)
    coin_frame.display_results_progressively(large_results, 0)
    wx.Yield()  # Allow UI to process pending events
    
    virtual_display = coin_frame.grid.GetCellValue(0, 1)
    
    # Verify virtual display format
    assert 'Total flips:' in virtual_display
    assert 'First' in virtual_display
    assert '[... ' in virtual_display and ' flips ...]' in virtual_display

def test_statistical_summary(coin_frame):
    """Test statistical summary generation and display"""
    test_results = ['Pile'] * 60 + ['Face'] * 40  # 60% Pile, 40% Face
    summary = coin_frame.generate_statistical_summary(test_results)
    
    # Verify statistical calculations
    assert 'Total Flips: 100' in summary
    assert 'Pile: 60' in summary
    assert 'Face: 40' in summary
    assert '60.00%' in summary  # Pile percentage
    assert '40.00%' in summary  # Face percentage
    assert 'Ratio Pile/Face: 1.500' in summary

def test_handle_flip_coins_enhanced(coin_frame):
    """Test enhanced coin flip handling with metadata tracking and GPU processing"""
    coin_frame.coin_input.SetValue(50)
    event = wx.CommandEvent(wx.EVT_BUTTON.typeId)
    
    # Execute flip operation
    coin_frame.handle_flip_coins(event)
    
    # Verify grid content
    assert coin_frame.grid.GetCellValue(0, GRID_COLUMNS['NOTATION']) == "50 pièces"
    
    # Verify device usage
    if torch.cuda.is_available():
        assert str(coin_frame.device) == 'cuda'
    else:
        assert str(coin_frame.device) == 'cpu'
    
    # Verify results are within expected range
    total_text = coin_frame.grid.GetCellValue(0, GRID_COLUMNS['TOTAL'])
    piles = int(total_text.split('\n')[0].split(': ')[1])
    faces = int(total_text.split('\n')[1].split(': ')[1])
    assert piles + faces == 50

def test_coin_input_limits(coin_frame):
    """Test spin control limits"""
    coin_frame.coin_input.SetValue(COIN_MIN_COUNT)
    assert coin_frame.coin_input.GetValue() == COIN_MIN_COUNT
    
    coin_frame.coin_input.SetValue(COIN_MAX_COUNT)
    assert coin_frame.coin_input.GetValue() == COIN_MAX_COUNT
    
    # Test value clamping
    coin_frame.coin_input.SetValue(COIN_MAX_COUNT + 1)
    assert coin_frame.coin_input.GetValue() == COIN_MAX_COUNT

def test_track_game_history():
    """Test game history tracking with GPU metadata"""
    
    # Test with dice metadata
    dice_metadata = {
        'dice_name': 'test_dice',
        'number': 5,
        'faces': 6,
        'device': 'cuda:0'
    }
    dice_results = [1, 2, 3, 4, 5]
    dice_event = track_game_history('custom_dice', dice_results, dice_metadata)
    
    # Verify dice event structure
    assert isinstance(dice_event, dict)
    assert dice_event['game_type'] == 'custom_dice'
    assert dice_event['result'] == dice_results
    assert isinstance(dice_event['timestamp'], datetime)
    assert dice_event['metadata'] == dice_metadata

    # Test with coin metadata
    coin_metadata = {
        'num_coins': 10,
        'piles': 6,
        'faces': 4,
        'device': 'cuda:0'
    }
    coin_results = ['Pile', 'Face'] * 5
    coin_event = track_game_history('coin', coin_results, coin_metadata)
    
    # Verify coin event structure
    assert isinstance(coin_event, dict)
    assert coin_event['game_type'] == 'coin'
    assert coin_event['result'] == coin_results
    assert isinstance(coin_event['timestamp'], datetime)
    assert coin_event['metadata'] == coin_metadata

def test_game_history():
    """Test game history tracking across the session"""
    # Reset history before test
    GameHistory._history = []
    
    # Create test events
    dice_event = track_game_history('custom_dice', [1, 2, 3], {
        'dice_name': 'test_dice',
        'number': 3,
        'faces': 6,
        'device': 'cuda:0'
    })

    coin_event = track_game_history('coin', ['Pile', 'Face'], {
        'num_coins': 2,
        'piles': 1,
        'faces': 1,
        'device': 'cuda:0'
    })

    # Add events to history
    history = GameHistory.get_instance()
    history.add_event(dice_event)
    history.add_event(coin_event)

    # Verify history contents
    stored_history = history.get_history()
    assert len(stored_history) == 2
    
    # Verify event contents
    assert stored_history[0] == dice_event
    assert stored_history[1] == coin_event
    
    # Verify event structure
    for event in stored_history:
        assert 'timestamp' in event
        assert 'game_type' in event
        assert 'result' in event
        assert 'metadata' in event

def test_history_statistics():
    """Test statistical analysis of game history"""
    # Get singleton instance and clear any existing history
    history = GameHistory.get_instance()
    history._history = []

    # Add test events with varied timestamps
    events = [
        {
            'timestamp': datetime(2024, 1, 1, 10, 0),
            'game_type': 'standard_dice',
            'result': [6],
            'metadata': {'won': True}
        },
        {
            'timestamp': datetime(2024, 1, 1, 11, 0),
            'game_type': 'coin',
            'result': ['Pile'],
            'metadata': {'won': False}
        }
    ]

    for event in events:
        history.add_event(event)

    # Generate report using the actual implementation
    report = generate_game_report(history.get_history())

    # Verify the statistics
    assert report['total_games'] == 2
    assert report['games_by_type']['standard_dice'] == 1
    assert report['games_by_type']['coin'] == 1
    assert report['session_duration'] == 60.0  # 1 hour = 60 minutes
    assert report['win_loss_ratio']['wins'] == 1
    assert report['win_loss_ratio']['losses'] == 1
    assert report['win_loss_ratio']['ratio'] == 0.5
    assert report['trends']['streak'] == 1

def test_calculate_odds():
    # Test standard dice odds
    assert calculate_odds('standard_dice', {'target': 1, 'sides': 6}) == 1/6
    # Test coin odds
    assert calculate_odds('coin', {}) == 0.5
    # Test invalid game type
    assert calculate_odds('invalid_type', {}) == 0.0

@pytest.fixture
def sample_session_data():
    return [
        {
            'timestamp': datetime(2024, 1, 1, 10, 0),
            'game_type': 'standard_dice',
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
    assert report['games_by_type']['standard_dice'] == 1
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

