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
        virtual_threshold: int = COIN_VIRTUAL_THRESHOLD,
        values_per_line: int = ITEMS_PER_LINE
    ) -> None:
        def create_virtual_display(data: List[str], sample_size: int = 1000) -> str:
            # Format first chunk
            first_chunk = [' → '.join(data[i:i+values_per_line]) 
                                for i in range(0, min(sample_size, len(data)), values_per_line)]
            # Format last chunk
            last_chunk = [' → '.join(data[i:i+values_per_line]) 
                                for i in range(max(len(data)-sample_size, 0), len(data), values_per_line)]
            
            return (
                f"Total flips: {len(data):,}\n\n"
                f"First {sample_size} results:\n"
                f"\n".join(first_chunk) + "\n\n"
                f"[... {len(data) - 2*sample_size:,} flips ...]\n\n"
                f"Last {sample_size} results:\n"
                f"\n".join(last_chunk)
            )

        # Virtual mode check
        if len(results) > virtual_threshold:
            virtual_display = create_virtual_display(results)
            wx.CallAfter(self.grid.SetCellValue, row, 1, virtual_display)
            return

        self.handle_sequence_display(results, row)

    def handle_sequence_display(self, results: List[str], row: int) -> None:
        """Efficiently handle large sequence displays with buffering and chunking.
        
        Args:
            results: List of coin flip results
            row: Grid row to update
        """
        buffer = []
        last_update = time.time()
        
        def flush_buffer():
            if buffer:
                formatted = ' → '.join(buffer)
                current = self.grid.GetCellValue(row, GRID_COLUMNS['DETAILS'])
                new_value = f"{current}\n{formatted}" if current else formatted
                wx.CallAfter(self.grid.SetCellValue, row, GRID_COLUMNS['DETAILS'], new_value)
                wx.CallAfter(self.grid.AutoSizeRow, row)
                buffer.clear()
        
        for i, result in enumerate(results):
            buffer.append(result)
            
            # Flush buffer when full or enough time has passed
            if (len(buffer) >= ITEMS_PER_LINE or 
                time.time() - last_update >= SEQUENCE_UPDATE_INTERVAL):
                flush_buffer()
                last_update = time.time()
                
                # Allow UI to process events
                wx.YieldIfNeeded()
                time.sleep(0.001)  # Prevent UI freezing
                
        # Flush any remaining results
        flush_buffer()
        
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
        
        if selected_mode == ViewMode.FULL.value:
            self.handle_sequence_display(results, row)
        elif selected_mode == ViewMode.STATISTICS.value:
            self.grid.SetCellValue(row, 1, self.generate_statistical_summary(results))
        else:  # Sample mode
            sample_size = min(COIN_SAMPLE_SIZE, len(results))
            sample_display = (
                f"Sample of first {sample_size} results:\n" +
                ' → '.join(results[:sample_size]) +
                f"\n... and {len(results) - sample_size} more results"
            )
            self.grid.SetCellValue(row, 1, sample_display)

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

            # Colonne DETAILS - déjà géré par update_display()
            self.update_display(results, 0)

            for col in range(len(GRID_COLUMNS)):
                self.grid.SetColSize(col, self.grid.GetColSize(col) + 10)  # Add padding

            # Ensure the grid uses available space
            self.grid.ForceRefresh()
        
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

