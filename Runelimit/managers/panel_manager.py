import wx
from events import TerrainHoverEvent
import random

class PanelManager:
    def __init__(self, parent):
        self.parent = parent
        self.panels = {}
        self.main_sizer = None
        self.faces = [
            ["Marais", "Riviere"],
            ["Montagne", "Plaine", "Route"],
            ["Riviere", "Foret"],
            ["Route", "Plaine", "Colline"],
            ["Route", "Riviere"],
            ["Route", "Plaine", "Colline"]
        ]
        
    def create_main_panel(self):
        main_panel = wx.Panel(self.parent)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        left_panel = wx.Panel(main_panel)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        canvas = wx.Panel(left_panel)
        canvas.SetBackgroundColour(wx.WHITE)
        left_sizer.Add(canvas, 1, wx.EXPAND)
        left_panel.SetSizer(left_sizer)
        
        self.main_sizer.Add(left_panel, 2, wx.EXPAND|wx.ALL, 5)
        
        self.panels['main'] = main_panel
        self.panels['left'] = left_panel
        self.panels['canvas'] = canvas
        
        return main_panel, self.main_sizer

    def create_movement_panel(self, player_name):
        movement_panel = wx.Panel(self.panels['main'])
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Tour
        turn_box = wx.StaticBox(movement_panel, label="Tour")
        turn_sizer = wx.StaticBoxSizer(turn_box, wx.VERTICAL)
        turn_text = wx.StaticText(movement_panel, label=f"Tour 1")
        turn_sizer.Add(turn_text, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(turn_sizer, 0, wx.EXPAND|wx.ALL, 5)

        # Joueur
        player_box = wx.StaticBox(movement_panel, label="Joueur actif")
        player_sizer = wx.StaticBoxSizer(player_box, wx.VERTICAL)
        player_text = wx.StaticText(movement_panel, label=player_name)
        player_sizer.Add(player_text, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(player_sizer, 0, wx.EXPAND|wx.ALL, 5)

        # Phase
        phase_box = wx.StaticBox(movement_panel, label="Phase")
        phase_sizer = wx.StaticBoxSizer(phase_box, wx.VERTICAL)
        phase_text = wx.StaticText(movement_panel, label="Mouvement")
        phase_sizer.Add(phase_text, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(phase_sizer, 0, wx.EXPAND|wx.ALL, 5)

        # Dés
        dice_box = wx.StaticBox(movement_panel, label="Dés de mouvement")
        dice_sizer = wx.StaticBoxSizer(dice_box, wx.VERTICAL)
        
        # Résultats des dés
        dice_results = wx.ScrolledWindow(movement_panel)
        dice_results.SetScrollRate(0, 20)
        results_sizer = wx.BoxSizer(wx.VERTICAL)
        dice_results.SetSizer(results_sizer)
        dice_sizer.Add(dice_results, 1, wx.EXPAND|wx.ALL, 5)
        
        main_sizer.Add(dice_sizer, 1, wx.EXPAND|wx.ALL, 5)

        # Boutons
        button_box = wx.StaticBox(movement_panel, label="Actions")
        button_sizer = wx.StaticBoxSizer(button_box, wx.VERTICAL)
        roll_btn = wx.Button(movement_panel, label="Lancer les dés")
        cancel_btn = wx.Button(movement_panel, label="Annuler le mouvement")
        cancel_btn.Hide()
        
        button_sizer.Add(roll_btn, 0, wx.EXPAND|wx.ALL, 5)
        button_sizer.Add(cancel_btn, 0, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

        movement_panel.SetSizer(main_sizer)
        
        return {
            'panel': movement_panel,
            'turn_text': turn_text,
            'player_text': player_text,
            'phase_text': phase_text,
            'dice_results': dice_results,
            'results_sizer': results_sizer,
            'roll_btn': roll_btn,
            'cancel_btn': cancel_btn
        }

    def create_dice_panel(self, dice_results, index, movement_phase):
        dice_panel = wx.Panel(dice_results)
        dice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        face_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        face = random.choice(self.faces)
        
        dice_btn = wx.Button(dice_panel, label=f"Dé {index+1}")
        dice_btn.SetBackgroundColour(wx.WHITE)
        dice_btn.dice_index = index
        
        face_buttons = []
        for terrain in face:
            btn = wx.Button(dice_panel, label=terrain)
            btn.SetBackgroundColour(wx.WHITE)
            face_buttons.append(btn)
            face_sizer.Add(btn, 0, wx.ALL|wx.CENTER, 2)
            
            self._bind_face_events(btn, face_buttons, dice_btn, movement_phase)
            
        dice_btn.Bind(wx.EVT_BUTTON, lambda evt: self._on_dice_click(evt, dice_btn, face_buttons))
        
        dice_sizer.Add(dice_btn, 0, wx.ALL|wx.CENTER, 5)
        dice_sizer.Add(face_sizer, 0, wx.ALL|wx.CENTER, 5)
        
        dice_panel.SetSizer(dice_sizer)
        return dice_panel

    def _bind_face_events(self, btn, face_buttons, dice_btn, movement_phase):
        def on_face_click(evt):
            if dice_btn.GetBackgroundColour() != wx.RED:
                if btn.GetBackgroundColour() == wx.GREEN:
                    btn.SetBackgroundColour(wx.WHITE)
                    movement_phase.selected_face = None
                    wx.PostEvent(self.parent, TerrainHoverEvent(terrain=None, is_selected=False))
                else:
                    if movement_phase.selected_face:
                        movement_phase.selected_face.SetBackgroundColour(wx.WHITE)
                    for b in face_buttons:
                        b.SetBackgroundColour(wx.WHITE)
                    btn.SetBackgroundColour(wx.GREEN)
                    movement_phase.selected_face = btn
                    wx.PostEvent(self.parent, TerrainHoverEvent(terrain=btn.GetLabel(), is_selected=True))
                    
        btn.Bind(wx.EVT_BUTTON, on_face_click)
        
        def on_hover(evt):
            if not movement_phase.selected_face:
                wx.PostEvent(self.parent, TerrainHoverEvent(terrain=btn.GetLabel(), is_selected=False))
            evt.Skip()
            
        def on_leave(evt):
            if not movement_phase.selected_face:
                wx.PostEvent(self.parent, TerrainHoverEvent(terrain=None, is_selected=False))
            evt.Skip()
            
        btn.Bind(wx.EVT_ENTER_WINDOW, on_hover)
        btn.Bind(wx.EVT_LEAVE_WINDOW, on_leave)

    def _on_dice_click(self, evt, dice_btn, face_buttons):
        current_color = dice_btn.GetBackgroundColour()
        new_color = wx.RED if current_color == wx.WHITE else wx.WHITE
        dice_btn.SetBackgroundColour(new_color)
        for btn in face_buttons:
            btn.Enable(new_color == wx.WHITE)

    def add_movement_phase(self, movement_phase):
        if self.main_sizer:
            self.main_sizer.Add(movement_phase, 1, wx.EXPAND|wx.ALL, 5)
            self.panels['movement'] = movement_phase
            
    def get_canvas(self):
        return self.panels.get('canvas')
    
    def refresh_panels(self):
        for panel in self.panels.values():
            panel.Refresh()
