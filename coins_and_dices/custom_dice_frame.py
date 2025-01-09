import random
from .game_history import GameHistory
import wx
import json
import os
from typing import Dict, List, Union, Optional, Tuple, Any
from .custom_dice_dialog import CustomDiceDialog
from .constants import (
    CUSTOM_DICE_FRAME_SIZE, 
    CUSTOM_DICE_RESULT_AREA_SIZE,
    CUSTOM_DICE_MAX_COUNT,
    CUSTOM_DICE_MIN_COUNT
)

class CustomDiceFrame(wx.Frame):
    """
    A frame for managing and rolling custom dice.
    
    Attributes:
        CUSTOM_DICES_FILE (str): Path to the JSON file storing custom dice configurations
        panel (wx.Panel): Main panel containing UI elements
        custom_dices (Dict): Dictionary storing custom dice configurations
    """
    
    CUSTOM_DICES_FILE: str = os.path.join(os.path.dirname(__file__), 'custom_dices.json')

    def __init__(self) -> None:
        """Initialize the custom dice frame with all UI components."""
        super().__init__(parent=None, title='Dés Personnalisés', size=CUSTOM_DICE_FRAME_SIZE)
        self.panel: wx.Panel = wx.Panel(self)
        self.custom_dices: Dict[str, Dict[str, Union[int, List[str]]]] = self.load_custom_dices()
        self._init_ui()
        self.Center()
        self.Show()

    def _init_ui(self) -> None:
        """Initialize and arrange all UI components in the frame."""
        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        self._add_new_dice_button(main_sizer)
        self._add_dice_controls(main_sizer)
        self._add_roll_button(main_sizer)
        self._add_results_area(main_sizer)
        self.panel.SetSizer(main_sizer)

    def _add_new_dice_button(self, sizer: wx.BoxSizer) -> None:
        """
        Add a button for creating new custom dice.
        
        Args:
            sizer: The sizer to add the button to
        """
        new_dice_btn: wx.Button = wx.Button(self.panel, label="Créer un nouveau dé")
        new_dice_btn.Bind(wx.EVT_BUTTON, self.on_new_custom_dice)
        sizer.Add(new_dice_btn, 0, wx.ALL|wx.CENTER, 5)

    def _add_dice_controls(self, main_sizer: wx.BoxSizer) -> None:
        """
        Add controls for dice selection and quantity.
        
        Args:
            main_sizer: The main sizer to add controls to
        """
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
        """
        Add edit and delete buttons for custom dice management.
        
        Args:
            sizer: The sizer to add the buttons to
        """
        edit_btn: wx.Button = wx.Button(self.panel, label="Éditer")
        delete_btn: wx.Button = wx.Button(self.panel, label="Supprimer")
        
        edit_btn.Bind(wx.EVT_BUTTON, self.on_edit_custom_dice)
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_custom_dice)
        
        sizer.Add(edit_btn, 0, wx.ALL, 5)
        sizer.Add(delete_btn, 0, wx.ALL, 5)

    def _add_roll_button(self, sizer: wx.BoxSizer) -> None:
        """
        Add the roll button for dice rolling.
        
        Args:
            sizer: The sizer to add the button to
        """
        roll_btn: wx.Button = wx.Button(self.panel, label="Lancer")
        roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_custom_dice)
        sizer.Add(roll_btn, 0, wx.ALL|wx.CENTER, 5)

    def _add_results_area(self, sizer: wx.BoxSizer) -> None:
        """
        Add the results text area.
        
        Args:
            sizer: The sizer to add the results area to
        """
        self.custom_result: wx.TextCtrl = wx.TextCtrl(
            self.panel,
            style=wx.TE_MULTILINE|wx.TE_READONLY,
            size=CUSTOM_DICE_RESULT_AREA_SIZE
        )
        sizer.Add(self.custom_result, 1, wx.EXPAND|wx.ALL, 5)

    def _get_selected_dice_name(self) -> str:
        """
        Get the name of the currently selected dice.
        
        Returns:
            str: The selected dice name or empty string if none selected
        """
        if self.custom_dice_choice.GetSelection() == -1:
            return ""
        return self.custom_dice_choice.GetString(self.custom_dice_choice.GetSelection())

    def _refresh_dice_list(self, selected_name: str = "") -> None:
        """
        Refresh the dice choice control with updated items.
        
        Args:
            selected_name: Optional name to select after refresh
        """
        self.custom_dice_choice.SetItems(list(self.custom_dices.keys()))
        if selected_name:
            self.custom_dice_choice.SetStringSelection(selected_name)

    def load_custom_dices(self) -> Dict[str, Dict[str, Union[int, List[str]]]]:
        """
        Load custom dice configurations from file.
        
        Returns:
            Dict containing dice configurations or empty dict if loading fails
        """
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
        """
        Save a custom dice configuration.
        
        Args:
            name: Name of the dice
            values: List of face values for the dice
            
        Raises:
            ValueError: If name or values are empty
        """
        if not name or not values:
            raise ValueError("Name and values must not be empty")
            
        self.custom_dices[name] = {
            'faces': len(values),
            'values': values
        }
        self._save_custom_dices()

    def roll_custom_dice(self, dice_name: str, number: int) -> List[str]:
        """
        Roll the specified custom dice.
        
        Args:
            dice_name: Name of the dice to roll
            number: Number of times to roll
            
        Returns:
            List of roll results
        """
        if dice_name in self.custom_dices:
            return [random.choice(self.custom_dices[dice_name]['values']) 
                   for _ in range(number)]
        return []

    # Event handlers with proper type hints
    def on_new_custom_dice(self, event: wx.CommandEvent) -> None:
        """Handle creation of new custom dice."""
        dialog = CustomDiceDialog(self)
        self._handle_new_dice_dialog(dialog)
        dialog.Destroy()

    def on_edit_custom_dice(self, event: wx.CommandEvent) -> None:
        """Handle editing of existing custom dice."""
        dice_name = self._get_selected_dice_name()
        if not dice_name:
            return
            
        dialog = self._create_edit_dialog(dice_name)
        if dialog.ShowModal() == wx.ID_OK:
            new_data = dialog.get_values()
            self._update_dice_data(dice_name, new_data)
        dialog.Destroy()

    def on_delete_custom_dice(self, event: wx.CommandEvent) -> None:
        """Handle deletion of custom dice."""
        dice_name = self._get_selected_dice_name()
        if not dice_name:
            return
            
        if self._show_delete_confirmation(dice_name):
            self._delete_dice(dice_name)
            
    def on_roll_custom_dice(self, event: wx.CommandEvent) -> None:
        """Handle rolling of selected custom dice."""
        dice_name = self._get_selected_dice_name()
        if not dice_name:
            return
        
        number = self.custom_dice_number.GetValue()
        results = self.roll_custom_dice(dice_name, number)
        
        # Track custom dice roll
        metadata = {
            'dice_name': dice_name,
            'number': number,
            'faces': self.custom_dices[dice_name]['faces']
        }
        from project import track_game_history

        game_event = track_game_history('custom_dice', results, metadata)
        GameHistory.get_instance().add_event(game_event)        
        
        self.custom_result.SetValue("\n".join(map(str, results)))

    def _save_custom_dices(self) -> None:
        """
        Save all custom dice configurations to the JSON file.
        """
        try:
            with open(self.CUSTOM_DICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.custom_dices, f, indent=4)
            self._refresh_dice_list()
        except IOError as e:
            wx.MessageBox(f"Error saving dices: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def _handle_new_dice_dialog(self, dialog: CustomDiceDialog) -> None:
        """
        Handle the creation of a new custom dice from dialog input.
        
        Args:
            dialog: The CustomDiceDialog instance containing new dice data
        """
        if dialog.ShowModal() == wx.ID_OK:
            dice_data = dialog.get_values()
            self.save_custom_dice(dice_data['name'], dice_data['faces'])
            self._refresh_dice_list(dice_data['name'])

    def _show_delete_confirmation(self, dice_name: str) -> bool:
        """
        Display a confirmation dialog for dice deletion.
        
        Args:
            dice_name: Name of the dice to be deleted
            
        Returns:
            bool: True if user confirms deletion, False otherwise
        """
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
        """
        Delete a custom dice configuration.
        
        Args:
            dice_name: Name of the dice to delete
        """
        if dice_name in self.custom_dices:
            del self.custom_dices[dice_name]
            self._save_custom_dices()

    def _create_edit_dialog(self, dice_name: str) -> CustomDiceDialog:
        """
        Create a dialog for editing an existing custom dice.
        
        Args:
            dice_name: Name of the dice to edit
            
        Returns:
            CustomDiceDialog: Dialog pre-filled with existing dice data
        """
        dialog = CustomDiceDialog(self)
        
        # Pre-fill with existing data
        dice_data = self.custom_dices[dice_name]
        dialog.name_ctrl.SetValue(dice_name)
        dialog.faces_ctrl.SetValue(dice_data['faces'])
        
        # Update face fields with existing values
        dialog.update_faces_inputs(dice_data['faces'])
        for ctrl, value in zip(dialog.values_ctrls, dice_data['values']):
            ctrl.SetValue(value)
            
        return dialog

    def _update_dice_data(self, dice_name: str, new_data: Dict[str, Any]) -> None:
        """
        Update an existing custom dice data.
        
        Args:
            dice_name: Name of the dice to update
            new_data: New dice data containing name and faces
        """
        # If name changed, remove old entry
        if new_data['name'] != dice_name:
            del self.custom_dices[dice_name]
            
        # Save with new data
        self.save_custom_dice(new_data['name'], new_data['faces'])
        
        # Refresh list with new name selected
        self._refresh_dice_list(new_data['name'])
