

import math
import wx


from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal


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

        sizer_h0 = wx.BoxSizer(wx.HORIZONTAL)
        toadd= [ (w, 0, wx.ALIGN_CENTER, 0) for w in [use_txt,self.check]]
        sizer_h0.AddMany(toadd)


        sizer_v = wx.BoxSizer(wx.VERTICAL)



        sizer_v.AddMany([sizer_h0])



        self.SetSizer(sizer_v)
        sizer_v.SetSizeHints(self)
        self.Layout()



        # Bindings

        self.check.Bind(wx.EVT_CHECKBOX, self.on_check)
        self.check_edit_room.Bind(wx.EVT_CHECKBOX, self.on_check_edit)

        self.slider_heat_gain.Bind(wx.EVT_SLIDER, self.on_slide_heat_gain)


    def on_check_edit(self, event):
        self.hsp_input.Enable(enable=event.IsChecked())
        self.L1_input.Enable(enable=event.IsChecked())
        self.L2_input.Enable(enable=event.IsChecked())

        if not(event.IsChecked()):
            h= self.hsp_input.GetValue()
            L1= self.L1_input.GetValue()
            L2= self.L2_input.GetValue()

            self.solver.wall.room.set_shape((L1,L2,h))


    def on_check(self, event):
        self.slider_Tint.Enable(enable=not(event.IsChecked()))
        return





    def update(self):

        if (self.check.IsChecked()):
            self.slider_Tout.SetValue(int(self.solver.Tout))





