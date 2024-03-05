import wx

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
# from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg

class PanelAnimatedFigure(wx.Panel):
    def __init__(self, parent, figure, minsize=(640,400)):
        wx.Panel.__init__(self, parent)
        self.parent=parent
        self.fixed_min_size=minsize
        self.canvas = FigureCanvasWxAgg(self, -1, figure)
        self.canvas.SetMinSize(self.fixed_min_size)
        self.canvas.draw_idle()
        self.canvas.flush_events()

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.canvas, 1, wx.BOTTOM|wx.EXPAND, 0)
        self.SetSizer(self.sizer)

        self.Fit()


    def LoadFigure(self,figure):
        self.Freeze()
        self.Disable()
        canvas = FigureCanvasWxAgg(self, -1, figure)
        canvas.SetMinSize(self.fixed_min_size)
        
        self.sizer.Replace(self.canvas, canvas)

        self.canvas.Destroy()
        self.canvas=canvas
        
        self.canvas.draw_idle()
        self.canvas.flush_events()
        self.Enable()
        self.Thaw()
        
    def Refresh(self):

        # self.Disable()
        
        self.canvas.draw_idle()
        # self.canvas.flush_events()
        # self.Enable()
        # self.Thaw()

