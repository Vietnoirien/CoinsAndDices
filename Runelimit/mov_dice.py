import wx
import random
from events import TerrainHoverEvent
class MovementPhase(wx.Panel):
    def __init__(self, parent, player_name):
        super().__init__(parent)
        self.turn_count = 1
        self.current_phase = "Mouvement"
        self.selected_face = None
        self.player_movements = []
        self.last_movement = None
        self.last_face_used = None
        self.player = None  # Référence au joueur
        self.starting_position = None
        self.movement_history = []  # Nouvelle liste pour stocker l'historique des mouvements
    
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
    
        # Bouton d'annulation
        self.cancel_btn = wx.Button(self, label="Annuler le mouvement")
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel_move)
        main_sizer.Add(self.cancel_btn, 0, wx.EXPAND|wx.ALL, 5)
    
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
        self.parent = parent

    def lock_selected_face(self):
        if self.selected_face:
            # Capturer la position de départ AVANT tout mouvement
            if not self.player_movements and self.starting_position is None:
                self.starting_position = self.GetTopLevelParent().get_player_position()
                print(f"Setting starting position to: {self.starting_position}")
                
            dice_panel = self.selected_face.GetParent()
            dice_btn = dice_panel.GetChildren()[0]
            
            # Stocker toutes les informations nécessaires pour l'annulation
            movement_info = {
                'face': self.selected_face,
                'movement': self.selected_face.GetLabel(),
                'dice_panel': dice_panel,
                'dice_btn': dice_btn,
                'position': self.player.position
            }
            self.movement_history.append(movement_info)
            
            # Sauvegarder l'état avant le verrouillage
            self.last_face_used = self.selected_face
            self.last_movement = self.selected_face.GetLabel()
            
            # Désactiver le dé principal
            dice_btn.SetBackgroundColour(wx.RED)
            dice_btn.Disable()
            
            # Récupérer l'index directement depuis le bouton principal
            dice_index = dice_btn.dice_index
            
            # Désactiver le bouton de relance
            reroll_btn = dice_panel.GetChildren()[-1]
            self.rerolls_used.add(dice_index)
            reroll_btn.Disable()
            reroll_btn.SetBackgroundColour(wx.LIGHT_GREY)
            
            # Désactiver la face sélectionnée
            self.selected_face.Disable()
            
            # Stocker le mouvement
            self.player_movements.append(self.selected_face.GetLabel())
            self.selected_face = None    
    
    def create_dice_panel(self, index):
        dice_panel = wx.Panel(self.dice_results)
        dice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        face_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Nouveau sizer horizontal pour les faces
    
        face = random.choice(self.faces)
    
        # Bouton principal du dé
        dice_btn = wx.Button(dice_panel, label=f"Dé {index+1}")
        dice_btn.SetBackgroundColour(wx.WHITE)
        dice_btn.dice_index = index
        # Création des boutons de face
        face_buttons = []
        for terrain in face:
            btn = wx.Button(dice_panel, label=terrain)
            btn.SetBackgroundColour(wx.WHITE)
            face_buttons.append(btn)
            face_sizer.Add(btn, 0, wx.ALL|wx.CENTER, 2)  # Espacement de 2 pixels entre les faces

            def create_face_handler(buttons, clicked_btn, dice_button):
                def on_click(evt):
                    if dice_button.GetBackgroundColour() != wx.RED:
                        if clicked_btn.GetBackgroundColour() == wx.GREEN:
                            clicked_btn.SetBackgroundColour(wx.WHITE)
                            self.selected_face = None
                            top_parent = self.GetTopLevelParent()
                            wx.PostEvent(top_parent, TerrainHoverEvent(terrain=None, is_selected=False))
                        else:
                            if self.selected_face:
                                self.selected_face.SetBackgroundColour(wx.WHITE)
                            for b in buttons:
                                b.SetBackgroundColour(wx.WHITE)
                            clicked_btn.SetBackgroundColour(wx.GREEN)
                            self.selected_face = clicked_btn
                            top_parent = self.GetTopLevelParent()
                            wx.PostEvent(top_parent, TerrainHoverEvent(terrain=clicked_btn.GetLabel(), is_selected=True))
                return on_click

            def create_hover_handler(terrain_type):
                def on_hover(evt):
                    if not self.selected_face:
                        top_parent = self.GetTopLevelParent()
                        wx.PostEvent(top_parent, TerrainHoverEvent(terrain=terrain_type, is_selected=False))
                    evt.Skip()
                def on_leave(evt):
                    if not self.selected_face:
                        top_parent = self.GetTopLevelParent()
                        wx.PostEvent(top_parent, TerrainHoverEvent(terrain=None, is_selected=False))
                    evt.Skip()
                return on_hover, on_leave
            
            btn.Bind(wx.EVT_BUTTON, create_face_handler(face_buttons, btn, dice_btn))
            hover, leave = create_hover_handler(terrain)
            btn.Bind(wx.EVT_ENTER_WINDOW, hover)
            btn.Bind(wx.EVT_LEAVE_WINDOW, leave)


