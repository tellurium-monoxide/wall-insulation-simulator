import wx
from wx.lib.masked import NumCtrl
import wx.lib.scrolledpanel as scrolled
import matplotlib.backends.backend_wxagg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from threading import Thread
import time
from wall import Wall, Layer, Material, DefaultMaterials, DefaultScenarios

from localizer.localizer import Localizer

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


    
    

class PanelAnimatedFigure(wx.Panel):
    def __init__(self, parent, figure, min_size=(640,400)):
        wx.Panel.__init__(self, parent)
        self.parent=parent
        self.fixed_min_size=min_size
        self.canvas = FigureCanvasWxAgg(self, -1, figure)
        self.canvas.SetMinSize(self.fixed_min_size)
        self.canvas.draw_idle()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.canvas, 1, wx.BOTTOM|wx.EXPAND, 0)
        self.SetSizer(self.sizer)

        self.Fit()

        
    def LoadFigure(self,figure):
        self.Freeze()
        self.Disable()
        self.canvas.Destroy()
        self.canvas = FigureCanvasWxAgg(self, -1, figure)
        self.canvas.SetMinSize(self.fixed_min_size)
        self.canvas.draw_idle()
        self.Enable()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.BOTTOM|wx.EXPAND,0)
        self.SetSizer(self.sizer)
        self.Thaw()


class PanelNumericInput(wx.Panel):
    def __init__(self, parent, name="", def_val=1,integerWidth = 6,fractionWidth = 3, unit="", unit_scale=1):
        wx.Panel.__init__(self, parent)
        self.unit_scale=unit_scale
        self.def_val=def_val
        self.label=wx.StaticText(self, label=name, style=wx.ALIGN_RIGHT)
        self.eq=wx.StaticText(self, label=" = ",)
        self.num_ctrl = NumCtrl(self, value=def_val, integerWidth = integerWidth,fractionWidth = fractionWidth,allowNone = False,allowNegative = False,)
        self.unit=wx.StaticText(self, label=unit)

        self.sizer_h=wx.BoxSizer(wx.HORIZONTAL)

        self.sizer_h.Add(self.label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL , 0)
        self.sizer_h.Add(self.eq, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL , 0)
        self.sizer_h.Add(self.num_ctrl, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL , 0)
        self.sizer_h.Add(self.unit, 2, wx.LEFT | wx.ALIGN_CENTER_VERTICAL , 5)

        self.SetSizer(self.sizer_h)
        self.Fit()

    def GetValue(self):
        return (self.num_ctrl.GetValue()/self.unit_scale)
    def SetValue(self, val):
        self.num_ctrl.SetValue(val*self.unit_scale)


class PanelMaterialCreator(wx.Panel):
    def __init__(self, parent, localizer=Localizer()):
        wx.Panel.__init__(self, parent, style=wx.BORDER_STATIC)
        self.localizer=localizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)


        
        self.button_create= wx.Button(self)
        self.localizer.link(self.button_create.SetLabel, "button_create_mat", "button_create_mat")
        self.localizer.link(self.button_create.SetToolTip, "button_create_mat_tooltip", "button_create_mat_tooltip")
        self.sizer.Add(self.button_create,0, wx.ALL | wx.EXPAND,2)
        
        self.ctrl_save_name= wx.TextCtrl(self)
        self.sizer.Add(self.ctrl_save_name,0, wx.ALL | wx.EXPAND,2)



        # ask for mat param 1: lambda
        self.input_layer_mat_lambda=PanelNumericInput(self,name="\u03BB", unit="W/m/K")
        self.sizer.Add(self.input_layer_mat_lambda)


        # ask for mat param 2: rho
        self.input_layer_mat_rho=PanelNumericInput(self,name="\u03C1",unit="kg/m3")
        self.sizer.Add(self.input_layer_mat_rho)

        # ask for mat param 3: Cp
        self.input_layer_mat_cp=PanelNumericInput(self,name="Cp",unit="J/kg/K")
        self.sizer.Add(self.input_layer_mat_cp)



        self.SetSizer(self.sizer)
        self.Fit()
