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
    and supports virtual mode with full sequence viewing capability.
    
    Attributes:
        panel (wx.Panel): Main panel containing UI elements
        coin_input (wx.SpinCtrl): Input control for number of coins
        grid (wx.grid.Grid): Grid displaying results and statistics
        device (torch.device): GPU device if available, otherwise CPU
        show_all_btn (wx.Button): Button for displaying full sequence in virtual mode
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
        self.show_all_btn: Optional[wx.Button] = None
        self.current_results: List[str] = []
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

    def show_full_sequence(self, results: List[str]) -> None:
        """Display the complete sequence progressively with progress tracking.
    
        Implements progressive loading of coin flip results with visual feedback.
        Updates the grid cell content in batches while maintaining performance
        and responsiveness.
    
        Args:
            results: Complete list of coin flip results to display as strings
                    where each string is either 'Pile' or 'Face'
        """
        progress_dialog: wx.ProgressDialog = wx.ProgressDialog(
            "Loading Full Sequence",
            "Processing results...",
            maximum=len(results),
            parent=self,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME
        )
    
        # Clear existing content
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
            
                # Update grid with all formatted results so far
                display_text: str = "\n".join(formatted_results)
                self.grid.SetCellValue(2, 1, display_text)
                self.grid.AutoSizeRow(2)
                self.grid.ForceRefresh()
            
                progress_dialog.Update(i)
                wx.Yield()
                last_update = current_time
    
        # Final update with any remaining results
        remaining_results: List[str] = results[i:]
        if remaining_results:
            final_batch: str = self.format_sequence(remaining_results)
            formatted_results.append(final_batch)
            final_display: str = "\n".join(formatted_results)
            self.grid.SetCellValue(2, 1, final_display)
            self.grid.AutoSizeRow(2)
            self.grid.ForceRefresh()
    
        progress_dialog.Destroy()
        
    def update_grid_results(
        self,
        results: List[str],
        batch_size: int = COIN_BATCH_SIZE,
        virtual_threshold: int = COIN_VIRTUAL_THRESHOLD
    ) -> None:
        """Update grid with optimized coin flip results and statistics.
        
        Implements efficient display strategies with full sequence viewing capability:
        - Virtual mode with expandable full view
        - Progressive loading for all datasets
        - Memory-efficient processing
        
        Args:
            results: List of coin flip results ('Pile' or 'Face')
            batch_size: Size of each processing batch for progressive loading
            virtual_threshold: Size threshold for switching to virtual display mode
        """
        def create_virtual_display(data: List[str], sample_size: int = COIN_SAMPLE_SIZE) -> str:
            """Create initial summarized view with option to expand."""
            return (
                f"Total flips: {len(data):,}\n\n"
                f"First {sample_size} results:\n"
                f"{self.format_sequence(data[:sample_size])}\n\n"
                f"[... Click 'Show All' to view {len(data) - 2*sample_size:,} more flips ...]\n\n"
                f"Last {sample_size} results:\n"
                f"{self.format_sequence(data[-sample_size:])}"
            )
        
        # Store current results for show_all functionality
        self.current_results = results
        
        # Clear and update statistics
        self.grid.ClearGrid()
        piles: int = results.count('Pile')
        faces: int = results.count('Face')
        
        # Update statistics
        self.grid.SetCellValue(0, 0, "Pile")
        self.grid.SetCellValue(0, 1, str(piles))
        self.grid.SetCellValue(1, 0, "Face")
        self.grid.SetCellValue(1, 1, str(faces))
        self.grid.SetCellValue(2, 0, "Séquence")
        
        if len(results) > virtual_threshold:
            # Create "Show All" button
            if self.show_all_btn:
                self.show_all_btn.Destroy()
            
            self.show_all_btn = wx.Button(self.panel, label="Show All Results")
            self.show_all_btn.Bind(
                wx.EVT_BUTTON, 
                lambda evt: self.show_full_sequence(self.current_results)
            )
            
            # Add button to panel
            self.panel.GetSizer().Add(self.show_all_btn, 0, wx.ALL|wx.CENTER, 5)
            self.panel.Layout()
            
            # Show initial summary
            self.grid.SetCellValue(2, 1, create_virtual_display(results))
        else:
            # Direct display for smaller datasets
            self.grid.SetCellValue(2, 1, self.format_sequence(results))
        
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