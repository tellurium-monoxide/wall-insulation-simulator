import wx
import wx.lib.newevent
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


from ...localizer.localizer import Localizer

from ..controls_numeric_values.bounded_value import PanelNumericInput as PanelNumericInput



# events to be propagated to the main panel when simulation parameters changes
eventWallSetupChanged, EVT_WALL_SETUP_CHANGED = wx.lib.newevent.NewCommandEvent()
eventWallMaterialListChanged, EVT_WALL_MATERIALS_CHANGED = wx.lib.newevent.NewCommandEvent()





class PanelMaterialCreator(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='Create or delete a material', style=wx.DEFAULT_FRAME_STYLE)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        sizer_h1=wx.BoxSizer(wx.HORIZONTAL)
        self.choice_delete = wx.Choice(self, choices=self.solver.wall.config.get_material_list())

        self.choice_delete.SetSelection(0)


        self.button_create= wx.Button(self)
        self.button_create.Bind(wx.EVT_BUTTON, self.on_button_save)
        self.localizer.link(self.button_create.SetLabel, "button_save_mat", "button_save_mat")
        self.localizer.link(self.button_create.SetToolTip, "button_save_mat_tooltip", "button_save_mat_tooltip")

        self.button_save_as= wx.Button(self)
        self.button_save_as.Bind(wx.EVT_BUTTON, self.on_button_save_as)
        self.localizer.link(self.button_save_as.SetLabel, "button_save_as_mat", "button_save_as_mat")
        self.localizer.link(self.button_save_as.SetToolTip, "button_save_as_mat_tooltip", "button_save_as_mat_tooltip")


        self.button_delete= wx.Button(self)
        self.button_delete.Bind(wx.EVT_BUTTON, self.on_button_delete)
        self.localizer.link(self.button_delete.SetLabel, "button_delete_mat", "button_delete_mat")
        self.localizer.link(self.button_delete.SetToolTip, "button_delete_mat_tooltip", "button_delete_mat_tooltip")

        sizer_h1.Add(self.choice_delete,1, wx.ALL | wx.EXPAND,5)
        sizer_h1.Add(self.button_create,0, wx.ALL,5)

        sizer_h1.Add(self.button_delete,0, wx.ALL,5)

        self.sizer.Add(sizer_h1,0,wx.EXPAND,0)

        sizer_h2=wx.BoxSizer(wx.HORIZONTAL)



        self.ctrl_save_name= wx.TextCtrl(self, )
        sizer_h2.Add(self.ctrl_save_name,1, wx.ALL | wx.EXPAND,5)
        sizer_h2.Add(self.button_save_as,0, wx.ALL,5)

        self.sizer.Add(sizer_h2,0,wx.EXPAND,0)

        # ask for mat param 1: lambda
        self.input_layer_mat_lambda=PanelNumericInput(self,name="\u03BB", unit="W/m/K")
        self.sizer.Add(self.input_layer_mat_lambda,0,wx.ALL,0)


        # ask for mat param 2: rho
        self.input_layer_mat_rho=PanelNumericInput(self,name="\u03C1",unit="kg/m3")
        self.sizer.Add(self.input_layer_mat_rho,0,wx.ALL,0)

        # ask for mat param 3: Cp
        self.input_layer_mat_cp=PanelNumericInput(self,name="Cp",unit="J/kg/K")
        self.sizer.Add(self.input_layer_mat_cp,0,wx.ALL,0)


        self.choice_delete.Bind(wx.EVT_CHOICE, self.on_choice_mat)
        self.on_choice_mat(None)

        self.SetSizer(self.sizer)
        self.sizer.SetSizeHints(self)
        self.Fit()
        self.Show()


    def on_choice_mat(self,event):
        iselect=self.choice_delete.GetSelection()
        mat_name=self.choice_delete.GetStrings()[iselect]

        mat=self.solver.wall.config.get_material(mat_name)
        self.set_mat_vals(mat)

    def set_mat_vals(self, mat):
        self.input_layer_mat_lambda.SetValue(mat.la)

        self.input_layer_mat_rho.SetValue(mat.rho)

        self.input_layer_mat_cp.SetValue(mat.Cp)

    def on_button_delete(self, event):
        confirm_dialog=wx.MessageDialog(self, "del", style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_WARNING)

        answer=confirm_dialog.ShowModal()
        if answer == wx.ID_OK:
            print("ok")

            name_to_be_del=self.choice_delete.GetStrings()[self.choice_delete.GetSelection()]
            name_list=self.solver.wall.config.get_list_presets_using_material(name_to_be_del)


            print(name_to_be_del)
            if len(name_list)>0:
                text="Material is used in a preset wall, do you wish to proceed with deletion ? This will remove the following presets:\n"
                for preset in name_list:
                    text+= preset + "\n"
                mat_used_dialog=wx.MessageDialog(self,text , style=wx.YES_NO | wx.ICON_WARNING)
                answer2=mat_used_dialog.ShowModal()

                if answer2 == wx.ID_YES:
                    print(name_list)
                    # TODO : remove presets
                elif answer2 == wx.ID_NO:
                    print("cancel used material deletion")
                    return

            # can remove the mat
            removed=self.solver.wall.config.remove_material(name_to_be_del, force_delete=True)
            if not(removed):
                inform_dialog=wx.MessageDialog(self, "Material was not deleted, probably because it is used in all existing presets, or it is the only material.", style=wx.OK)

                answer=inform_dialog.ShowModal()

            event = eventWallMaterialListChanged(wx.NewIdRef())
            wx.PostEvent(self, event)
            self.Close()

        elif answer == wx.CANCEL:
            print("cancel material deletion")

    def on_button_save(self, event):

        la=self.input_layer_mat_lambda.GetValue()
        rho=self.input_layer_mat_rho.GetValue()
        Cp=self.input_layer_mat_cp.GetValue()

        # name=self.ctrl_save_name.GetValue()
        # if len(name)==0: # takes name from choice above as we assume the goal is to overwrite it
            # error_dialog=wx.MessageDialog(self, "Must have a name", style=wx.OK | wx.ICON_WARNING)
            # answer=error_dialog.ShowModal()
            # self.ctrl_save_name.SetFocus()
            # self.ctrl_save_name.SetBackground()
        name=self.choice_delete.GetStrings()[self.choice_delete.GetSelection()]
        # else:
        if name in self.solver.wall.config.get_material_list():
            error_dialog=wx.MessageDialog(self, "Name taken, do you want to overwrite it?", style=wx.YES_NO | wx.ICON_WARNING)
            answer=error_dialog.ShowModal()
            if answer==wx.ID_YES:
                print("overwrite")
            elif answer==wx.ID_NO:
                # print("cancel")
                self.ctrl_save_name.SetFocus()
                return
        # material can then be created, and event is emitted
        self.solver.wall.config.add_material( Material(la=la, rho=rho, Cp=Cp, name=name))
        event = eventWallMaterialListChanged(wx.NewIdRef())
        wx.PostEvent(self, event)
        self.Close()

    def on_button_save_as(self, event):
        name=self.ctrl_save_name.GetValue()
        if len(name)==0: # takes name from choice above as we assume the goal is to overwrite it
            error_dialog=wx.MessageDialog(self, "Must have a name", style=wx.OK | wx.ICON_WARNING)
            answer=error_dialog.ShowModal()
            self.ctrl_save_name.SetFocus()
            # self.ctrl_save_name.SetBackground()
            return
        if name in self.solver.wall.config.get_material_list():
            error_dialog=wx.MessageDialog(self, "Name taken, do you want to overwrite it?", style=wx.YES_NO | wx.ICON_WARNING)
            answer=error_dialog.ShowModal()
            if answer==wx.ID_YES:
                print("overwrite")
            elif answer==wx.ID_NO:
                # print("cancel")
                self.ctrl_save_name.SetFocus()
                return
        la=self.input_layer_mat_lambda.GetValue()
        rho=self.input_layer_mat_rho.GetValue()
        Cp=self.input_layer_mat_cp.GetValue()
        self.solver.wall.config.add_material( Material(la=la, rho=rho, Cp=Cp, name=name))
        event = eventWallMaterialListChanged(wx.NewIdRef())
        wx.PostEvent(self, event)
        self.Close()

