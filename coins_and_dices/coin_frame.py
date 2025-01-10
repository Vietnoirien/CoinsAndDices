from typing import List, Optional, Tuple, Dict
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
    """Enhanced hardware-adaptive coin flipping simulation with optimized performance.
    
    Features:
    - Adaptive processing using available hardware (GPU/CPU)
    - Asynchronous processing using worker threads
    - Results caching for large datasets
    - Progressive UI updates
    - Memory-efficient result handling
    """
    
    def __init__(self) -> None:
        super().__init__(parent=None, title='Lanceur de Pièces', size=WINDOW_SIZE)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.result_queue: queue.Queue = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self.cache: Dict[int, List[str]] = {}
        self.grid: Optional[wx.grid.Grid] = None
        self.current_results: List[str] = []  # Store current results
        self.view_mode: Optional[wx.Choice] = None
        self.init_ui()

    def setup_grid(self) -> None:
        """Setup and configure the results grid with appropriate columns and formatting."""
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(3, 2)
        self.grid.SetColLabelValue(0, "Résultat")
        self.grid.SetColLabelValue(1, "Détails")
        
        attr = wx.grid.GridCellAttr()
        attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        self.grid.SetColAttr(1, attr)
        
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetRowLabelValue(1, "")
        self.grid.SetRowLabelValue(2, "")
        
        self.grid.AutoSizeColumns()

    def init_ui(self) -> None:
        """Initialize and setup all UI components including panel, controls, and grid."""
        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        coin_ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.coin_input = wx.SpinCtrl(
            self.panel, 
            min=COIN_MIN_COUNT,
            max=COIN_MAX_COUNT,
            initial=1
        )
        
        coin_ctrl_sizer.Add(
            wx.StaticText(self.panel, label="Nombre de pièces:"), 
            0, 
            wx.ALL|wx.CENTER, 
            5
        )
        coin_ctrl_sizer.Add(self.coin_input, 1, wx.ALL, 5)
        sizer.Add(coin_ctrl_sizer, 0, wx.EXPAND)
        
        # Add view mode selector
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
        sizer.Add(view_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        flip_btn = wx.Button(self.panel, label="Lancer les pièces")
        flip_btn.Bind(wx.EVT_BUTTON, self.handle_flip_coins)
        sizer.Add(flip_btn, 0, wx.ALL, 5)
        
        self.setup_grid()
        sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(sizer)
        self.Center()
        self.Show()

    def flip_coins_gpu(self, num_coins: int) -> List[str]:
        """Execute optimized coin flips using available hardware.
    
        Args:
            num_coins: Number of coins to flip
        
        Returns:
            List[str]: Coin flip results
        """
        if self.device.type == 'cpu':
            # Set random seed based on current time for true randomness
            torch.manual_seed(int(time.time()))
            random_tensor = torch.rand(num_coins)
            return ['Pile' if x < 0.5 else 'Face' for x in random_tensor]
        
        with torch.cuda.device(self.device):
            results_tensor = torch.bernoulli(
                torch.full((num_coins,), 0.5, device=self.device)
            )
            return ['Pile' if x else 'Face' for x in results_tensor.cpu()]
        
    def process_coins_worker(self, num_coins: int) -> None:
        """Background worker for coin processing.
        
        Handles computation asynchronously to prevent UI freezing.
        
        Args:
            num_coins: Number of coins to process
        """
        try:
            if num_coins in self.cache:
                results = self.cache[num_coins]
            else:
                results = self.flip_coins_gpu(num_coins)
                if num_coins <= COIN_CACHE_SIZE:
                    self.cache[num_coins] = results
            
            self.result_queue.put(('success', results))
        except Exception as e:
            self.result_queue.put(('error', str(e)))

    def handle_flip_coins(self, event: wx.CommandEvent) -> None:
        """Enhanced coin flip event handler with progress tracking.
        
        Implements asynchronous processing with UI feedback.
        
        Args:
            event: Button click event
        """
        num_coins: int = self.coin_input.GetValue()
        
        if self.worker_thread and self.worker_thread.is_alive():
            return
            
        progress: Optional[wx.ProgressDialog] = None
        if num_coins > BATCH_SIZE:
            progress = wx.ProgressDialog(
                "Processing", 
                "Flipping coins...",
                maximum=100,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_SMOOTH
            )
            
        def check_results() -> None:
            """Monitor worker thread and update UI with results."""
            if not self.worker_thread.is_alive():
                if progress:
                    progress.Destroy()
                    
                status, data = self.result_queue.get()
                if status == 'success':
                    self.current_results = data  # Store current results
                    self.update_grid_results(data)
                    metadata = {
                        'num_coins': num_coins,
                        'piles': data.count('Pile'),
                        'faces': data.count('Face'),
                        'device': str(self.device)
                    }
                    from project import track_game_history
                    game_event = track_game_history('coin', data, metadata)
                    GameHistory.get_instance().add_event(game_event)
                else:
                    wx.MessageBox(data, "Error", wx.OK | wx.ICON_ERROR)
                return
                
            if progress:
                progress.Pulse()
            wx.CallLater(100, check_results)

        self.worker_thread = threading.Thread(
            target=self.process_coins_worker,
            args=(num_coins,)
        )
        self.worker_thread.start()
        check_results()
        
    def update_grid_results(self, results: List[str]) -> None:
        """Optimized grid update with progressive loading.
        
        Implements efficient display strategies with batched updates.
        
        Args:
            results: Coin flip results to display
        """
        self.grid.ClearGrid()
        
        piles: int = results.count('Pile')
        faces: int = results.count('Face')
        self.grid.SetCellValue(0, 0, "Pile")
        self.grid.SetCellValue(0, 1, str(piles))
        self.grid.SetCellValue(1, 0, "Face")
        self.grid.SetCellValue(1, 1, str(faces))
        self.grid.SetCellValue(2, 0, "Séquence")
        
        if len(results) > COIN_VIRTUAL_THRESHOLD:
            self.display_virtual_results(results)
        else:
            self.display_full_results(results)
            
        self.grid.AutoSizeColumns()
        self.grid.AutoSizeRow(2)

    def display_virtual_results(self, results: List[str]) -> None:
        """Display optimized virtual view for large datasets.
        
        Args:
            results: Complete result set
        """
        sample_text: str = (
            f"Total flips: {len(results):,}\n\n"
            f"First {COIN_SAMPLE_SIZE} results:\n"
            f"{' → '.join(map(str, results[:COIN_SAMPLE_SIZE]))}\n\n"
            f"[... {len(results) - 2*COIN_SAMPLE_SIZE:,} more flips ...]\n\n"
            f"Last {COIN_SAMPLE_SIZE} results:\n"
            f"{' → '.join(map(str, results[-COIN_SAMPLE_SIZE:]))}"
        )
        self.grid.SetCellValue(2, 1, sample_text)

    def format_sequence(self, results: List[str], items_per_line: int = ITEMS_PER_LINE) -> str:
        """Format the coin flip results into a readable sequence with line breaks.

        Args:
            results: List of coin flip results
            items_per_line: Number of items to display per line
    
        Returns:
            str: Formatted string with coin flip sequence
        """
        formatted_lines: List[str] = []
        for i in range(0, len(results), items_per_line):
            line_items = results[i:i + items_per_line]
            formatted_lines.append(" → ".join(line_items))
        return "\n".join(formatted_lines)

    def display_full_results(self, results: List[str]) -> None:
        """Display complete results with batched updates for smaller datasets.

        Args:
            results: List of coin flip results to display
        """
        if len(results) > COIN_VIRTUAL_THRESHOLD:
            self.show_full_sequence(results)
        else:
            formatted_text = []
            for i in range(0, len(results), COIN_BATCH_DISPLAY):
                batch = results[i:i + COIN_BATCH_DISPLAY]
                formatted_text.append(" → ".join(batch))
    
            self.grid.SetCellValue(2, 1, "\n".join(formatted_text))

    def show_full_sequence(self, results: List[str]) -> None:
        """Display the complete sequence progressively with progress tracking.

        Args:
            results: Complete list of coin flip results
        """
        progress_dialog: wx.ProgressDialog = wx.ProgressDialog(
            "Loading Full Sequence",
            "Processing results...",
            maximum=len(results),
            parent=self,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME
        )

        self.grid.SetCellValue(2, 1, "")
        self.grid.ForceRefresh()

        formatted_results: List[str] = []
        update_interval: float = COIN_UPDATE_INTERVAL
        last_update: float = time.time()

        for i in range(0, len(results), COIN_BATCH_SIZE):
            current_time: float = time.time()
            if current_time - last_update >= update_interval:
                batch: List[str] = results[i:i + COIN_BATCH_SIZE]
                formatted_batch: str = self.format_sequence(batch)
                formatted_results.append(formatted_batch)
        
                display_text: str = "\n".join(formatted_results)
                self.grid.SetCellValue(2, 1, display_text)
                self.grid.AutoSizeRow(2)
                self.grid.ForceRefresh()
        
                progress_dialog.Update(i)
                wx.Yield()
                last_update = current_time

        remaining_results: List[str] = results[i:]
        if remaining_results:
            final_batch: str = self.format_sequence(remaining_results)
            formatted_results.append(final_batch)
            final_display: str = "\n".join(formatted_results)
            self.grid.SetCellValue(2, 1, final_display)
            self.grid.AutoSizeRow(2)
            self.grid.ForceRefresh()

        progress_dialog.Destroy()
        
    def __del__(self) -> None:
        """Cleanup resources when frame is destroyed."""
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()

    def generate_statistics(self, results: List[str]) -> str:
        """Generate statistical summary of coin flip results.
        
        Args:
            results: List of coin flip results
            
        Returns:
            str: Formatted statistical summary
        """
        total = len(results)
        piles = results.count('Pile')
        faces = results.count('Face')
        pile_percent = (piles / total) * 100
        face_percent = (faces / total) * 100
        
        return (
            f"Total Flips: {total:,}\n"
            f"Pile: {piles:,} ({pile_percent:.2f}%)\n"
            f"Face: {faces:,} ({face_percent:.2f}%)\n"
            f"Ratio Pile/Face: {pile_percent/face_percent:.3f}"
        )

    def on_view_mode_change(self, event: wx.CommandEvent) -> None:
        """Handle changes in view mode selection.
        
        Args:
            event: View mode change event
        """
        if not self.current_results:
            return
            
        selected_mode = ViewMode(self.view_mode.GetString(self.view_mode.GetSelection()))
        
        if selected_mode == ViewMode.STATISTICS:
            self.grid.SetCellValue(2, 1, self.generate_statistics(self.current_results))
        elif selected_mode == ViewMode.SAMPLE:
            self.display_virtual_results(self.current_results)
        else:  # ViewMode.FULL
            self.display_full_results(self.current_results)
        
        self.grid.AutoSizeRow(2)
