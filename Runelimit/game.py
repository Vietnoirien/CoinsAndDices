import wx
from Hyperbolic_Paraboloide import create_paraboloid_canvas
from player import Player
import random
from managers.manager_setup import setup_managers

class RunelimitGame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Runelimit', size=(1024, 768))
        
        # Forcer les dimensions minimales
        self.SetMinSize((800, 600))
        
        # Initialisation des managers
        self.hex_manager, self.drawing_manager, self.biome_manager = setup_managers(13, 14)
        
        # Calculer la taille après création de la fenêtre
        self.hex_manager.calculate_hex_size(1024, 768)
        self.panel = wx.Panel(self)
        self.setup_ui()
        self.Show()  # Ajouter cette ligne
        
    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Titre
        title = wx.StaticText(self.panel, label="Runelimit")
        title.SetFont(wx.Font(48, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(title, 0, wx.ALL|wx.CENTER, 20)
        
        # Canvas du paraboloïde
        canvas = create_paraboloid_canvas(self.panel)
        main_sizer.Add(canvas, 1, wx.EXPAND|wx.ALL, 10)
        
        # Bouton de démarrage
        start_btn = wx.Button(self.panel, label="Démarrer la partie", size=(200, 60))
        start_btn.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        start_btn.Bind(wx.EVT_BUTTON, self.on_start)
        main_sizer.Add(start_btn, 0, wx.ALL|wx.CENTER, 20)
        
        self.panel.SetSizer(main_sizer)
        self.Center()
        
    def on_start(self, event):
        # Effacer le contenu actuel
        self.panel.DestroyChildren()
        
        # Nouveau sizer pour la page de sélection
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Titre
        title = wx.StaticText(self.panel, label="Nombre de joueurs")
        title.SetFont(wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(title, 0, wx.ALL|wx.CENTER, 40)
        
        # Sélecteur de nombre de joueurs
        player_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.player_count = wx.SpinCtrl(self.panel, min=2, max=6, initial=2, size=(100, -1))
        player_sizer.Add(wx.StaticText(self.panel, label="Joueurs: "), 0, wx.CENTER|wx.ALL, 5)
        player_sizer.Add(self.player_count, 0, wx.ALL, 5)
        main_sizer.Add(player_sizer, 0, wx.CENTER|wx.ALL, 20)
        
        # Bouton de validation
        validate_btn = wx.Button(self.panel, label="Valider", size=(200, 60))
        validate_btn.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        validate_btn.Bind(wx.EVT_BUTTON, self.on_player_count_selected)
        main_sizer.Add(validate_btn, 0, wx.ALL|wx.CENTER, 20)
        
        self.panel.SetSizer(main_sizer)
        self.panel.Layout()
        
    def on_player_count_selected(self, event):
        self.num_players = self.player_count.GetValue()
        self.current_player = 0
        self.players = []

        # Récupérer les villes du centre de la carte
        self.cities = []
        biomes_data = Player.load_biomes()
        for pos_str, biome in biomes_data["biomes"].items():  # Accéder à la sous-clé "biomes"
            coords = pos_str.strip('()').split(',')
            pos = (int(coords[0]), int(coords[1]))
            if biome == "Ville" and 2 <= pos[0] <= 8 and 2 <= pos[1] <= 8:
                self.cities.append(pos)
        # Récupérer les personnages disponibles
        self.available_characters = Player.get_available_characters()
    
        self.show_next_player_selection()

    def show_next_player_selection(self):
        self.panel.DestroyChildren()
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        character = random.choice(self.available_characters)
        starting_pos = random.choice(self.cities)
        player = Player(character, starting_pos)
        player.player_name = player.name

        # Création du champ de saisie comme titre
        self.name_ctrl = wx.TextCtrl(self.panel, style=wx.TE_CENTER)
        self.name_ctrl.SetValue(f"Joueur {self.current_player + 1}")
        self.name_ctrl.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(self.name_ctrl, 0, wx.ALL|wx.CENTER|wx.EXPAND, 20)

        # Affichage des informations
        info_text = (f"Personnage: {player.player_name}\n"
                    f"Position de départ: Ville en {starting_pos}\n"
                    f"PV: {player.pv}\n"
                    f"Mêlée: {player.melee} (Dégâts: {player.melee_degat})\n"
                    f"Distance: {player.distance} (Dégâts: {player.distance_degat})\n"
                    f"Magie: {player.magie} (Dégâts: {player.magie_degat})")
        
        info = wx.StaticText(self.panel, label=info_text)
        info.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(info, 0, wx.ALL|wx.CENTER, 20)

        # Bouton suivant
        if self.current_player < self.num_players - 1:
            next_btn = wx.Button(self.panel, label="Joueur suivant", size=(200, 60))
            next_btn.Bind(wx.EVT_BUTTON, self.on_next_player)
        else:
            next_btn = wx.Button(self.panel, label="Commencer la partie", size=(200, 60))
            next_btn.Bind(wx.EVT_BUTTON, self.start_game)
            
        main_sizer.Add(next_btn, 0, wx.ALL|wx.CENTER, 20)
        
        player.name = self.name_ctrl.GetValue()
        self.players.append(player)
        
        self.panel.SetSizer(main_sizer)
        self.panel.Layout()


    def on_next_player(self, event):
        self.current_player += 1
        self.show_next_player_selection()

    def start_game(self, event):
        from table import GameTable
        self.Hide()
        game_table = GameTable(self.players)

def main():
    app = wx.App()
    RunelimitGame()
    app.MainLoop()

if __name__ == '__main__':
    main()