class PanelLayer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)



        self.input_layer_width=PanelNumericInput(self,name="e", unit="mm", unit_scale=1000, fractionWidth = 0)
        self.sizer.Add(self.input_layer_width)

        self.list_choices=["custom"]+list(DefaultMaterials.keys())
        

        self.typechoice= wx.Choice(self,choices=self.list_choices)
        self.typechoice.SetSelection(0)
        self.typechoice.Bind(wx.EVT_CHOICE, self.on_choice_mat)
        self.sizer.Add(self.typechoice, 0, wx.ALL | wx.EXPAND , 3)


        # ask for mat param 1: lambda
        self.input_layer_mat_lambda=PanelNumericInput(self,name="\u03BB", unit="W/m/K")
        self.sizer.Add(self.input_layer_mat_lambda)


        # ask for mat param 2: rho
        self.input_layer_mat_rho=PanelNumericInput(self,name="\u03C1",unit="kg/m3")
        self.sizer.Add(self.input_layer_mat_rho)

        # ask for mat param 3: Cp
        self.input_layer_mat_cp=PanelNumericInput(self,name="Cp",unit="J/kg/K")
        self.sizer.Add(self.input_layer_mat_cp)



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

        self.button_edit= wx.Button(self, label="Edit layers")
        self.localizer.link(self.button_edit.SetLabel, "button_edit", "button_edit")
        
        self.button_add= wx.Button(self, label='Add layer')
        self.localizer.link(self.button_add.SetLabel, "button_add", "button_add")
        
        self.button_remove= wx.Button(self, label='Remove layer')
        self.localizer.link(self.button_remove.SetLabel, "button_remove", "button_remove")
        
        self.button_load= wx.Button(self, label='Load')
        self.localizer.link(self.button_load.SetLabel, "button_load", "button_load")
        self.localizer.link(self.button_load.SetToolTip, "button_load_tooltip", "button_load_tooltip")
        
        

        self.list_scenarios=["custom"]+list(DefaultScenarios.keys())
        self.choice_scenario= wx.Choice(self,choices=self.list_scenarios)
        self.choice_scenario.SetSelection(0)
        
        self.button_save= wx.Button(self, label='Load')
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
        self.sizer_h.Add(self.ctrl_save_name, 0, wx.ALL, 5)







        self.sizer_v.Add(self.sizer_h, 0, wx.ALL, 3)

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

class PanelTempControl(wx.Panel):
    def __init__(self, parent, wall):
        wx.Panel.__init__(self, parent)

        sizer_h = wx.BoxSizer(wx.HORIZONTAL)


        self.slider_Tint=wx.Slider(self,value=wall.Tint,minValue=wall.Tmin, maxValue=wall.Tmax, style=wx.SL_LABELS, size=(300,-1), name="Tint")
        sizer_h.Add(self.slider_Tint, 5, wx.LEFT | wx.EXPAND, 5)

        self.slider_Tout=wx.Slider(self,value=wall.Tout,minValue=wall.Tmin, maxValue=wall.Tmax, style=wx.SL_LABELS, size=(300,-1))
        sizer_h.Add(self.slider_Tout, 5, wx.LEFT | wx.EXPAND, 5)

        self.SetSizer(sizer_h)

        self.Fit()

    def update(self,wall):
        self.slider_Tint.SetValue(wall.Tint)
        self.slider_Tout.SetValue(wall.Tout)
        self.Fit()



