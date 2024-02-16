import wx
from wx.lib.masked import NumCtrl
#import wx.lib.scrolledpanel
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx


from wall import Wall, Layer, Material, DefaultMaterialList, DefaultMaterials


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
    def __init__(self, parent, figure):
        wx.Panel.__init__(self, parent)
        self.canvas = FigureCanvas(self, -1, figure)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
    def LoadFigure(self,figure):
        old=self.canvas
        self.Freeze()
        self.Disable()
        self.canvas = FigureCanvas(self, -1, figure)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT)
        self.SetSizer(self.sizer)
        self.Fit()
        # ~ self.canvas.draw()
        old.Destroy()
        self.Enable()
        self.Thaw()
        

class PanelNumericInput(wx.Panel):
    def __init__(self, parent, name="", def_val=1,integerWidth = 6,fractionWidth = 2, unit=""):
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
        
        self.list_choices=["custom"]+DefaultMaterialList()
        
        self.typechoice= wx.Choice(self,choices=self.list_choices)
        self.typechoice.SetSelection(0)
        self.typechoice.Bind(wx.EVT_CHOICE, self.on_choice_mat)
        self.sizer.Add(self.typechoice, 0, wx.ALL | wx.EXPAND , 3)
        
        
        # ask for mat param 1: lambda
        self.input_layer_mat_lambda=PanelNumericInput(self,name="la", unit="W/m/K")        
        self.sizer.Add(self.input_layer_mat_lambda)

        
        # ask for mat param 2: rho
        self.input_layer_mat_rho=PanelNumericInput(self,name="rho",unit="kg/m3")        
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
        self.typechoice.SetSelection(0)
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
        

    def add_layer(self, event):
        lay= PanelLayer(self)
        self.layer_panels.append(lay)
        self.sizer_h.Add(lay, 0, wx.LEFT, 5)
        self.Fit()
        self.parent.Fit()

    def remove_layer(self, event):
        if len(self.layer_panels)>1:
            self.layer_panels.pop().Destroy()
            self.Fit()
            self.parent.Fit()
            
class PanelLayerMgr(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        
        self.button_freeze= wx.Button(self, label="Edit layers")
        self.button_add= wx.Button(self, label='Add layer')
        self.button_remove= wx.Button(self, label='Remove layer')
        
        
        
        self.sizer_h.Add(self.button_freeze, 0, wx.LEFT, 5)
        self.sizer_h.Add(self.button_add, 0, wx.LEFT, 3) 
        self.sizer_h.Add(self.button_remove, 0, wx.LEFT, 5)
        
        
        
        
        
        
        
        self.sizer_v.Add(self.sizer_h, 0, wx.LEFT, 3) 
        
        self.panel_layer_list=PanelLayerList(self)
        self.sizer_v.Add(self.panel_layer_list, 0, wx.LEFT, 3)
        
        self.button_add.Bind(wx.EVT_BUTTON, self.panel_layer_list.add_layer)
        self.button_remove.Bind(wx.EVT_BUTTON, self.panel_layer_list.remove_layer)
        self.button_freeze.Bind(wx.EVT_BUTTON, self.freeze)
        
        
        self.SetSizer(self.sizer_v)
        self.Fit()
    
        self.is_frozen=False
        self.freeze(wx.IdleEvent())
        
    def freeze(self, event):
        self.is_frozen=not(self.is_frozen)
        if not(self.is_frozen): # set it to unfrozen state
            self.button_freeze.SetLabel("Confirm layers")
            self.panel_layer_list.Enable()
            self.button_add.Enable()
            self.button_remove.Enable()
            # ~ self.panel_layers.Thaw()
        else:# set to frozen state and send confirmed layers above
            self.button_freeze.SetLabel("Edit layers")
            # ~ self.panel_layers.Freeze()
            self.panel_layer_list.Disable()
            self.button_add.Disable()
            self.button_remove.Disable()
            layers=self.gather_layers()
            event = EventNewLayers(myEVT_NEW_LAYERS, self.GetId())
            event.SetLayers(layers)
            self.GetEventHandler().ProcessEvent(event)
            
    def gather_layers(self):
        layers=[]
        for panel_layer in self.panel_layer_list.layer_panels:
            layer = panel_layer.get_layer()
            layers.append(layer)
        return layers
        

            
class MainFrame(wx.Frame):   
    def __init__(self):
        super().__init__(parent=None, title='wall-simulator',size=(1000, 1000))
        
        
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
        
        
        # main vertical sizer
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)
        
