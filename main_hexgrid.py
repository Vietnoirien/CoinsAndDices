import wx
from hexagonal_grid import HexagonalGrid

def main():
    app = wx.App()
    frame = HexagonalGrid()
    app.MainLoop()

if __name__ == '__main__':
    main()
