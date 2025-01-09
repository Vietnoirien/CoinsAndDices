import wx
from typing import Dict, Any
from .constants import WINDOW_SIZE
from .game_history import GameHistory

class StatsFrame(wx.Frame):
    """
    A frame that displays game statistics and history.
    
    This class creates a window showing various statistics about the game session,
    including total throws, game type distribution, session duration, and performance metrics.
    
    Attributes:
        panel (wx.Panel): Main panel containing the statistics display
        game_history (GameHistory): Singleton instance managing game history
        stats_text (wx.TextCtrl): Text control displaying formatted statistics
    """

    def __init__(self) -> None:
        """Initialize the statistics frame with default settings."""
        super().__init__(
            parent=None,
            title="Statistiques des lancers",
            size=WINDOW_SIZE
        )
        self.panel: wx.Panel = wx.Panel(self)
        self.game_history: GameHistory = GameHistory.get_instance()
        self.stats_text: wx.TextCtrl
        self.init_ui()
        self.Center()
        self.Show()

    def init_ui(self) -> None:
        """
        Initialize the user interface components.
        
        Creates and configures the text control for displaying statistics
        within a vertical box sizer.
        """
        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.stats_text = wx.TextCtrl(
            self.panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )
        
        main_sizer.Add(self.stats_text, 1, wx.ALL | wx.EXPAND, 5)
        self.update_stats()
        self.panel.SetSizer(main_sizer)

    def update_stats(self) -> None:
        """
        Update the statistics display with current game data.
        
        Retrieves the current game history, generates a report, and formats
        the statistics into a readable text format displayed in the stats_text control.
        """
        from project import generate_game_report

        session_data: Dict[str, Any] = self.game_history.get_history()
        report: Dict[str, Any] = generate_game_report(session_data)
        
        stats_text: str = (
            f"=== Statistiques de jeu ===\n\n"
            f"Total des lancers: {report['total_games']}\n"
            f"Lancers de dés: {report['games_by_type']['standard_dice']}\n"
            f"Lancers dés personnalisés: {report['games_by_type']['custom_dice']}\n\n"
            f"Lancers de pièces: {report['games_by_type']['coin']}\n"
            f"Lancers Runebound: {report['games_by_type']['runebound']}\n"
            f"Durée de la session: {report['session_duration']} minutes\n\n"
            f"=== Performances ===\n"
            f"Victoires: {report['win_loss_ratio']['wins']}\n"
            f"Défaites: {report['win_loss_ratio']['losses']}\n"
            f"Ratio V/D: {report['win_loss_ratio']['ratio']}\n\n"
            f"Plus longue série de victoires: {report['trends']['streak']}\n"
            f"Jeu le plus joué: {report['trends']['favorite_game']}\n"
        )
        
        self.stats_text.SetValue(stats_text)
