from typing import List, Optional, Tuple, Dict, Union
import time
import threading
import queue
import wx
import wx.grid
import torch
from .game_history import GameHistory
from .constants import *
from enum import Enum

class ViewMode(Enum):
    """Display modes for coin flip results."""
    FULL = "Full"
    SAMPLE = "Sample" 
    STATISTICS = "Statistics"

class CoinFrame(wx.Frame):
    """Enhanced hardware-adaptive coin flipping simulation with GPU optimization.
    
    Features:
    - GPU-optimized batch processing
    - Progressive display updates
    - Multiple view modes
    - Memory-efficient result handling
    
    Attributes:
        device (torch.device): GPU device if available, otherwise CPU
        result_queue (queue.Queue): Queue for async result processing
        worker_thread (Optional[threading.Thread]): Background processing thread
        grid (Optional[wx.grid.Grid]): Grid for displaying results
        current_results (List[str]): Current flip results
        view_mode (Optional[wx.Choice]): Display mode selector
    """
    
    def __init__(self) -> None:
        super().__init__(parent=None, title='Lanceur de Pièces', size=WINDOW_SIZE)
        self.device: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.result_queue: queue.Queue = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self.grid: Optional[wx.grid.Grid] = None
        self.current_results: List[str] = []
        self.view_mode: Optional[wx.Choice] = None
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize and setup all UI components including panel, controls, and grid."""
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Input controls
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.coin_input = wx.SpinCtrl(
            self.panel, 
            min=COIN_MIN_COUNT,
            max=COIN_MAX_COUNT,
            initial=1
        )
        
        input_sizer.Add(
            wx.StaticText(self.panel, label="Nombre de pièces:"), 
            0, 
            wx.ALL|wx.CENTER, 
            5
        )
        input_sizer.Add(self.coin_input, 1, wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND)
        
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
        
        # Flip button
        flip_btn = wx.Button(self.panel, label="Lancer les pièces")
        flip_btn.Bind(wx.EVT_BUTTON, self.handle_flip_coins)
        main_sizer.Add(flip_btn, 0, wx.ALL|wx.CENTER, 5)
        
        # Setup grid with proper columns
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(1, len(GRID_COLUMNS))
        
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
        
        main_sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def flip_coins_gpu(self, num_coins: int) -> List[str]:
        """Generate random coin flips using GPU acceleration with batch processing.
        
        Args:
            num_coins: Number of coins to flip
            
        Returns:
            List of coin flip results ('Pile' or 'Face')
        """
        results: List[str] = []
        remaining: int = num_coins
        
        while remaining > 0:
            batch_size: int = min(DICE_BATCH_SIZE, remaining)
            random_tensor: torch.Tensor = torch.rand(batch_size, device=self.device)
            results.extend(['Pile' if x < 0.5 else 'Face' for x in random_tensor.cpu()])
            remaining -= batch_size
            
        return results
    
    def display_results_progressively(
        self,
        results: List[str],
        row: int,
        batch_size: int = BATCH_SIZE,
        virtual_threshold: int = COIN_VIRTUAL_THRESHOLD
    ) -> None:
        def create_virtual_display(data: List[str], sample_size: int = 1000) -> str:
            return (
                f"Total flips: {len(data):,}\n\n"
                f"First {sample_size} results:\n"
                f"{' → '.join(data[:sample_size])}\n\n"
                f"[... {len(data) - 2*sample_size:,} flips ...]\n\n"
                f"Last {sample_size} results:\n"
                f"{' → '.join(data[-sample_size:])}"
            )

        def update_cell(start_idx: int, end_idx: int, is_first: bool = False) -> None:
            batch = results[start_idx:end_idx]
            if is_first:
                new_value = ' → '.join(batch)
            else:
                current_value = self.grid.GetCellValue(row, 1)
                new_value = f"{current_value} → {' → '.join(batch)}"
            
            wx.CallAfter(lambda: self.grid.SetCellValue(row, 1, new_value))
            wx.CallAfter(lambda: self.grid.AutoSizeRow(row))
            wx.WakeUpIdle()

        # Virtual mode check
        if len(results) > virtual_threshold:
            virtual_display = create_virtual_display(results)
            wx.CallAfter(self.grid.SetCellValue, row, 1, virtual_display)
            return

        # Progressive display with proper sequencing
        update_interval = 0.1
        last_update = time.time()
        
        # First batch
        update_cell(0, batch_size, True)
        
        # Subsequent batches
        for start_idx in range(batch_size, len(results), batch_size):
            current_time = time.time()
            if current_time - last_update >= update_interval:
                end_idx = min(start_idx + batch_size, len(results))
                update_cell(start_idx, end_idx)
                last_update = current_time
                time.sleep(0.01)  # Small delay to prevent UI freezing    
    
    def generate_statistical_summary(self, results: List[str]) -> str:
        """Generate a comprehensive statistical summary of flip results.
        
        Args:
            results: List of coin flip results
            
        Returns:
            Formatted string containing statistical summary
        """
        total = len(results)
        piles = results.count('Pile')
        faces = results.count('Face')
        
        return (
            f"Total Flips: {total:,}\n"
            f"Pile: {piles:,} ({(piles/total)*100:.2f}%)\n"
            f"Face: {faces:,} ({(faces/total)*100:.2f}%)\n"
            f"Ratio Pile/Face: {piles/faces:.3f}"
        )

    def update_display(self, results: List[str], row: int) -> None:
        """Update the grid display based on current view mode.
        
        Args:
            results: List of coin flip results
            row: Grid row to update
        """
        selected_mode = self.view_mode.GetString(self.view_mode.GetSelection())
        
        if selected_mode == "Statistics":
            self.grid.SetCellValue(row, 1, self.generate_statistical_summary(results))
        elif selected_mode == "Sample":
            sample_size = min(1000, len(results))
            sample_display = (
                f"Sample of first {sample_size} results:\n" +
                ' → '.join(results[:sample_size]) +
                f"\n... and {len(results) - sample_size} more results"
            )
            self.grid.SetCellValue(row, 1, sample_display)
        else:  # "Full" mode
            self.display_results_progressively(results, row)

    def handle_flip_coins(self, event: wx.CommandEvent) -> None:
        """Handle the coin flip button click event with enhanced display handling.
    
        Args:
            event: The button click event
        """
        try:
            num_coins: int = self.coin_input.GetValue()
        
            self.grid.ClearGrid()
            results = self.flip_coins_gpu(num_coins)
            self.current_results = results
        
            piles = results.count('Pile')
            faces = results.count('Face')
            # Colonne NOTATION
            self.grid.SetCellValue(0, GRID_COLUMNS['NOTATION'], f"{num_coins} pièces")

            # Colonne DETAILS - déjà géré par update_display()
            self.update_display(results, 0)

            # Colonne TOTAL
            self.grid.SetCellValue(0, GRID_COLUMNS['TOTAL'], 
                f"Pile: {piles}\nFace: {faces}")

            # Colonne AVERAGE
            self.grid.SetCellValue(0, GRID_COLUMNS['AVERAGE'],
                f"Pile: {piles/num_coins:.2%}\nFace: {faces/num_coins:.2%}")

            # Colonne MINMAX
            self.grid.SetCellValue(0, GRID_COLUMNS['MINMAX'],
                f"Ratio P/F: {piles/faces:.3f}")
            self.grid.AutoSizeColumns()
            self.grid.AutoSizeRows()
        
            # Track history
            metadata = {
                'num_coins': num_coins,
                'piles': piles,
                'faces': faces,
                'device': str(self.device)
            }
        
            from project import track_game_history
            game_event = track_game_history('coin', results, metadata)
            GameHistory.get_instance().add_event(game_event)
        
        except Exception as e:
            wx.MessageDialog(self, f"Erreur: {str(e)}", "Erreur").ShowModal()

    def on_view_mode_change(self, event: wx.CommandEvent) -> None:
        """Handle changes in view mode selection.
        
        Args:
            event: The view mode change event
        """
        if self.current_results:
            self.update_display(self.current_results, 0)

    def __del__(self) -> None:
        """Cleanup resources when the frame is destroyed."""
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()

