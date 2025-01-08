from typing import List, Set, Optional
from .game_history import GameHistory
import wx
import random
from .constants import (
    RUNEBOUND_FRAME_SIZE, 
    RUNEBOUND_FACES, 
    RUNEBOUND_MAX_DICE, 
    RUNEBOUND_MIN_DICE,
    RUNEBOUND_INITIAL_DICE
)

class DiceButtonHandler:
    """Handles dice button click events and state management."""
    
    @staticmethod
    def handle_click(dice_button: wx.Button, face_buttons: List[wx.Button]) -> None:
        current_color = dice_button.GetBackgroundColour()
        if current_color == wx.RED:
            dice_button.SetBackgroundColour(wx.WHITE)
            for btn in face_buttons:
                btn.Enable(True)
        else:
            dice_button.SetBackgroundColour(wx.RED)
            for btn in face_buttons:
                btn.SetBackgroundColour(wx.WHITE)
                btn.Enable(False)

class FaceButtonHandler:
    """Handles face button click events and state management."""
    
    @staticmethod
    def handle_click(current_buttons: List[wx.Button], clicked_button: wx.Button, 
                    dice_button: wx.Button) -> None:
        if not dice_button.GetBackgroundColour() == wx.RED:
            for button in current_buttons:
                button.SetBackgroundColour(wx.WHITE)
            clicked_button.SetBackgroundColour(wx.GREEN)

