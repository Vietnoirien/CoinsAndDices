from typing import List, Optional, Tuple
import time
import wx
import wx.grid
import torch
from .game_history import GameHistory
from .constants import (
    WINDOW_SIZE, COIN_MAX_COUNT, COIN_MIN_COUNT, 
    BATCH_SIZE, ITEMS_PER_LINE, COIN_VIRTUAL_THRESHOLD,
    COIN_BATCH_SIZE, COIN_SAMPLE_SIZE, COIN_UPDATE_INTERVAL
)

class CoinFrame(wx.Frame):
    """A frame that simulates flipping coins using GPU acceleration and displays results in a grid.
    
    This implementation uses PyTorch for GPU-accelerated coin flips, enabling efficient
    processing of large numbers of coins. Results are displayed in a grid with statistics
    and supports virtual mode for large datasets.
    
    Attributes:
        panel (wx.Panel): Main panel containing UI elements
        coin_input (wx.SpinCtrl): Input control for number of coins
        grid (wx.grid.Grid): Grid displaying results and statistics
        device (torch.device): GPU device if available, otherwise CPU
    """
    
    def __init__(self) -> None:
        """Initialize the CoinFrame with GPU support."""
        super().__init__(
            parent=None, 
            title='Lanceur de Pièces (GPU Edition)', 
            size=WINDOW_SIZE
        )
        self.device: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.panel: wx.Panel
        self.coin_input: wx.SpinCtrl
        self.grid: wx.grid.Grid
        self.init_ui()
        
    def init_ui(self) -> None:
        """Initialize and setup all UI components including panel, controls, and grid."""
        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Controls section
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
        
        flip_btn = wx.Button(self.panel, label="Lancer les pièces")
        flip_btn.Bind(wx.EVT_BUTTON, self.handle_flip_coins)
        sizer.Add(flip_btn, 0, wx.ALL, 5)
        
        self.setup_grid()
        sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(sizer)
        self.Center()
        self.Show()

    def setup_grid(self) -> None:
        """Setup and configure the results grid with appropriate columns and formatting."""
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(3, 2)
        self.grid.SetColLabelValue(0, "Résultat")
        self.grid.SetColLabelValue(1, "Détails")
        
        attr = wx.grid.GridCellAttr()
        attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        self.grid.SetColAttr(1, attr)
        self.grid.AutoSizeColumns()

    def flip_coins_gpu(self, num_coins: int) -> List[str]:
        """Perform GPU-accelerated coin flips using batch processing.
        
        Args:
            num_coins: Number of coins to flip
            
        Returns:
            List[str]: List of coin flip results ('Pile' or 'Face')
        """
        results: List[str] = []
        remaining: int = num_coins
        
        while remaining > 0:
            batch_size: int = min(BATCH_SIZE, remaining)
            random_tensor: torch.Tensor = torch.rand(batch_size, device=self.device)
            batch_results: torch.Tensor = random_tensor < 0.5
            results.extend(['Pile' if x else 'Face' for x in batch_results.cpu()])
            remaining -= batch_size
            
        return results

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

    def update_grid_results(
        self,
        results: List[str],
        batch_size: int = COIN_BATCH_SIZE,
        virtual_threshold: int = COIN_VIRTUAL_THRESHOLD
    ) -> None:
        """Update grid with optimized coin flip results and statistics.
        
        Implements efficient display strategies:
        - Virtual mode for large datasets (>1M flips)
        - Progressive loading for medium datasets
        - Direct display for small datasets
        
        Args:
            results: List of coin flip results ('Pile' or 'Face')
            batch_size: Size of each processing batch for progressive loading
            virtual_threshold: Size threshold for switching to virtual display mode
        """
        def create_virtual_display(data: List[str], sample_size: int = COIN_SAMPLE_SIZE) -> str:
            """Create summarized view for very large datasets."""
            return (
                f"Total flips: {len(data):,}\n\n"
                f"First {sample_size} results:\n"
                f"{self.format_sequence(data[:sample_size])}\n\n"
                f"[... {len(data) - 2*sample_size:,} flips ...]\n\n"
                f"Last {sample_size} results:\n"
                f"{self.format_sequence(data[-sample_size:])}"
            )
        
        def update_sequence_cell(batch: List[str], is_first: bool = False) -> None:
            """Update sequence cell with new batch of results."""
            if is_first:
                new_value: str = self.format_sequence(batch)
                self.grid.SetCellValue(2, 1, new_value)
            else:
                current_value: str = self.grid.GetCellValue(2, 1)
                new_value: str = f"{current_value}\n{self.format_sequence(batch)}"
                self.grid.SetCellValue(2, 1, new_value)
        
        # Clear and update statistics
        self.grid.ClearGrid()
        piles: int = results.count('Pile')
        faces: int = results.count('Face')
        
        # Update statistics immediately
        self.grid.SetCellValue(0, 0, "Pile")
        self.grid.SetCellValue(0, 1, str(piles))
        self.grid.SetCellValue(1, 0, "Face")
        self.grid.SetCellValue(1, 1, str(faces))
        self.grid.SetCellValue(2, 0, "Séquence")
        
        # Handle display based on result size
        if len(results) > virtual_threshold:
            virtual_display: str = create_virtual_display(results)
            self.grid.SetCellValue(2, 1, virtual_display)
        else:
            # Progressive loading for medium to large datasets
            update_interval: float = COIN_UPDATE_INTERVAL
            last_update: float = time.time()
            
            # Initial batch - always display first
            first_batch: List[str] = results[:batch_size]
            update_sequence_cell(first_batch, True)
            wx.Yield()
            
            # Remaining batches with throttling
            for i in range(batch_size, len(results), batch_size):
                current_time: float = time.time()
                if current_time - last_update >= update_interval:
                    batch: List[str] = results[i:i + batch_size]
                    update_sequence_cell(batch, False)
                    wx.Yield()
                    last_update = current_time
        
        self.grid.AutoSizeColumns()
        self.grid.AutoSizeRow(2)

    def handle_flip_coins(self, event: wx.CommandEvent) -> None:
        """Handle coin flip button click event with progress tracking for large numbers.
        
        Args:
            event: Button click event
        """
        try:
            num_coins: int = self.coin_input.GetValue()
            progress: Optional[wx.ProgressDialog] = None
            
            if num_coins > BATCH_SIZE:
                progress = wx.ProgressDialog(
                    "Processing", 
                    "Flipping coins...",
                    maximum=num_coins,
                    parent=self,
                    style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
                )
            
            results: List[str] = self.flip_coins_gpu(num_coins)
            
            metadata: dict = {
                'num_coins': num_coins,
                'piles': results.count('Pile'),
                'faces': results.count('Face'),
                'device': str(self.device)
            }
            
            from project import track_game_history
            game_event = track_game_history('coin', results, metadata)
            GameHistory.get_instance().add_event(game_event)
            
            self.update_grid_results(results)
            
            if progress:
                progress.Destroy()
                
        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)