from .game_history import GameHistory
import wx
import wx.grid
import random
from typing import List

# Constants
WINDOW_SIZE = (800, 600)
MIN_COINS = 1
MAX_COINS = 100
INITIAL_COINS = 1
ITEMS_PER_LINE = 15

class CoinFrame(wx.Frame):
    """A frame that simulates flipping coins and displays results in a grid.
    
    Attributes:
        panel: Main panel containing UI elements
        coin_input: Input control for number of coins
        grid: Grid displaying results and statistics
    """
    
    def __init__(self) -> None:
        super().__init__(parent=None, title='Lanceur de Pièces', size=WINDOW_SIZE)
        self.init_ui()
        
    def init_ui(self) -> None:
        """Initialize and setup all UI components."""
        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Section contrôles
        coin_ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.coin_input = wx.SpinCtrl(
            self.panel, 
            min=MIN_COINS, 
            max=MAX_COINS, 
            initial=INITIAL_COINS
        )
        coin_ctrl_sizer.Add(
            wx.StaticText(self.panel, label="Nombre de pièces:"), 
            0, 
            wx.ALL|wx.CENTER, 
            5
        )
        coin_ctrl_sizer.Add(self.coin_input, 1, wx.ALL, 5)
        sizer.Add(coin_ctrl_sizer, 0, wx.EXPAND)
        
        # Bouton de lancement
        flip_btn = wx.Button(self.panel, label="Lancer les pièces")
        flip_btn.Bind(wx.EVT_BUTTON, self.handle_flip_coins)
        sizer.Add(flip_btn, 0, wx.ALL, 5)
        
        self.setup_grid()
        sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(sizer)
        self.Center()
        self.Show()

    def setup_grid(self) -> None:
        """Setup and configure the results grid."""
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(3, 2)
        self.grid.SetColLabelValue(0, "Résultat")
        self.grid.SetColLabelValue(1, "Détails")
        
        # Configuration de l'alignement et du retour à la ligne
        attr = wx.grid.GridCellAttr()
        attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        self.grid.SetColAttr(1, attr)
        
        self.grid.AutoSizeColumns()

    def format_sequence(self, results: List[str], items_per_line: int = ITEMS_PER_LINE) -> str:
        """Format the coin flip results into a readable sequence.
        
        Args:
            results: List of coin flip results ('Pile' or 'Face')
            items_per_line: Number of items to display per line
            
        Returns:
            Formatted string with coin flip sequence
        """
        formatted_lines = []
        for i in range(0, len(results), items_per_line):
            line_items = results[i:i + items_per_line]
            formatted_lines.append(" → ".join(line_items))
        return "\n".join(formatted_lines)

    def handle_flip_coins(self, event: wx.CommandEvent) -> None:
        """Handle coin flip button click event and update results.

        Args:
            event: Button click event
        """
        try:
            num_coins = self.coin_input.GetValue()
            results = ['Pile' if random.random() < 0.5 else 'Face' 
                    for _ in range(num_coins)]
    
            # Track the coin flip event
            metadata = {
                'num_coins': num_coins,
                'piles': results.count('Pile'),
                'faces': results.count('Face')
            }
            from project import track_game_history

            game_event = track_game_history('coin', results, metadata)
            GameHistory.get_instance().add_event(game_event)
    
            self.grid.ClearGrid()
    
            piles = results.count('Pile')
            faces = results.count('Face')
    
            self.grid.SetCellValue(0, 0, "Pile")
            self.grid.SetCellValue(0, 1, str(piles))
            self.grid.SetCellValue(1, 0, "Face")
            self.grid.SetCellValue(1, 1, str(faces))
            self.grid.SetCellValue(2, 0, "Séquence")
            self.grid.SetCellValue(2, 1, self.format_sequence(results))
    
            # Ajustement automatique des dimensions
            self.grid.AutoSizeColumns()
            self.grid.AutoSizeRow(2)
    
        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)