class PanelWallInfo(wx.Panel):
    def __init__(self, parent, localizer=Localizer()):
        wx.Panel.__init__(self, parent)
        self.localizer=localizer
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

        self.info_time=wx.StaticText(self,label="")
        self.sizer_v.Add(self.info_time, 0, wx.LEFT, 3)
        
        self.info_dt=wx.StaticText(self,label="")
        self.sizer_v.Add(self.info_dt, 0, wx.LEFT, 3)

        self.info_Rth=wx.StaticText(self,label="")
        self.sizer_v.Add(self.info_Rth, 0, wx.LEFT, 3)

        self.info_phi=wx.StaticText(self,label="")
        self.sizer_v.Add(self.info_phi, 0, wx.LEFT, 3)
        self.info_phi2=wx.StaticText(self,label="")
        self.sizer_v.Add(self.info_phi2, 0, wx.LEFT, 3)
        
        self.info_Nx=wx.StaticText(self,label="")
        self.sizer_v.Add(self.info_Nx, 0, wx.LEFT, 3)
        self.info_limit=wx.StaticText(self,label="")
        self.sizer_v.Add(self.info_limit, 0, wx.LEFT, 3)

        self.SetSizer(self.sizer_v)
        self.SetMinSize((350,-1))
        self.Fit()

    def update_info(self,wall):
        self.Freeze()
        self.info_time.SetLabel("Time = %s" % wall.get_formatted_time())
        self.info_dt.SetLabel("Time step = %s" % wall.get_formatted_time_step())
        Rth=sum([l.Rth for l in wall.layers])
        self.info_Rth.SetLabel("Total thermal resistance = %g K.m²/W" % Rth)
        phi_int_to_wall=wall.compute_phi()
        self.info_phi.SetLabel("Thermal flux from interior to wall = %g W/m²" % phi_int_to_wall)
        phi_int_to_out = (wall.Tout-wall.Tint) / Rth
        self.info_phi2.SetLabel("Thermal flux from interior to out  = %g W/m²" % phi_int_to_out)
        Nx= sum([layer.Npoints for layer in wall.layers])
        self.info_Nx.SetLabel("Nx= %d" % Nx)
        limiter=(wall.steps_to_statio/wall.limiter_ratio)
        self.info_limit.SetLabel("limiter = %g" % limiter)
        self.Fit()
        self.Thaw()

class MainPanel(wx.Panel):
    def __init__(self,parent,localizer=Localizer()):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.localizer=localizer
        wall=Wall()

        dt=1
        wall.set_time_step(dt)

        mat1=Material(la=1,rho=1,Cp=1)


        layer1=Layer(e=1, mat=mat1)

        wall.add_layer(layer1)

        wall.set_inside_temp(19)
        wall.set_outside_temp(5)


        wall.draw()

        self.wall=wall

        # ~ parent.status_bar.SetStatusText("a")


        self.run_sim=False



        # main vertical sizer
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

        space=5
# =============================================================================
# panel with main actions
# =============================================================================
        self.panel_menu = wx.Panel(self)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)

        # ~ self.panel_menu.button_run = wx.Button(self.panel_menu, label='Run')
        self.panel_menu.button_run = wx.Button(self.panel_menu)
        self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button", "run_button")
        self.localizer.link(self.panel_menu.button_run.SetToolTip, "run_button_tooltip", "run_button_tooltip")
        self.panel_menu.button_run.Bind(wx.EVT_BUTTON, self.on_press_run)
        sizer_h.Add(self.panel_menu.button_run, 0, wx.ALL, space)
        
        self.panel_menu.button_adv = wx.Button(self.panel_menu, label='Advance one timestep')
        self.localizer.link(self.panel_menu.button_adv.SetLabel, "button_advance", "button_advance")
        self.panel_menu.button_adv.Bind(wx.EVT_BUTTON, self.on_press_advance)
        sizer_h.Add(self.panel_menu.button_adv, 0, wx.ALL, space)

        self.panel_menu.button_statio = wx.Button(self.panel_menu, label='Set statio')
        self.localizer.link(self.panel_menu.button_statio.SetLabel, "button_statio", "button_statio")
        self.localizer.link(self.panel_menu.button_statio.SetToolTip, "button_statio_tooltip", "button_statio_tooltip")
        self.panel_menu.button_statio.Bind(wx.EVT_BUTTON, self.on_press_statio)
        sizer_h.Add(self.panel_menu.button_statio, 0, wx.ALL, space)

        self.panel_menu.button_reset = wx.Button(self.panel_menu, label='Reset')
        self.panel_menu.button_reset.Bind(wx.EVT_BUTTON, self.on_press_reset)
        sizer_h.Add(self.panel_menu.button_reset, 0, wx.ALL, space)

        # ~ self.panel_menu.lang_choice=wx.Choice(self.panel_menu, choices=[s.upper() for s in self.localizer.langs])
        # ~ self.panel_menu.lang_choice.SetSelection(0)
        # ~ self.panel_menu.lang_choice.Bind(wx.EVT_CHOICE, self.on_lang_choice)
        # ~ sizer_h.Add(self.panel_menu.lang_choice, 0, wx.ALL, space)
        
        self.panel_menu.SetSizer(sizer_h)

        self.sizer_v.Add(self.panel_menu,0, wx.ALL,2)
