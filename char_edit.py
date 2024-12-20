import wx
import json
import os
from monster_edit import MonsterEditor

class CharacterEditor(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
    
        # Modification du sizer principal pour utiliser GROW
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)
    
        # Création des panneaux avec gestion explicite de la taille
        self.init_panel = wx.Panel(self)
        self.editor_panel = wx.Panel(self)
    
        # Configuration du sizer de l'éditeur
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor_panel.SetSizer(self.editor_sizer)
    
        # Configuration du sélecteur de personnage
        char_select_panel = wx.Panel(self.editor_panel)
        char_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
    
        self.char_choice = wx.Choice(char_select_panel, choices=self.get_available_characters())
        new_char_btn = wx.Button(char_select_panel, label="Nouveau personnage")
        char_label = wx.StaticText(char_select_panel, label="Personnage :")
    
        char_select_sizer.Add(char_label, 0, wx.ALL|wx.CENTER, 5)
        char_select_sizer.Add(self.char_choice, 1, wx.ALL|wx.EXPAND, 5)
        char_select_sizer.Add(new_char_btn, 0, wx.ALL, 5)
    
        char_select_panel.SetSizer(char_select_sizer)
    
        # Ajout des flags GROW aux panneaux
        self.main_sizer.Add(self.init_panel, 1, wx.EXPAND|wx.ALL|wx.GROW, 10)
        self.main_sizer.Add(self.editor_panel, 1, wx.EXPAND|wx.ALL|wx.GROW, 10)
    
        # Ajout du sélecteur au panneau d'édition
        self.editor_sizer.Add(char_select_panel, 0, wx.EXPAND|wx.ALL, 5)
    
        # Configuration initiale
        self.setup_init_panel()
        self.ensure_directory_structure()
    
        # Définition des champs avec leurs valeurs par défaut
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
    
        # Initialisation des contrôles et création des champs
        self.controls = {}
        self.create_fields()
        self.create_buttons()
    
        # Configuration des événements
        self.char_choice.Bind(wx.EVT_CHOICE, self.on_character_selected)
        new_char_btn.Bind(wx.EVT_BUTTON, self.on_new_character)
    
        # État initial
        self.editor_panel.Hide()

    def create_fields(self):
        # Modification du scroll_window pour remplir l'espace
        self.scroll_window = wx.ScrolledWindow(self.editor_panel)
        self.scroll_window.SetScrollRate(0, 20)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
    
        # Ajustement du FlexGridSizer
        grid_sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=15)
        grid_sizer.AddGrowableCol(1, 2)  # Augmentation du ratio de croissance

        # Création des champs de formulaire
        for field_name, (label, control_class) in self.fields.items():
            # Configuration du label
            label_widget = wx.StaticText(self.scroll_window, label=f"{label}:")
            font = label_widget.GetFont()
            font.SetPointSize(9)  # Taille de police plus lisible
            label_widget.SetFont(font)
        
            # Création du contrôle avec dimensions appropriées
            control = control_class(self.scroll_window)
            self.controls[field_name] = control
            grid_sizer.Add(label_widget, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
            grid_sizer.Add(control, 1, wx.EXPAND|wx.ALL, 5)

        # Ajout des flags GROW au scroll_sizer
        scroll_sizer.Add(grid_sizer, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)
        self.scroll_window.SetSizer(scroll_sizer)
    
        # Modification de l'ajout du scroll_window
        self.editor_sizer.Add(self.scroll_window, 1, wx.EXPAND|wx.ALL|wx.GROW, 5)

    def setup_init_panel(self):
        init_sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_char_button = wx.Button(self.init_panel, label="Créer un personnage")
        init_sizer.Add(self.create_char_button, 1, wx.ALL|wx.CENTER|wx.GROW, 20)
        self.init_panel.SetSizer(init_sizer)

    def ensure_directory_structure(self):
        char_dir = 'Runelimit/characters'
        if not os.path.exists(char_dir):
            os.makedirs(char_dir)

    def toggle_panels(self):
        self.init_panel.Hide()
        self.editor_panel.Show()
        self.Layout()

    def validate_character_data(self, data):
        if not data['name'].strip():
            return False, "Le nom du personnage ne peut pas être vide"
        return True, ""

    def show_editor(self, event):
        parent = self.GetParent()
        for child in parent.GetChildren():
            if isinstance(child, (CharacterEditor, MonsterEditor)):
                child.Hide()
        self.Show()
        self.toggle_panels()
        parent.Layout()

    def create_buttons(self):
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        save_btn = wx.Button(self.editor_panel, label="Sauvegarder")
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        
        cancel_btn = wx.Button(self.editor_panel, label="Annuler")
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        button_sizer.Add(save_btn, 1, wx.ALL, 5)
        button_sizer.Add(cancel_btn, 1, wx.ALL, 5)
        
        self.editor_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

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
        valid, message = self.validate_character_data(data)
        
        if not valid:
            wx.MessageBox(message, "Erreur de validation", wx.OK | wx.ICON_ERROR)
            return
            
        self.save_character(data)

    def on_cancel(self, event):
        self.editor_panel.Hide()
        self.init_panel.Show()
        parent = self.GetParent()
        parent.GetChildren()[0].Show()  # Montre le panneau de boutons
        self.Layout()

    def on_new_character(self, event):
        for control in self.controls.values():
            if isinstance(control, wx.TextCtrl):
                control.SetValue("")
            else:
                control.SetValue(control.GetMin())

    def on_character_selected(self, event):
        selected = self.char_choice.GetString(self.char_choice.GetSelection())
        self.load_character(selected)
