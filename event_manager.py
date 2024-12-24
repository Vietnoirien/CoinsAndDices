import wx
import json
from typing import Dict, Any


class EventManager:
    def __init__(self, hex_manager):
        self.hex_manager = hex_manager
        self.tile_events = {}
        self.event_types = ["None", "City", "Tier1", "Tier2", "Tier3", "Tier4"]
        self.load_events()

    def create_event_panel(self, parent):
        panel = wx.Panel(parent)
        self.editor_panel = wx.Panel(panel)
        editor_sizer = wx.BoxSizer(wx.VERTICAL)

        # Ajout des informations de la tuile sélectionnée
        self.tile_info = wx.StaticText(self.editor_panel, label="")
        self.biome_info = wx.StaticText(self.editor_panel, label="")

        title_label = wx.StaticText(self.editor_panel, label="Type d'événement")
    
        # Création du menu déroulant
        self.event_choice = wx.Choice(self.editor_panel, choices=self.event_types)
        self.event_choice.SetSelection(0)  # Sélectionne "None" par défaut
    
        self.event_text = wx.TextCtrl(self.editor_panel, style=wx.TE_MULTILINE)

        # Création d'un sizer horizontal pour les boutons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(self.editor_panel, label="Sauvegarder")
        cancel_button = wx.Button(self.editor_panel, label="Annuler")
    
        button_sizer.Add(save_button, 1, wx.ALL, 5)
        button_sizer.Add(cancel_button, 1, wx.ALL, 5)

        editor_sizer.Add(self.tile_info, 0, wx.ALL, 5)
        editor_sizer.Add(self.biome_info, 0, wx.ALL, 5)
        editor_sizer.Add(title_label, 0, wx.ALL, 5)
        editor_sizer.Add(self.event_choice, 0, wx.EXPAND|wx.ALL, 5)
        editor_sizer.Add(self.event_text, 1, wx.EXPAND|wx.ALL, 5)
        editor_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

        self.editor_panel.SetSizer(editor_sizer)

        # Sizer principal
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.editor_panel, 1, wx.EXPAND)
        panel.SetSizer(main_sizer)

        save_button.Bind(wx.EVT_BUTTON, self.on_save_event)
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        return panel

    def on_cancel(self, event):
            # Réinitialiser les champs
            self.event_choice.SetSelection(0)
            self.event_text.SetValue("")
        
            # Retourner au panneau principal
            main_frame = wx.GetTopLevelParent(self.editor_panel)
            panel_manager = main_frame.panel_manager
            panel_manager.show_buttons_panel()

    def update_tile_info(self, hex_pos):
        if hex_pos:
            biome = self.hex_manager.biome_manager.get_biome(hex_pos)
            self.tile_info.SetLabel(f"Position: {hex_pos}")
            self.biome_info.SetLabel(f"Biome: {biome}")

    def on_save_event(self, event):
        if self.hex_manager.last_clicked_hex:
            hex_pos = str(self.hex_manager.last_clicked_hex)
            event_type = self.event_choice.GetString(self.event_choice.GetSelection())
            event_text = self.event_text.GetValue()
        
            if event_type != "None":
                self.tile_events[hex_pos] = {
                    "type": event_type,
                    "description": event_text
                }
            else:
                # Si type est "None", on supprime l'événement
                self.tile_events.pop(hex_pos, None)
        
            # On sauvegarde une seule fois à la fin
            self.save_events()
            
    def load_events(self):
        try:
            with open('Runelimit/biomes.json', 'r') as f:
                data = json.load(f)
                self.tile_events = data.get('events', {})
        except (FileNotFoundError, json.JSONDecodeError):
            self.tile_events = {}
            
    def save_events(self):
        try:
            with open('Runelimit/biomes.json', 'r') as f:
                data = json.load(f)
            
            data['events'] = self.tile_events
            
            with open('Runelimit/biomes.json', 'w') as f:
                json.dump(data, f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {
                'biomes': {},
                'river_paths': {'rivers': [], 'routes': []},
                'events': self.tile_events
            }
            with open('Runelimit/biomes.json', 'w') as f:
                json.dump(data, f)

    def get_tile_event(self, hex_pos):
        event_data = self.tile_events.get(str(hex_pos), {})
        if event_data:
            return event_data.get("type", "None"), event_data.get("description", "")
        return "None", ""

    def on_hex_click(self, hex_pos):
        if hex_pos:
            self.hex_manager.set_highlighted_hex(hex_pos)
            event_type, event_desc = self.get_tile_event(hex_pos)  # On déstructure le tuple
            self.event_choice.SetStringSelection(event_type)
            self.event_text.SetValue(event_desc)  # On utilise uniquement la description
            self.hex_manager.last_clicked_hex = hex_pos