class RuneboundFrame(wx.Frame):
    """A frame for handling Runebound dice rolling game mechanics.
    
    This class manages the UI and logic for a dice-rolling game including
    multiple dice with different faces and reroll capabilities.
    """

    def __init__(self) -> None:
        """Initialize the Runebound frame with all necessary controls."""
        super().__init__(parent=None, title='Dés Runebound', size=RUNEBOUND_FRAME_SIZE)
        
        self.rerolls_used: Set[int] = set()
        self.dice_panels: List[wx.Panel] = []
        
        self._init_ui()
        
    def _init_ui(self) -> None:
        """Initialize all UI components and layout."""
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Initialize dice count control
        self.dice_count = self._create_dice_counter()
        dice_sizer = self._create_dice_sizer()
        main_sizer.Add(dice_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Create roll button
        roll_btn = self._create_styled_button(self.panel, "Lancer les dés", wx.WHITE)
        roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_dice)
        main_sizer.Add(roll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        # Initialize scroll area
        self.scroll = self._init_scroll_area()
        main_sizer.Add(self.scroll, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def _create_styled_button(self, parent: wx.Window, label: str, 
                            color: wx.Colour) -> wx.Button:
        """Create a button with specified style settings.
        
        Args:
            parent: Parent window for the button
            label: Button label text
            color: Background color for the button
        
        Returns:
            Configured wx.Button instance
        """
        btn = wx.Button(parent, label=label)
        btn.SetBackgroundColour(color)
        return btn

    def _create_dice_counter(self) -> wx.SpinCtrl:
        """Create and configure the dice count spinner control."""
        return wx.SpinCtrl(
            self.panel, 
            min=RUNEBOUND_MIN_DICE,
            max=RUNEBOUND_MAX_DICE,
            initial=RUNEBOUND_INITIAL_DICE
        )

    def _create_dice_sizer(self) -> wx.BoxSizer:
        """Create the sizer for dice count controls."""
        dice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dice_sizer.Add(wx.StaticText(self.panel, label="Nombre de dés:"), 
                      0, wx.ALL|wx.CENTER, 5)
        dice_sizer.Add(self.dice_count, 0, wx.ALL, 5)
        return dice_sizer

    def _init_scroll_area(self) -> wx.ScrolledWindow:
        """Initialize the scrolled window for dice results."""
        scroll = wx.ScrolledWindow(self.panel)
        scroll.SetScrollRate(0, 20)
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll.SetSizer(self.scroll_sizer)
        return scroll

    def create_dice_panel(self, index: int) -> wx.Panel:
        """Create a panel containing dice controls and face buttons.
        
        Args:
            index: The index of the die being created
        
        Returns:
            A configured wx.Panel containing the dice controls
        """
        dice_panel = wx.Panel(self.scroll)
        dice_panel.index = index
        
        # Create the sizer first and set it to the panel
        dice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dice_panel.SetSizer(dice_sizer)  # This line is crucial
        
        face = random.choice(RUNEBOUND_FACES)
        dice_panel.current_face = face
        
        dice_btn = self._create_styled_button(dice_panel, f"Dé {index+1}", wx.WHITE)
        reroll_btn = self._create_reroll_button(dice_panel, index)
        
        # Add initial buttons to sizer
        dice_sizer.Add(dice_btn, 0, wx.ALL|wx.CENTER, 5)
        dice_sizer.Add(reroll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        # Create face buttons
        buttons = self._create_face_buttons(dice_panel, face, dice_btn)
        
        dice_btn.Bind(
            wx.EVT_BUTTON, 
            lambda evt: DiceButtonHandler.handle_click(dice_btn, buttons)
        )
        
        return dice_panel
    
    def _create_reroll_button(self, parent: wx.Panel, index: int) -> wx.Button:
        """Create and configure a reroll button for a die.
        
        Args:
            parent: Parent panel for the button
            index: Index of the associated die
        
        Returns:
            Configured reroll button
        """
        reroll_btn = self._create_styled_button(parent, "↻", 
                                              wx.BLUE if index not in self.rerolls_used 
                                              else wx.LIGHT_GREY)
        reroll_btn.dice_index = index
        reroll_btn.SetForegroundColour(wx.WHITE if index not in self.rerolls_used 
                                     else wx.BLACK)
        
        if index in self.rerolls_used:
            reroll_btn.Disable()
            
        reroll_btn.Bind(wx.EVT_BUTTON, self._on_reroll)
        return reroll_btn

    def _create_face_buttons(self, parent: wx.Panel, face: List[str], 
                           dice_btn: wx.Button) -> List[wx.Button]:
        """Create buttons for each face of a die.
        
        Args:
            parent: Parent panel for the buttons
            face: List of face values
            dice_btn: Associated dice button
        
        Returns:
            List of created face buttons
        """
        buttons: List[wx.Button] = []
        for element in face:
            btn = self._create_styled_button(parent, element, wx.WHITE)
            buttons.append(btn)
            btn.Bind(
                wx.EVT_BUTTON,
                lambda evt, b=btn: FaceButtonHandler.handle_click(buttons, b, dice_btn)
            )
            parent.GetSizer().Add(btn, 0, wx.ALL, 5)
        return buttons

    def _on_reroll(self, event: wx.CommandEvent) -> None:
        """Handle reroll button clicks."""
        btn = event.GetEventObject()
        if btn.dice_index not in self.rerolls_used:
            self.rerolls_used.add(btn.dice_index)
            btn.SetBackgroundColour(wx.LIGHT_GREY)
            btn.SetForegroundColour(wx.BLACK)
            btn.Disable()
            self.reroll_single_die(btn.dice_index)

    def reroll_single_die(self, index: int) -> None:
        """Reroll a specific die and update the UI.
        
        Args:
            index: Index of the die to reroll
        """
        new_panel = self.create_dice_panel(index)
        self.scroll_sizer.Replace(self.dice_panels[index], new_panel)
        self.dice_panels[index].Destroy()
        self.dice_panels[index] = new_panel
        self.scroll_sizer.Layout()
        self.scroll.FitInside()
        
    def on_roll_dice(self, event: wx.CommandEvent) -> None:
        """Handle the roll dice button click event."""
        self.rerolls_used.clear()
        self.scroll_sizer.Clear(True)
        self.dice_panels.clear()
        
        num_dice = self.dice_count.GetValue()
        results = []
        for i in range(num_dice):
            dice_panel = self.create_dice_panel(i)
            results.append(dice_panel.current_face)
            self.dice_panels.append(dice_panel)
            self.scroll_sizer.Add(dice_panel, 0, wx.EXPAND|wx.ALL, 5)
        
        # Track Runebound dice roll
        metadata = {
            'num_dice': num_dice,
            'rerolls_available': True
        }
        from project import track_game_history

        game_event = track_game_history('runebound', results, metadata)
        GameHistory.get_instance().add_event(game_event)
        
        self.scroll_sizer.Layout()
        self.scroll.FitInside()
