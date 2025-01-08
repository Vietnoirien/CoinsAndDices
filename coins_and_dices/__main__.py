import wx
from .home_page import HomePage

def main():
    app = wx.App()
    home = HomePage()
    app.MainLoop()

if __name__ == '__main__':
    main()
