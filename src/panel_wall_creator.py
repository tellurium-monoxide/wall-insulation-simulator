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
from physics_module.solver import Layer, DefaultScenarios, Material, DefaultMaterials
from physics_module.solver import SolverHeatEquation1dMultilayer as Solver
# ~ from physics_module.materials import Material, DefaultMaterials

from localizer.localizer import Localizer

from panel_input_physical_value import PanelNumericInput as PanelNumericInput

myEVT_NEW_LAYERS = wx.NewEventType()
EVT_NEW_LAYERS = wx.PyEventBinder(myEVT_NEW_LAYERS, 1)

class EventNewLayers(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.layers = None

    def SetLayers(self, val):
        self.layers = val

    def GetLayers(self):
        return self.layers






class PanelMaterialCreator(wx.Panel):
    def __init__(self, parent, localizer=None):
        wx.Panel.__init__(self, parent, style=wx.BORDER_STATIC)

        self.localizer=Localizer.get_localizer(localizer)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        sizer_h1=wx.BoxSizer(wx.HORIZONTAL)
        self.choice_delete = wx.Choice(self, choices=list(DefaultMaterials.keys()))
        self.choice_delete.SetSelection(0)


        self.button_delete= wx.Button(self)
        self.button_delete.Bind(wx.EVT_BUTTON, self.on_button_delete)
        self.localizer.link(self.button_delete.SetLabel, "button_delete_mat", "button_delete_mat")
        self.localizer.link(self.button_delete.SetToolTip, "button_delete_mat_tooltip", "button_delete_mat_tooltip")

        sizer_h1.Add(self.choice_delete,1, wx.ALL | wx.EXPAND,5)
        sizer_h1.Add(self.button_delete,0, wx.ALL,5)

        self.sizer.Add(sizer_h1,0,wx.EXPAND,0)

        sizer_h2=wx.BoxSizer(wx.HORIZONTAL)

        self.button_create= wx.Button(self)
        self.localizer.link(self.button_create.SetLabel, "button_create_mat", "button_create_mat")
        self.localizer.link(self.button_create.SetToolTip, "button_create_mat_tooltip", "button_create_mat_tooltip")

        self.ctrl_save_name= wx.TextCtrl(self, )
        sizer_h2.Add(self.ctrl_save_name,1, wx.ALL | wx.EXPAND,5)
        sizer_h2.Add(self.button_create,0, wx.ALL,5)

        self.sizer.Add(sizer_h2,0,wx.EXPAND,0)

        # ask for mat param 1: lambda
        self.input_layer_mat_lambda=PanelNumericInput(self,name="\u03BB", unit="W/m/K")
        self.sizer.Add(self.input_layer_mat_lambda,0,wx.EXPAND,0)


        # ask for mat param 2: rho
        self.input_layer_mat_rho=PanelNumericInput(self,name="\u03C1",unit="kg/m3")
        self.sizer.Add(self.input_layer_mat_rho,0,wx.EXPAND,0)

        # ask for mat param 3: Cp
        self.input_layer_mat_cp=PanelNumericInput(self,name="Cp",unit="J/kg/K")
        self.sizer.Add(self.input_layer_mat_cp,0,wx.EXPAND,0)



        self.SetSizer(self.sizer)
        self.Fit()

    def on_button_delete(self, event):
        confirm_dialog=wx.MessageDialog(self, "del", style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_WARNING)

        answer=confirm_dialog.ShowModal()
        if answer == wx.ID_OK:
            print("ok")
        elif answer == wx.CANCEL:
            print("cancel")

class PanelLayer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)



        self.input_layer_width=PanelNumericInput(self,name="e", unit="mm", unit_scale=1000, fractionWidth = 0)
        self.sizer.Add(self.input_layer_width,0,wx.EXPAND,0)

        self.list_choices=["custom"]+list(DefaultMaterials.keys())


        self.typechoice= wx.Choice(self,choices=self.list_choices)
        self.typechoice.SetSelection(0)
        self.typechoice.Bind(wx.EVT_CHOICE, self.on_choice_mat)
        self.sizer.Add(self.typechoice, 0, wx.ALL | wx.EXPAND , 3)


        # ask for mat param 1: lambda
        self.input_layer_mat_lambda=PanelNumericInput(self,name="\u03BB", unit="W/m/K")
        self.sizer.Add(self.input_layer_mat_lambda,0,wx.EXPAND,0)


        # ask for mat param 2: rho
        self.input_layer_mat_rho=PanelNumericInput(self,name="\u03C1",unit="kg/m3")
        self.sizer.Add(self.input_layer_mat_rho,0,wx.EXPAND,0)

        # ask for mat param 3: Cp
        self.input_layer_mat_cp=PanelNumericInput(self,name="Cp",unit="J/kg/K")
        self.sizer.Add(self.input_layer_mat_cp,0,wx.EXPAND,0)



        self.SetSizer(self.sizer)
        self.Fit()

    def on_choice_mat(self,event):
        iselect=self.typechoice.GetSelection()
        mat_name=self.list_choices[iselect]
        if iselect>0:
            mat=DefaultMaterials[mat_name]
            self.input_layer_mat_lambda.SetValue(mat.la)

            self.input_layer_mat_rho.SetValue(mat.rho)

            self.input_layer_mat_cp.SetValue(mat.Cp)
            self.disable_mat_input()
        else:
            self.input_layer_mat_lambda.Enable()
            self.input_layer_mat_rho.Enable()
            self.input_layer_mat_cp.Enable()


    def disable_mat_input(self):
        self.input_layer_mat_lambda.Disable()
        self.input_layer_mat_rho.Disable()
        self.input_layer_mat_cp.Disable()

    def get_layer(self):
        la=self.input_layer_mat_lambda.GetValue()
        rho=self.input_layer_mat_rho.GetValue()
        Cp=self.input_layer_mat_cp.GetValue()

        iselect=self.typechoice.GetSelection()
        mat_name=self.list_choices[iselect]

        mat=Material(la=la, rho=rho, Cp=Cp, name=mat_name)

        e=self.input_layer_width.GetValue()

        layer=Layer(e=e, mat=mat)
        return layer

    def set_layer(self, layer):
        try:
            mat_id=self.list_choices.index(layer.mat.name)
        except ValueError:
            mat_id=0
        if mat_id>0:
            self.disable_mat_input()
        self.typechoice.SetSelection(mat_id)
        self.input_layer_width.SetValue(layer.e)
        self.input_layer_mat_lambda.SetValue(layer.mat.la)
        self.input_layer_mat_rho.SetValue(layer.mat.rho)
        self.input_layer_mat_cp.SetValue(layer.mat.Cp)


