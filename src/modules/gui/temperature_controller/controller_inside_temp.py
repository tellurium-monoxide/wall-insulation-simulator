
import wx


from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal


class ControlInsideTemp(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer



        # content:

        # check box to activate the feature:
        use_txt= wx.StaticText(self, label="Activate ? ")
        self.check = wx.CheckBox(self)

        sizer_h0 = wx.BoxSizer(wx.HORIZONTAL)
        toadd= [ (w, 0, wx.ALIGN_CENTER, 0) for w in [use_txt,self.check]]
        sizer_h0.AddMany(toadd)
        # room geometry:

        hsp= wx.StaticText(self, label="Hsp = ")
        hsp_input= CtrlPositiveBoundedDecimal(self, min_value=1, max_value=20)
        hsp_unit= wx.StaticText(self, label="m")


        sizer_h1 = wx.BoxSizer(wx.HORIZONTAL)

        toadd= [ (w, 0, wx.ALIGN_CENTER, 0) for w in [hsp,hsp_input,hsp_unit]]
        sizer_h1.AddMany(toadd)

        txt= wx.StaticText(self, label="Murs : ")
        l1_input= CtrlPositiveBoundedDecimal(self, min_value=1, max_value=20)
        xtxt= wx.StaticText(self, label="x")
        l2_input= CtrlPositiveBoundedDecimal(self, min_value=1, max_value=20)
        len_unit= wx.StaticText(self, label="m")

        sizer_h2 = wx.BoxSizer(wx.HORIZONTAL)
        toadd= [ (w, 0, wx.ALIGN_CENTER, 0) for w in [txt,l1_input,xtxt,l2_input,len_unit]]
        sizer_h2.AddMany(toadd)

        # heating and current heat loss indicator:

        wx_sl_style = wx.SL_LABELS | wx.SL_VERTICAL | wx.SL_INVERSE
        heat_gain_leg=wx.StaticText(self, label="P_heater", style = wx.ALIGN_CENTRE_HORIZONTAL)
        self.slider_heat_gain=wx.Slider(self,value=0,minValue=-100, maxValue=100, style=wx_sl_style)
        heat_loss_leg=wx.StaticText(self, label="P_lost", style = wx.ALIGN_CENTRE_HORIZONTAL)
        self.slider_heat_loss=wx.Slider(self,value=0,minValue=self.solver.Tmin, maxValue=self.solver.Tmax, style=wx_sl_style | wx.SL_LEFT , name="Tout")
        self.slider_heat_gain.Disable()
        self.slider_heat_loss.Disable()
        self.slider_heat_gain.SetPageSize(1)
        self.slider_heat_gain.SetToolTip("Set the heating power (in Watts). You can use the keyboard arrows after clicking the slider to set it precisely.")




        sizer_h3 = wx.FlexGridSizer(2,2, 0, 0)
        sizer_h3.AddGrowableRow(1, proportion=1)
        toadd= [ (w, 1, wx.EXPAND, 0) for w in [heat_gain_leg,heat_loss_leg, self.slider_heat_gain, self.slider_heat_loss]]
        sizer_h3.AddMany(toadd)

        sizer_v = wx.BoxSizer(wx.VERTICAL)



        sizer_v.AddMany([sizer_h0,sizer_h1, (sizer_h2, 0, wx.EXPAND, 0), (sizer_h3, 1, wx.EXPAND, 0)])



        self.SetSizer(sizer_v)
        sizer_v.SetSizeHints(self)
        self.Layout()


        # Bindings

        self.check.Bind(wx.EVT_CHECKBOX, self.on_check)

        self.slider_heat_gain.Bind(wx.EVT_SLIDER, self.on_slide_heat_gain)


    def on_check(self, event):
        self.solver.Tint_is_variable =  event.IsChecked()
        self.slider_heat_gain.Enable(enable=event.IsChecked())
        self.GetParent().panel_fig_sliders.slider_Tint.Enable(enable=not(event.IsChecked()))

    def on_slide_heat_gain(self, event):
        val_gain=self.slider_heat_gain.GetValue()
        self.solver.wall.room.heating_power=val_gain


    def update_slider_ranges(self, val):
        val=int(val)
        vmin=self.slider_heat_loss.GetMin()
        vmax=self.slider_heat_loss.GetMax()
        if (abs(val)> abs(vmin) or abs(val)>abs(vmax) or abs(vmax) >5 * (abs(val)+100)) and abs(val)<1e6:
            new_val=abs(val)+10
            prev_val_gain=self.slider_heat_gain.GetValue()
            prev_val_loss=self.slider_heat_loss.GetValue()
            self.slider_heat_gain.SetMin(-new_val)
            self.slider_heat_gain.SetMax(new_val)
            self.slider_heat_loss.SetMin(-new_val)
            self.slider_heat_loss.SetMax(new_val)
            self.slider_heat_gain.SetValue(prev_val_gain)
            self.slider_heat_loss.SetValue(prev_val_loss)
        return

    def update(self):

        heat_loss=int(self.solver.compute_heat_loss())
        self.update_slider_ranges(heat_loss)

        if abs(heat_loss)<1e6:
            self.slider_heat_loss.SetValue(heat_loss)
        if not(self.check.IsChecked()):
            self.slider_heat_gain.SetValue(heat_loss)
        else:
            self.GetParent().panel_fig_sliders.slider_Tint.SetValue(int(self.solver.Tint))
        self.GetParent().Layout()


