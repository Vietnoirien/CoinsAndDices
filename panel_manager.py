import wx

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

    def create_buttons(self):
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.char_button = wx.Button(self.buttons_panel, label="Créer un personnage")
        self.monster_button = wx.Button(self.buttons_panel, label="Créer un monstre")
        
        self.char_button.Bind(wx.EVT_BUTTON, lambda evt: self.show_char_editor())
        self.monster_button.Bind(wx.EVT_BUTTON, lambda evt: self.show_monster_editor())
        
        buttons_sizer.Add(self.char_button, 1, wx.ALL|wx.EXPAND, 5)
        buttons_sizer.Add(self.monster_button, 1, wx.ALL|wx.EXPAND, 5)
        self.buttons_panel.SetSizer(buttons_sizer)

    def register_panels(self, buttons_panel, char_editor, monster_editor, right_panel):
        self.buttons_panel = buttons_panel
        self.char_editor = char_editor
        self.monster_editor = monster_editor
        self.right_panel = right_panel
        self.create_buttons()

    def show_char_editor(self):
        self.buttons_panel.Hide()
        self.char_editor.Show()
        self.buttons_panel.Disable()
        self.char_editor.init_panel.Hide()
        self.char_editor.editor_panel.Show()
        self.monster_editor.Hide()
        self.force_layout()

    def show_monster_editor(self):
        self.buttons_panel.Hide()
        self.buttons_panel.Disable()
        self.monster_editor.Show()
        self.monster_editor.init_panel.Hide()
        self.monster_editor.editor_panel.Show()
        self.char_editor.Hide()
        self.force_layout()

    def show_buttons_panel(self):
        self.buttons_panel.Show()
        self.buttons_panel.Enable()
        self.char_editor.Hide()
        self.monster_editor.Hide()
        self.force_layout()

    def force_layout(self):
        self.main_frame.panel.Layout()
        self.right_panel.Layout()
        self.char_editor.Layout()
        self.monster_editor.Layout()
        self.main_frame.Refresh()

    def toggle_editor_panels(self, editor):
        editor.init_panel.Hide()
        editor.editor_panel.Show()
        editor.Layout()
