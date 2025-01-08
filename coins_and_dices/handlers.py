from typing import Callable
import wx

class FrameEventHandler:
    @staticmethod
    def create_child_close_handler(parent: wx.Frame, child: wx.Frame) -> Callable:
        def handler(event: wx.Event) -> None:
            child.Destroy()
            parent.Show()
            event.Skip()
        return handler
