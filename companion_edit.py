import wx
import json
import os

class CompanionEditor(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.init_panel = wx.Panel(self)
        self.editor_panel = wx.Panel(self)

        # Créer editor_sizer AVANT de l'utiliser
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor_panel.SetSizer(self.editor_sizer)

        init_sizer = wx.BoxSizer(wx.HORIZONTAL)
        init_btn = wx.Button(self.init_panel, label="Initialiser les compagnons de base")
        reset_btn = wx.Button(self.init_panel, label="Réinitialiser aux valeurs par défaut")

        init_btn.Bind(wx.EVT_BUTTON, self.on_init_default_companions)
        reset_btn.Bind(wx.EVT_BUTTON, self.on_reset_to_default)

        init_sizer.Add(init_btn, 0, wx.ALL, 5)
        init_sizer.Add(reset_btn, 0, wx.ALL, 5)
        self.init_panel.SetSizer(init_sizer)

        import_sizer = wx.BoxSizer(wx.VERTICAL)
        self.import_text = wx.TextCtrl(self.editor_panel, style=wx.TE_MULTILINE, size=(-1, 100))
        import_btn = wx.Button(self.editor_panel, label="Importer")
        import_btn.Bind(wx.EVT_BUTTON, self.on_import)

        import_sizer.Add(self.import_text, 1, wx.EXPAND|wx.ALL, 5)
        import_sizer.Add(import_btn, 0, wx.EXPAND|wx.ALL, 5)
        self.editor_sizer.Add(import_sizer, 0, wx.EXPAND|wx.ALL, 5)
    
        self.main_sizer.Add(self.init_panel, 0, wx.EXPAND|wx.ALL, 5)
        self.main_sizer.Add(self.editor_panel, 1, wx.EXPAND|wx.ALL, 5)
    
        self.SetSizer(self.main_sizer)
    
        self.companion_buffer = {}
        self.editor_panel.Hide()
    
        # Définir les champs pour un compagnon
        self.fields = {
            'name': ('Nom', wx.TextCtrl),
            'golds_cost': ('Coût en or', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'pv': ('Points de Vie', lambda p: wx.SpinCtrl(p, min=1, max=100)),
            'fatigue': ('Fatigue', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'effect': ('Effet', wx.TextCtrl),
            'description': ('Description', wx.TextCtrl),
            'distance': ('Distance', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'distance_degat': ('Dégâts Distance', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'melee': ('Mêlée', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'melee_degat': ('Dégâts Mêlée', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'magie': ('Magie', lambda p: wx.SpinCtrl(p, min=0, max=100)),
            'magie_degat': ('Dégâts Magie', lambda p: wx.SpinCtrl(p, min=0, max=100))
        }        
        self.controls = {}
    
        self.ensure_directory_structure()
        self.create_selection_controls()
        self.create_fields()
        self.create_buttons()
        
    def create_fields(self):
        self.scroll_window = wx.ScrolledWindow(self.editor_panel)
        self.scroll_window.SetScrollRate(0, 20)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        grid_sizer = wx.FlexGridSizer(cols=2)
        grid_sizer.AddGrowableCol(1, 1)

        for field_name, (label, control_class) in self.fields.items():
            label_widget = wx.StaticText(self.scroll_window, label=f"{label}:")
            font = label_widget.GetFont()
            font.SetPointSize(8)
            label_widget.SetFont(font)

            if control_class == wx.TextCtrl:
                control = control_class(self.scroll_window, size=(240, 20))
            else:
                control = control_class(self.scroll_window)
                if control_class == wx.SpinCtrl:
                    control.SetMinSize((32, -1))
            self.controls[field_name] = control
            grid_sizer.Add(label_widget, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 15)
            grid_sizer.Add(control, 0, wx.ALIGN_RIGHT, 5)

        scroll_sizer.Add(grid_sizer, 1, wx.EXPAND|wx.ALL, 2)
        self.scroll_window.SetSizer(scroll_sizer)
        self.editor_sizer.Add(self.scroll_window, 1, wx.EXPAND)

    def create_buttons(self):
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(self.editor_panel, label="Sauvegarder")
        delete_btn = wx.Button(self.editor_panel, label="Supprimer")
        cancel_btn = wx.Button(self.editor_panel, label="Annuler")
        
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        button_sizer.Add(save_btn, 0, wx.ALL, 5)
        button_sizer.Add(delete_btn, 0, wx.ALL, 5)
        button_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        self.editor_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

    def ensure_directory_structure(self):
        if not os.path.exists('Runelimit/companions'):
            os.makedirs('Runelimit/companions')

    def get_companion_data(self):
        data = {}
        for field_name, control in self.controls.items():
            if isinstance(control, wx.TextCtrl):
                data[field_name] = control.GetValue()
            else:  # SpinCtrl
                data[field_name] = control.GetValue()
        return data

    def save_companion(self, data):
        if not data['name'].strip():
            wx.MessageBox("Le nom du compagnon ne peut pas être vide", "Erreur", wx.OK | wx.ICON_ERROR)
            return False
        
        duplicates = self.find_duplicate_companions(data['name'])
        if duplicates:
            if not self.handle_duplicate_companions(data['name'], duplicates):
                return False
                
        directory = 'Runelimit/companions'
        file_path = f'{directory}/{data["name"]}.json'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.companion_choice.SetItems(self.get_available_companions())
        self.companion_choice.SetStringSelection(data["name"])
        return True

    def on_save(self, event):
        data = self.get_companion_data()
        if self.save_companion(data):
            wx.MessageBox("Compagnon sauvegardé avec succès", "Succès", wx.OK | wx.ICON_INFORMATION)

    def on_delete(self, event):
        if self.companion_choice.GetSelection() == -1:
            wx.MessageBox("Veuillez sélectionner un compagnon à supprimer", "Erreur", wx.OK | wx.ICON_ERROR)
            return

        selected_companion = self.companion_choice.GetString(self.companion_choice.GetSelection())
        file_path = f'Runelimit/companions/{selected_companion}.json'

        dialog = wx.MessageDialog(
            self,
            f"Êtes-vous sûr de vouloir supprimer le compagnon {selected_companion} ?\nCette action est irréversible.",
            "Confirmation de suppression",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )

        if dialog.ShowModal() == wx.ID_YES:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    self.companion_choice.SetItems(self.get_available_companions())
                    self.companion_choice.SetSelection(-1)
                    self.reset_fields()
                    wx.MessageBox("Compagnon supprimé avec succès", "Succès", wx.OK | wx.ICON_INFORMATION)
                except OSError as e:
                    wx.MessageBox(f"Erreur lors de la suppression : {str(e)}", "Erreur", wx.OK | wx.ICON_ERROR)
    def on_cancel(self, event):
        self.reset_fields()
        self.companion_choice.SetSelection(-1)
        main_frame = wx.GetTopLevelParent(self)
        panel_manager = main_frame.panel_manager
        panel_manager.show_buttons_panel()
        panel_manager.force_layout()

    def reset_fields(self):
        for control in self.controls.values():
            if isinstance(control, wx.TextCtrl):
                control.SetValue("")
            else:
                control.SetValue(control.GetMin())
                  
    def parse_companion_text(self, text):
        lines = [line.strip() for line in text.split('\n') if line.strip() and not line.startswith('-')]
        
        # Nom (première ligne)
        name = lines[0]
        
        # Coût en or (deuxième ligne)
        golds_cost = int(lines[1])
        
        # PV et fatigue (lignes suivantes)
        pv = int(lines[2])
        fatigue = int(lines[3])
        
        # Effet (ligne suivante)
        effect = lines[4]
        
        # Description (entre astérisques)
        description = lines[5].strip('*')
        
        # Stats de combat (3 dernières lignes)
        combat_stats = lines[-3:]
        distance, distance_degat = map(int, combat_stats[0].split('/'))
        melee, melee_degat = map(int, combat_stats[1].split('/'))
        magie, magie_degat = map(int, combat_stats[2].split('/'))
        
        return {
            'name': name,
            'golds_cost': golds_cost,
            'pv': pv,
            'fatigue': fatigue,
            'effect': effect,
            'description': description,
            'distance': distance,
            'distance_degat': distance_degat,
            'melee': melee,
            'melee_degat': melee_degat,
            'magie': magie,
            'magie_degat': magie_degat
        }
    
    def fill_form_from_text(self, text):
        data = self.parse_companion_text(text)
        for field_name, value in data.items():
            if field_name in self.controls:
                self.controls[field_name].SetValue(value)

    def on_import(self, event):
        text = self.import_text.GetValue()
        if text.strip():
            self.fill_form_from_text(text)

    def on_init_default_companions(self, event):
        success_count = self.init_default_companions()
        wx.MessageBox(f"{success_count} compagnons ont été initialisés avec succès", 
                    "Succès", wx.OK | wx.ICON_INFORMATION)

    def init_default_companions(self):
        directory = 'Runelimit/companions'
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith('.json'):
                    os.remove(os.path.join(directory, file))

        # Utiliser default.txt au lieu de default_companions.txt
        file_path = 'Runelimit/companions/default.txt'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    companions = self.parse_companions_file(content)
                    
                    success_count = 0
                    for companion_data in companions:
                        if self.save_companion(companion_data):
                            success_count += 1
                    return success_count
            except Exception as e:
                wx.MessageBox(f"Erreur lors de l'initialisation : {str(e)}", 
                            "Erreur", wx.OK | wx.ICON_ERROR)
        return 0
    def parse_companions_file(self, file_content):
        companions = []
        current_companion = []

        for line in file_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('-'):
                current_companion.append(line)
            elif line.startswith('-'):
                if current_companion:
                    companions.append(self.parse_companion_text('\n'.join(current_companion)))
                current_companion = []

        return companions

    def on_reset_to_default(self, event):
        dialog = wx.MessageDialog(
            self,
            "Cette action va supprimer tous les compagnons existants et réinitialiser avec les compagnons par défaut. Continuer ?",
            "Confirmation de réinitialisation", 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        
        if dialog.ShowModal() == wx.ID_YES:
            success_count = self.init_default_companions()
            self.reset_fields()
            wx.MessageBox(f"{success_count} compagnons ont été réinitialisés avec succès",
                        "Succès", wx.OK | wx.ICON_INFORMATION)

    def create_selection_controls(self):
        select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        reset_btn = wx.Button(self.editor_panel, label="Reset")
        reset_btn.Bind(wx.EVT_BUTTON, self.on_reset)
        
        self.companion_choice = wx.Choice(self.editor_panel, choices=self.get_available_companions())
        self.companion_choice.Bind(wx.EVT_CHOICE, self.on_companion_selected)
        
        select_sizer.Add(reset_btn, 0, wx.ALL|wx.CENTER, 5)
        select_sizer.Add(wx.StaticText(self.editor_panel, label="Compagnon :"), 0, wx.CENTER|wx.ALL, 5)
        select_sizer.Add(self.companion_choice, 1, wx.EXPAND|wx.ALL, 5)
        
        self.editor_sizer.Add(select_sizer, 0, wx.EXPAND|wx.ALL, 5)

    def get_available_companions(self):
        directory = 'Runelimit/companions'
        companions = []
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith('.json'):
                    companions.append(file[:-5])
        return sorted(companions)

    def on_companion_selected(self, event):
        if self.companion_choice.GetSelection() != -1:
            selected_companion = self.companion_choice.GetString(self.companion_choice.GetSelection())
            self.load_companion(selected_companion)

    def load_companion(self, companion_name):
        file_path = f'Runelimit/companions/{companion_name}.json'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for field_name, value in data.items():
                        if field_name in self.controls:
                            self.controls[field_name].SetValue(value)
            except json.JSONDecodeError:
                pass

    def on_reset(self, event):
        dialog = wx.MessageDialog(
            self,
            "Voulez-vous réinitialiser le formulaire ?",
            "Confirmation",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        
        if dialog.ShowModal() == wx.ID_YES:
            self.reset_fields()
            self.companion_choice.SetSelection(-1)

    def find_duplicate_companions(self, companion_name):
        duplicates = []
        current_companion_data = self.get_companion_data()
        
        directory = 'Runelimit/companions'
        for file in os.listdir(directory):
            if file.endswith('.json') and file != f"{companion_name}.json":
                path = os.path.join(directory, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        # Correction ici : 'health' -> 'pv'
                        relevant_fields = ['pv', 'distance', 'distance_degat', 
                                        'melee', 'melee_degat', 'magie', 'magie_degat']
                        
                        is_duplicate = all(
                            current_companion_data[field] == existing_data[field]
                            for field in relevant_fields
                        )
                        
                        if is_duplicate:
                            duplicates.append(file[:-5])
                except json.JSONDecodeError:
                    continue                  
        return duplicates
    def handle_duplicate_companions(self, companion_name, duplicates):
        message = f"Des compagnons identiques existent : {', '.join(duplicates)}\n"
        message += "Voulez-vous :\n"
        message += "1. Garder le nouveau compagnon\n"
        message += "2. Garder un compagnon existant\n"
        message += "3. Garder tous les compagnons"
        
        dialog = wx.SingleChoiceDialog(
            self,
            message,
            "Gestion des doublons",
            ['Nouveau compagnon', 'Compagnon existant', 'Garder tous']
        )
        
        if dialog.ShowModal() == wx.ID_OK:
            choice = dialog.GetSelection()
            if choice == 0:  # Nouveau compagnon
                for duplicate in duplicates:
                    file_path = f'Runelimit/companions/{duplicate}.json'
                    if os.path.exists(file_path):
                        os.remove(file_path)
                return True
            elif choice == 1:  # Compagnon existant
                return False
            else:  # Garder tous
                return True
                    
        dialog.Destroy()
        return False