# =============================================================================
# panel to manage layer
# =============================================================================
        self.mat_creator=PanelMaterialCreator(self, localizer=self.localizer)
        self.layermgr=PanelLayerMgr(self, localizer=self.localizer)
        self.layermgr.panel_layer_list.load_layers(self.wall.layers)
        
        sizer_h=wx.BoxSizer(wx.HORIZONTAL)
        sizer_h.Add(self.mat_creator,0, wx.ALL | wx.EXPAND,2)
        sizer_h.Add(self.layermgr,0, wx.ALL,2)
        
        self.sizer_v.Add(sizer_h,0, wx.ALL | wx.ALL,2)
# =============================================================================
# panel to show animated figure
# =============================================================================


        self.panel_fig_sliders=wx.Panel(self)

        self.slider_Tint=wx.Slider(self.panel_fig_sliders,value=self.wall.Tint,minValue=self.wall.Tmin, maxValue=self.wall.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tint")
        self.panelfig = PanelAnimatedFigure(self.panel_fig_sliders, self.wall.figure)
        self.slider_Tout=wx.Slider(self.panel_fig_sliders,value=self.wall.Tout,minValue=self.wall.Tmin, maxValue=self.wall.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_LEFT | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tout")

        self.panel_info=PanelWallInfo(self.panel_fig_sliders, self.localizer)
        self.panel_info.update_info(self.wall)

        # create a FlexGridSizer to position the figure, sliders...
        sizer_h_fig_sliders = wx.FlexGridSizer(2,4,10,10)
        sizer_h_fig_sliders.AddGrowableRow(1, proportion=1)
        sizer_h_fig_sliders.AddGrowableCol(1, proportion=1)
        sizer_h_fig_sliders.AddGrowableCol(3, proportion=1)

        # add content to the sizer
        sizer_h_fig_sliders.Add(wx.StaticText(self.panel_fig_sliders,label="Tint (°C)"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_h_fig_sliders.Add(wx.StaticText(self.panel_fig_sliders,label="Temperature in the wall") ,1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_h_fig_sliders.Add(wx.StaticText(self.panel_fig_sliders,label="Text (°C)"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_h_fig_sliders.Add(wx.StaticText(self.panel_fig_sliders,label="Info"), 0,0)
        sizer_h_fig_sliders.Add(self.slider_Tint, 0,wx.EXPAND)
        sizer_h_fig_sliders.Add(self.panelfig, 1,wx.EXPAND)
        sizer_h_fig_sliders.Add(self.slider_Tout, 0, wx.EXPAND)

        sizer_h_fig_sliders.Add(self.panel_info, 1, wx.EXPAND)
        self.panel_fig_sliders.SetSizer(sizer_h_fig_sliders)
        sizer_h_fig_sliders.SetSizeHints(self.panel_fig_sliders)
        self.sizer_h_fig_sliders=sizer_h_fig_sliders

        self.sizer_v.Add(self.panel_fig_sliders, 1, wx.ALL | wx.EXPAND, 2)



# =============================================================================
# set the main sizer
# =============================================================================
        self.SetSizer(self.sizer_v)
        self.sizer_v.SetSizeHints(parent)


# =============================================================================
# bindings
# =============================================================================
        # manage main update
        self.updates=0
        self.time_last_redraw=time.process_time()
        self.this_run_time=0
        self.this_run_updates=0
        
        self.timer_update_redraw= wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer_redraw, self.timer_update_redraw)
        
        

        self.Bind(EVT_NEW_LAYERS, self.on_receive_layers)

        self.slider_Tint.Bind(wx.EVT_SLIDER, self.on_slide_Tint)
        self.slider_Tout.Bind(wx.EVT_SLIDER, self.on_slide_Tout)
        self.Bind(wx.EVT_CLOSE , self.on_close)


    def on_close(self,event):
        if self.run_sim:
            self.timer_update_redraw.Stop()
            self.run_sim=False
        event.skip()

    def on_press_run(self, event):
        self.run_sim=not(self.run_sim)
        if self.run_sim:
            self.update_in_thread()
            self.timer_update_redraw.Start(30)
            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button_pause", "run_button")
            self.panel_menu.button_adv.Disable()
        else:
            self.timer_update_redraw.Stop()
            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button", "run_button")
            self.panel_menu.button_adv.Enable()
            self.this_run_time=0
            self.this_run_updates=0


    def on_receive_layers(self, event):
        layers=event.GetLayers()
        self.wall.change_layers(layers)
        self.redraw()

    def on_press_statio(self,event):
        self.wall.solve_stationnary()
        self.wall.time=0
        self.redraw()

    def on_press_reset(self,event):
        self.wall.remesh()
        self.redraw()


    def on_slide_Tint(self,event):
        Tint= self.slider_Tint.GetValue()
        self.wall.set_inside_temp(Tint)
        if not(self.run_sim):
            self.redraw()

    def on_slide_Tout(self,event):
        Tout= self.slider_Tout.GetValue()
        self.wall.set_outside_temp(Tout)
        if not(self.run_sim):
            self.redraw()
            
    # ~ def on_lang_choice(self,event):
        # ~ sel=self.panel_menu.lang_choice.GetSelection()
        # ~ lang=self.localizer.langs[sel]
        # ~ self.localizer.set_lang(lang)
        # ~ self.Layout()


    def on_timer_update(self,event):
        self.update_sim()
        self.updates+=1
    def on_press_advance(self,event):
        self.update_sim()
        self.redraw()
        
    def on_timer_redraw(self,event):
        if self.thread.is_alive():
            self.thread.join()
            
        self.redraw()
        # ~ print("updates since last redraw ",self.updates)
        
        time_new_redraw=time.process_time()
        self.time_since_redraw=time_new_redraw-self.time_last_redraw
        # ~ print("updates since last redraw ",self.time_since_redraw * 1000, 'ms')
        
        self.this_run_time+=self.time_since_redraw
        self.this_run_updates+=self.updates
        # ~ print("updates per seconds :",self.this_run_updates/self.this_run_time)
        # ~ print("progression to statio :",self.wall.time_to_statio/(self.wall.time+self.wall.dt))
        
        self.time_last_redraw=time.process_time()
        
        self.updates=0
        
        self.update_in_thread()
        
    def update_in_thread(self):
        self.thread = Thread(target=self.update_sim)
        self.thread.start()
        self.updates+=1
        
    def update_sim(self):
        
        self.wall.advance_time()
        
        if self.run_sim:
            time_new_redraw=time.process_time()
            self.time_since_redraw=time_new_redraw-self.time_last_redraw
            
            if self.time_since_redraw*1000 < self.timer_update_redraw.GetInterval() and not(self.time_since_redraw > 0 and self.updates/self.time_since_redraw > self.wall.steps_to_statio/self.wall.limiter_ratio):
                wx.CallAfter(self.update_in_thread)
        



    def redraw(self):
        self.panel_info.update_info(self.wall)
        self.wall.draw()
        self.panelfig.LoadFigure(self.wall.figure)
        
        


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='wall-simulator', style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER))
        
        self.localizer=Localizer()
        self.localizer.set_lang("fr")
        menubar = wx.MenuBar()
        menu_edit=wx.Menu()
        menu_lang=wx.Menu()
        
        
        actions={}
        for lang in self.localizer.langs:
            item=menu_lang.Append(-1, lang.upper(), '')
            self.Bind(wx.EVT_MENU,  self.on_lang_change)
            
            
        
        # ~ menu_edit.AppendSubMenu(menu_lang, 'Lang')
        
        menubar.Append(menu_lang, 'Lang')
        
        self.SetMenuBar(menubar)
        
        
        
        self.main_panel=MainPanel(self, localizer=self.localizer)
        
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

        self.sizer_v.Add(self.main_panel, 1, wx.EXPAND, 0)

        
        self.SetSizer(self.sizer_v)
        self.sizer_v.SetSizeHints(self)
# =============================================================================
# show the frame
# =============================================================================
        # ~ display = wx.Display(0)
        # ~ x, y, w, h = display.GetGeometry()
        # ~ self.SetPosition((w, h))
        self.Show()
        # ~ self.Maximize(True)

    def on_lang_change(self,event):
        self.localizer.set_lang(event.GetEventObject().FindItemById(event.GetId()).GetItemLabel().lower())
        self.Layout()

if __name__ == '__main__':
    app = wx.App()

    frame = MainFrame()





    app.MainLoop()

