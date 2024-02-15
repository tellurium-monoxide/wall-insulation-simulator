import wx
from wx.lib.masked import NumCtrl
#import wx.lib.scrolledpanel
import matplotlib.backends.backend_wxagg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx


from wall import Wall, Layer, Material, DefaultMaterials, DefaultScenarios


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

class Localizer:
    
    def __init__(self):
        self.langs=["en","fr"]
        self.lang="en"
        
        self.texts={}
        for lang in self.langs:
            self.texts[lang]={}
        self.texts["en"]["run_button"]="Start"
        self.texts["fr"]["run_button"]="Démarrer"
        
        self.texts["en"]["run_button_pause"]="Stop"
        self.texts["fr"]["run_button_pause"]="Arrêter"
        
        self.texts["en"]["run_button_tooltip"]="Start simulating the diffusion of heat in the wall."
        self.texts["fr"]["run_button_tooltip"]="Démarre la simulation de diffusion de la température dans le mur."
        
        self.links={}
    def get_text(self, text_id):
        if text_id in self.texts[self.lang]:
            return self.texts[self.lang][text_id]
        else:
            return "missing text"
    def link(self,setter, text_id, link_name):
        
        setter(self.get_text(text_id))
        self.links[link_name]=(setter,text_id)
        
    def set_lang(self,lang):
        self.lang=lang
        for key, link in self.links.items():
            setter,text_id=link
            setter(self.get_text(text_id))
            print(text_id)
    
    

class PanelAnimatedFigure(wx.Panel):
    def __init__(self, parent, figure):
        wx.Panel.__init__(self, parent)
        self.parent=parent
        self.fixed_min_size=(640,400)
        self.canvas = FigureCanvasWxAgg(self, -1, figure)
        self.canvas.draw_idle()
        self.canvas.SetMinSize(self.fixed_min_size)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(self.sizer)
        
        self.Disable()
        self.Fit()
    def LoadFigure(self,figure):
        self.Freeze()
        self.canvas.Destroy()
        self.sizer.Destroy()
        self.canvas = FigureCanvasWxAgg(self, -1, figure)
        self.canvas.draw_idle()
        self.canvas.SetMinSize(self.fixed_min_size)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND,0)
        self.SetSizer(self.sizer)
        # ~ self.sizer.SetSizeHints(self.parent)

        self.Thaw()


class PanelNumericInput(wx.Panel):
    def __init__(self, parent, name="", def_val=1,integerWidth = 6,fractionWidth = 3, unit=""):
        wx.Panel.__init__(self, parent)

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
        return self.num_ctrl.GetValue()
    def SetValue(self, val):
        self.num_ctrl.SetValue(val)


class PanelLayer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)



        self.input_layer_width=PanelNumericInput(self,name="e", unit="m")
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
            self.input_layer_mat_lambda.Disable()
            self.input_layer_mat_rho.SetValue(mat.rho)
            self.input_layer_mat_rho.Disable()
            self.input_layer_mat_cp.SetValue(mat.Cp)
            self.input_layer_mat_cp.Disable()
        else:
            self.input_layer_mat_lambda.Enable()
            self.input_layer_mat_rho.Enable()
            self.input_layer_mat_cp.Enable()


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
        self.typechoice.SetSelection(mat_id)
        self.input_layer_width.SetValue(layer.e)
        self.input_layer_mat_lambda.SetValue(layer.mat.la)
        self.input_layer_mat_rho.SetValue(layer.mat.rho)
        self.input_layer_mat_cp.SetValue(layer.mat.Cp)


class PanelLayerList(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # ~ wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent,size=(wx.DisplaySize()[0],200))
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
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)

        self.button_edit= wx.Button(self, label="Edit layers")
        self.button_add= wx.Button(self, label='Add layer')
        self.button_remove= wx.Button(self, label='Remove layer')
        self.button_load= wx.Button(self, label='Load')
        

        self.list_scenarios=["custom"]+list(DefaultScenarios.keys())
        self.choice_scenario= wx.Choice(self,choices=self.list_scenarios)
        self.choice_scenario.SetSelection(0)

        self.sizer_h.Add(self.button_edit, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_add, 0, wx.ALL, 5)
        self.sizer_h.Add(self.button_remove, 0, wx.ALL, 5)
        self.sizer_h.AddSpacer(20)
        self.sizer_h.Add(self.button_load, 0, wx.ALL, 5)
        self.sizer_h.Add(self.choice_scenario, 0, wx.ALL, 5)







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
            self.button_edit.SetLabel("Confirm")
            self.panel_layer_list.Enable()
            self.button_add.Enable()
            self.button_remove.Enable()
            if set_custom:
                self.choice_scenario.SetSelection(0)
            # ~ self.panel_layers.Thaw()
        else:# set to frozen state and send confirmed layers above
            self.button_edit.SetLabel("Edit layers")
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
    def on_press_remove_layer(self, event):
        self.panel_layer_list.remove_layer()
        
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
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

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

        self.SetSizer(self.sizer_v)
        self.Fit()

    def update_info(self,wall):
        self.info_time.SetLabel("Time = %s" % wall.get_formatted_time())
        self.info_dt.SetLabel("Time step = %s" % wall.get_formatted_time_step())
        Rth=sum([l.Rth for l in wall.layers])
        self.info_Rth.SetLabel("Total thermal resistance = %g K.m²/W" % Rth)
        phi_int_to_wall=wall.compute_phi()
        self.info_phi.SetLabel("Thermal flux from interior to wall = %g W/m²" % phi_int_to_wall)
        phi_int_to_out = (wall.Tout-wall.Tint) / Rth
        self.info_phi2.SetLabel("Thermal flux from interior to out  = %g W/m²" % phi_int_to_out)
        self.Fit()

class MainPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)


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




        self.run_sim=False



        self.localizer=Localizer()

        # main vertical sizer
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

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
        sizer_h.Add(self.panel_menu.button_run, 0, wx.ALL, 2)
        
        self.panel_menu.button_adv = wx.Button(self.panel_menu, label='Advance one timestep')
        self.panel_menu.button_adv.Bind(wx.EVT_BUTTON, self.update_sim)
        sizer_h.Add(self.panel_menu.button_adv, 0, wx.ALL, 2)

        self.panel_menu.button_statio = wx.Button(self.panel_menu, label='Set statio')
        self.panel_menu.button_statio.Bind(wx.EVT_BUTTON, self.on_press_statio)
        sizer_h.Add(self.panel_menu.button_statio, 0, wx.ALL, 2)

        self.panel_menu.button_reset = wx.Button(self.panel_menu, label='Reset')
        self.panel_menu.button_reset.Bind(wx.EVT_BUTTON, self.on_press_reset)
        sizer_h.Add(self.panel_menu.button_reset, 0, wx.ALL, 2)

        self.panel_menu.lang_choice=wx.Choice(self.panel_menu, choices=[s.upper() for s in self.localizer.langs])
        self.panel_menu.lang_choice.SetSelection(0)
        self.panel_menu.lang_choice.Bind(wx.EVT_CHOICE, self.on_lang_choice)
        sizer_h.Add(self.panel_menu.lang_choice, 0, wx.ALL, 2)
        
        self.panel_menu.SetSizer(sizer_h)

        self.sizer_v.Add(self.panel_menu,0, wx.ALL,2)
# =============================================================================
# panel to manage layer
# =============================================================================
        self.layermgr=PanelLayerMgr(self)
        self.sizer_v.Add(self.layermgr,0, wx.ALL | wx.ALL,2)
# =============================================================================
# panel to show animated figure
# =============================================================================


        self.panel_fig_sliders=wx.Panel(self)

        self.slider_Tint=wx.Slider(self.panel_fig_sliders,value=self.wall.Tint,minValue=self.wall.Tmin, maxValue=self.wall.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tint")
        self.panelfig = PanelAnimatedFigure(self.panel_fig_sliders, self.wall.figure)
        self.slider_Tout=wx.Slider(self.panel_fig_sliders,value=self.wall.Tout,minValue=self.wall.Tmin, maxValue=self.wall.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_LEFT | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tout")

        self.panel_info=PanelWallInfo(self.panel_fig_sliders)
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
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_sim, self.timer)

        self.Bind(EVT_NEW_LAYERS, self.on_receive_layers)

        self.slider_Tint.Bind(wx.EVT_SLIDER, self.on_slide_Tint)
        self.slider_Tout.Bind(wx.EVT_SLIDER, self.on_slide_Tout)





    def on_press_run(self, event):
        self.run_sim=not(self.run_sim)
        if self.run_sim:
            self.timer.Start(30)
            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button_pause", "run_button")
            self.panel_menu.button_adv.Disable()
        else:
            self.timer.Stop()
            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button", "run_button")
            self.panel_menu.button_adv.Enable()


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
            
    def on_lang_choice(self,event):
        sel=self.panel_menu.lang_choice.GetSelection()
        lang=self.localizer.langs[sel]
        self.localizer.set_lang(lang)



    def update_sim(self,event):

        self.wall.advance_time()
        self.redraw()


    def redraw(self):
        self.panel_info.update_info(self.wall)
        self.wall.draw()
        self.panelfig.LoadFigure(self.wall.figure)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='wall-simulator',size=(1000, 1000))
        
        self.main_panel=MainPanel(self)
        self.CreateToolBar()
# =============================================================================
# show the frame
# =============================================================================
        # ~ display = wx.Display(0)
        # ~ x, y, w, h = display.GetGeometry()
        # ~ self.SetPosition((w, h))
        self.Show()
        # ~ self.Maximize(True)

if __name__ == '__main__':
    app = wx.App()

    frame = MainFrame()





    app.MainLoop()

