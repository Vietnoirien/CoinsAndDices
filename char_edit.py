import wx
import json
import os

class CharacterEditor(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Éditeur de Personnage', size=(400, 600))
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Sélecteur de personnage
        char_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.char_choice = wx.Choice(self.panel, choices=self.get_available_characters())
        self.char_choice.Bind(wx.EVT_CHOICE, self.on_character_selected)
        new_char_btn = wx.Button(self.panel, label="Nouveau personnage")
        new_char_btn.Bind(wx.EVT_BUTTON, self.on_new_character)
        
        char_select_sizer.Add(wx.StaticText(self.panel, label="Personnage :"), 0, wx.ALL|wx.CENTER, 5)
        char_select_sizer.Add(self.char_choice, 1, wx.ALL, 5)
        char_select_sizer.Add(new_char_btn, 0, wx.ALL, 5)
        
        self.main_sizer.Add(char_select_sizer, 0, wx.EXPAND|wx.ALL, 5)

        # Définition des champs avec les attributs
        self.fields = {
            'name': ('Nom', wx.TextCtrl),
            'level': ('Niveau', lambda p: wx.SpinCtrl(p, min=1, max=100, initial=1)),
            'exp': ('Expérience', lambda p: wx.SpinCtrl(p, min=0, max=10000, initial=0)),
            'gold': ('Or', lambda p: wx.SpinCtrl(p, min=0, max=10000, initial=3)),
            'pv': ('Points de Vie', lambda p: wx.SpinCtrl(p, min=1, max=100, initial=4)),
            'fatigue': ('Fatigue', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=3)),
            'distance': ('Distance', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'distance_degat': ('Dégâts Distance', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'melee': ('Mêlée', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'melee_degat': ('Dégâts Mêlée', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'magie': ('Magie', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0)),
            'magie_degat': ('Dégâts Magie', lambda p: wx.SpinCtrl(p, min=0, max=100, initial=0))
        }   
             
        self.controls = {}
        self.create_fields()
        self.create_buttons()

        self.panel.SetSizer(self.main_sizer)
        self.Center()
        self.Show()

    def create_fields(self):
        for field_name, (label, control_class) in self.fields.items():
            field_sizer = wx.BoxSizer(wx.HORIZONTAL)
            label_widget = wx.StaticText(self.panel, label=f"{label}:")
            control = control_class(self.panel)
            
            self.controls[field_name] = control
            
            field_sizer.Add(label_widget, 0, wx.ALL|wx.CENTER, 5)
            field_sizer.Add(control, 1, wx.ALL|wx.EXPAND, 5)
            
            self.main_sizer.Add(field_sizer, 0, wx.EXPAND|wx.ALL, 5)

    def create_buttons(self):
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        save_btn = wx.Button(self.panel, label="Sauvegarder")
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        
        cancel_btn = wx.Button(self.panel, label="Annuler")
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        button_sizer.Add(save_btn, 1, wx.ALL, 5)
        button_sizer.Add(cancel_btn, 1, wx.ALL, 5)
        
        self.main_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

    def get_available_characters(self):
        if not os.path.exists('Runelimit/characters'):
            os.makedirs('Runelimit/characters')
        return [f.replace('.json', '') for f in os.listdir('Runelimit/characters') if f.endswith('.json')]

    def get_character_data(self):
        data = {}
        for field_name, control in self.controls.items():
            if isinstance(control, wx.TextCtrl):
                data[field_name] = control.GetValue()
            else:  # SpinCtrl
                data[field_name] = control.GetValue()
        return data

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
        # Mise à jour de la liste des personnages
        self.char_choice.SetItems(self.get_available_characters())
        self.char_choice.SetStringSelection(char_name)

    def on_save(self, event):
        data = self.get_character_data()
        self.save_character(data)
        self.char_choice.SetItems(self.get_available_characters())  # Rafraîchit la liste

    def on_cancel(self, event):
        self.Close()

    def on_new_character(self, event):
        for control in self.controls.values():
            if isinstance(control, wx.TextCtrl):
                control.SetValue("")
            else:
                control.SetValue(control.GetMin())

    def on_character_selected(self, event):
        selected = self.char_choice.GetString(self.char_choice.GetSelection())
        self.load_character(selected)
