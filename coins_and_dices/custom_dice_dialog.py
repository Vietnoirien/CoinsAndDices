from typing import Dict, List, Union, Optional
import wx
from .constants import (
    CUSTOM_DICE_MAX_COUNT,
    CUSTOM_DICE_MIN_COUNT,
)

class CustomDiceDialog(wx.Dialog):
    # Class-level constants for strings
    TITLE = "Créer un dé personnalisé"
    LABEL_DICE_NAME = "Nom du dé:"
    LABEL_FACES_COUNT = "Nombre de faces:"
    LABEL_FACE = "Face"
    BTN_CREATE = "Créer"
    BTN_CANCEL = "Annuler"
    ERROR_EMPTY_NAME = "Le nom du dé ne peut pas être vide"
    ERROR_EMPTY_FACE = "La face {} ne peut pas être vide"
    
    def __init__(self, parent: wx.Window) -> None:
        """Initialize the custom dice dialog.
        
        Args:
            parent: Parent window for the dialog
        """
        super().__init__(parent, title=self.TITLE, size=(400, 600))
        
        self.SetMinSize((400, 400))
        self.SetMaxSize((600, 800))
        
        # Persistent storage for face values
        self.stored_values: List[str] = []
        self.values_ctrls: List[wx.TextCtrl] = []
        
        self._init_ui()
        self.update_faces_inputs(6)
        self.Fit()

    def _init_ui(self) -> None:
        """Initialize all UI components and layout."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.scroll_panel = wx.ScrolledWindow(self)
        self.scroll_panel.SetScrollRate(0, 20)
        
        self.panel = wx.Panel(self.scroll_panel)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add UI components
        panel_sizer.Add(self.create_name_controls(), 0, wx.EXPAND|wx.ALL, 5)
        panel_sizer.Add(self.create_faces_controls(), 0, wx.EXPAND|wx.ALL, 5)
        
        self.values_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.Add(self.values_sizer, 1, wx.EXPAND|wx.ALL, 5)
        panel_sizer.Add(self.create_buttons(), 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        self.panel.SetSizer(panel_sizer)
        self.scroll_panel.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.scroll_panel.GetSizer().Add(self.panel, 1, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(self.scroll_panel, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

    def create_name_controls(self) -> wx.Sizer:
        """Create and return the name input controls.
        
        Returns:
            wx.Sizer: Sizer containing name controls
        """
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_label = wx.StaticText(self.panel, label=self.LABEL_DICE_NAME)
        self.name_ctrl = wx.TextCtrl(self.panel)
        name_sizer.Add(name_label, 0, wx.ALL|wx.CENTER, 5)
        name_sizer.Add(self.name_ctrl, 1, wx.ALL|wx.EXPAND, 5)
        return name_sizer

    def create_faces_controls(self) -> wx.Sizer:
        """Create and return the faces count controls.
        
        Returns:
            wx.Sizer: Sizer containing faces count controls
        """
        faces_sizer = wx.BoxSizer(wx.HORIZONTAL)
        faces_label = wx.StaticText(self.panel, label=self.LABEL_FACES_COUNT)
        self.faces_ctrl = wx.SpinCtrl(
            self.panel,
            min=CUSTOM_DICE_MIN_COUNT,
            max=CUSTOM_DICE_MAX_COUNT,
            initial=6
        )
        self.faces_ctrl.Bind(wx.EVT_SPINCTRL, self.on_faces_changed)
        faces_sizer.Add(faces_label, 0, wx.ALL|wx.CENTER, 5)
        faces_sizer.Add(self.faces_ctrl, 1, wx.ALL|wx.EXPAND, 5)
        return faces_sizer

    def create_buttons(self) -> wx.Sizer:
        """Create and return the dialog buttons.
        
        Returns:
            wx.Sizer: Sizer containing dialog buttons
        """
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self.panel, wx.ID_OK, self.BTN_CREATE)
        cancel_btn = wx.Button(self.panel, wx.ID_CANCEL, self.BTN_CANCEL)
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        return btn_sizer

    def update_faces_inputs(self, num_faces: int) -> None:
        """Update the face input controls based on the number of faces.
        
        Args:
            num_faces: Number of faces to create inputs for
        """
        current_values = [ctrl.GetValue() for ctrl in self.values_ctrls]
        
        # Update persistent storage
        if len(current_values) > len(self.stored_values):
            self.stored_values.extend(current_values[len(self.stored_values):])
        else:
            for i, value in enumerate(current_values):
                if i < len(self.stored_values):
                    self.stored_values[i] = value
        
        self.cleanup()
        
        for i in range(num_faces):
            face_sizer = wx.BoxSizer(wx.HORIZONTAL)
            face_label = wx.StaticText(self.panel, label=f"{self.LABEL_FACE} {i+1}:")
            ctrl = wx.TextCtrl(self.panel)
            
            if i < len(self.stored_values):
                ctrl.SetValue(self.stored_values[i])
                
            self.values_ctrls.append(ctrl)
            face_sizer.Add(face_label, 0, wx.ALL|wx.CENTER, 5)
            face_sizer.Add(ctrl, 1, wx.ALL|wx.EXPAND, 5)
            self.values_sizer.Add(face_sizer, 0, wx.EXPAND)
        
        self.panel.Layout()
        self.scroll_panel.FitInside()

    def on_faces_changed(self, event: wx.SpinEvent) -> None:
        """Handle changes to the number of faces.
        
        Args:
            event: Spin control event
        """
        self.update_faces_inputs(self.faces_ctrl.GetValue())

    def validate_inputs(self) -> bool:
        """Validate all input fields.
        
        Returns:
            bool: True if all inputs are valid, False otherwise
        """
        if not self.name_ctrl.GetValue().strip():
            wx.MessageBox(self.ERROR_EMPTY_NAME, "Erreur", wx.OK | wx.ICON_ERROR)
            return False
        
        for i, ctrl in enumerate(self.values_ctrls):
            if not ctrl.GetValue().strip():
                wx.MessageBox(
                    self.ERROR_EMPTY_FACE.format(i+1),
                    "Erreur",
                    wx.OK | wx.ICON_ERROR
                )
                return False
        return True

    def cleanup(self) -> None:
        """Clean up all face input controls."""
        for ctrl in self.values_ctrls:
            ctrl.Destroy()
        self.values_ctrls.clear()
        self.values_sizer.Clear(True)

    def on_ok(self, event: wx.CommandEvent) -> None:
        """Handle OK button click.
        
        Args:
            event: Button click event
        """
        if self.validate_inputs():
            event.Skip()

    def get_values(self) -> Dict[str, Union[str, List[str]]]:
        """Get the dialog's input values.
        
        Returns:
            Dict containing the dice name and face values
        """
        return {
            'name': self.name_ctrl.GetValue().strip(),
            'faces': [ctrl.GetValue().strip() for ctrl in self.values_ctrls]
        }

    def __del__(self) -> None:
        """Clean up resources when the dialog is destroyed."""
        self.faces_ctrl.Unbind(wx.EVT_SPINCTRL)
