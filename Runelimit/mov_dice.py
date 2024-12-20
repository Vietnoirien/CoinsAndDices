import wx
import random
from events import TerrainHoverEvent

class MovementPhase(wx.Panel):
    def __init__(self, parent, player_name):
        super().__init__(parent)
        self.turn_count = 1
        self.current_phase = "Mouvement"
        
        # Création du sizer principal
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Section compteur de tours
        turn_box = wx.StaticBox(self, label="Tour")
        turn_sizer = wx.StaticBoxSizer(turn_box, wx.VERTICAL)
        self.turn_text = wx.StaticText(self, label=f"Tour {self.turn_count}")
        turn_sizer.Add(self.turn_text, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(turn_sizer, 0, wx.EXPAND|wx.ALL, 5)

        # Section joueur actif
        player_box = wx.StaticBox(self, label="Joueur actif")
        player_sizer = wx.StaticBoxSizer(player_box, wx.VERTICAL)
        self.player_text = wx.StaticText(self, label=player_name)
        player_sizer.Add(self.player_text, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(player_sizer, 0, wx.EXPAND|wx.ALL, 5)

        
        # Section phase actuelle
        phase_box = wx.StaticBox(self, label="Phase")
        phase_sizer = wx.StaticBoxSizer(phase_box, wx.VERTICAL)
        self.phase_text = wx.StaticText(self, label=self.current_phase)
        phase_sizer.Add(self.phase_text, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(phase_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Section dés de mouvement
        dice_box = wx.StaticBox(self, label="Dés de mouvement")
        self.dice_sizer = wx.StaticBoxSizer(dice_box, wx.VERTICAL)
        
        # Bouton pour lancer les dés
        self.roll_btn = wx.Button(self, label="Lancer les dés")
        self.roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_dice)
        self.dice_sizer.Add(self.roll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        # Zone pour afficher les résultats des dés
        self.dice_results = wx.ScrolledWindow(self)
        self.dice_results.SetScrollRate(0, 20)
        self.results_sizer = wx.BoxSizer(wx.VERTICAL)
        self.dice_results.SetSizer(self.results_sizer)
        self.dice_sizer.Add(self.dice_results, 1, wx.EXPAND|wx.ALL, 5)
        
        main_sizer.Add(self.dice_sizer, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Configuration des faces des dés Runebound
        self.faces = [
            ["Marais", "Riviere"],
            ["Montagne", "Plaine", "Route"],
            ["Riviere", "Foret"],
            ["Route", "Plaine", "Colline"],
            ["Route", "Riviere"],
            ["Route", "Plaine", "Colline"]
        ]
        
        self.rerolls_used = set()
        self.parent = parent  # Garder une référence au parent pour les événements

    def create_dice_panel(self, index):
        dice_panel = wx.Panel(self.dice_results)
        dice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        face = random.choice(self.faces)
        
        # Bouton principal du dé
        dice_btn = wx.Button(dice_panel, label=f"Dé {index+1}")
        dice_btn.SetBackgroundColour(wx.WHITE)
        
        # Bouton de relance
        reroll_btn = wx.Button(dice_panel, label="↻")
        reroll_btn.dice_index = index
        
        if index in self.rerolls_used:
            reroll_btn.Disable()
            reroll_btn.SetBackgroundColour(wx.LIGHT_GREY)
        else:
            reroll_btn.SetBackgroundColour(wx.BLUE)
            reroll_btn.SetForegroundColour(wx.WHITE)

        def create_hover_handler(terrain_type):
            def on_hover(evt):
                print(f"Hover sur: {terrain_type}")  # Debug
                top_parent = self.GetTopLevelParent()
                wx.PostEvent(top_parent, TerrainHoverEvent(terrain=terrain_type))
            def on_leave(evt):
                print("Leave")  # Debug
                top_parent = self.GetTopLevelParent()
                wx.PostEvent(top_parent, TerrainHoverEvent(terrain=None))
            return on_hover, on_leave
        
        # Création des boutons de face
        face_buttons = []
        for terrain in face:
            btn = wx.Button(dice_panel, label=terrain)
            btn.SetBackgroundColour(wx.WHITE)
            face_buttons.append(btn)
            
            def create_face_handler(buttons, clicked_btn, dice_button):
                def on_click(evt):
                    if dice_button.GetBackgroundColour() != wx.RED:
                        # Si le bouton est déjà vert, on le désélectionne
                        if clicked_btn.GetBackgroundColour() == wx.GREEN:
                            clicked_btn.SetBackgroundColour(wx.WHITE)
                        else:
                            # Sinon on désélectionne les autres et on le sélectionne
                            for b in buttons:
                                b.SetBackgroundColour(wx.WHITE)
                            clicked_btn.SetBackgroundColour(wx.GREEN)
                return on_click
            
            btn.Bind(wx.EVT_BUTTON, create_face_handler(face_buttons, btn, dice_btn))
            dice_sizer.Add(btn, 0, wx.ALL, 5)
        
            hover, leave = create_hover_handler(terrain)
            btn.Bind(wx.EVT_ENTER_WINDOW, hover)
            btn.Bind(wx.EVT_LEAVE_WINDOW, leave)            

        def on_reroll(evt):
            btn = evt.GetEventObject()
            if btn.dice_index not in self.rerolls_used:
                self.rerolls_used.add(btn.dice_index)
                btn.SetBackgroundColour(wx.LIGHT_GREY)
                btn.Disable()
                self.reroll_single_die(btn.dice_index)
        
        reroll_btn.Bind(wx.EVT_BUTTON, on_reroll)
        
        def on_dice_click(evt):
            current_color = dice_btn.GetBackgroundColour()
            new_color = wx.RED if current_color == wx.WHITE else wx.WHITE
            dice_btn.SetBackgroundColour(new_color)
            for btn in face_buttons:
                btn.Enable(new_color == wx.WHITE)
        
        dice_btn.Bind(wx.EVT_BUTTON, on_dice_click)
        
        dice_sizer.Insert(0, dice_btn, 0, wx.ALL|wx.CENTER, 5)
        dice_sizer.Add(reroll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        dice_panel.SetSizer(dice_sizer)
        return dice_panel

    def reroll_single_die(self, index):
        new_panel = self.create_dice_panel(index)
        self.results_sizer.Replace(self.dice_panels[index], new_panel)
        self.dice_panels[index].Destroy()
        self.dice_panels[index] = new_panel
        self.results_sizer.Layout()
        self.dice_results.FitInside()

    def on_roll_dice(self, event):
        self.rerolls_used.clear()
        self.results_sizer.Clear(True)
        self.dice_panels = []
        
        for i in range(5):  # 5 dés par défaut pour Runebound
            dice_panel = self.create_dice_panel(i)
            self.dice_panels.append(dice_panel)
            self.results_sizer.Add(dice_panel, 0, wx.EXPAND|wx.ALL, 5)
        
        self.results_sizer.Layout()
        self.dice_results.FitInside()

    def next_turn(self):
        self.turn_count += 1
        self.turn_text.SetLabel(f"Tour {self.turn_count}")
