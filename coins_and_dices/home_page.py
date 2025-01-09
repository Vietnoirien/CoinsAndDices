from typing import Optional, Type
import wx
from .standard_dice_frame import StandardDiceFrame
from .coin_frame import CoinFrame
from .custom_dice_frame import CustomDiceFrame
from .runebound_frame import RuneboundFrame
from .stats_frame import StatsFrame
from .constants import (
    WINDOW_SIZE,
    BUTTON_SIZE,
    QUIT_BUTTON_SIZE,
    TITLE_FONT_SIZE,
    BUTTON_FONT_SIZE,
    DESCRIPTION_FONT_SIZE,
    TITLE_PADDING,
    BUTTON_PADDING,
    DESCRIPTION_PADDING
)
from .config import UI_CONFIG
from .handlers import FrameEventHandler

class HomePage(wx.Frame):
    """
    Main application window that serves as the entry point for the Coins and Dices application.
    
    This class creates the main menu interface with buttons to access different game features
    like standard dice, coins, custom dice, and Runebound dice.
    """

    def __init__(self) -> None:
        """
        Initialize the HomePage frame with the main UI components.
        Sets up the main window, creates the panel, and displays the interface.
        """
        super().__init__(
            parent=None, 
            title=UI_CONFIG['title'], 
            size=WINDOW_SIZE
        )
        self.panel: wx.Panel = wx.Panel(self)
        self.init_ui()
        self.Center()
        self.Show()

    def init_ui(self) -> None:
        """
        Initialize the user interface components.
        Creates the main layout, title, buttons, and quit button.
        """
        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title: wx.StaticText = wx.StaticText(self.panel, label=UI_CONFIG['welcome_text'])
        title.SetFont(wx.Font(TITLE_FONT_SIZE, wx.FONTFAMILY_DEFAULT, 
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(title, 0, wx.ALL|wx.CENTER, TITLE_PADDING)
        
        # Create buttons from configuration
        for button_config in UI_CONFIG['buttons']:
            self.create_button_panel(main_sizer, button_config)
        
        # Quit button
        quit_btn: wx.Button = wx.Button(self.panel, label="Quitter", size=QUIT_BUTTON_SIZE)
        quit_btn.Bind(wx.EVT_BUTTON, self.on_quit)
        main_sizer.Add(quit_btn, 0, wx.ALL|wx.CENTER, TITLE_PADDING)
        
        self.panel.SetSizer(main_sizer)

    def create_button_panel(self, main_sizer: wx.BoxSizer, 
                          button_config: dict) -> None:
        """
        Create a panel containing a button and its description.
        
        Args:
            main_sizer: The main sizer to add the button panel to
            button_config: Dictionary containing button configuration (label, handler, description)
        """
        button_panel: wx.Panel = wx.Panel(self.panel)
        button_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        
        btn: wx.Button = wx.Button(button_panel, label=button_config['label'], 
                                 size=BUTTON_SIZE)
        btn.SetFont(wx.Font(BUTTON_FONT_SIZE, wx.FONTFAMILY_DEFAULT, 
                          wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        handler = getattr(self, button_config['handler'])
        btn.Bind(wx.EVT_BUTTON, handler)
        
        desc: wx.StaticText = wx.StaticText(button_panel, label=button_config['description'])
        desc.SetFont(wx.Font(DESCRIPTION_FONT_SIZE, wx.FONTFAMILY_DEFAULT, 
                           wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        
        button_sizer.Add(btn, 0, wx.ALL|wx.CENTER, DESCRIPTION_PADDING)
        button_sizer.Add(desc, 0, wx.ALL|wx.CENTER, DESCRIPTION_PADDING)
        
        button_panel.SetSizer(button_sizer)
        main_sizer.Add(button_panel, 0, wx.ALL|wx.CENTER, BUTTON_PADDING)

    def open_frame(self, frame_class: Type[wx.Frame]) -> None:
        """
        Open a new frame and hide the current one.
        
        Args:
            frame_class: The class of the frame to be opened
        """
        self.Hide()
        frame: wx.Frame = frame_class()
        frame.Bind(
            wx.EVT_CLOSE, 
            FrameEventHandler.create_child_close_handler(self, frame)
        )

    def open_dice_frame(self, event: wx.CommandEvent) -> None:
        """
        Event handler for opening the standard dice frame.
        
        Args:
            event: The button click event
        """
        self.open_frame(StandardDiceFrame)

    def open_coins(self, event: wx.CommandEvent) -> None:
        """
        Event handler for opening the coin flip frame.
        
        Args:
            event: The button click event
        """
        self.open_frame(CoinFrame)

    def open_custom_dice(self, event: wx.CommandEvent) -> None:
        """
        Event handler for opening the custom dice frame.
        
        Args:
            event: The button click event
        """
        self.open_frame(CustomDiceFrame)

    def open_runebound(self, event: wx.CommandEvent) -> None:
        """
        Event handler for opening the Runebound dice frame.
        
        Args:
            event: The button click event
        """
        self.open_frame(RuneboundFrame)

    def open_stats(self, event: wx.CommandEvent) -> None:
        """
        Event handler for opening the statistics frame.
        
        Args:
            event: The button click event
        """
        self.open_frame(StatsFrame)

    def on_quit(self, event: wx.CommandEvent) -> None:
        """
        Event handler for the quit button.
        
        Args:
            event: The button click event
        """
        self.Close()

