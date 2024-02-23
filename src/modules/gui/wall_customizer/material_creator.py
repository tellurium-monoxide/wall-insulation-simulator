import wx

import wx.lib.scrolledpanel as scrolled


# local imports
from ...physics.solver import Layer, Material



from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal as PanelNumericInput
from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal

from .controls_materials import DisplayMaterialProp, InputMaterialProp


from ..events import *



class PanelMaterialCreator(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, style=wx.CAPTION | wx.CLOSE_BOX| wx.FRAME_FLOAT_ON_PARENT)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.localizer.link(self.SetTitle, "button_create_material", "title_mat_creator")
        # self.localizer.link(self.SetTitle, "title_mat_creator", "title_mat_creator", text="Create or delete a material")

        parent.Disable()
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        sizer_h1=wx.BoxSizer(wx.HORIZONTAL)
        self.choice_delete = wx.Choice(self, choices=self.solver.wall.config.get_material_list())

        self.choice_delete.SetSelection(0)


        self.button_create= wx.Button(self)
        self.button_create.Bind(wx.EVT_BUTTON, self.on_button_save)
        self.localizer.link(self.button_create.SetLabel, "button_save_mat", "button_save_mat")
        self.localizer.link(self.button_create.SetToolTip, "button_save_mat_tooltip", "button_save_mat_tooltip")




        self.button_delete= wx.Button(self)
        self.button_delete.Bind(wx.EVT_BUTTON, self.on_button_delete)
        self.localizer.link(self.button_delete.SetLabel, "button_delete_mat", "button_delete_mat")
        self.localizer.link(self.button_delete.SetToolTip, "button_delete_mat_tooltip", "button_delete_mat_tooltip")

        sizer_h1.Add(self.choice_delete,1, wx.ALL | wx.EXPAND,5)
        sizer_h1.Add(self.button_create,0, wx.ALL,5)

        sizer_h1.Add(self.button_delete,0, wx.ALL,5)

        self.sizer.Add(sizer_h1,0,wx.EXPAND,0)




        # input material properties
        self.input=InputMaterialProp(self)
        self.sizer.Add(self.input,0,wx.ALL | wx.EXPAND,0)



        # Save under new name
        self.ctrl_save_name= wx.TextCtrl(self, )
        self.button_save_as= wx.Button(self)
        self.button_save_as.Bind(wx.EVT_BUTTON, self.on_button_save_as)
        self.localizer.link(self.button_save_as.SetLabel, "button_save_as_mat", "button_save_as_mat")
        self.localizer.link(self.button_save_as.SetToolTip, "button_save_as_mat_tooltip", "button_save_as_mat_tooltip")

        sizer_h2=wx.BoxSizer(wx.HORIZONTAL)
        sizer_h2.Add(self.ctrl_save_name,1, wx.ALL | wx.EXPAND,5)
        sizer_h2.Add(self.button_save_as,0, wx.ALL,5)

        self.sizer.Add(sizer_h2,0,wx.EXPAND,0)

        # Bindings
        self.choice_delete.Bind(wx.EVT_CHOICE, self.on_choice_mat)
        self.Bind(wx.EVT_CLOSE , self.on_close)


        self.on_choice_mat(None)

        self.SetSizer(self.sizer)
        self.sizer.SetSizeHints(self)
        self.Fit()
        pos=wx.GetMousePosition()
        self.SetPosition(pos)
        self.Show()

    def on_close(self,event):
        self.parent.Enable()
        event.Skip()


    def on_choice_mat(self,event):
        iselect=self.choice_delete.GetSelection()
        mat_name=self.choice_delete.GetStrings()[iselect]

        mat=self.solver.wall.config.get_material(mat_name)
        self.input.SetValues(mat_name)


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

        la,rho,Cp=self.input.GetValues()

        # name=self.ctrl_save_name.GetValue()
        # if len(name)==0: # takes name from choice above as we assume the goal is to overwrite it
            # error_dialog=wx.MessageDialog(self, "Must have a name", style=wx.OK | wx.ICON_WARNING)
            # answer=error_dialog.ShowModal()
            # self.ctrl_save_name.SetFocus()
            # self.ctrl_save_name.SetBackground()
        name=self.choice_delete.GetStrings()[self.choice_delete.GetSelection()]
        # else:
        if name in self.solver.wall.config.get_material_list():
            with wx.MessageDialog(self, "",style=wx.YES_NO | wx.ICON_WARNING) as error_dialog:

                self.localizer.link(error_dialog.SetMessage, "dialog_overwrite_name", "dialog_overwrite_name")
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
