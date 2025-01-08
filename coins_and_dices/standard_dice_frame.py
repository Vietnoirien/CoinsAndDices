from typing import List, Tuple, Optional
from .game_history import GameHistory
import wx
import wx.grid
import random
import re
from .constants import CUSTOM_DICE_FRAME_SIZE, CUSTOM_DICE_MAX_COUNT

class StandardDiceFrame(wx.Frame):
    """A frame for rolling and displaying standard dice results."""
    
    # Grid column indices
    GRID_COLUMNS = {
        'NOTATION': 0,
        'DETAILS': 1,
        'TOTAL': 2,
        'AVERAGE': 3,
        'MINMAX': 4
    }
    
    # Dice constraints
    MAX_DICE: int = CUSTOM_DICE_MAX_COUNT
    MAX_SIDES: int = 1000
    MAX_ROLLS_PER_LINE: int = 30

    def __init__(self) -> None:
        """Initialize the StandardDiceFrame with UI components."""
        super().__init__(
            parent=None,
            title='Lanceur de Dés Standards',
            size=CUSTOM_DICE_FRAME_SIZE
        )
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize and setup all UI components."""
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Input area setup
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dice_input = wx.TextCtrl(self.panel, size=(300, -1))
        input_sizer.Add(
            wx.StaticText(self.panel, label="Notation (ex: 2d6 3d8):"),
            0, wx.ALL|wx.CENTER, 5
        )
        input_sizer.Add(self.dice_input, 1, wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Roll button setup
        roll_btn = wx.Button(self.panel, label="Lancer les dés")
        roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_dice)
        main_sizer.Add(roll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        # Results grid setup
        self.setup_grid()
        main_sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)

        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def setup_grid(self) -> None:
        """Setup the results grid with appropriate columns and formatting."""
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(0, len(self.GRID_COLUMNS))
        
        column_labels = {
            self.GRID_COLUMNS['NOTATION']: "Notation",
            self.GRID_COLUMNS['DETAILS']: "Détails des lancers",
            self.GRID_COLUMNS['TOTAL']: "Total",
            self.GRID_COLUMNS['AVERAGE']: "Moyenne",
            self.GRID_COLUMNS['MINMAX']: "Min/Max"
        }
        
        for col, label in column_labels.items():
            self.grid.SetColLabelValue(col, label)
        
        self.grid.AutoSizeColumns()

    def format_rolls_display(self, rolls: List[int]) -> str:
        """Format the roll results for display.
        
        Args:
            rolls: List of dice roll results
            
        Returns:
            Formatted string representation of rolls
        """
        formatted_lines = []
        for i in range(0, len(rolls), self.MAX_ROLLS_PER_LINE):
            chunk = rolls[i:i + self.MAX_ROLLS_PER_LINE]
            formatted_lines.append(str(chunk))
        return '\n'.join(formatted_lines)

    def validate_dice_input(self, notation: str) -> bool:
        """Validate the dice notation format and constraints.
        
        Args:
            notation: Dice notation string (e.g., "2d6")
            
        Returns:
            True if valid, False otherwise
        """
        if not notation.strip():
            return False
        if not re.match(r'^\d+d\d+$', notation.lower()):
            return False
        num_dice, sides = self.parse_dice_notation(notation)
        return (0 < num_dice <= self.MAX_DICE and 
                0 < sides <= self.MAX_SIDES)

    def parse_dice_notation(self, notation: str) -> Optional[Tuple[int, int]]:
        """Parse the dice notation into number of dice and sides.
        
        Args:
            notation: Dice notation string (e.g., "2d6")
            
        Returns:
            Tuple of (number of dice, number of sides) or None if invalid
        """
        match = re.match(r'(\d+)d(\d+)', notation.lower())
        if match:
            return int(match.group(1)), int(match.group(2))
        return None

    def roll_dice(self, number: int, sides: int) -> List[int]:
        """Generate random dice rolls.
        
        Args:
            number: Number of dice to roll
            sides: Number of sides on each die
            
        Returns:
            List of random roll results
        """
        return [random.randint(1, sides) for _ in range(number)]

    def on_roll_dice(self, event: wx.CommandEvent) -> None:
        """Handle the dice roll button click event.
        
        Args:
            event: The button click event
        """
        try:
            dice_notations = self.dice_input.GetValue().split()
            
            self.grid.ClearGrid()
            if self.grid.GetNumberRows() > 0:
                self.grid.DeleteRows(0, self.grid.GetNumberRows())
            self.grid.AppendRows(len(dice_notations))
            
            for i, notation in enumerate(dice_notations):
                if not self.validate_dice_input(notation):
                    raise ValueError(f"Invalid dice notation: {notation}")
                
                parsed = self.parse_dice_notation(notation)
                if parsed:
                    num_dice, sides = parsed
                    rolls = self.roll_dice(num_dice, sides)
                    total = sum(rolls)
                    average = total / len(rolls)
                    
                    # Track each dice roll
                    metadata = {
                        'notation': notation,
                        'num_dice': num_dice,
                        'sides': sides,
                        'total': total
                    }
                    from project import track_game_history

                    game_event = track_game_history('standard_dice', rolls, metadata)
                    GameHistory.get_instance().add_event(game_event)
                    
                    formatted_rolls = self.format_rolls_display(rolls)
                    
                    self.grid.SetCellValue(i, self.GRID_COLUMNS['NOTATION'], notation)
                    self.grid.SetCellValue(i, self.GRID_COLUMNS['DETAILS'], formatted_rolls)
                    self.grid.SetCellValue(i, self.GRID_COLUMNS['TOTAL'], str(total))
                    self.grid.SetCellValue(i, self.GRID_COLUMNS['AVERAGE'], f"{average:.2f}")
                    self.grid.SetCellValue(i, self.GRID_COLUMNS['MINMAX'],
                                         f"Min: {min(rolls)} | Max: {max(rolls)}")
                    
                    self.grid.SetCellSize(i, self.GRID_COLUMNS['DETAILS'], 1, 1)
                    attr = wx.grid.GridCellAttr()
                    attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
                    attr.SetReadOnly(True)
                    self.grid.SetRowAttr(i, attr)
            
            self.grid.AutoSizeRows()
            self.grid.AutoSizeColumns()
            
        except Exception as e:
            wx.MessageDialog(self, f"Erreur: {str(e)}", "Erreur").ShowModal()

    def __del__(self) -> None:
        """Cleanup resources when the frame is destroyed."""
        if hasattr(self, 'grid'):
            self.grid.Destroy()
