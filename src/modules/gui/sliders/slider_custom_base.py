

import wx
import numpy as np

class SliderCustomBase(wx.Panel):
    def __init__(self, parent, nsteps, orientation):
        wx.Panel.__init__(self,parent)
        
        
        # print(self.base)
        slider_orient=  wx.SL_HORIZONTAL if orientation=="h" else wx.SL_VERTICAL
        
        slider_dir= wx.SL_HORIZONTAL if orientation=="h" else wx.SL_INVERSE
        
        
        self.slider= wx.Slider(self, minValue=0, maxValue=nsteps, style=slider_orient | slider_dir)
        self.label= wx.StaticText(self, label="%.2f" % (self.slider.GetValue()))
        self.label_min=wx.StaticText(self, label="")
        self.label_max=wx.StaticText(self, label="")
        
        
        
        if orientation=="h":
            sizer=wx.FlexGridSizer(2,3,0,0)
            sizer.AddGrowableCol(1)
            
            sizer.Add(wx.StaticText(self),0,wx.ALL, 0)
            sizer.Add(self.label,1,wx.ALIGN_CENTER, 1)
            sizer.Add(wx.StaticText(self),0,wx.ALL, 0)
            sizer.Add(self.label_min,0,wx.ALIGN_CENTER, 0)
            sizer.Add(self.slider, 1, wx.EXPAND, 0)
            sizer.Add(self.label_max,0,wx.ALIGN_CENTER, 0)
            
            
            self.SetSizer(sizer)
        elif orientation=="v":
            sizer=wx.FlexGridSizer(3,2,0,0)
            sizer.AddGrowableRow(1)
            
            sizer.Add(wx.StaticText(self),0,wx.ALL, 0)
            sizer.Add(self.label_max,0,wx.ALIGN_CENTER, 0)
            
            sizer.Add(self.label,1,wx.ALIGN_CENTER, 1)
            sizer.Add(self.slider, 1, wx.EXPAND, 0)
            
            sizer.Add(wx.StaticText(self),0,wx.ALL, 0)
            sizer.Add(self.label_min,0,wx.ALIGN_CENTER, 0)
            
            
            
            
            self.SetSizer(sizer)
        
        
        # self.slider.Bind(wx.EVT_SLIDER, self.on_slide)
        
    # def on_slide(self, event):
        # self.label.SetLabel(label="%.2f" % (self.GetValue()))
        # self.Layout()
        # self.GetParent().Fit()
        
    def GetValue(self):
        return self.slider.GetValue()
    def SetMinLabel(self,label=""):
        return self.label_min.SetLabel(label=label)
    def SetMaxLabel(self,label=""):
        return self.label_max.SetLabel(label=label)


    # def SetValue(self):
