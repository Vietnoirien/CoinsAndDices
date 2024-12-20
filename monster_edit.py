import wx
import json
import os

class MonsterEditor(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        
        # Modification du sizer principal pour utiliser GROW
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)
        
        # Création des panneaux avec gestion explicite de la taille
        self.init_panel = wx.Panel(self)
        self.editor_panel = wx.Panel(self)
        
        # Ajout des flags GROW aux panneaux
        self.main_sizer.Add(self.init_panel, 1, wx.EXPAND|wx.ALL|wx.GROW, 10)
        self.main_sizer.Add(self.editor_panel, 1, wx.EXPAND|wx.ALL|wx.GROW, 10)
        
        # Ajout du buffer
        self.monster_buffer = {}
        
        self.editor_panel.Hide()
        
        # Configuration des sizers
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.setup_init_panel()
        
        # Assure la structure des répertoires
        self.ensure_directory_structure()
        
        # Configuration du sélecteur de classe
        class_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.class_choice = wx.Choice(self.editor_panel, choices=["1", "2", "3", "4"])
        self.monster_choice = wx.Choice(self.editor_panel, choices=self.get_available_monsters("1"))
        
        class_select_sizer.Add(wx.StaticText(self.editor_panel, label="Classe :"), 0, wx.ALL|wx.CENTER, 5)
        class_select_sizer.Add(self.class_choice, 1, wx.ALL, 5)
        class_select_sizer.Add(wx.StaticText(self.editor_panel, label="Monstre :"), 0, wx.ALL|wx.CENTER, 5)
        class_select_sizer.Add(self.monster_choice, 1, wx.ALL, 5)
        
        self.editor_sizer.Add(class_select_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Définition des champs
        self.fields = {
            'name': ('Nom', wx.TextCtrl),
            'health': ('Points de Vie', lambda p: wx.SpinCtrl(p, min=1, max=100)),
            'before_combat': ('Avant Combat', wx.TextCtrl),
            'in_combat': ('En Combat', wx.TextCtrl),
            'reward': ('Récompense', wx.TextCtrl),
            'distance': ('Distance', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'distance_degat': ('Dégâts Distance', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'melee': ('Mêlée', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'melee_degat': ('Dégâts Mêlée', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'magie': ('Magie', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'magie_degat': ('Dégâts Magie', lambda p: wx.SpinCtrl(p, min=0, max=100))
        }
        self.controls = {}
        self.create_fields()
        self.create_buttons()
        
        # Ajouter après la création des boutons existants
        
        self.editor_panel.SetSizer(self.editor_sizer)
        
        # Bindings
        self.class_choice.Bind(wx.EVT_CHOICE, self.on_class_selected)
        self.monster_choice.Bind(wx.EVT_CHOICE, self.on_monster_selected)
        self.create_monster_button.Bind(wx.EVT_BUTTON, self.show_editor)
    def parse_monster_text(self, text):
        words = text.strip().split()
        combat_stats = words[-3:]
        words = words[:-3]
        
        health_index = next(i for i, word in enumerate(words) if word.isdigit())
        name = " ".join(words[:health_index])
        health = int(words[health_index])
        
        distance, distance_degat = map(int, combat_stats[0].split('/'))
        melee, melee_degat = map(int, combat_stats[1].split('/'))
        magie, magie_degat = map(int, combat_stats[2].split('/'))
        
        return {
            'name': name,
            'health': health,
            'distance': distance,
            'distance_degat': distance_degat,
            'melee': melee,
            'melee_degat': melee_degat,
            'magie': magie,
            'magie_degat': magie_degat,
            'before_combat': '',
            'in_combat': '',
            'reward': ''
        }

    def fill_form_from_text(self, text):
        data = self.parse_monster_text(text)
        for field_name, value in data.items():
            if field_name in self.controls:
                self.controls[field_name].SetValue(value)

    def on_import(self, event):
        dialog = wx.TextEntryDialog(
            self,
            "Entrez le texte du monstre:",
            "Import monstre",
            style=wx.TE_MULTILINE|wx.OK|wx.CANCEL
        )
        if dialog.ShowModal() == wx.ID_OK:
            self.fill_form_from_text(dialog.GetValue())
        dialog.Destroy()
    def setup_init_panel(self):
        init_sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_monster_button = wx.Button(self.init_panel, label="Créer un monstre")
        init_sizer.Add(self.create_monster_button, 0, wx.ALL|wx.CENTER, 20)
        self.init_panel.SetSizer(init_sizer)

    def ensure_directory_structure(self):
        base_dir = 'Runelimit/monsters'
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        for class_num in range(1, 5):
            class_dir = f'{base_dir}/class_{class_num}'
            if not os.path.exists(class_dir):
                os.makedirs(class_dir)

    def toggle_panels(self):
        self.init_panel.Hide()
        self.editor_panel.Show()
        self.Layout()

    def show_editor(self, event):
        from char_edit import CharacterEditor
        parent = self.GetParent()
        for child in parent.GetChildren():
            if isinstance(child, (CharacterEditor, MonsterEditor)):
                child.Hide()
        self.Show()
        self.toggle_panels()
        parent.Layout()

    def validate_monster_data(self, data):
        if not data['name'].strip():
            return False, "Le nom du monstre ne peut pas être vide"
        return True, ""

    def on_monster_selected(self, event):
        if self.monster_choice.GetSelection() != -1:
            selected_class = self.class_choice.GetString(self.class_choice.GetSelection())
            selected_monster = self.monster_choice.GetString(self.monster_choice.GetSelection())
            self.load_monster(selected_class, selected_monster)

    def create_fields(self):
        # Création du ScrolledWindow pour les champs
        self.scroll_window = wx.ScrolledWindow(self.editor_panel)
        self.scroll_window.SetScrollRate(0, 20)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        # Grille pour les champs de formulaire
        grid_sizer = wx.FlexGridSizer(cols=2, vgap=2, hgap=10)
        grid_sizer.AddGrowableCol(1, 1)

        # Ajout des champs de formulaire
        for field_name, (label, control_class) in self.fields.items():
            label_widget = wx.StaticText(self.scroll_window, label=f"{label}:")
            font = label_widget.GetFont()
            font.SetPointSize(8)
            label_widget.SetFont(font)
    
            if control_class == wx.TextCtrl:
                control = control_class(self.scroll_window, size=(240, 20))
            else:
                control = control_class(self.scroll_window)
                control.SetInitialSize((80, 20))
        
            self.controls[field_name] = control
            grid_sizer.Add(label_widget, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 15)
            grid_sizer.Add(control, 0, wx.ALIGN_RIGHT, 5)

        scroll_sizer.Add(grid_sizer, 1, wx.EXPAND|wx.ALL, 2)
        self.scroll_window.SetSizer(scroll_sizer)
    
        # Ajout du ScrolledWindow au sizer principal
        self.editor_sizer.Add(self.scroll_window, 1, wx.EXPAND)
    
        # Création de la zone d'import
        import_sizer = wx.BoxSizer(wx.VERTICAL)
        self.import_text = wx.TextCtrl(self.editor_panel, style=wx.TE_MULTILINE, size=(-1, 100))
        import_btn = wx.Button(self.editor_panel, label="Importer")
        import_btn.Bind(wx.EVT_BUTTON, self.on_import)
    
        import_sizer.Add(self.import_text, 1, wx.EXPAND|wx.ALL, 5)
        import_sizer.Add(import_btn, 0, wx.EXPAND|wx.ALL, 5)
    
        # Ajout de la zone d'import au sizer principal
        self.editor_sizer.Add(import_sizer, 0, wx.EXPAND|wx.ALL, 5)
    
        # Création des boutons de sauvegarde/annulation
    
        # Mise à jour du layout
        self.scroll_window.Layout()
        self.editor_panel.Layout()

    def on_import(self, event):
        text = self.import_text.GetValue()
        if text.strip():
            self.fill_form_from_text(text)

    def get_monster_data(self):
        data = {}
        for field_name, control in self.controls.items():
            if isinstance(control, wx.TextCtrl):
                data[field_name] = control.GetValue()
            else:  # SpinCtrl
                data[field_name] = control.GetValue()
        return data

    def load_monster(self, class_num, monster_name):
        file_path = f'Runelimit/monsters/class_{class_num}/{monster_name}.json'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for field_name, value in data.items():
                        if field_name in self.controls:
                            self.controls[field_name].SetValue(value)
            except json.JSONDecodeError:
                pass

    def save_monster(self, data):
        selected_class = self.class_choice.GetString(self.class_choice.GetSelection())
        monster_name = data['name']
        directory = f'Runelimit/monsters/class_{selected_class}'
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        file_path = f'{directory}/{monster_name}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.monster_choice.SetItems(self.get_available_monsters(selected_class))
        self.monster_choice.SetStringSelection(monster_name)

    def on_save(self, event):
        if self.class_choice.GetSelection() == -1:
            wx.MessageBox("Veuillez sélectionner une classe", "Erreur", wx.OK | wx.ICON_ERROR)
            return
            
        data = self.get_monster_data()
        valid, message = self.validate_monster_data(data)
        
        if not valid:
            wx.MessageBox(message, "Erreur de validation", wx.OK | wx.ICON_ERROR)
            return
            
        self.save_monster(data)

    def on_cancel(self, event):
        self.reset_fields()
        self.editor_panel.Hide()
        self.init_panel.Show()
        parent = self.GetParent()
        parent.GetChildren()[0].Show()  # Montre le panneau de boutons
        self.Layout()

    def reset_fields(self):
        for control in self.controls.values():
            if isinstance(control, wx.TextCtrl):
                control.SetValue("")
            else:
                control.SetValue(control.GetMin())

    def get_available_monsters(self, class_num):
        """
        Retourne la liste des monstres disponibles pour une classe donnée
        """
        directory = f'Runelimit/monsters/class_{class_num}'
        if not os.path.exists(directory):
            os.makedirs(directory)
            return []
        
        monsters = []
        for file in os.listdir(directory):
            if file.endswith('.json'):
                monsters.append(file[:-5])  # Enlève l'extension .json
        return sorted(monsters)

    def on_class_selected(self, event):
        # Sauvegarde des données actuelles dans le buffer
        if self.class_choice.GetSelection() != -1:
            self.monster_buffer = self.get_monster_data()
        
        selected_class = self.class_choice.GetString(self.class_choice.GetSelection())
        self.monster_choice.SetItems(self.get_available_monsters(selected_class))
        self.monster_choice.SetSelection(-1)
        
        # Restauration des données du buffer au lieu de réinitialiser
        if self.monster_buffer:
            for field_name, value in self.monster_buffer.items():
                if field_name in self.controls:
                    self.controls[field_name].SetValue(value)

    def parse_monster_text(self, text):
        """
        Parse le texte formaté et retourne un dictionnaire avec les données du monstre
        Format attendu: "Nom Santé ... X1/Y1 X2/Y2 X3/Y3"
        """
        # Séparation en mots
        words = text.strip().split()
        
        # Extraction des stats de combat (les 3 derniers éléments)
        combat_stats = words[-3:]
        # Suppression des stats du texte original
        words = words[:-3]
        
        # Recherche du premier nombre (points de vie)
        health_index = next(i for i, word in enumerate(words) if word.isdigit())
        
        # Le nom est tout ce qui précède les points de vie
        name = " ".join(words[:health_index])
        health = int(words[health_index])
        
        # Parse les stats de combat
        distance, distance_degat = map(int, combat_stats[0].split('/'))
        melee, melee_degat = map(int, combat_stats[1].split('/'))
        magie, magie_degat = map(int, combat_stats[2].split('/'))
        
        return {
            'name': name,
            'health': health,
            'distance': distance,
            'distance_degat': distance_degat,
            'melee': melee,
            'melee_degat': melee_degat,
            'magie': magie,
            'magie_degat': magie_degat,
            'before_combat': '',  # Champs texte vides pour l'instant
            'in_combat': '',
            'reward': ''
        }

    def fill_form_from_text(self, text):
        """
        Remplit le formulaire à partir du texte formaté
        """
        data = self.parse_monster_text(text)
        for field_name, value in data.items():
            if field_name in self.controls:
                self.controls[field_name].SetValue(value)

    def create_buttons(self):
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        save_btn = wx.Button(self.editor_panel, label="Sauvegarder")
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        
        cancel_btn = wx.Button(self.editor_panel, label="Annuler") 
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        button_sizer.Add(save_btn, 1, wx.ALL, 5)
        button_sizer.Add(cancel_btn, 1, wx.ALL, 5)
        
        self.editor_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

    def save_to_new_class(self, old_class, new_class, monster_name):
        # Suppression de l'ancien fichier
        old_path = f'Runelimit/monsters/class_{old_class}/{monster_name}.json'
        if os.path.exists(old_path):
            os.remove(old_path)
        
        # Sauvegarde dans la nouvelle classe
        data = self.get_monster_data()
        self.save_monster(data)