class PanelLayer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.BORDER_STATIC)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer


        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)



        self.input_layer_width=PanelNumericInput(self,name="e", unit="cm", unit_scale=100, min_value=1, max_value=100, def_val=10)
        self.sizer.Add(self.input_layer_width,0,wx.EXPAND,0)



        self.typechoice= wx.Choice(self,choices=self.solver.wall.config.get_material_list())

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


        self.sizer_h.Add(self.sizer,0,wx.EXPAND,0)

        self.button_rem= wx.Button(self, label="x", size=(30,-1))
        self.button_add= wx.Button(self, label="+", size=(30,-1))


        self.sizer_v2 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_v2.Add(self.button_rem,1,wx.ALL,2)
        self.sizer_v2.Add(self.button_add,1,wx.ALL,2)
        self.sizer_h.Add(self.sizer_v2,0,wx.ALL,2)

        self.SetSizer(self.sizer_h)

        self.typechoice.SetSelection(0)
        mat_name=self.typechoice.GetStrings()[0]
        self.set_mat_vals(mat_name)

        self.Layout()
        self.Fit()

    def on_choice_mat(self,event):
        iselect=self.typechoice.GetSelection()
        mat_name=self.typechoice.GetStrings()[iselect]

        # mat=self.solver.wall.config.get_material(mat_name)
        self.set_mat_vals(mat_name)
        self.disable_mat_input()

    def set_mat_vals(self, mat_name):
        mat=self.solver.wall.config.get_material(mat_name)
        self.input_layer_mat_lambda.SetValue(mat.la)

        self.input_layer_mat_rho.SetValue(mat.rho)

        self.input_layer_mat_cp.SetValue(mat.Cp)
        self.disable_mat_input()

    def disable_mat_input(self):
        self.input_layer_mat_lambda.Disable()
        self.input_layer_mat_rho.Disable()
        self.input_layer_mat_cp.Disable()

    def get_layer(self):
        # la=self.input_layer_mat_lambda.GetValue()
        # rho=self.input_layer_mat_rho.GetValue()
        # Cp=self.input_layer_mat_cp.GetValue()

        iselect=self.typechoice.GetSelection()
        mat_name=self.typechoice.GetStrings()[iselect]

        mat=self.solver.wall.config.get_material(mat_name)

        e=self.input_layer_width.GetValue()

        layer=Layer(e=e, mat=mat)
        return layer

    def set_layer(self, layer):
        try:
            mat_id=self.solver.wall.config.get_material_list().index(layer.mat.name)
        except ValueError:
            print("Trying to set layer with unregistered name")
            mat_id=0
        if mat_id>=0:
            self.disable_mat_input()
        self.typechoice.SetSelection(mat_id)
        self.set_mat_vals(layer.mat.name)
        self.input_layer_width.SetValue(layer.e)
        # self.input_layer_mat_lambda.SetValue(layer.mat.la)
        # self.input_layer_mat_rho.SetValue(layer.mat.rho)
        # self.input_layer_mat_cp.SetValue(layer.mat.Cp)

    def update_material_names(self):
        iselect=self.typechoice.GetSelection()
        mat_name=self.typechoice.GetStrings()[iselect]
        try:
            mat_new_id=self.solver.wall.config.get_material_list().index(mat_name)
        except ValueError:
            mat_new_id=0
            mat_name=self.solver.wall.config.get_material_list()[0]
        # else:
        # print(self.typechoice.GetStrings())
        self.typechoice.SetItems( self.solver.wall.config.get_material_list() )
        self.typechoice.SetSelection(mat_new_id)
        mat=self.solver.wall.config.get_material(mat_name)
        self.set_mat_vals(mat)



