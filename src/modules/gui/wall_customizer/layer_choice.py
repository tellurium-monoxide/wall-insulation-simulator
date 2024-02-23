import wx

import wx.lib.scrolledpanel as scrolled


import matplotlib.backends.backend_wxagg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from functools import partial
from threading import Thread
import time
import copy

# local imports
from ...physics.solver import Layer, Material



from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal as PanelNumericInput
from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal

from .controls_materials import DisplayMaterialProp, InputMaterialProp


from ..events import *


class PanelLayer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.BORDER_STATIC)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer


        # first column controls: layer data
        self.input_layer_width=PanelNumericInput(self,name="e", unit="cm", unit_scale=100, min_value=1, max_value=100, def_val=10)

        self.typechoice= wx.Choice(self,choices=self.solver.wall.config.get_material_list())

        self.display_mat=DisplayMaterialProp(self)
        self.display_mat.set_values(self.solver.wall.config.get_material_list()[0])

        # second column controls: add/remove layers
        # self.button_rem= wx.Button(self, label="x", style=wx.BU_EXACTFIT)
        self.button_rem= wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_MINUS), style=wx.BU_EXACTFIT)
        self.button_rem.SetToolTip("Remove this layer")
        # self.button_add= wx.Button(self, label="+", style=wx.BU_EXACTFIT)
        self.button_add= wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_PLUS), style=wx.BU_EXACTFIT)
        self.button_add.SetToolTip("Add a layer to the right of this one")


        # add everything to sizers
        self.sizer_v1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_v1.Add(self.input_layer_width,0,wx.EXPAND,0)
        self.sizer_v1.Add(self.typechoice, 0, wx.ALL | wx.EXPAND , 3)
        self.sizer_v1.Add(self.display_mat,1,wx.EXPAND | wx.ALL,0)

        self.sizer_v2 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_v2.Add(self.button_add,1,wx.ALL,2)
        self.sizer_v2.Add(self.button_rem,1,wx.ALL,2)
        

        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_h.Add(self.sizer_v1,0,wx.EXPAND,0)
        self.sizer_h.Add(self.sizer_v2,0,wx.ALL,2)

        self.SetSizer(self.sizer_h)


        # Bindings
        self.typechoice.Bind(wx.EVT_CHOICE, self.on_choice_mat)


        # last minute setup
        self.typechoice.SetSelection(0)
        mat_name=self.typechoice.GetStrings()[0]
        self.set_mat_vals(mat_name)

        self.Layout()
        self.Fit()

    def on_choice_mat(self,event):
        iselect=self.typechoice.GetSelection()
        mat_name=self.typechoice.GetStrings()[iselect]

        self.set_mat_vals(mat_name)
        self.disable_mat_input()

    def set_mat_vals(self, mat_name):
        self.display_mat.set_values(mat_name)
        mat=self.solver.wall.config.get_material(mat_name)

        self.disable_mat_input()

    def disable_mat_input(self):

        return

    def get_layer(self):

        iselect=self.typechoice.GetSelection()
        mat_name=self.typechoice.GetStrings()[iselect]

        mat=self.solver.wall.config.get_material(mat_name)

        e=self.input_layer_width.GetValue()

        layer=Layer(e=e, mat=mat)
        return layer

    def set_layer(self, layer):
        try:
            mat_id=self.typechoice.GetStrings().index(layer.mat.name)
            mat_name=layer.mat.name
        except ValueError:
            print("Trying to set layer with unregistered name")
            mat_id=0
            mat_name=self.typechoice.GetStrings()[0]
        if mat_id>=0:
            self.disable_mat_input()
        self.typechoice.SetSelection(mat_id)
        self.set_mat_vals(mat_name)
        self.input_layer_width.SetValue(layer.e)


    def update_material_names(self):
        iselect=self.typechoice.GetSelection()
        mat_name=self.typechoice.GetStrings()[iselect]
        try:
            mat_new_id=self.solver.wall.config.get_material_list().index(mat_name)
        except ValueError:
            mat_new_id=0
            mat_name=self.solver.wall.config.get_material_list()[0]
        self.typechoice.SetItems( self.solver.wall.config.get_material_list() )
        self.typechoice.SetSelection(mat_new_id)
        self.set_mat_vals(mat_name)

    def disable_input(self):
        self.input_layer_width.Disable()
        self.typechoice.Disable()
        self.button_rem.Disable()
        self.button_add.Disable()

    def enable_input(self):
        self.input_layer_width.Enable()
        self.typechoice.Enable()
        self.button_rem.Enable()
        self.button_add.Enable()


