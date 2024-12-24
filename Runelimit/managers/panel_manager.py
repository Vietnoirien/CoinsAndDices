import wx

class PanelManager:
    def __init__(self, parent):
        self.parent = parent
        self.panels = {}
        self.main_sizer = None  # Ajout d'une référence au sizer principal
        
    def create_main_panel(self):
        main_panel = wx.Panel(self.parent)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Stockage du sizer
        
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
    
    def add_movement_phase(self, movement_phase):
        if self.main_sizer:  # Utilisation du sizer stocké
            self.main_sizer.Add(movement_phase, 1, wx.EXPAND|wx.ALL, 5)
            self.panels['movement'] = movement_phase            
    def get_canvas(self):
        """Récupère le canvas"""
        return self.panels.get('canvas')
    
    def refresh_panels(self):
        """Rafraîchit tous les panels"""
        for panel in self.panels.values():
            panel.Refresh()
