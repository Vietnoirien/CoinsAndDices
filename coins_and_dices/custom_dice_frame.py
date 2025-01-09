import random
from .game_history import GameHistory
import wx
import json
import os
import torch
import time
from typing import Dict, List, Union, Optional, Tuple, Any
from .custom_dice_dialog import CustomDiceDialog
from .constants import (
    CUSTOM_DICE_FRAME_SIZE, 
    CUSTOM_DICE_RESULT_AREA_SIZE,
    CUSTOM_DICE_MAX_COUNT,
    CUSTOM_DICE_MIN_COUNT,
    BATCH_SIZE,
    COIN_VIRTUAL_THRESHOLD,
    COIN_SAMPLE_SIZE
)

class CustomDiceFrame(wx.Frame):
    """
    A frame for managing and rolling custom dice with GPU acceleration.
    
    This implementation uses PyTorch for GPU-accelerated dice rolls, enabling efficient
    processing of large numbers of dice. Results are displayed with virtual mode support
    for large datasets and includes progress tracking.
    
    Attributes:
        CUSTOM_DICES_FILE (str): Path to the JSON file storing custom dice configurations
        device (torch.device): GPU device if available, otherwise CPU
        panel (wx.Panel): Main panel containing UI elements
        custom_dices (Dict): Dictionary storing custom dice configurations
        custom_dice_choice (wx.Choice): Dropdown for selecting custom dice
        custom_dice_number (wx.SpinCtrl): Input for number of dice to roll
        custom_result (wx.TextCtrl): Text area for displaying results
    """
    
    CUSTOM_DICES_FILE: str = os.path.join(os.path.dirname(__file__), 'custom_dices.json')

    def __init__(self) -> None:
        """Initialize the custom dice frame with GPU support and UI components."""
        super().__init__(parent=None, title='Dés Personnalisés', size=CUSTOM_DICE_FRAME_SIZE)
        self.device: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.panel: wx.Panel = wx.Panel(self)
        self.custom_dices: Dict[str, Dict[str, Union[int, List[str]]]] = self.load_custom_dices()
        self._init_ui()
        self.Center()
        self.Show()


    def roll_custom_dice(self, dice_name: str, number: int) -> List[str]:
        """
        Roll custom dice using GPU acceleration with batch processing.
        
        Implements efficient batch processing using PyTorch for GPU-accelerated
        random number generation. Handles large numbers of rolls by processing
        in smaller batches to prevent memory issues.
        
        Args:
            dice_name: Name of the dice configuration to use
            number: Total number of dice to roll
            
        Returns:
            List[str]: List of roll results as strings
        """
        if dice_name not in self.custom_dices:
            return []

        values: List[str] = self.custom_dices[dice_name]['values']
        num_faces: int = len(values)
        results: List[str] = []
        remaining: int = number

        while remaining > 0:
            batch_size: int = min(BATCH_SIZE, remaining)
            random_tensor: torch.Tensor = torch.rand(batch_size, device=self.device)
            indices: torch.Tensor = (random_tensor * num_faces).long()
            batch_results: List[str] = [values[idx.item()] for idx in indices.cpu()]
            results.extend(batch_results)
            remaining -= batch_size

        return results

    def _display_virtual_results(self, results: List[str]) -> None:
        """
        Display results using virtual mode for large datasets.
        
        Creates a summarized view showing the first and last samples
        of results with a count of hidden items for large datasets.
        
        Args:
            results: Complete list of dice roll results
        """
        sample_text: str = (
            f"Total rolls: {len(results):,}\n\n"
            f"First {COIN_SAMPLE_SIZE} results:\n"
            f"{' → '.join(map(str, results[:COIN_SAMPLE_SIZE]))}\n\n"
            f"[... {len(results) - 2*COIN_SAMPLE_SIZE:,} more results ...]\n\n"
            f"Last {COIN_SAMPLE_SIZE} results:\n"
            f"{' → '.join(map(str, results[-COIN_SAMPLE_SIZE:]))}"
        )
        self.custom_result.SetValue(sample_text)

    def on_roll_custom_dice(self, event: wx.CommandEvent) -> None:
        """
        Handle rolling of selected custom dice with progress tracking.
        
        Implements progress tracking for large rolls and uses virtual display
        mode for large result sets. Includes error handling and game history tracking.
        
        Args:
            event: Button click event
        """
        dice_name: str = self._get_selected_dice_name()
        if not dice_name:
            return
        
        number: int = self.custom_dice_number.GetValue()
        progress: Optional[wx.ProgressDialog] = None

        try:
            if number > BATCH_SIZE:
                progress = wx.ProgressDialog(
                    "Processing",
                    "Rolling dice...",
                    maximum=number,
                    parent=self,
                    style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
                )

            results: List[str] = self.roll_custom_dice(dice_name, number)
            
            metadata: Dict[str, Any] = {
                'dice_name': dice_name,
                'number': number,
                'faces': self.custom_dices[dice_name]['faces'],
                'device': str(self.device)
            }
            
            from project import track_game_history
            game_event = track_game_history('custom_dice', results, metadata)
            GameHistory.get_instance().add_event(game_event)

            if number > COIN_VIRTUAL_THRESHOLD:
                self._display_virtual_results(results)
            else:
                self.custom_result.SetValue("\n".join(map(str, results)))

            if progress:
                progress.Destroy()

        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            
    def _init_ui(self) -> None:
        """Initialize and arrange all UI components in the frame with GPU-aware status."""
        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add GPU status indicator
        gpu_status: str = "GPU" if torch.cuda.is_available() else "CPU"
        status_text: wx.StaticText = wx.StaticText(
            self.panel, 
            label=f"Processing Mode: {gpu_status}"
        )
        main_sizer.Add(status_text, 0, wx.ALL|wx.CENTER, 5)
        
        self._add_new_dice_button(main_sizer)
        self._add_dice_controls(main_sizer)
        self._add_roll_button(main_sizer)
        self._add_results_area(main_sizer)
        self.panel.SetSizer(main_sizer)

    def _add_new_dice_button(self, sizer: wx.BoxSizer) -> None:
        """Add button for creating new custom dice."""
        new_dice_btn: wx.Button = wx.Button(self.panel, label="Créer un nouveau dé")
        new_dice_btn.Bind(wx.EVT_BUTTON, self.on_new_custom_dice)
        sizer.Add(new_dice_btn, 0, wx.ALL|wx.CENTER, 5)

    def _add_dice_controls(self, main_sizer: wx.BoxSizer) -> None:
        """Add controls for dice selection and quantity with batch-aware limits."""
        dice_ctrl_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.custom_dice_choice: wx.Choice = wx.Choice(
            self.panel, 
            choices=list(self.custom_dices.keys())
        )
        self.custom_dice_number: wx.SpinCtrl = wx.SpinCtrl(
            self.panel,
            min=CUSTOM_DICE_MIN_COUNT,
            max=CUSTOM_DICE_MAX_COUNT,
            initial=1
        )
        
        controls: List[Tuple[wx.Window, int]] = [
            (wx.StaticText(self.panel, label="Sélectionner le dé:"), 0),
            (self.custom_dice_choice, 1),
            (wx.StaticText(self.panel, label="Nombre:"), 0),
            (self.custom_dice_number, 0)
        ]
        
        for control, proportion in controls:
            dice_ctrl_sizer.Add(control, proportion, wx.ALL|wx.CENTER, 5)

        self._add_edit_delete_buttons(dice_ctrl_sizer)
        main_sizer.Add(dice_ctrl_sizer, 0, wx.EXPAND|wx.ALL, 5)

    def _add_edit_delete_buttons(self, sizer: wx.BoxSizer) -> None:
        """Add edit and delete buttons with proper event handling."""
        edit_btn: wx.Button = wx.Button(self.panel, label="Éditer")
        delete_btn: wx.Button = wx.Button(self.panel, label="Supprimer")
        
        edit_btn.Bind(wx.EVT_BUTTON, self.on_edit_custom_dice)
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_custom_dice)
        
        sizer.Add(edit_btn, 0, wx.ALL, 5)
        sizer.Add(delete_btn, 0, wx.ALL, 5)

    def _add_roll_button(self, sizer: wx.BoxSizer) -> None:
        """Add the GPU-accelerated roll button."""
        roll_btn: wx.Button = wx.Button(self.panel, label="Lancer (GPU)")
        roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_custom_dice)
        sizer.Add(roll_btn, 0, wx.ALL|wx.CENTER, 5)

    def _add_results_area(self, sizer: wx.BoxSizer) -> None:
        """Add results area with virtual mode support."""
        self.custom_result: wx.TextCtrl = wx.TextCtrl(
            self.panel,
            style=wx.TE_MULTILINE|wx.TE_READONLY,
            size=CUSTOM_DICE_RESULT_AREA_SIZE
        )
        sizer.Add(self.custom_result, 1, wx.EXPAND|wx.ALL, 5)

    def load_custom_dices(self) -> Dict[str, Dict[str, Union[int, List[str]]]]:
        """Load and validate custom dice configurations from file."""
        try:
            if os.path.exists(self.CUSTOM_DICES_FILE):
                with open(self.CUSTOM_DICES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not all(isinstance(d, dict) and 'faces' in d and 'values' in d 
                              for d in data.values()):
                        raise ValueError("Invalid dice data structure")
                    return data
            return {}
        except (json.JSONDecodeError, ValueError) as e:
            wx.MessageBox(f"Error loading dices: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            return {}

    def save_custom_dice(self, name: str, values: List[str]) -> None:
        """Save a custom dice configuration with validation."""
        if not name or not values:
            raise ValueError("Name and values must not be empty")
            
        self.custom_dices[name] = {
            'faces': len(values),
            'values': values
        }
        self._save_custom_dices()

    def _save_custom_dices(self) -> None:
        """Save all custom dice configurations with error handling."""
        try:
            with open(self.CUSTOM_DICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.custom_dices, f, indent=4)
            self._refresh_dice_list()
        except IOError as e:
            wx.MessageBox(f"Error saving dices: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def _handle_new_dice_dialog(self, dialog: CustomDiceDialog) -> None:
        """Handle new dice creation dialog with validation."""
        if dialog.ShowModal() == wx.ID_OK:
            dice_data = dialog.get_values()
            self.save_custom_dice(dice_data['name'], dice_data['faces'])
            self._refresh_dice_list(dice_data['name'])

    def _show_delete_confirmation(self, dice_name: str) -> bool:
        """Show deletion confirmation dialog with clear messaging."""
        message = f"Êtes-vous sûr de vouloir supprimer le dé '{dice_name}' ?"
        dialog = wx.MessageDialog(
            self,
            message,
            "Confirmation de suppression",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        result = dialog.ShowModal()
        dialog.Destroy()
        return result == wx.ID_YES

    def _delete_dice(self, dice_name: str) -> None:
        """Delete a custom dice with proper cleanup."""
        if dice_name in self.custom_dices:
            del self.custom_dices[dice_name]
            self._save_custom_dices()

    def _create_edit_dialog(self, dice_name: str) -> CustomDiceDialog:
        """Create pre-filled dialog for editing existing dice."""
        dialog = CustomDiceDialog(self)
        dice_data = self.custom_dices[dice_name]
        dialog.name_ctrl.SetValue(dice_name)
        dialog.faces_ctrl.SetValue(dice_data['faces'])
        dialog.update_faces_inputs(dice_data['faces'])
        
        for ctrl, value in zip(dialog.values_ctrls, dice_data['values']):
            ctrl.SetValue(value)
            
        return dialog

    def _update_dice_data(self, dice_name: str, new_data: Dict[str, Any]) -> None:
        """Update existing dice data with proper cleanup and refresh."""
        if new_data['name'] != dice_name:
            del self.custom_dices[dice_name]
        self.save_custom_dice(new_data['name'], new_data['faces'])
        self._refresh_dice_list(new_data['name'])

    def on_new_custom_dice(self, event: wx.CommandEvent) -> None:
        """Handle creation of new custom dice through dialog."""
        dialog = CustomDiceDialog(self)
        self._handle_new_dice_dialog(dialog)
        dialog.Destroy()

    def on_edit_custom_dice(self, event: wx.CommandEvent) -> None:
        """
        Handle editing of existing custom dice.
        
        Opens a pre-filled dialog with existing dice data and updates
        the configuration if changes are confirmed.
        
        Args:
            event: Button click event
        """
        dice_name = self._get_selected_dice_name()
        if not dice_name:
            return
            
        dialog = self._create_edit_dialog(dice_name)
        if dialog.ShowModal() == wx.ID_OK:
            new_data = dialog.get_values()
            self._update_dice_data(dice_name, new_data)
        dialog.Destroy()

    def on_delete_custom_dice(self, event: wx.CommandEvent) -> None:
        """
        Handle deletion of custom dice.
        
        Shows confirmation dialog before deleting selected dice configuration.
        
        Args:
            event: Button click event
        """
        dice_name = self._get_selected_dice_name()
        if not dice_name:
            return
            
        if self._show_delete_confirmation(dice_name):
            self._delete_dice(dice_name)

    def _get_selected_dice_name(self) -> str:
        """
        Get the name of the currently selected dice.
        
        Retrieves the selected dice name from the choice control,
        handling the case where no dice is selected.
        
        Returns:
            str: The selected dice name or empty string if none selected
        """
        if self.custom_dice_choice.GetSelection() == -1:
            return ""
        return self.custom_dice_choice.GetString(self.custom_dice_choice.GetSelection())