#        def on_reroll(evt):
#            btn = evt.GetEventObject()
#            if btn.dice_index not in self.rerolls_used:
#                self.rerolls_used.add(btn.dice_index)
#                btn.SetBackgroundColour(wx.LIGHT_GREY)
#                btn.Disable()
#                self.reroll_single_die(btn.dice_index)
        
#        reroll_btn.Bind(wx.EVT_BUTTON, on_reroll)
      
        def on_dice_click(evt):
            current_color = dice_btn.GetBackgroundColour()
            new_color = wx.RED if current_color == wx.WHITE else wx.WHITE
            dice_btn.SetBackgroundColour(new_color)
            for btn in face_buttons:
                btn.Enable(new_color == wx.WHITE)
        
        dice_btn.Bind(wx.EVT_BUTTON, on_dice_click)
        
        dice_sizer.Insert(0, dice_btn, 0, wx.ALL|wx.CENTER, 5)
        dice_sizer.Add(face_sizer, 0, wx.ALL|wx.CENTER, 5)  # Ajout du face_sizer
        
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
        self.selected_face = None
        
        # Créer les 5 dés
        for i in range(5):
            dice_panel = self.create_dice_panel(i)
            self.dice_panels.append(dice_panel)
            self.results_sizer.Add(dice_panel, 0, wx.EXPAND|wx.ALL, 5)
        
        # Désactiver et cacher le bouton de lancement
        self.roll_btn.Disable()
        self.roll_btn.Hide()
        
        self.results_sizer.Layout()
        self.dice_results.FitInside()

    def next_turn(self):
        self.turn_count += 1
        self.turn_text.SetLabel(f"Tour {self.turn_count}")
    
    def cancel_last_move(self):
        if self.movement_history:  # Utiliser movement_history au lieu de last_face_used
            # Récupérer le dernier mouvement de l'historique
            last_move = self.movement_history.pop()
    
            # Restaurer la position
            top_window = self.GetTopLevelParent()
            if len(self.player_movements) == 1:
                self.player.position = self.starting_position
                top_window.players[0].position = self.starting_position
            else:
                # Restaurer à la position précédente
                if len(self.movement_history) > 0:
                    previous_move = self.movement_history[-1]
                    self.player.position = previous_move['position']
                    top_window.players[0].position = previous_move['position']
        
            # Réinitialiser les éléments visuels
            dice_btn = last_move['dice_btn']
            dice_btn.SetBackgroundColour(wx.WHITE)
            dice_btn.Enable()
    
            reroll_btn = last_move['dice_panel'].GetChildren()[-1]
            if dice_btn.dice_index in self.rerolls_used:
                self.rerolls_used.remove(dice_btn.dice_index)
            reroll_btn.Enable()
            reroll_btn.SetBackgroundColour(wx.WHITE)
    
            last_move['face'].Enable()
            last_move['face'].SetBackgroundColour(wx.WHITE)
    
            if self.player_movements:
                self.player_movements.pop()
        
            # Forcer le rafraîchissement du canvas
            top_window.canvas.Refresh()
    def on_cancel_move(self, event):
        self.cancel_last_move()

    def set_player(self, player):
        self.player = player
        self.starting_position = player.position