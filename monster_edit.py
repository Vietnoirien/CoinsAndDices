import wx
import json
import os

class MonsterEditor(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
    
        # Main vertical sizer for the entire editor
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
    
        # Create panels with proper expansion
        self.init_panel = wx.Panel(self)
        self.editor_panel = wx.Panel(self)
    
        # Add panels to main sizer with correct proportions
        self.main_sizer.Add(self.init_panel, 0, wx.EXPAND|wx.ALL, 5)
        self.main_sizer.Add(self.editor_panel, 1, wx.EXPAND|wx.ALL, 5)
    
        self.SetSizer(self.main_sizer)
    
        self.monster_buffer = {}
        self.editor_panel.Hide()
        # Ajouter le bouton d'initialisation et le bouton reset dans le init_panel
        init_sizer = wx.BoxSizer(wx.HORIZONTAL)
        init_btn = wx.Button(self.init_panel, label="Initialiser les monstres de base")
        reset_btn = wx.Button(self.init_panel, label="Réinitialiser aux valeurs par défaut")
    
        init_btn.Bind(wx.EVT_BUTTON, self.on_init_default_monsters)
        reset_btn.Bind(wx.EVT_BUTTON, self.on_reset_to_default)
    
        init_sizer.Add(init_btn, 0, wx.ALL, 5)
        init_sizer.Add(reset_btn, 0, wx.ALL, 5)
        self.init_panel.SetSizer(init_sizer)
        
        # Editor panel sizer setup
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor_panel.SetSizer(self.editor_sizer)
        # Class and monster selection setup with proper spacing
        class_select_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Ajout du bouton de réinitialisation
        reset_class_btn = wx.Button(self.editor_panel, label="Reset")
        reset_class_btn.Bind(wx.EVT_BUTTON, self.on_reset_class)

        self.class_choice = wx.Choice(self.editor_panel, choices=["1", "2", "3", "4"])
        self.monster_choice = wx.Choice(self.editor_panel, choices=self.get_available_monsters("1"))

        class_select_sizer.Add(reset_class_btn, 0, wx.ALL|wx.CENTER, 5)
        class_select_sizer.Add(wx.StaticText(self.editor_panel, label="Classe :"), 0, wx.CENTER|wx.ALL, 5)
        class_select_sizer.Add(self.class_choice, 1, wx.EXPAND|wx.ALL, 5)
        class_select_sizer.Add(wx.StaticText(self.editor_panel, label="Monstre :"), 0, wx.CENTER|wx.ALL, 5)
        class_select_sizer.Add(self.monster_choice, 1, wx.EXPAND|wx.ALL, 5)
        self.editor_sizer.Add(class_select_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Monster fields definition
        self.fields = {
            'name': ('Nom', wx.TextCtrl),
            'health': ('Points de Vie', lambda p: wx.SpinCtrl(p, min=1, max=100)),
            'description': ('Description', wx.TextCtrl),
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
        
        # Import section with proper sizing
        import_sizer = wx.BoxSizer(wx.VERTICAL)
        self.import_text = wx.TextCtrl(self.editor_panel, style=wx.TE_MULTILINE, size=(-1, 100))
        import_btn = wx.Button(self.editor_panel, label="Importer")
        import_btn.Bind(wx.EVT_BUTTON, self.on_import)
        
        import_sizer.Add(self.import_text, 1, wx.EXPAND|wx.ALL, 5)
        import_sizer.Add(import_btn, 0, wx.EXPAND|wx.ALL, 5)
        self.editor_sizer.Add(import_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Save/Cancel buttons with proper sizing
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(self.editor_panel, label="Sauvegarder")
        delete_btn = wx.Button(self.editor_panel, label="Supprimer")  # Nouveau bouton
        cancel_btn = wx.Button(self.editor_panel, label="Annuler")
        
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)  # Nouveau binding
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        button_sizer.Add(save_btn, 0, wx.ALL, 5)
        button_sizer.Add(delete_btn, 0, wx.ALL, 5)  # Ajout du bouton
        button_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        self.editor_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)        
        # Bindings
        self.class_choice.Bind(wx.EVT_CHOICE, self.on_class_selected)
        self.monster_choice.Bind(wx.EVT_CHOICE, self.on_monster_selected)
        
        self.ensure_directory_structure()

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
                    control.SetMinSize((32, -1))  # Set minimum width to 32 pixels
            self.controls[field_name] = control
            grid_sizer.Add(label_widget, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 15)
            grid_sizer.Add(control, 0, wx.ALIGN_RIGHT, 5)

        scroll_sizer.Add(grid_sizer, 1, wx.EXPAND|wx.ALL, 2)
        self.scroll_window.SetSizer(scroll_sizer)
        self.editor_sizer.Add(self.scroll_window, 1, wx.EXPAND)
        
    def ensure_directory_structure(self):
        base_dir = 'Runelimit/monsters'
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        for class_num in range(1, 5):
            class_dir = f'{base_dir}/class_{class_num}'
            if not os.path.exists(class_dir):
                os.makedirs(class_dir)

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

    def find_duplicate_monsters(self, monster_name):
        duplicates = []
        current_monster_data = self.get_monster_data()
        
        for class_num in range(1, 5):
            path = f'Runelimit/monsters/class_{class_num}/{monster_name}.json'
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        # Compare uniquement les attributs pertinents
                        relevant_fields = ['health', 'distance', 'distance_degat', 
                                         'melee', 'melee_degat', 'magie', 'magie_degat']
                        
                        is_duplicate = all(
                            current_monster_data[field] == existing_data[field]
                            for field in relevant_fields
                        )
                        
                        if is_duplicate:
                            duplicates.append(str(class_num))
                except json.JSONDecodeError:
                    continue                  
        return duplicates
    
    def handle_duplicate_monsters(self, monster_name, duplicates):
        message = f"Un monstre identique existe dans les classes : {', '.join(duplicates)}\n"
        message += "Voulez-vous :\n"
        message += "1. Garder le nouveau monstre et supprimer les doublons\n"
        message += "2. Garder un monstre existant\n"
        message += "3. Garder tous les monstres"
        
        dialog = wx.SingleChoiceDialog(
            self,
            message,
            "Gestion des doublons",
            ['Nouveau monstre', 'Monstre existant', 'Garder tous']
        )
        
        if dialog.ShowModal() == wx.ID_OK:
            choice = dialog.GetSelection()
            if choice == 0:  # Nouveau monstre
                for class_num in duplicates:
                    file_path = f'Runelimit/monsters/class_{class_num}/{monster_name}.json'
                    if os.path.exists(file_path):
                        os.remove(file_path)
                return True
            elif choice == 1:  # Monstre existant
                class_dialog = wx.SingleChoiceDialog(
                    self,
                    "Choisir la classe à conserver :",
                    "Sélection de classe",
                    duplicates
                )
                if class_dialog.ShowModal() == wx.ID_OK:
                    selected_class = class_dialog.GetStringSelection()
                    # Supprimer tous les autres doublons sauf celui sélectionné
                    for class_num in duplicates:
                        if class_num != selected_class:
                            file_path = f'Runelimit/monsters/class_{class_num}/{monster_name}.json'
                            if os.path.exists(file_path):
                                os.remove(file_path)
                    return False
                class_dialog.Destroy()
            else:  # Garder tous
                return True
                
        dialog.Destroy()
        return False
    
    def save_monster(self, data):
        if self.class_choice.GetSelection() == -1:
            return False
        
        selected_class = self.class_choice.GetString(self.class_choice.GetSelection())
        monster_name = data['name']
    
        duplicates = self.find_duplicate_monsters(monster_name)
        if duplicates:
            if not self.handle_duplicate_monsters(monster_name, duplicates):
                return False
            
        directory = f'Runelimit/monsters/class_{selected_class}'
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        file_path = f'{directory}/{monster_name}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.monster_choice.SetItems(self.get_available_monsters(selected_class))
        self.monster_choice.SetStringSelection(monster_name)
        return True   
      
    def get_available_monsters(self, class_num):
        directory = f'Runelimit/monsters/class_{class_num}'
        if not os.path.exists(directory):
            os.makedirs(directory)
            return []
        
        monsters = []
        for file in os.listdir(directory):
            if file.endswith('.json'):
                monsters.append(file[:-5])
        return sorted(monsters)

    def fill_form_from_text(self, text):
        data = self.parse_monster_text(text)
        for field_name, value in data.items():
            if field_name in self.controls:
                self.controls[field_name].SetValue(value)

    def on_import(self, event):
        text = self.import_text.GetValue()
        if text.strip():
            self.fill_form_from_text(text)

    def on_save(self, event):
        data = self.get_monster_data()
        if not data['name'].strip():
            wx.MessageBox("Le nom du monstre ne peut pas être vide", "Erreur", wx.OK | wx.ICON_ERROR)
            return
            
        if self.save_monster(data):
            wx.MessageBox("Monstre sauvegardé avec succès", "Succès", wx.OK | wx.ICON_INFORMATION)

    def on_cancel(self, event):
        self.reset_fields()
        main_frame = wx.GetTopLevelParent(self)
        panel_manager = main_frame.panel_manager
        panel_manager.show_buttons_panel()
        
    def reset_fields(self):
        for control in self.controls.values():
            if isinstance(control, wx.TextCtrl):
                control.SetValue("")
            else:
                control.SetValue(control.GetMin())

    def on_class_selected(self, event):
        if self.class_choice.GetSelection() != -1:
            self.monster_buffer = self.get_monster_data()
        
        selected_class = self.class_choice.GetString(self.class_choice.GetSelection())
        self.monster_choice.SetItems(self.get_available_monsters(selected_class))
        self.monster_choice.SetSelection(-1)
        
        if self.monster_buffer:
            for field_name, value in self.monster_buffer.items():
                if field_name in self.controls:
                    self.controls[field_name].SetValue(value)

    def on_monster_selected(self, event):
        class_selection = self.class_choice.GetSelection()
        monster_selection = self.monster_choice.GetSelection()
    
        if class_selection != -1 and monster_selection != -1:
            selected_class = self.class_choice.GetString(class_selection)
            selected_monster = self.monster_choice.GetString(monster_selection)
            self.load_monster(selected_class, selected_monster)

    def parse_monster_text(self, text):
        # Filtrer les lignes non vides
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        # Extraction du nom (première ligne)
        name = lines[0]
        
        # Recherche du nombre de points de vie
        health = None
        current_line = 1
        for i, line in enumerate(lines[1:], 1):
            try:
                health = int(line)
                current_line = i + 1
                break
            except ValueError:
                continue
                
        if health is None:
            raise ValueError("Points de vie non trouvés")
        
        # Recherche de la description entre *
        description = ""
        for i, line in enumerate(lines[current_line:], current_line):
            if line.startswith('*') and line.endswith('*'):
                description = line.strip('*')
                current_line = i + 1
                break
        
        # Les 3 dernières lignes sont toujours les stats de combat
        combat_stats = lines[-3:]
        distance, distance_degat = map(int, combat_stats[0].split('/'))
        melee, melee_degat = map(int, combat_stats[1].split('/'))
        magie, magie_degat = map(int, combat_stats[2].split('/'))
        
        return {
            'name': name,
            'health': health,
            'description': description,
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

    def parse_class_file(self, file_content):
        monsters = []
        current_monster = []

        for line in file_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('-'):
                current_monster.append(line)
            elif line.startswith('-'):
                if current_monster:
                    name = current_monster[0]
                    health = int(''.join(filter(str.isdigit, current_monster[1])))
                
                    description = ""
                    for line in current_monster:
                        if line.startswith('*') and line.endswith('*'):
                            description = line.strip('*')
                            break
                
                    stats = [x for x in current_monster if '/' in x][-3:]
                    
                    # Gestion spéciale pour les stats variables
                    def parse_stat(stat_str):
                        parts = stat_str.split('/')
                        val1 = int(''.join(filter(str.isdigit, parts[0])))
                        # Si la valeur contient 'x', on met 0 par défaut
                        val2 = 0 if 'x' in parts[1].lower() else int(''.join(filter(str.isdigit, parts[1])))
                        return val1, val2

                    distance, distance_degat = parse_stat(stats[0])
                    melee, melee_degat = parse_stat(stats[1])
                    magie, magie_degat = parse_stat(stats[2])
                
                    monster_data = {
                        'name': name,
                        'health': health,
                        'description': description,
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
                    monsters.append(monster_data)
                current_monster = []

        return monsters
    
    def on_delete(self, event):
        if self.class_choice.GetSelection() == -1 or self.monster_choice.GetSelection() == -1:
            wx.MessageBox("Veuillez sélectionner un monstre à supprimer", "Erreur", wx.OK | wx.ICON_ERROR)
            return

        selected_class = self.class_choice.GetString(self.class_choice.GetSelection())
        selected_monster = self.monster_choice.GetString(self.monster_choice.GetSelection())

        # Vérifier si le monstre est utilisé dans une partie en cours
        file_path = f'Runelimit/monsters/class_{selected_class}/{selected_monster}.json'

        try:
            dialog = wx.MessageDialog(
                self,
                f"Êtes-vous sûr de vouloir supprimer le monstre {selected_monster} ?\nCette action est irréversible.",
                "Confirmation de suppression",
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
            )

            if dialog.ShowModal() == wx.ID_YES:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        # Mettre à jour l'interface
                        self.monster_choice.SetItems(self.get_available_monsters(selected_class))
                        self.monster_choice.SetSelection(-1)
                        self.reset_fields()
                        wx.MessageBox("Monstre supprimé avec succès", "Succès", wx.OK | wx.ICON_INFORMATION)
                    except OSError as e:
                        wx.MessageBox(f"Erreur lors de la suppression : {str(e)}", "Erreur", wx.OK | wx.ICON_ERROR)
                else:
                    wx.MessageBox("Le fichier du monstre n'existe plus", "Erreur", wx.OK | wx.ICON_ERROR)
        finally:
            dialog.Destroy()

    def on_reset_to_default(self, event):
        dialog = wx.MessageDialog(
            self,
            "Cette action va supprimer tous les monstres existants et réinitialiser avec les monstres par défaut. Continuer ?",
            "Confirmation de réinitialisation",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        
        if dialog.ShowModal() == wx.ID_YES:
            total_success = 0
            for class_num in range(1, 5):
                total_success += self.reset_class(class_num)
            
            # Mise à jour de l'interface
            current_class = self.class_choice.GetSelection()
            if current_class != -1:
                self.monster_choice.SetItems(self.get_available_monsters(str(current_class + 1)))
                self.monster_choice.SetSelection(-1)
            self.reset_fields()
            
            wx.MessageBox(f"{total_success} monstres ont été réinitialisés avec succès", 
                        "Succès", wx.OK | wx.ICON_INFORMATION)

    def on_init_default_monsters(self, event):
        total_success_count = 0
        for class_num in range(1, 5):
            total_success_count += self.reset_class(class_num)
                    
        wx.MessageBox(f"{total_success_count} monstres ont été initialisés avec succès", 
                    "Succès", wx.OK | wx.ICON_INFORMATION)

    def reset_class(self, class_num):
        # Nettoyer le répertoire de la classe
        directory = f'Runelimit/monsters/class_{class_num}'
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith('.json'):
                    os.remove(os.path.join(directory, file))
        
        # Charger et initialiser les monstres par défaut pour cette classe
        file_path = f'Runelimit/monsters/class_{class_num}/class{class_num}.txt'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    monsters = self.parse_class_file(content)
                    
                    # Forcer la sélection de la classe
                    self.class_choice.SetSelection(class_num - 1)
                    
                    # Sauvegarder chaque monstre
                    success_count = 0
                    for monster_data in monsters:
                        if self.save_monster(monster_data):
                            success_count += 1
                    return success_count
            except Exception as e:
                wx.MessageBox(f"Erreur lors du traitement de la classe {class_num}: {str(e)}", 
                            "Erreur", wx.OK | wx.ICON_ERROR)
        return 0
    
    def on_reset_class(self, event):
        if self.class_choice.GetSelection() == -1:
            wx.MessageBox("Veuillez sélectionner une classe", "Erreur", wx.OK | wx.ICON_ERROR)
            return
        
        selected_class = self.class_choice.GetString(self.class_choice.GetSelection())
    
        # Dialogue de confirmation
        dialog = wx.MessageDialog(
            self,
            f"Êtes-vous sûr de vouloir réinitialiser tous les monstres de la classe {selected_class} ?\nCette action est irréversible.",
            "Confirmation de réinitialisation",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
    
        if dialog.ShowModal() == wx.ID_YES:
            success_count = self.reset_class(int(selected_class))
        
            # Mise à jour de la liste des monstres
            self.monster_choice.SetItems(self.get_available_monsters(selected_class))
            self.monster_choice.SetSelection(-1)
            self.reset_fields()
        
            wx.MessageBox(f"{success_count} monstres ont été réinitialisés pour la classe {selected_class}", 
                        "Succès", wx.OK | wx.ICON_INFORMATION)
    
        dialog.Destroy()