class PanelLayerList(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # ~ scrolled.ScrolledPanel.__init__(self, parent,size=(wx.DisplaySize()[0],200))
        # ~ self.SetupScrolling()
        self.parent=parent

        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.layer_panels=[PanelLayer(self)]

        for lay in self.layer_panels:
            self.sizer_h.Add(lay, 0, wx.LEFT, 3)

        self.SetSizer(self.sizer_h)
        self.Fit()



    def add_layer(self):
        self.Freeze()
        lay= PanelLayer(self)
        self.layer_panels.append(lay)
        self.sizer_h.Add(lay, 0, wx.LEFT, 5)
        self.Fit()
        self.parent.Fit()
        self.Thaw()

    def remove_layer(self):
        if len(self.layer_panels)>1:
            self.layer_panels.pop().Destroy()
            self.Fit()
            self.parent.Fit()
            return True
        return False

    def gather_layers(self):
        layers=[]
        for panel_layer in self.layer_panels:
            layer = panel_layer.get_layer()
            layers.append(layer)
        return layers

    def set_layer_amount(self, n):
        while len(self.layer_panels)>n:
            self.remove_layer()
        while len(self.layer_panels)<n:
            self.add_layer()

    def load_layers(self,layers):
        self.Freeze()
        self.set_layer_amount(len(layers))
        for i in range(len(layers)):
            self.layer_panels[i].set_layer(layers[i])
        self.Thaw()


class PanelLayerMgr(wx.Panel):
    def __init__(self, parent, localizer=Localizer()):
        wx.Panel.__init__(self, parent, style=wx.BORDER_STATIC)
        self.localizer=localizer
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)

        self.button_edit= wx.Button(self)
        self.localizer.link(self.button_edit.SetLabel, "button_edit", "button_edit")

        self.button_add= wx.Button(self)
        self.localizer.link(self.button_add.SetLabel, "button_add", "button_add")

        self.button_remove= wx.Button(self)
        self.localizer.link(self.button_remove.SetLabel, "button_remove", "button_remove")

        self.button_load= wx.Button(self)
        self.localizer.link(self.button_load.SetLabel, "button_load", "button_load")
        self.localizer.link(self.button_load.SetToolTip, "button_load_tooltip", "button_load_tooltip")



        self.list_scenarios=["custom"]+list(DefaultScenarios.keys())
        self.choice_scenario= wx.Choice(self,choices=self.list_scenarios)
        self.choice_scenario.SetSelection(0)

        self.button_save= wx.Button(self)
        self.localizer.link(self.button_save.SetLabel, "button_save", "button_save")
        self.localizer.link(self.button_save.SetToolTip, "button_save_tooltip", "button_save_tooltip")

        self.ctrl_save_name= wx.TextCtrl(self)
        # ~ self.localizer.link(self.ctrl_save_name.SetLabel, "button_save", "button_save")
        # ~ self.localizer.link(self.ctrl_save_name.SetToolTip, "button_save_tooltip", "button_save_tooltip")

        self.sizer_h.Add(self.button_edit, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_add, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_remove, 0, wx.ALL, 5)
        self.sizer_h.AddSpacer(20)
        self.sizer_h.Add(self.button_load, 0, wx.ALL, 5)
        self.sizer_h.Add(self.choice_scenario, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_save, 0, wx.ALL, 5)
        self.sizer_h.Add(self.ctrl_save_name, 0, wx.ALL | wx.EXPAND, 5)







        self.sizer_v.Add(self.sizer_h, 0, wx.ALL, 0)

        self.panel_layer_list=PanelLayerList(self)
        self.sizer_v.Add(self.panel_layer_list, 0, wx.ALL, 3)

        self.button_edit.Bind(wx.EVT_BUTTON, self.on_press_button_edit)
        self.button_add.Bind(wx.EVT_BUTTON, self.on_press_add_layer)
        self.button_remove.Bind(wx.EVT_BUTTON, self.on_press_remove_layer)
        self.button_load.Bind(wx.EVT_BUTTON, self.on_press_load_scenario)



        self.SetSizer(self.sizer_v)


        self.Fit()

        self.is_frozen=False
        self.toggle_edit()

    def on_press_button_edit(self,event):
        self.toggle_edit()

    def toggle_edit(self, set_custom=True):
        self.is_frozen=not(self.is_frozen)
        if not(self.is_frozen): # set it to unfrozen state
            self.localizer.link(self.button_edit.SetLabel, "button_edit_confirm", "button_edit")
            self.panel_layer_list.Enable()
            self.button_add.Enable()
            if len(self.panel_layer_list.layer_panels)>1:
                self.button_remove.Enable()
            if set_custom:
                self.choice_scenario.SetSelection(0)
            # ~ self.panel_layers.Thaw()
        else:# set to frozen state and send confirmed layers above
            self.localizer.link(self.button_edit.SetLabel, "button_edit", "button_edit")
            # ~ self.panel_layers.Freeze()
            self.panel_layer_list.Disable()
            self.button_add.Disable()
            self.button_remove.Disable()
            self.send_layers()


    def send_layers(self):
        layers=self.panel_layer_list.gather_layers()
        event = EventNewLayers(myEVT_NEW_LAYERS, self.GetId())
        event.SetLayers(layers)
        self.GetEventHandler().ProcessEvent(event)

    def on_press_add_layer(self, event):
        self.panel_layer_list.add_layer()
        self.button_remove.Enable()

    def on_press_remove_layer(self, event):
        self.panel_layer_list.remove_layer()
        if len(self.panel_layer_list.layer_panels)==1:
            self.button_remove.Disable()

    def on_press_load_scenario(self,event):
        sel=self.choice_scenario.GetSelection()
        if (self.is_frozen):
                self.toggle_edit(set_custom=False)
        if sel>0:
            scenario_name=self.list_scenarios[sel]
            scenario=DefaultScenarios[scenario_name]
            self.panel_layer_list.load_layers(scenario.layers)
            self.send_layers()
        if not(self.is_frozen):
                self.toggle_edit(set_custom=False)
        if len(self.panel_layer_list.layer_panels)==1:
            self.button_remove.Disable()


