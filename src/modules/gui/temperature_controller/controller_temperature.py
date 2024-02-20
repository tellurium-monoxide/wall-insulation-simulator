
import wx



from .controller_inside_temp import ControlInsideTemp

class ControllerTemp(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.solver=parent.solver
        self.localizer=parent.localizer





        self.ctrl_inside = ControlInsideTemp(self)


        sizer=wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.ctrl_inside, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)



    def update(self):
        self.ctrl_inside.update()
