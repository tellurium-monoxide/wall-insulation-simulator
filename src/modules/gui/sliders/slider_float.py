


import wx
import numpy as np

from .slider_custom_base import SliderCustomBase

class SliderFloat(SliderCustomBase):
    def __init__(self, parent, minValue=0, maxValue=1, nsteps=100, orientation="h"):
        SliderCustomBase.__init__(self,parent,nsteps, orientation, )
        
        self.minValue=minValue
        self.maxValue=maxValue
        
        self.slope=(maxValue-minValue)/nsteps


    
        self.slider.Bind(wx.EVT_SLIDER, self.on_slide)
        
    def on_slide(self, event):
        self.label.SetLabel(label="%.2f" % (self.GetValue()))
        self.Layout()
        self.GetParent().Fit()
        event.Skip()
        
    def GetValue(self):
        vs=self.slider.GetValue()
        
        v=self.minValue + vs * self.slope
        
        # print(v, vs)
        return v
