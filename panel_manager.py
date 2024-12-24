import wx

class PanelManager:
    def __init__(self, main_frame):
        self.main_frame = main_frame
        self.buttons_panel = None
        self.char_editor = None
        self.monster_editor = None
        self.right_panel = None
        self.char_button = None
        self.monster_button = None
        self.companion_editor = None
        self.companion_button = None
        self.event_editor = None
        self.event_button = None

    def create_buttons(self):
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
    
        self.char_button = wx.Button(self.buttons_panel, label="Créer un personnage")
        self.monster_button = wx.Button(self.buttons_panel, label="Créer un monstre")
        self.companion_button = wx.Button(self.buttons_panel, label="Créer un compagnon")
        self.event_button = wx.Button(self.buttons_panel, label="Éditer événement")
    
        self.char_button.Bind(wx.EVT_BUTTON, lambda evt: self.show_char_editor())
        self.monster_button.Bind(wx.EVT_BUTTON, lambda evt: self.show_monster_editor())
        self.companion_button.Bind(wx.EVT_BUTTON, lambda evt: self.show_companion_editor())
        self.event_button.Bind(wx.EVT_BUTTON, lambda evt: self.show_event_editor())
    
        buttons_sizer.Add(self.char_button, 0, wx.ALL|wx.EXPAND, 5)
        buttons_sizer.Add(self.monster_button, 0, wx.ALL|wx.EXPAND, 5)
        buttons_sizer.Add(self.companion_button, 0, wx.ALL|wx.EXPAND, 5)
        buttons_sizer.Add(self.event_button, 0, wx.ALL|wx.EXPAND, 5)
    
        self.buttons_panel.SetSizer(buttons_sizer)

    def register_panels(self, buttons_panel, char_editor, monster_editor, companion_editor, event_editor, right_panel):
        self.buttons_panel = buttons_panel
        self.char_editor = char_editor
        self.monster_editor = monster_editor
        self.companion_editor = companion_editor
        self.event_editor = event_editor
        self.right_panel = right_panel

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.buttons_panel, 0, wx.EXPAND|wx.ALL, 5)
        right_sizer.Add(self.char_editor, 1, wx.EXPAND|wx.ALL, 5)
        right_sizer.Add(self.monster_editor, 1, wx.EXPAND|wx.ALL, 5)
        right_sizer.Add(self.companion_editor, 1, wx.EXPAND|wx.ALL, 5)
        right_sizer.Add(self.event_editor, 1, wx.EXPAND|wx.ALL, 5)

        self.right_panel.SetSizer(right_sizer)
        self.create_buttons()

    def _hide_all_panels(self):
        self.buttons_panel.Hide()
        self.buttons_panel.Disable()
        self.char_editor.Hide()
        self.monster_editor.Hide()
        self.companion_editor.Hide()
        self.event_editor.Hide()

    def show_char_editor(self):
        self._hide_all_panels()
        self.char_editor.Show()
        self.char_editor.editor_panel.Show()
        self.force_layout()

    def show_monster_editor(self):
        self._hide_all_panels()
        self.monster_editor.Show()
        self.monster_editor.editor_panel.Show()
        self.force_layout()

    def show_companion_editor(self):
        self._hide_all_panels()
        self.companion_editor.Show()
        self.companion_editor.editor_panel.Show()
        self.force_layout()

    def show_event_editor(self):
        self._hide_all_panels()
        self.event_editor.Show()
        self.force_layout()

    def show_buttons_panel(self):
        self._hide_all_panels()
        self.buttons_panel.Show()
        self.buttons_panel.Enable()
        self.force_layout()

    def force_layout(self):
        self.right_panel.GetSizer().Layout()
        self.main_frame.panel.Layout()
        self.main_frame.Layout()
        self.main_frame.Refresh()
        self.main_frame.Update()