# =============================================================================
# panel with main actions
# =============================================================================
        panel_menu = wx.Panel(self)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)        
    
        self.button_run = wx.Button(panel_menu, label='Run')
        self.button_run.Bind(wx.EVT_BUTTON, self.on_press_run)
        sizer_h.Add(self.button_run, 0, wx.LEFT, 5)
        
        self.button_statio = wx.Button(panel_menu, label='Set statio')
        self.button_statio.Bind(wx.EVT_BUTTON, self.on_press_statio)
        sizer_h.Add(self.button_statio, 0, wx.LEFT, 5)
        
        self.button_reset = wx.Button(panel_menu, label='Reset')
        self.button_reset.Bind(wx.EVT_BUTTON, self.on_press_reset)
        sizer_h.Add(self.button_reset, 0, wx.LEFT, 5)
        

        
        panel_menu.SetSizer(sizer_h)
        
        self.sizer_v.Add(panel_menu,0, wx.TOP,5)
# =============================================================================
# panel to change global parameters
# =============================================================================
        panel_params=wx.Panel(self)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        
        self.button_get_params = wx.Button(panel_params, label='Apply params')
        self.button_get_params.Bind(wx.EVT_BUTTON, self.on_press_get_params)
        sizer_h.Add(self.button_get_params, 1, wx.LEFT, 4)
        
        panel_params.input_dt=PanelNumericInput(panel_params, name="dt",unit="s", def_val=wall.dt,fractionWidth = 6)
        sizer_h.Add(panel_params.input_dt, 1, wx.LEFT, 5)
        
        panel_params.input_int_temp=PanelNumericInput(panel_params, name="Tint",unit="°C", def_val=wall.Tint)
        sizer_h.Add(panel_params.input_int_temp, 1, wx.LEFT, 5)
        
        panel_params.input_out_temp=PanelNumericInput(panel_params, name="Tout",unit="°C", def_val=wall.Tout)
        sizer_h.Add(panel_params.input_out_temp, 1, wx.LEFT, 5)
        
        panel_params.slider=wx.Slider(panel_params,minValue=-20, maxValue=50, style=wx.SL_LABELS)
        sizer_h.Add(panel_params.slider, 5, wx.ALL, 5)
        
        panel_params.SetSizer(sizer_h)
        self.panel_params=panel_params
        self.sizer_v.Add(self.panel_params,0, wx.ALL | wx.TOP,5)
# =============================================================================
# panel to manage layer
# =============================================================================
        self.layermgr=PanelLayerMgr(self)
        self.sizer_v.Add(self.layermgr,0, wx.ALL | wx.TOP,5)
# =============================================================================
# panel to show animated figure
# =============================================================================
        self.panelfig = PanelAnimatedFigure(self, self.wall.figure)
        self.sizer_v.Add(self.panelfig, 0, wx.ALL | wx.TOP, 5)
        
    
        # set the main sizer
        self.SetSizer(self.sizer_v)
        
        
        
        
        
        
        
# =============================================================================
# bindings
# =============================================================================
        # manage main update
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_sim, self.timer)
        
        self.Bind(EVT_NEW_LAYERS, self.on_receive_layers)
             
        self.Show()
        self.Maximize(True)
        
        
        

    def on_press_run(self, event):
        self.run_sim=not(self.run_sim)
        if self.run_sim:
            self.timer.Start(30)
            self.button_run.SetLabel("Pause")
            self.panel_params.input_dt.Disable()
        else:
            self.timer.Stop()
            self.button_run.SetLabel("Run")
            self.panel_params.input_dt.Enable()
            
            
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
        
    def on_press_get_params(self, event):
        dt = self.panel_params.input_dt.GetValue()
        Tint= self.panel_params.input_int_temp.GetValue()
        Tout= self.panel_params.input_out_temp.GetValue()
        
        self.wall.set_inside_temp(Tint)
        self.wall.set_outside_temp(Tout)
        
        if dt<1e-8:
            print("Entered dt too close to zero or negative.")
        elif abs(dt-self.wall.dt)/dt > 0.001:
            self.wall.set_time_step(dt)
        self.redraw()

        

    def update_sim(self,event):

        self.wall.advance_time()
        self.redraw()

    
    def redraw(self):
        self.panel_params.input_dt.SetValue(self.wall.dt)
        self.wall.draw()
        self.panelfig.LoadFigure(self.wall.figure)



        
        
if __name__ == '__main__':
    app = wx.App()
    
    frame = MainFrame()
    
    
  
    app.MainLoop()
    
