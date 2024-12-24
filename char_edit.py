import wx
import json
import os

class CharacterEditor(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Editor panel configuration
        self.editor_panel = wx.Panel(self)
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor_panel.SetSizer(self.editor_sizer)
        
        # Character selector setup
        self.setup_char_selector()
        
        # Fields setup
        self.setup_fields()
        
        # Add editor panel to main sizer with expansion
        self.main_sizer.Add(self.editor_panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(self.main_sizer)
        
        # Initial state
        self.editor_panel.Hide()

    def setup_char_selector(self):
        char_select_panel = wx.Panel(self.editor_panel)
        char_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.char_choice = wx.Choice(char_select_panel, choices=self.get_available_characters())
        new_char_btn = wx.Button(char_select_panel, label="Nouveau personnage")
        char_label = wx.StaticText(char_select_panel, label="Personnage :")
        
        char_select_sizer.Add(char_label, 0, wx.ALL|wx.CENTER, 5)
        char_select_sizer.Add(self.char_choice, 1, wx.ALL|wx.EXPAND, 5)
        char_select_sizer.Add(new_char_btn, 0, wx.ALL, 5)
        
        char_select_panel.SetSizer(char_select_sizer)
        self.editor_sizer.Add(char_select_panel, 0, wx.EXPAND|wx.ALL, 5)

    def create_fields(self):
        self.scroll_window = wx.ScrolledWindow(self.editor_panel)
        self.scroll_window.SetScrollRate(0, 20)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        
        grid_sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=15)
        grid_sizer.AddGrowableCol(1, 2)

        for field_name, (label, control_class) in self.fields.items():
            label_widget = wx.StaticText(self.scroll_window, label=f"{label}:")
            font = label_widget.GetFont()
            font.SetPointSize(9)
            label_widget.SetFont(font)
            
            control = control_class(self.scroll_window)
            self.controls[field_name] = control
            
            grid_sizer.Add(label_widget, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
            grid_sizer.Add(control, 1, wx.EXPAND|wx.ALL, 5)

        scroll_sizer.Add(grid_sizer, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)
        self.scroll_window.SetSizer(scroll_sizer)
        self.editor_sizer.Add(self.scroll_window, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)

    def create_buttons(self):
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        save_btn = wx.Button(self.editor_panel, label="Sauvegarder")
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        
        cancel_btn = wx.Button(self.editor_panel, label="Annuler")
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        button_sizer.Add(save_btn, 1, wx.ALL, 5)
        button_sizer.Add(cancel_btn, 1, wx.ALL, 5)
        
        self.editor_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

    def ensure_directory_structure(self):
        char_dir = 'Runelimit/characters'
        if not os.path.exists(char_dir):
            os.makedirs(char_dir)

    def get_available_characters(self):
        if not os.path.exists('Runelimit/characters'):
            os.makedirs('Runelimit/characters')
        return [f.replace('.json', '') for f in os.listdir('Runelimit/characters') if f.endswith('.json')]

    def get_character_data(self):
        return {field_name: control.GetValue() for field_name, control in self.controls.items()}

    def load_character(self, char_name):
        file_path = f'Runelimit/characters/{char_name}.json'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for field_name, value in data.items():
                        if field_name in self.controls:
                            self.controls[field_name].SetValue(value)
            except json.JSONDecodeError:
                pass

    def save_character(self, data):
        char_name = data['name']
        file_path = f'Runelimit/characters/{char_name}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.char_choice.SetItems(self.get_available_characters())
        self.char_choice.SetStringSelection(char_name)

    def validate_character_data(self, data):
        if not data['name'].strip():
            return False, "Le nom du personnage ne peut pas être vide"
        return True, ""

    def on_save(self, event):
        data = self.get_character_data()
        valid, message = self.validate_character_data(data)
        
        if not valid:
            wx.MessageBox(message, "Erreur de validation", wx.OK | wx.ICON_ERROR)
            return
            
        self.save_character(data)

    def on_cancel(self, event):
        self.reset_fields()
        # Navigate up through the parent hierarchy to find the main frame
        main_frame = wx.GetTopLevelParent(self)
        panel_manager = main_frame.panel_manager
        panel_manager.show_buttons_panel()
        
    def on_new_character(self, event):
        for control in self.controls.values():
            if isinstance(control, wx.TextCtrl):
                control.SetValue("")
            else:
                control.SetValue(control.GetMin())

    def on_character_selected(self, event):
        selected = self.char_choice.GetString(self.char_choice.GetSelection())
        self.load_character(selected)

    def reset_fields(self):
        for control in self.controls.values():
            if isinstance(control, wx.TextCtrl):
                control.SetValue("")
            else:
                control.SetValue(control.GetMin())

    def setup_fields(self):
        # Directory structure check
        self.ensure_directory_structure()
        
        # Fields definition with default values
        self.fields = {
            'name': ('Nom', wx.TextCtrl),
            'level': ('Niveau', lambda p: wx.SpinCtrl(p, min=1, max=100, initial=1)),
            'exp': ('Expérience', lambda p: wx.SpinCtrl(p, min=0, max=10000, initial=0)),
            'gold': ('Or', lambda p: wx.SpinCtrl(p, min=0, max=10000, initial=3)),
            'pv': ('❤️ Points de Vie', lambda p: wx.SpinCtrl(p, min=1, max=100, initial=4)),
            'fatigue': ('🔥 Fatigue', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=3)),
            'distance': ('🏹 Distance', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'distance_degat': ('🏹 Dégâts Distance', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'melee': ('⚔️ Mêlée', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'melee_degat': ('⚔️ Dégâts Mêlée', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'magie': ('☯️ Magie', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'magie_degat': ('☯️ Dégâts Magie', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0))
        }
        
        self.controls = {}
        self.create_fields()
        self.create_buttons()