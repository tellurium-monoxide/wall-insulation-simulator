

import math
import wx
from matplotlib.figure import Figure

from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from ..animated_figure import PanelAnimatedFigure

class ControlOutsideTemp(wx.Panel):

    def __init__(self, parent, slider_Tout):
        wx.Panel.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.slider_Tout=slider_Tout

        # content:

        # check box to activate the feature:
        use_txt= wx.StaticText(self, label="Activate ? ")
        self.check = wx.CheckBox(self)


        self.choice_cycle=wx.Choice(self,choices=self.solver.wall.config.get_temp_cycle_names_list())
        self.choice_cycle.SetSelection(0)
        
        self.button_show_cycle=wx.Button(self,label="Show cycle")

        sizer_h0 = wx.BoxSizer(wx.HORIZONTAL)
        toadd= [ (w, 0, wx.ALIGN_CENTER, 0) for w in [use_txt,self.check]]
        sizer_h0.AddMany(toadd)


        

        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_v.AddMany([sizer_h0, self.choice_cycle, self.button_show_cycle])




        self.SetSizer(sizer_v)
        sizer_v.SetSizeHints(self)
        self.Layout()



        # Bindings

        self.check.Bind(wx.EVT_CHECKBOX, self.on_check)
        self.button_show_cycle.Bind(wx.EVT_BUTTON, self.on_show_cycle)
        
        self.viz=CycleVisualizer(self)
        





    def on_check(self, event):
        self.slider_Tout.Enable(enable=not(event.IsChecked()))
        self.solver.Tout_use_cycle=(event.IsChecked())
        
        
    def on_show_cycle(self, event):
        self.viz.Show()
        self.button_show_cycle.Disable()






    def update(self):

        if (self.check.IsChecked()):
            self.slider_Tout.SetValue(int(self.solver.Tout))
            
        if self.viz.IsShown():
            self.viz.update()
            






class CycleVisualizer(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer
        
        self.SetTitle("Cycle visualization")
        
        
        self.figure = Figure()
        self.ax=self.figure.subplots()
        self.solver.wall.temp_cycle.plot_cycle(self.ax,time=self.solver.time)
        
        self.panel_fig = PanelAnimatedFigure(self, self.figure, minsize=(500,300))

        
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel_fig, 1, wx.EXPAND, 0)
        
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)
        self.Layout()
        
        self.Bind(wx.EVT_CLOSE , self.on_close)
        
        
        
        
        # self.Show()


    def on_close(self,event):
        self.parent.button_show_cycle.Enable()
        self.Hide()


    def update(self):
        self.solver.wall.temp_cycle.plot_cycle(self.ax,time=self.solver.time)
        self.panel_fig.Refresh()
        # self.Layout()
        
