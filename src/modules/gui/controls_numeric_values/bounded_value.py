import wx
from wx.lib.masked import NumCtrl
import wx.lib.scrolledpanel as scrolled
import matplotlib.backends.backend_wxagg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from threading import Thread
import time
import copy

# local imports








class ValidatorDecimalInputOnly(wx.Validator):
    def __init__(self, integer_width=4, fraction_width=3, min_value=0, max_value=10000):
        wx.Validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.filter_keys)
        self.Bind(wx.EVT_TEXT, self.control_length)
        self.allowedASCIIKeys=[ 46, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
        self.allowedControlKeys=[8,312, 314, 316]
        self.allowedWXKeys=[wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7,
                                        wx.WXK_NUMPAD8, wx.WXK_NUMPAD9, wx.WXK_DECIMAL,wx.WXK_LEFT,wx.WXK_RIGHT]

        self.allowedkeyCodes=self.allowedASCIIKeys+self.allowedWXKeys+self.allowedControlKeys
        self.integer_width=integer_width
        self.fraction_width=fraction_width
        self.min_value=min_value
        self.max_value=max_value
        # ~ self.previous_text=""



    def filter_keys(self,event):
        key=event.GetUnicodeKey()
        keyCode=event.GetKeyCode()
        textCtrl = self.GetWindow()
        # print(dir(event.EventObject))
        # print("keycode: ",key,keyCode)

        entered=textCtrl.GetValue()
        split=entered.split(".")
        self.previous_text=entered
        willRepeatPeriod= (keyCode==46 and ('.' in entered))

        if not(willRepeatPeriod) and( key in self.allowedkeyCodes or keyCode in self.allowedkeyCodes ):
            event.Skip()
    def control_length(self,event):
        # ~ print(dir(event.EventObject))
        textCtrl = self.GetWindow()
        entered=textCtrl.GetValue()
        if len(entered)>0:
            val=float(entered)
            if val < self.min_value:
                textCtrl.ChangeValue(str(self.min_value))
            if val > self.max_value:
                textCtrl.ChangeValue(str(self.max_value))
        else:
            textCtrl.ChangeValue(str(self.previous_text))
        split=entered.split(".")
        # print(split)
        if (len(split)>1 and len(split[1])>self.fraction_width):
            textCtrl.ChangeValue(self.previous_text)
        if len(entered)>=2 and entered[0]=="0" and entered[1]in "0":
            textCtrl.ChangeValue(self.previous_text)
        # if len(entered)==0:
            # textCtrl.ChangeValue("1")





    def Clone(self):
         """ Standard cloner.

             Note that every validator must implement the Clone() method.
         """
         return ValidatorDecimalInputOnly(min_value=self.min_value, max_value=self.max_value)


    def Validate(self, win):
         """ Validate the contents of the given text control.
         """
         textCtrl = self.GetWindow()
         entered = textCtrl.GetValue()

         if len(entered) == 0:
             wx.MessageBox("The numeric input must have something entered", "Error")
             textCtrl.SetBackgroundColour("pink")
             textCtrl.SetFocus()
             textCtrl.Refresh()
             return False
         else:
             val=float(entered)
             # print("validating", val,self.min_value,self.max_value )
             if val < self.min_value:

                 textCtrl.ChangeValue(str(self.min_value))
             if val > self.max_value:
                 textCtrl.ChangeValue(str(self.max_value))
             return True


    def TransferToWindow(self):
         """ Transfer data from validator to window.

             The default implementation returns False, indicating that an error
             occurred.  We simply return True, as we don't do any data transfer.
         """
         return True # Prevent wxDialog from complaining.


    def TransferFromWindow(self):
         """ Transfer data from window to validator.

             The default implementation returns False, indicating that an error
             occurred.  We simply return True, as we don't do any data transfer.
         """
         return True # Prevent wxDialog from complaining.


class CtrlPositiveBoundedDecimal(wx.Panel):
    def __init__(self, parent, name="", def_val=1,integerWidth = 6,fractionWidth = 3, unit="", unit_scale=1, min_value=0, max_value=10000):
        wx.Panel.__init__(self, parent)
        self.unit_scale=unit_scale
        self.def_val=def_val
        self.fractionWidth=fractionWidth


        validator=ValidatorDecimalInputOnly(min_value=min_value, max_value=max_value)

        self.num_ctrl = wx.TextCtrl(self, value=str(def_val), validator=validator, size=(50, -1))
        self.num_ctrl.SetToolTip("Min:%g\nMax:%g" % (min_value, max_value))


        self.sizer_h=wx.BoxSizer(wx.HORIZONTAL)


        self.sizer_h.Add(self.num_ctrl, 0, wx.ALL, 2)

        self.SetSizer(self.sizer_h)
        self.Fit()

    def GetValue(self):
        self.Validate()
        return (float(self.num_ctrl.GetValue())/self.unit_scale)
    def SetValue(self, val):
        self.num_ctrl.SetValue(str(val*self.unit_scale))