class PanelLayerList(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # ~ scrolled.ScrolledPanel.__init__(self, parent,size=(wx.DisplaySize()[0],200))
        # ~ self.SetupScrolling()
        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.button_add_begin= wx.Button(self, label="+", size=(30,-1))

        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.list_of_panel_layer=[]

        self.load_layers(self.solver.wall.layers)



        self.Fit()


    def update_sizer(self):
        while not(self.sizer_h.IsEmpty()):
            self.sizer_h.Detach(0)

        self.sizer_h.Add( self.button_add_begin)
        for i in range(len(self.list_of_panel_layer)):
            lay=self.list_of_panel_layer[i]
            lay.pos=i
            self.sizer_h.Add(lay, 0, wx.LEFT, 3)
            lay.button_rem.Bind(wx.EVT_BUTTON, partial(self.on_press_remove,pos=i))
            lay.button_add.Bind(wx.EVT_BUTTON, partial(self.on_press_add,pos=i+1))

        self.SetSizer(self.sizer_h, deleteOld=True)
        self.Fit()
        self.parent.Fit()

    def on_press_add(self, event, pos=None):
        # print(pos)
        self.add_layer(pos=pos)

    def add_layer(self, pos=None):
        if pos==None:
            pos=len(self.list_of_panel_layer)
        self.Freeze()
        lay= PanelLayer(self)
        self.list_of_panel_layer.insert(pos, lay)
        self.update_sizer()
        self.Thaw()

    def on_press_remove(self, event, pos=None):
        # print(pos)
        self.remove_layer(pos=pos)
    def remove_layer(self, pos=None):
        if pos==None:
            pos=len(self.list_of_panel_layer)-1
        if len(self.list_of_panel_layer)>1:

            self.list_of_panel_layer.pop(pos).Destroy()
            self.update_sizer()
            return True
        return False

    def gather_layers(self):
        layers=[]
        for panel_layer in self.list_of_panel_layer:
            layer = panel_layer.get_layer()
            layers.append(layer)
        return layers

    def set_layer_amount(self, n):
        while len(self.list_of_panel_layer)>n:
            self.remove_layer()
        while len(self.list_of_panel_layer)<n:
            self.add_layer()

    def load_layers(self,layers):
        # self.Freeze()
        self.set_layer_amount(len(layers))
        for i in range(len(layers)):
            self.list_of_panel_layer[i].set_layer(layers[i])
        self.Layout()
        self.Fit()
        # self.Thaw()


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

        # self.button_add= wx.Button(self)
        # self.localizer.link(self.button_add.SetLabel, "button_add", "button_add", text="Add at beginning")

        # self.button_remove= wx.Button(self)
        # self.localizer.link(self.button_remove.SetLabel, "button_remove", "button_remove")

        self.button_load= wx.Button(self)
        self.localizer.link(self.button_load.SetLabel, "button_load", "button_load")
        self.localizer.link(self.button_load.SetToolTip, "button_load_tooltip", "button_load_tooltip")




        self.choice_scenario= wx.Choice(self,choices=self.solver.wall.config.get_preset_list())
        self.choice_scenario.SetSelection(0)

        self.button_save= wx.Button(self)
        self.localizer.link(self.button_save.SetLabel, "button_save", "button_save")
        self.localizer.link(self.button_save.SetToolTip, "button_save_tooltip", "button_save_tooltip")

        self.ctrl_save_name= wx.TextCtrl(self)
        # ~ self.localizer.link(self.ctrl_save_name.SetLabel, "button_save", "button_save")
        # ~ self.localizer.link(self.ctrl_save_name.SetToolTip, "button_save_tooltip", "button_save_tooltip")

        self.button_create_material= wx.Button(self)
        self.localizer.link(self.button_create_material.SetLabel, "button_create_material", "button_create_material")

        self.button_collapse_list= wx.Button(self)
        self.localizer.link(self.button_collapse_list.SetLabel, "button_collapse_list", "button_collapse_list", text="Hide")

        self.sizer_h.Add(self.button_edit, 0, wx.ALL, 5)
        # self.sizer_h.Add(self.button_add, 0, wx.ALL, 5)
        # self.sizer_h.Add(self.button_remove, 0, wx.ALL, 5)
        self.sizer_h.AddSpacer(20)
        self.sizer_h.Add(self.button_load, 0, wx.ALL, 5)
        self.sizer_h.Add(self.choice_scenario, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_save, 0, wx.ALL, 5)
        self.sizer_h.Add(self.ctrl_save_name, 0, wx.ALL | wx.EXPAND, 5)
        self.sizer_h.Add(self.button_create_material, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_collapse_list, 0, wx.ALL, 5)







        self.sizer_v.Add(self.sizer_h, 0, wx.ALL, 0)

        self.panel_layer_list=PanelLayerList(self)
        self.sizer_v.Add(self.panel_layer_list, 0, wx.ALL, 3)

        self.button_edit.Bind(wx.EVT_BUTTON, self.on_press_button_edit)
        # self.button_add.Bind(wx.EVT_BUTTON, self.on_press_add_layer)
        self.panel_layer_list.button_add_begin.Bind(wx.EVT_BUTTON, self.on_press_add_layer)
        # self.button_remove.Bind(wx.EVT_BUTTON, self.on_press_remove_layer)
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
        self.panel_layer_list.Show(show=not(self.panel_layer_list.IsShown()))
        self.GetTopLevelParent().Layout()

    def on_press_button_edit(self,event):
        self.toggle_edit()

    def toggle_edit(self, set_custom=True):
        self.is_frozen=not(self.is_frozen)
        if not(self.is_frozen): # set it to unfrozen state
            self.localizer.link(self.button_edit.SetLabel, "button_edit_confirm", "button_edit")
            self.panel_layer_list.Enable()
            self.panel_layer_list.button_add_begin.Show()
            self.Layout()
            if set_custom:
                self.choice_scenario.SetSelection(0)
            # ~ self.panel_layers.Thaw()
        else:# set to frozen state and send confirmed layers above
            self.localizer.link(self.button_edit.SetLabel, "button_edit", "button_edit")
            self.panel_layer_list.Disable()
            self.send_layers(self.panel_layer_list.gather_layers())

            self.panel_layer_list.button_add_begin.Hide()
            self.Layout()

    def on_press_save_scenario(self,event):
        preset_name=self.ctrl_save_name.GetValue()
        if len(preset_name)==0:
            preset_name=self.choice_scenario.GetStrings()[self.choice_scenario.GetSelection()]
        if preset_name in self.solver.wall.config.get_preset_list():
            error_dialog=wx.MessageDialog(self, "Name taken, do you want to overwrite it?", style=wx.YES_NO | wx.ICON_WARNING)
            answer=error_dialog.ShowModal()
            if answer==wx.ID_NO:
                return
        layers=self.panel_layer_list.gather_layers()
        named_layers=[(l.e, l.mat.name) for l in layers]
        self.solver.wall.config.add_preset_wall(preset_name, named_layers)
        self.update_after_config_change()

    def send_layers(self, layers):
        # layers=self.panel_layer_list.gather_layers()
        self.solver.change_layers(layers)
        # ~ event = EventNewLayers(myEVT_NEW_LAYERS, self.GetId())
        # ~ event.SetLayers(layers)
        event = eventWallSetupChanged(wx.NewIdRef())
        wx.PostEvent(self, event)
        # ~ wx.QueueEvent(self.parent, event)
        # ~ self.GetEventHandler().ProcessEvent(event)

    def on_press_add_layer(self, event):
        self.panel_layer_list.add_layer(0)


    # def on_press_remove_layer(self, event):
        # self.panel_layer_list.remove_layer()
        # if len(self.panel_layer_list.list_of_panel_layer)==1:
            # self.button_remove.Disable()

    def on_press_load_scenario(self,event):
        self.load_preset()





    def load_preset(self):
        sel=self.choice_scenario.GetSelection()
        if (self.is_frozen):
                self.toggle_edit(set_custom=False)

        preset_name=self.choice_scenario.GetStrings()[sel]
        preset_wall=self.solver.wall.config.get_preset(preset_name)
        print("Loading preset :", preset_name, "with layers:")
        for layer in preset_wall:
            print("- ",layer.e,"m :", layer.mat.name)
        self.panel_layer_list.load_layers(preset_wall)
        self.send_layers(preset_wall)
        if not(self.is_frozen):
                self.toggle_edit(set_custom=False)
        if len(self.panel_layer_list.list_of_panel_layer)==1:
            self.button_remove.Disable()


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
        self.sizer.Add(self.wall_customizer)

