import wx


# local imports
from ...physics.solver import Layer, Material



from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal




class DisplayMaterialProp(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.sizer=wx.FlexGridSizer(3,6, 0, 6)
        self.sizer.AddGrowableCol(0, proportion=1)
        self.sizer.AddGrowableCol(5, proportion=1)

        # self.eq=wx.StaticText(self, label="=")
        self.la=wx.StaticText(self, label="\u03BB")
        self.la_value=wx.StaticText(self, label="")
        self.la_unit=wx.StaticText(self, label="W/m/K")

        self.rho=wx.StaticText(self, label="\u03C1")
        self.rho_value=wx.StaticText(self, label="")
        self.rho_unit=wx.StaticText(self, label="kg/m3")

        self.Cp=wx.StaticText(self, label="Cp")
        self.Cp_value=wx.StaticText(self, label="")
        self.Cp_unit=wx.StaticText(self, label="J/kg/K")

        self.sizer.Add(wx.StaticText(self, label=""))
        self.sizer.Add(self.la, 1, wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label="="), 1, wx.ALIGN_CENTER , 0)
        self.sizer.Add(self.la_value, 1, wx.LEFT , 0)
        self.sizer.Add(self.la_unit, 1, wx.ALL | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label=""))

        self.sizer.Add(wx.StaticText(self, label=""))
        self.sizer.Add(self.rho, 1, wx.LEFT | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label="="), 1, wx.LEFT | wx.ALIGN_CENTER , 0)
        self.sizer.Add(self.rho_value, 1, wx.LEFT , 0)
        self.sizer.Add(self.rho_unit, 1, wx.ALL | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label=""))

        self.sizer.Add(wx.StaticText(self, label=""))
        self.sizer.Add(self.Cp, 1, wx.LEFT | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label="="), 1, wx.LEFT | wx.ALIGN_CENTER , 0)
        self.sizer.Add(self.Cp_value, 1, wx.LEFT , 0)
        self.sizer.Add(self.Cp_unit, 1, wx.ALL | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label=""))


        for child in self.sizer.GetChildren():
            # font=child.GetWindow().GetFont()
            # font.SetPointSize(11)
            # child.GetWindow().SetFont(font)
            child.GetWindow().SetForegroundColour((100,100,100))

        self.SetSizer(self.sizer)


    def set_values(self, mat_name):
        mat=self.solver.wall.config.get_material(mat_name)
        self.la_value.SetLabel(str(mat.la))
        self.rho_value.SetLabel(str(mat.rho))
        self.Cp_value.SetLabel(str(mat.Cp))
        self.Layout()
        return
class InputMaterialProp(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.sizer=wx.FlexGridSizer(3,6, 0, 6)
        self.sizer.AddGrowableCol(0, proportion=1)
        self.sizer.AddGrowableCol(5, proportion=1)

        # self.eq=wx.StaticText(self, label="=")
        self.la=wx.StaticText(self, label="\u03BB")
        self.la_value=CtrlPositiveBoundedDecimal(self, min_value=0.001, max_value=10)
        self.la_unit=wx.StaticText(self, label="W/m/K")

        self.rho=wx.StaticText(self, label="\u03C1")
        self.rho_value=CtrlPositiveBoundedDecimal(self, min_value=1, max_value=10000)
        self.rho_unit=wx.StaticText(self, label="kg/m3")

        self.Cp=wx.StaticText(self, label="Cp")
        self.Cp_value=CtrlPositiveBoundedDecimal(self, min_value=100, max_value=10000)
        self.Cp_unit=wx.StaticText(self, label="J/kg/K")

        self.sizer.Add(wx.StaticText(self, label=""))
        self.sizer.Add(self.la, 1, wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label="="), 1, wx.ALIGN_CENTER , 0)
        self.sizer.Add(self.la_value, 1, wx.LEFT , 0)
        self.sizer.Add(self.la_unit, 1, wx.ALL | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label=""))

        self.sizer.Add(wx.StaticText(self, label=""))
        self.sizer.Add(self.rho, 1, wx.LEFT | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label="="), 1, wx.LEFT | wx.ALIGN_CENTER , 0)
        self.sizer.Add(self.rho_value, 1, wx.LEFT , 0)
        self.sizer.Add(self.rho_unit, 1, wx.ALL | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label=""))

        self.sizer.Add(wx.StaticText(self, label=""))
        self.sizer.Add(self.Cp, 1, wx.LEFT | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label="="), 1, wx.LEFT | wx.ALIGN_CENTER , 0)
        self.sizer.Add(self.Cp_value, 1, wx.LEFT , 0)
        self.sizer.Add(self.Cp_unit, 1, wx.ALL | wx.ALIGN_CENTER , 0)
        self.sizer.Add(wx.StaticText(self, label=""))


        # for child in self.sizer.GetChildren():
            # font=child.GetWindow().GetFont()
            # font.SetPointSize(11)
            # child.GetWindow().SetFont(font)
            # child.GetWindow().SetForegroundColour((100,100,100))

        self.SetSizer(self.sizer)


    def SetValues(self, mat_name):
        mat=self.solver.wall.config.get_material(mat_name)
        self.la_value.SetValue(mat.la)
        self.rho_value.SetValue(mat.rho)
        self.Cp_value.SetValue(mat.Cp)
        return

    def GetValues(self):

        la=self.la_value.GetValue()
        rho=self.rho_value.GetValue()
        Cp=self.Cp_value.GetValue()
        return la, rho, Cp

