import wx

# Événement pour le survol/sélection de terrain
terrainHoverEventType = wx.NewEventType()
EVT_TERRAIN_HOVER = wx.PyEventBinder(terrainHoverEventType)

class TerrainHoverEvent(wx.PyEvent):
    def __init__(self, terrain, is_selected=False):
        super().__init__()
        self.SetEventType(terrainHoverEventType)
        self.terrain = terrain
        self.is_selected = is_selected