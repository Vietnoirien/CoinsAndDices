import wx
import random
from events import TerrainHoverEvent

class MovementPhase:
    def __init__(self, panel_manager, player_name):
        self.panel_manager = panel_manager
        self.components = panel_manager.create_movement_panel(player_name)
        
        self.turn_count = 1
        self.current_phase = "Mouvement"
        self.selected_face = None
        self.player_movements = []
        self.last_movement = None
        self.last_face_used = None
        self.player = None
        self.starting_position = None
        self.movement_history = []
        self.dice_panels = []
        self.rerolls_used = set()
        
        self.components['roll_btn'].Bind(wx.EVT_BUTTON, self.on_roll_dice)
        self.components['cancel_btn'].Bind(wx.EVT_BUTTON, self.on_cancel_move)
        self.components['confirm_btn'].Bind(wx.EVT_BUTTON, self.on_confirm_movement)

    def lock_selected_face(self):
        if self.selected_face:
            dice_panel = self.selected_face.GetParent()
            dice_btn = dice_panel.GetChildren()[0]
            
            movement_info = {
                'face': self.selected_face,
                'movement': self.selected_face.GetLabel(),
                'dice_panel': dice_panel,
                'dice_btn': dice_btn,
                'position': self.player.position
            }
            self.movement_history.append(movement_info)
            
            self.last_face_used = self.selected_face
            self.last_movement = self.selected_face.GetLabel()
            
            dice_btn.SetBackgroundColour(wx.RED)
            dice_btn.Disable()
            
            dice_index = dice_btn.dice_index
            self.rerolls_used.add(dice_index)
            
            self.selected_face.Disable()
            self.player_movements.append(self.selected_face.GetLabel())
            self.selected_face = None
            
            # Montrer le bouton de confirmation dès qu'un mouvement est effectué
            self.components['confirm_btn'].Show()

    def on_roll_dice(self, event):
        if not self.player:
            return
        
        self.reset_dice()
        self.dice_panels = []
        self.starting_position = self.player.position
        
        for i in range(5):
            dice_panel = self.panel_manager.create_dice_panel(
                self.components['dice_results'], 
                i, 
                self
            )
            self.dice_panels.append(dice_panel)
            self.components['results_sizer'].Add(dice_panel, 0, wx.EXPAND|wx.ALL, 5)
        
        self.components['roll_btn'].Hide()
        self.components['cancel_btn'].Show()
        
        self.components['results_sizer'].Layout()
        self.components['dice_results'].FitInside()
        self.components['panel'].Layout()

    def cancel_last_move(self):
        if self.movement_history:
            last_move = self.movement_history.pop()
            
            if len(self.player_movements) == 1:
                self.player.position = self.starting_position
                self.panel_manager.parent.players[0].position = self.starting_position
            else:
                if len(self.movement_history) > 0:
                    previous_move = self.movement_history[-1]
                    self.player.position = previous_move['position']
                    self.panel_manager.parent.players[0].position = previous_move['position']
            
            last_move['dice_btn'].SetBackgroundColour(wx.WHITE)
            last_move['dice_btn'].Enable()
            last_move['face'].Enable()
            last_move['face'].SetBackgroundColour(wx.WHITE)
            
            if self.player_movements:
                self.player_movements.pop()
            
            # Cacher le bouton de confirmation si aucun mouvement n'est actif
            if not self.movement_history:
                self.components['confirm_btn'].Hide()
            
            self.panel_manager.parent.canvas.Refresh()

    def on_cancel_move(self, event):
        self.cancel_last_move()

    def on_confirm_movement(self, event):
        self.panel_manager.parent.start_event_phase()
        self.reset_dice()

    def set_player(self, player):
        self.player = player
        self.starting_position = player.position

    def reset_dice(self):
        self.selected_face = None
        self.player_movements = []
        self.movement_history = []
        self.starting_position = None
        self.rerolls_used.clear()
        
        self.components['roll_btn'].Enable()
        self.components['roll_btn'].Show()
        self.components['cancel_btn'].Hide()
        self.components['confirm_btn'].Hide()
        
        # Effacer uniquement les dés
        self.components['results_sizer'].Clear(True)
        self.components['panel'].Layout()

    def next_turn(self):
        self.turn_count += 1
        self.components['turn_text'].SetLabel(f"Tour {self.turn_count}")
