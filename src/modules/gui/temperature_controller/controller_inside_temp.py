
import math
import wx


from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal


class ControlInsideTemp(wx.Panel):

    def __init__(self, parent, slider_Tint):
        wx.Panel.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.slider_Tint=slider_Tint

        # content:

        # check box to activate the feature:
        use_txt= wx.StaticText(self, label="Activate ? ")
        self.check = wx.CheckBox(self)

        sizer_h0 = wx.BoxSizer(wx.HORIZONTAL)
        toadd= [ (w, 0, wx.ALIGN_CENTER, 0) for w in [use_txt,self.check]]
        sizer_h0.AddMany(toadd)
        # room geometry:

        # self.button_edit_room=wx.ToggleButton(self, label="edit", size=(40,-1))
        self.check_edit_room = wx.CheckBox(self)
        self.L1_input= CtrlPositiveBoundedDecimal(self, min_value=1, max_value=20)
        self.L2_input= CtrlPositiveBoundedDecimal(self, min_value=1, max_value=20)
        self.hsp_input= CtrlPositiveBoundedDecimal(self, min_value=1, max_value=20)


        sizer_h1 = wx.FlexGridSizer(2,7, 0, 0)
        sizer_h1.AddGrowableCol(6, proportion=1)

        sizer_h1.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)

        sizer_h1.Add(wx.StaticText(self, label="L"), 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(wx.StaticText(self, label="l"), 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(wx.StaticText(self, label="h"), 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(wx.StaticText(self, label="Edit"), 0, wx.ALIGN_RIGHT | wx.EXPAND, 0)

        sizer_h1.Add(wx.StaticText(self, label="Dim:"), 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(self.L1_input, 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(wx.StaticText(self, label="x"), 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(self.L2_input, 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(wx.StaticText(self, label="x"), 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(self.hsp_input, 0, wx.ALIGN_CENTER, 0)
        sizer_h1.Add(self.check_edit_room, 1, wx.ALIGN_RIGHT | wx.EXPAND, 0)






        # heating and current heat loss indicator:

        heat_gain_leg=wx.StaticText(self, label="P_heater (W)", style = wx.ALIGN_CENTRE_HORIZONTAL)
        heat_loss_leg=wx.StaticText(self, label="P_lost (W)", style = wx.ALIGN_CENTRE_HORIZONTAL)

        wx_sl_style = wx.SL_LABELS | wx.SL_VERTICAL | wx.SL_INVERSE
        self.slider_heat_gain=wx.Slider(self,value=0,minValue=-100, maxValue=100, style=wx_sl_style)
        self.slider_heat_loss=wx.Slider(self,value=0,minValue=-100, maxValue=100, style=wx_sl_style | wx.SL_LEFT)

        self.slider_heat_gain.Disable()
        self.slider_heat_loss.Disable()

        self.slider_heat_gain.SetToolTip("Set the heating power (in Watts). You can use the keyboard arrows after clicking the slider to set it precisely.")




        sizer_h3 = wx.FlexGridSizer(2,5, 0, 0)
        sizer_h3.AddGrowableRow(1, proportion=1)
        sizer_h3.AddGrowableCol(0, proportion=1)
        sizer_h3.AddGrowableCol(2, proportion=1)
        sizer_h3.AddGrowableCol(4, proportion=1)

        sizer_h3.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)
        sizer_h3.Add(heat_gain_leg, 0, wx.ALIGN_RIGHT, 0)
        sizer_h3.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)
        sizer_h3.Add(heat_loss_leg, 0, wx.ALIGN_LEFT, 0)
        sizer_h3.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)

        sizer_h3.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)
        sizer_h3.Add(self.slider_heat_gain, 0, wx.EXPAND, 0)
        sizer_h3.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)
        sizer_h3.Add(self.slider_heat_loss, 0, wx.EXPAND , 0)
        sizer_h3.Add(wx.StaticText(self, label=""), 0, wx.ALIGN_CENTER, 0)

        sizer_v = wx.BoxSizer(wx.VERTICAL)



        sizer_v.AddMany([sizer_h0,sizer_h1, (sizer_h3, 1, wx.EXPAND, 0)])



        self.SetSizer(sizer_v)
        sizer_v.SetSizeHints(self)
        self.Layout()

        # set the correct values in the inputs

        self.L1_input.SetValue(self.solver.wall.room.shape[0])
        self.L2_input.SetValue(self.solver.wall.room.shape[1])
        self.hsp_input.SetValue(self.solver.wall.room.shape[2])

        self.hsp_input.Disable()
        self.L1_input.Disable()
        self.L2_input.Disable()

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
        self.solver.Tint_is_variable =  event.IsChecked()
        self.slider_heat_gain.Enable(enable=event.IsChecked())
        self.slider_Tint.Enable(enable=not(event.IsChecked()))
        if event.IsChecked():
            val_gain=self.slider_heat_gain.GetValue()
            self.solver.wall.room.heating_power=val_gain

    def on_slide_heat_gain(self, event):
        val_gain=self.slider_heat_gain.GetValue()
        self.solver.wall.room.heating_power=val_gain


    def update_slider_ranges(self):
        Rwall = sum([l.Rth for l in self.solver.wall.layers])
        maxpow= int((self.solver.Tmax-self.solver.Tmin) / Rwall * self.solver.wall.room.surface)

        vmin=self.slider_heat_loss.GetMin()
        vmax=self.slider_heat_loss.GetMax()

        if vmax != maxpow and vmin != maxpow:
            prev_val_gain=self.slider_heat_gain.GetValue()
            prev_val_loss=self.slider_heat_loss.GetValue()
            self.slider_heat_gain.SetMin(-maxpow)
            self.slider_heat_gain.SetMax(maxpow)
            self.slider_heat_loss.SetMin(-maxpow)
            self.slider_heat_loss.SetMax(maxpow)
            self.slider_heat_gain.SetValue( min(maxpow, max(-maxpow, prev_val_gain)))

            val_gain=self.slider_heat_gain.GetValue()
            self.solver.wall.room.heating_power=val_gain




    def update(self):

        heat_loss=int(self.solver.compute_heat_loss())



        # self.solver.wall.room

        self.update_slider_ranges()

        if abs(heat_loss)<1e6:
            self.slider_heat_loss.SetValue(heat_loss)
        if not(self.check.IsChecked()):
            self.slider_heat_gain.SetValue(heat_loss)
        else:
            self.slider_Tint.SetValue(int(self.solver.Tint))





