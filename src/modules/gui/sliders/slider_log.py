

import wx
import numpy as np

from .slider_custom_base import SliderCustomBase

class SliderLog(SliderCustomBase):
    def __init__(self, parent, minValue=1, maxValue=100, nsteps=100, orientation="h"):
        SliderCustomBase.__init__(self,parent,nsteps, orientation, )
        
        self.minValue=minValue
        self.maxValue=maxValue
        
        self.base=(maxValue/minValue)**(1/nsteps)
        
        self.SetMinLabel(label="%g" % (self.minValue))
        self.SetMaxLabel(label="%g" % (self.maxValue))
        
        self.label.SetLabel(label="%.2f" % (self.GetValue()))
        
        
        self.slider.Bind(wx.EVT_SLIDER, self.on_slide)
        
    def on_slide(self, event):
        self.UpdateLabel()
        event.Skip()
        
    def GetValue(self):
        vs=self.slider.GetValue()
        
        v=self.minValue* self.base ** vs
        
        # print(v, vs)
        return v
    def SetValue(self, value):
        v=int(np.log(value/self.minValue)/np.log(self.base))
        
        self.slider.SetValue(v)
        self.UpdateLabel()
        return v

    def UpdateLabel(self):
        self.label.SetLabel(label="%.2f" % (self.GetValue()))
        # self.Layout()
        self.GetParent().Layout()
