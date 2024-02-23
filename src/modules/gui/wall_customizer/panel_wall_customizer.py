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

from ..events import *

from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal as PanelNumericInput
from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal

from .controls_materials import DisplayMaterialProp, InputMaterialProp

from .material_creator import PanelMaterialCreator

from .layer_choice_list import PanelLayerList, ScrolledLayerListWrapper





class PanelLayerMgr(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.BORDER_STATIC)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)

        self.button_edit= wx.Button(self)
        self.localizer.link(self.button_edit.SetLabel, "button_edit", "button_edit")


        self.button_load= wx.Button(self)
        self.localizer.link(self.button_load.SetLabel, "button_load", "button_load")
        self.localizer.link(self.button_load.SetToolTip, "button_load_tooltip", "button_load_tooltip")




        self.choice_scenario= wx.Choice(self,choices=self.solver.wall.config.get_preset_list())
        self.choice_scenario.SetSelection(0)

        self.button_save= wx.Button(self)
        self.localizer.link(self.button_save.SetLabel, "button_save", "button_save")
        self.localizer.link(self.button_save.SetToolTip, "button_save_tooltip", "button_save_tooltip")

        self.ctrl_save_name= wx.TextCtrl(self)

        self.button_create_material= wx.Button(self)
        self.localizer.link(self.button_create_material.SetLabel, "button_create_material", "button_create_material")

        self.button_collapse_list= wx.Button(self)
        self.localizer.link(self.button_collapse_list.SetLabel, "button_collapse_list", "button_collapse_list", text="Hide")

        self.sizer_h.Add(self.button_edit, 0, wx.ALL, 5)
        self.sizer_h.AddSpacer(20)
        self.sizer_h.Add(self.button_load, 0, wx.ALL, 5)
        self.sizer_h.Add(self.choice_scenario, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_save, 0, wx.ALL, 5)
        self.sizer_h.Add(self.ctrl_save_name, 0, wx.ALL | wx.EXPAND, 5)
        self.sizer_h.Add(self.button_create_material, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_collapse_list, 0, wx.ALL, 5)







        self.sizer_v.Add(self.sizer_h, 0, wx.ALL, 0)

        self.scrolled_list=ScrolledLayerListWrapper(self)
        self.panel_layer_list=self.scrolled_list.layer_list
        self.sizer_v.Add(self.scrolled_list, 0, wx.ALL, 3)

        self.button_edit.Bind(wx.EVT_BUTTON, self.on_press_button_edit)



        self.button_load.Bind(wx.EVT_BUTTON, self.on_press_load_scenario)
        self.button_save.Bind(wx.EVT_BUTTON, self.on_press_save_scenario)
        self.button_create_material.Bind(wx.EVT_BUTTON, self.on_press_button_create_material)
        self.button_collapse_list.Bind(wx.EVT_BUTTON, self.on_press_button_collapse_list)


        self.SetSizer(self.sizer_v)


        self.Bind(EVT_WALL_MATERIALS_CHANGED, self.on_wall_config_change)

        self.Fit()

        self.is_frozen=False
        self.toggle_edit()

    def on_press_button_create_material(self,event):
        mat_creator=PanelMaterialCreator(self)
    def on_press_button_collapse_list(self,event):
        self.scrolled_list.Show(show=not(self.scrolled_list.IsShown()))
        self.GetTopLevelParent().Layout()

    def on_press_button_edit(self,event):
        self.toggle_edit()

    def toggle_edit(self):
        self.is_frozen=not(self.is_frozen)
        if not(self.is_frozen): # set it to unfrozen state
            self.localizer.link(self.button_edit.SetLabel, "button_edit_confirm", "button_edit")
            self.panel_layer_list.enable_input()
            self.button_load.Disable()
            self.button_save.Disable()
            self.ctrl_save_name.Disable()
            self.choice_scenario.Disable()
            

        else:
            self.localizer.link(self.button_edit.SetLabel, "button_edit", "button_edit")
            self.panel_layer_list.disable_input()
            self.send_layers(self.panel_layer_list.gather_layers())
            self.button_load.Enable()
            self.button_save.Enable()
            self.ctrl_save_name.Enable()
            self.choice_scenario.Enable()

        self.Layout()

    def on_press_save_scenario(self,event):
        preset_name=self.ctrl_save_name.GetValue()
        if len(preset_name)==0:
            preset_name=self.choice_scenario.GetStrings()[self.choice_scenario.GetSelection()]
        # if preset_name in self.solver.wall.config.get_preset_list():
            # with wx.MessageDialog(self, "", style=wx.YES_NO | wx.ICON_WARNING) as error_dialog:

                # self.localizer.link(error_dialog.SetMessage, "dialog_overwrite_name_preset", "dialog_overwrite_name_preset")
                # answer=error_dialog.ShowModal()
                # if answer==wx.ID_NO:
                    # return

        layers=self.panel_layer_list.gather_layers()
        print("Saving preset : >", preset_name, "< with layers:")
        for layer in layers:
            print("- ",layer.e,"m :", layer.mat.name)

        named_layers=[(l.e, l.mat.name) for l in layers]
        self.solver.wall.config.add_preset_wall(preset_name, named_layers)
        self.update_after_config_change()

    def send_layers(self, layers):
        self.solver.change_layers(layers)
        event = eventWallSetupChanged(wx.NewIdRef())
        wx.PostEvent(self, event)


    def on_press_load_scenario(self,event):
        self.load_preset()





    def load_preset(self):
        sel=self.choice_scenario.GetSelection()
        if (self.is_frozen):
                self.toggle_edit()

        preset_name=self.choice_scenario.GetStrings()[sel]
        preset_wall=self.solver.wall.config.get_preset(preset_name)
        print("Loading preset : >", preset_name, "< with layers:")
        for layer in preset_wall:
            print("- ",layer.e,"m :", layer.mat.name)
        self.panel_layer_list.load_layers(preset_wall)
        self.send_layers(preset_wall)
        if not(self.is_frozen):
                self.toggle_edit()



    def on_wall_config_change(self,event):
        self.update_after_config_change()

    def update_after_config_change(self):
        iselect=self.choice_scenario.GetSelection()
        preset_name=self.choice_scenario.GetStrings()[iselect]
        try:
            preset_new_id=self.solver.wall.config.get_preset_list().index(preset_name)
        except ValueError:
            preset_new_id=0
        # print(self.typechoice.GetStrings())
        self.choice_scenario.SetItems( self.solver.wall.config.get_preset_list() )
        self.choice_scenario.SetSelection(preset_new_id)
        for panel in self.panel_layer_list.list_of_panel_layer:
            panel.update_material_names()
        self.load_preset()



class StaticBoxWallCustomizerWrapper(wx.StaticBox):
    def __init__(self, parent):
        wx.StaticBox.__init__(self, parent, label="Wall customizer")

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.sizer=wx.StaticBoxSizer(self, wx.VERTICAL)


        self.wall_customizer=PanelLayerMgr(self)
        self.sizer.Add(self.wall_customizer, 1, wx.EXPAND, 0)

