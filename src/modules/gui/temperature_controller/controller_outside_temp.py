

import math
import wx


from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

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





    def on_check(self, event):
        self.slider_Tout.Enable(enable=not(event.IsChecked()))
        self.solver.Tout_use_cycle=(event.IsChecked())
        
        
    def on_show_cycle(self, event):
        CycleVisualizer(self)






    def update(self):

        if (self.check.IsChecked()):
            self.slider_Tout.SetValue(int(self.solver.Tout))
            






class CycleVisualizer(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer
        
        self.SetTitle("Cycle visualization")
        
        figure=self.solver.wall.temp_cycle.plot_cycle()
        self.canvas = FigureCanvasWxAgg(self, -1, figure)
        # self.canvas.SetMinSize(self.fixed_min_size)
        self.canvas.draw_idle()
        
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND, 0)
        
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)
        self.Fit()
        self.Show()


