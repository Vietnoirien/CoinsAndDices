import time
from typing import List, Tuple, Optional, Union, Dict, Literal
from .game_history import GameHistory
import wx
import wx.grid
import torch
import re
import statistics
from enum import Enum
from .constants import (
    STANDARD_DICE_FRAME_SIZE, MAX_DICE, MAX_SIDES,
    MAX_ROLLS_PER_LINE, GRID_COLUMNS, DICE_BATCH_SIZE
)

class ViewMode(Enum):
    FULL = "Full"
    SAMPLE = "Sample"
    STATISTICS = "Statistics"

class StandardDiceFrame(wx.Frame):
    """A frame for rolling and displaying standard dice results with GPU acceleration.
    
    Handles large-scale dice rolls with multiple display modes and progressive loading.
    
    Attributes:
        panel (wx.Panel): Main panel containing UI elements
        dice_input (wx.TextCtrl): Input control for dice notation
        grid (wx.grid.Grid): Grid displaying results and statistics
        device (torch.device): GPU device if available, otherwise CPU
        view_mode (wx.Choice): Control for selecting result display mode
        LARGE_RESULT_THRESHOLD (int): Threshold for switching to summary mode
    """
    
    LARGE_RESULT_THRESHOLD: int = 10000

    def __init__(self) -> None:
        super().__init__(
            parent=None,
            title='Lanceur de Dés Standards (GPU Edition)',
            size=STANDARD_DICE_FRAME_SIZE
        )
        self.device: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.panel: wx.Panel
        self.dice_input: wx.TextCtrl
        self.grid: wx.grid.Grid
        self.view_mode: wx.Choice
        self.current_rolls: List[Union[int, float]] = []
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize and setup all UI components including view mode selector."""
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Input controls
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dice_input = wx.TextCtrl(self.panel, size=(300, -1))
        input_sizer.Add(
            wx.StaticText(self.panel, label="Notation (ex: 2d6, 3d1e6):"),
            0, wx.ALL|wx.CENTER, 5
        )
        input_sizer.Add(self.dice_input, 1, wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # View mode selector
        view_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.view_mode = wx.Choice(
            self.panel,
            choices=[mode.value for mode in ViewMode]
        )
        self.view_mode.SetSelection(0)
        self.view_mode.Bind(wx.EVT_CHOICE, self.on_view_mode_change)
        view_sizer.Add(
            wx.StaticText(self.panel, label="Mode d'affichage:"),
            0, wx.ALL|wx.CENTER, 5
        )
        view_sizer.Add(self.view_mode, 0, wx.ALL, 5)
        main_sizer.Add(view_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Roll button
        roll_btn = wx.Button(self.panel, label="Lancer les dés")
        roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_dice)
        main_sizer.Add(roll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        self.setup_grid()
        main_sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        
        # Export button for large results
        export_btn = wx.Button(self.panel, label="Exporter les résultats")
        export_btn.Bind(wx.EVT_BUTTON, self.on_export_results)
        main_sizer.Add(export_btn, 0, wx.ALL|wx.CENTER, 5)
        
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def generate_statistical_summary(self, rolls: List[Union[int, float]]) -> str:
        """Generate a comprehensive statistical summary of roll results.
        
        Args:
            rolls: List of dice roll results
            
        Returns:
            Formatted string containing statistical summary
        """
        return (
            f"Total Rolls: {len(rolls):,}\n"
            f"Average: {statistics.mean(rolls):.2f}\n"
            f"Median: {statistics.median(rolls):.2f}\n"
            f"Std Dev: {statistics.stdev(rolls):.2f}\n"
            f"Min: {min(rolls):.2f}\n"
            f"Max: {max(rolls):.2f}"
        )

    def summarize_large_results(
        self,
        rolls: List[Union[int, float]],
        threshold: int = 1000
    ) -> str:
        """Create a summary for large result sets with sampling.
        
        Args:
            rolls: List of dice roll results
            threshold: Maximum number of results to display in full
            
        Returns:
            Formatted string containing summarized results
        """
        if len(rolls) > threshold:
            sample_size = min(100, len(rolls))
            sampled_rolls = rolls[:sample_size]
            return (
                f"Sample of first {sample_size} results:\n" +
                self.format_rolls_display(sampled_rolls) +
                f"\n... and {len(rolls) - sample_size} more results"
            )
        return self.format_rolls_display(rolls)

    import time

    def display_results_progressively(
        self,
        rolls: List[Union[int, float]],
        row: int,
        batch_size: int = 10000,
        virtual_threshold: int = 1_000_000
    ) -> None:
        """Display roll results progressively with virtual mode for large datasets.
    
        Implements an efficient display strategy:
        - For datasets > virtual_threshold: Shows summary with first/last sections
        - For smaller datasets: Uses batched progressive loading with throttling
    
        Args:
            rolls: List of dice roll results to display
            row: Grid row index to update
            batch_size: Number of results to process per batch for regular display
            virtual_threshold: Size threshold to switch to virtual display mode
        """
        def create_virtual_display(
            data: List[Union[int, float]], 
            sample_size: int = 1000
        ) -> str:
            """Create a summarized view for very large datasets.

            Args:
                data: Complete list of roll results
                sample_size: Number of entries to show at start and end
        
            Returns:
                str: Formatted string containing the virtual display summary
            """
            return (
                f"Total entries: {len(data):,}\n\n"
                f"First {sample_size} results:\n"
                f"{self.format_rolls_display(data[:sample_size])}\n\n"
                f"[... {len(data) - 2*sample_size:,} entries ...]\n\n"
                f"Last {sample_size} results:\n"
                f"{self.format_rolls_display(data[-sample_size:])}"
            )    
        
        def update_cell(
            batch: List[Union[int, float]], 
            is_first: bool = False
        ) -> None:
            """Update grid cell with new batch of results.
        
            Args:
                batch: List of results to append to display
                is_first: Flag indicating if this is the first batch
            """
            if is_first:
                new_value: str = self.format_rolls_display(batch)
            else:
                current_value: str = self.grid.GetCellValue(row, GRID_COLUMNS['DETAILS'])
                new_value: str = (current_value + "\n" + self.format_rolls_display(batch)).strip()
            self.grid.SetCellValue(row, GRID_COLUMNS['DETAILS'], new_value)
    
        # Use virtual mode for large datasets
        if len(rolls) > virtual_threshold:
            virtual_display: str = create_virtual_display(rolls)
            wx.CallAfter(
                self.grid.SetCellValue,
                row,
                GRID_COLUMNS['DETAILS'],
                virtual_display
            )
            return
    
        # Progressive display for smaller datasets
        update_interval: float = 0.1  # seconds
        last_update: float = time.time()
    
        # Initialize with first batch
        first_batch: List[Union[int, float]] = rolls[:batch_size]
        wx.CallAfter(update_cell, first_batch, True)
        wx.Yield()
    
        # Process remaining batches
        for i in range(batch_size, len(rolls), batch_size):
            current_time: float = time.time()
            if current_time - last_update >= update_interval:
                batch: List[Union[int, float]] = rolls[i:i + batch_size]
                wx.CallAfter(update_cell, batch)
                wx.Yield()
                last_update = current_time    
    
    def update_display(
        self,
        rolls: List[Union[int, float]],
        row: int
    ) -> None:
        """Update the grid display based on current view mode.
    
        Args:
            rolls: List of dice roll results
            row: Grid row to update
        """
        # Ensure grid has enough rows
        if self.grid.GetNumberRows() <= row:
            self.grid.AppendRows(1)

        # Get the selected view mode string directly
        selected_mode = self.view_mode.GetString(self.view_mode.GetSelection())
    
        # Use if/elif instead of enum conversion to prevent recursion
        if selected_mode == "Statistics":
            self.grid.SetCellValue(row, GRID_COLUMNS['DETAILS'],
                             self.generate_statistical_summary(rolls))
        elif selected_mode == "Sample":
            self.grid.SetCellValue(row, GRID_COLUMNS['DETAILS'],
                             self.summarize_large_results(rolls))
        else:  # "Full" mode
            self.display_results_progressively(rolls, row)

    def on_view_mode_change(self, event: wx.CommandEvent) -> None:
        """Handle changes in view mode selection.
        
        Args:
            event: The view mode change event
        """
        if self.current_rolls:
            self.update_display(self.current_rolls, self.grid.GetNumberRows() - 1)

    def on_export_results(self, event: wx.CommandEvent) -> None:
        """Handle export button click for saving full results.
        
        Args:
            event: The button click event
        """
        if not self.current_rolls:
            return
            
        with wx.FileDialog(
            self, "Export Results", wildcard="CSV files (*.csv)|*.csv",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    file.write("Roll Results\n")
                    for roll in self.current_rolls:
                        file.write(f"{roll}\n")
            except IOError:
                wx.LogError(f"Cannot save results to file '{pathname}'.")
                
    def setup_grid(self) -> None:
        """Setup and configure the results grid with appropriate columns."""
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(0, len(GRID_COLUMNS))
        
        column_labels: Dict[int, str] = {
            GRID_COLUMNS['NOTATION']: "Notation",
            GRID_COLUMNS['DETAILS']: "Détails des lancers",
            GRID_COLUMNS['TOTAL']: "Total",
            GRID_COLUMNS['AVERAGE']: "Moyenne",
            GRID_COLUMNS['MINMAX']: "Min/Max"
        }
        
        for col, label in column_labels.items():
            self.grid.SetColLabelValue(col, label)
            attr = wx.grid.GridCellAttr()
            attr.SetReadOnly(True)
            self.grid.SetColAttr(col, attr)
        
        self.grid.AutoSizeColumns()

    def roll_dice_gpu(self, number: int, sides: Union[int, float]) -> List[Union[int, float]]:
        """Generate random dice rolls using GPU acceleration with batch processing."""
        results = []
        remaining = number
    
        while remaining > 0:
            batch_size = min(DICE_BATCH_SIZE, remaining)
            random_tensor = torch.rand(batch_size, device=self.device)
            scaled_tensor = (random_tensor * sides).floor() + 1
            results.extend(scaled_tensor.cpu().tolist())
            remaining -= batch_size
            
        return results

    def format_rolls_display(self, rolls: List[Union[int, float]]) -> str:
        """Format the roll results for display with line breaks.
        
        Args:
            rolls: List of dice roll results
            
        Returns:
            Formatted string representation of rolls
        """
        formatted_lines: List[str] = []
        for i in range(0, len(rolls), MAX_ROLLS_PER_LINE):
            chunk = rolls[i:i + MAX_ROLLS_PER_LINE]
            if isinstance(chunk[0], float):
                line = " → ".join(f"{x:.2f}" for x in chunk)
            else:
                line = " → ".join(str(x) for x in chunk)
            formatted_lines.append(line)
        return "\n".join(formatted_lines)

    def validate_dice_notation(self, notation: str) -> bool:
        """Validate the dice notation format and constraints.
        
        Args:
            notation: Dice notation string (e.g., "2d6" or "3d1e6")
            
        Returns:
            True if valid, False otherwise
        """
        if not notation.strip():
            return False
            
        match = re.match(r'^(\d+)d((?:\d+(?:\.\d*)?)|(?:\d*\.\d+)|(?:\d+e\d+))$', notation.lower())
        if not match:
            return False
            
        num_dice: int = int(match.group(1))
        sides: float = float(match.group(2))
        
        return 0 < num_dice <= MAX_DICE and sides > 0

    def parse_dice_notation(self, notation: str) -> Optional[Tuple[int, float]]:
        """Parse the dice notation into number of dice and sides.
        
        Args:
            notation: Dice notation string (e.g., "2d6" or "3d1e6")
            
        Returns:
            Tuple of (number of dice, number of sides) or None if invalid
        """
        match = re.match(r'^(\d+)d((?:\d+(?:\.\d*)?)|(?:\d*\.\d+)|(?:\d+e\d+))$', notation.lower())
        if match:
            return int(match.group(1)), float(match.group(2))
        return None

    def on_roll_dice(self, event: wx.CommandEvent) -> None:
        """Handle the dice roll button click event with enhanced display handling.
        
        Args:
            event: The button click event
        """
        try:
            dice_notations: List[str] = self.dice_input.GetValue().split()
            
            self.grid.ClearGrid()
            if self.grid.GetNumberRows() > 0:
                self.grid.DeleteRows(0, self.grid.GetNumberRows())
            self.grid.AppendRows(len(dice_notations))
            
            for i, notation in enumerate(dice_notations):
                if not self.validate_dice_notation(notation):
                    raise ValueError(f"Invalid dice notation: {notation}")
                
                parsed = self.parse_dice_notation(notation)
                if parsed:
                    num_dice, sides = parsed
                    rolls = self.roll_dice_gpu(num_dice, sides)
                    self.current_rolls = rolls
                    
                    total = sum(rolls)
                    average = total / len(rolls)
                    
                    metadata = {
                        'notation': notation,
                        'num_dice': num_dice,
                        'sides': sides,
                        'total': total,
                        'device': str(self.device)
                    }
                    
                    self.grid.SetCellValue(i, GRID_COLUMNS['NOTATION'], notation)
                    self.update_display(rolls, i)
                    self.grid.SetCellValue(i, GRID_COLUMNS['TOTAL'], f"{total:.2f}")
                    self.grid.SetCellValue(i, GRID_COLUMNS['AVERAGE'], f"{average:.2f}")
                    self.grid.SetCellValue(
                        i,
                        GRID_COLUMNS['MINMAX'],
                        f"Min: {min(rolls):.2f} | Max: {max(rolls):.2f}"
                    )
            
            self.grid.AutoSizeRows()
            self.grid.AutoSizeColumns()
            
        except Exception as e:
            wx.MessageDialog(self, f"Erreur: {str(e)}", "Erreur").ShowModal()

def __del__(self) -> None:
    """Cleanup resources when the frame is destroyed."""
    if hasattr(self, 'grid') and self.grid:
        try:
            self.grid.Destroy()
        except:
            pass
