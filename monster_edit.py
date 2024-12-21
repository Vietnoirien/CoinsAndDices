import wx
import json
import os

class MonsterEditor(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)
        
        self.init_panel = wx.Panel(self)
        self.editor_panel = wx.Panel(self)
        
        self.main_sizer.Add(self.init_panel, 1, wx.EXPAND|wx.ALL|wx.GROW, 10)
        self.main_sizer.Add(self.editor_panel, 1, wx.EXPAND|wx.ALL|wx.GROW, 10)
        
        self.monster_buffer = {}
        self.editor_panel.Hide()
        
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor_panel.SetSizer(self.editor_sizer)
        
        # Class and monster selection setup
        class_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.class_choice = wx.Choice(self.editor_panel, choices=["1", "2", "3", "4"])
        self.monster_choice = wx.Choice(self.editor_panel, choices=self.get_available_monsters("1"))
        
        class_select_sizer.Add(wx.StaticText(self.editor_panel, label="Classe :"), 0, wx.ALL|wx.CENTER, 5)
        class_select_sizer.Add(self.class_choice, 1, wx.ALL, 5)
        class_select_sizer.Add(wx.StaticText(self.editor_panel, label="Monstre :"), 0, wx.ALL|wx.CENTER, 5)
        class_select_sizer.Add(self.monster_choice, 1, wx.ALL, 5)
        
        self.editor_sizer.Add(class_select_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Monster fields definition
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
        
        # Import section
        import_sizer = wx.BoxSizer(wx.VERTICAL)
        self.import_text = wx.TextCtrl(self.editor_panel, style=wx.TE_MULTILINE, size=(-1, 100))
        import_btn = wx.Button(self.editor_panel, label="Importer")
        import_btn.Bind(wx.EVT_BUTTON, self.on_import)
        
        import_sizer.Add(self.import_text, 1, wx.EXPAND|wx.ALL, 5)
        import_sizer.Add(import_btn, 0, wx.EXPAND|wx.ALL, 5)
        self.editor_sizer.Add(import_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Save/Cancel buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(self.editor_panel, label="Sauvegarder")
        cancel_btn = wx.Button(self.editor_panel, label="Annuler")
        
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        button_sizer.Add(save_btn, 1, wx.ALL, 5)
        button_sizer.Add(cancel_btn, 1, wx.ALL, 5)
        self.editor_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Bindings
        self.class_choice.Bind(wx.EVT_CHOICE, self.on_class_selected)
        self.monster_choice.Bind(wx.EVT_CHOICE, self.on_monster_selected)
        
        self.ensure_directory_structure()

    def create_fields(self):
        self.scroll_window = wx.ScrolledWindow(self.editor_panel)
        self.scroll_window.SetScrollRate(0, 20)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        grid_sizer = wx.FlexGridSizer(cols=2, vgap=2, hgap=10)
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
                control.SetInitialSize((80, 20))
        
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

    def save_monster(self, data):
        if self.class_choice.GetSelection() == -1:
            return False
            
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
        if self.monster_choice.GetSelection() != -1:
            selected_class = self.class_choice.GetString(self.class_choice.GetSelection())
            selected_monster = self.monster_choice.GetString(self.monster_choice.GetSelection())
            self.load_monster(selected_class, selected_monster)
