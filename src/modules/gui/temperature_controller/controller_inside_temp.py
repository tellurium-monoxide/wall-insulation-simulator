
import wx


from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal


class ControlInsideTemp(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer




