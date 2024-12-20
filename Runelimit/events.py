import wx

# Créer un type d'événement personnalisé
terrainHoverEventType = wx.NewEventType()
EVT_TERRAIN_HOVER = wx.PyEventBinder(terrainHoverEventType)

class TerrainHoverEvent(wx.PyEvent):
    def __init__(self, terrain):
        super().__init__()
        self.SetEventType(terrainHoverEventType)
        self.terrain = terrain
