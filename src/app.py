import wx
from wx.lib.masked import NumCtrl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

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
		self.sizer.Add(self.canvas, 1, wx.LEFT)
		self.SetSizer(self.sizer)
		self.Fit()
	def LoadFigure(self,figure):
		old=self.canvas
		self.Freeze()
		self.canvas = FigureCanvas(self, -1, figure)
		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.canvas, 1, wx.LEFT)
		self.SetSizer(self.sizer)
		self.Fit()
		# ~ self.canvas.draw()
		# ~ self.Refresh()
		# ~ self.Fit()
		old.Destroy()
		self.Thaw()
		# ~ self.Refresh()
		


class PanelLayer(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		
		
		
		self.sizer_h1=wx.BoxSizer(wx.HORIZONTAL)
		label=wx.StaticText(self, label="e=")
		self.width_ctrl = NumCtrl(self, value=1, integerWidth = 6,fractionWidth = 2,allowNone = False,allowNegative = False,)
			
		self.sizer_h1.Add(label, 0, wx.ALL | wx.EXPAND, 3) 
		self.sizer_h1.Add(self.width_ctrl, 0, wx.ALL | wx.EXPAND, 3) 
		
		self.sizer.Add(self.sizer_h1)
		
		self.list_choices=["custom"]+DefaultMaterialList()
		
		self.typechoice= wx.Choice(self,choices=self.list_choices)
		self.typechoice.SetSelection(0)
		self.typechoice.Bind(wx.EVT_CHOICE, self.on_choice_mat)
		self.sizer.Add(self.typechoice, 0, wx.ALL | wx.EXPAND, 3)
		
		
		# ask for mat param 1: lambda
		self.sizer_h2=wx.BoxSizer(wx.HORIZONTAL)
		label=wx.StaticText(self, label="la=")
		self.mat_la_ctrl = NumCtrl(self, value=1, integerWidth = 6,fractionWidth = 2,allowNone = False,allowNegative = False,)
			
		self.sizer_h2.Add(label, 0, wx.ALL | wx.EXPAND, 3) 
		self.sizer_h2.Add(self.mat_la_ctrl, 0, wx.ALL | wx.EXPAND, 3) 
		
		self.sizer.Add(self.sizer_h2)
		
		# ask for mat param 2: rho
		self.sizer_h3=wx.BoxSizer(wx.HORIZONTAL)
		label=wx.StaticText(self, label="rho=")
		self.mat_rho_ctrl = NumCtrl(self, value=1, integerWidth = 6,fractionWidth = 2,allowNone = False,allowNegative = False,)
			
		self.sizer_h3.Add(label, 0, wx.ALL | wx.EXPAND, 3) 
		self.sizer_h3.Add(self.mat_rho_ctrl, 0, wx.ALL | wx.EXPAND, 3) 
		
		self.sizer.Add(self.sizer_h3)
		
		# ask for mat param 3: Cp
		self.sizer_h4=wx.BoxSizer(wx.HORIZONTAL)
		label=wx.StaticText(self, label="Cp=")
		self.mat_cp_ctrl = NumCtrl(self, value=1, integerWidth = 6,fractionWidth = 2,allowNone = False,allowNegative = False,)
			
		self.sizer_h4.Add(label, 0, wx.ALL | wx.EXPAND, 3) 
		self.sizer_h4.Add(self.mat_cp_ctrl, 0, wx.ALL | wx.EXPAND, 3) 
		
		self.sizer.Add(self.sizer_h4)
		
		

		self.SetSizer(self.sizer)
		self.Fit()
		
	def on_choice_mat(self,event):
		iselect=self.typechoice.GetSelection()
		mat_name=self.list_choices[iselect]
		if iselect>0:
			mat=DefaultMaterials[mat_name]
			self.mat_la_ctrl.SetValue(mat.la)
			self.mat_la_ctrl.Disable()
			self.mat_rho_ctrl.SetValue(mat.rho)
			self.mat_rho_ctrl.Disable()
			self.mat_cp_ctrl.SetValue(mat.Cp)
			self.mat_cp_ctrl.Disable()
		else:
			self.mat_la_ctrl.Enable()
			self.mat_rho_ctrl.Enable()
			self.mat_cp_ctrl.Enable()
		# ~ print("on_choice was triggered. Selected item is: " + str(self.typechoice.GetSelection()))
		
		
	def get_layer(self):
		la=self.mat_la_ctrl.GetValue()
		rho=self.mat_rho_ctrl.GetValue()
		Cp=self.mat_cp_ctrl.GetValue()
		mat=Material(la=la, rho=rho, Cp=Cp)
		e=self.width_ctrl.GetValue()
		layer=Layer(e=e, mat=mat)
		return layer
		
class PanelLayerList(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
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
		
		self.button_add= wx.Button(self, label='Add layer')
		self.button_remove= wx.Button(self, label='Remove layer')
		self.button_freeze= wx.Button(self, label="Edit layers")
		
		
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
		super().__init__(parent=None, title='Hello World',size=(1000, 800))
		
		
		wall=Wall()
		
		dt=0.08
		wall.set_time_step(dt)
		
		mat1=Material(la=0.05,rho=1,Cp=1)
		mat2=Material(la=0.4,rho=3,Cp=1)
		
		layer1=Layer(e=1, mat=mat1)
		layer2=Layer(e=2, mat=mat2)
		
		wall.add_layer(layer1)
		wall.add_layer(layer2)
		
		wall.set_inside_temp(19)
		wall.set_outside_temp(5)
		
		
		
		print(wall.courant)
	
		# ~ wall.solve_stationnary()
		wall.draw()
		
		self.wall=wall
		
		
		
		
		self.run_sim=False
		
		
		
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
		
# =============================================================================
# panel to manage layer
# =============================================================================
		self.layermgr=PanelLayerMgr(self)
# =============================================================================
# panel to show animated figure
# =============================================================================
		self.panelfig = PanelAnimatedFigure(self, self.wall.figure)
		
		
# =============================================================================
# panel to show figure
# =============================================================================
		self.sizer_v = wx.BoxSizer(wx.VERTICAL)
		self.sizer_v.Add(panel_menu,0, wx.TOP,5)
		
		
		self.sizer_v.Add(self.layermgr,0, wx.ALL | wx.TOP,5)
		self.sizer_v.Add(self.panelfig, 0, wx.ALL | wx.TOP, 5)
		
		self.SetSizer(self.sizer_v)
		
# =============================================================================
# bindings
# =============================================================================
		# manage main update
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update_sim, self.timer)
		
		self.Bind(EVT_NEW_LAYERS, self.on_receive_layers)
			 
		self.Show()
		
		
		

	def on_press_run(self, event):
		self.run_sim=not(self.run_sim)
		if self.run_sim:
			self.timer.Start(30)
			self.button_run.SetLabel("Pause")
		else:
			self.timer.Stop()
			self.button_run.SetLabel("Run")
			
		# ~ self.text_ctrl = wx.TextCtrl(panel)
		# ~ my_sizer.Add(self.text_ctrl, 0, wx.ALL | wx.EXPAND, 5)    
		# ~ value = self.text_ctrl.GetValue()
		# ~ if not value:
			# ~ print("You didn't enter anything!")
		# ~ else:
			# ~ print(f'You typed: "{value}"')

	def on_receive_layers(self, event):
		layers=event.GetLayers()
		self.wall.change_layers(layers)
		print(len(self.wall.layers))
		self.redraw()
		# ~ self.wall.ax.clear()
		# ~ self.wall.draw_wall()
		# ~ self.panelfig.LoadFigure(self.wall.figure)
		
		# ~ print(layers[0].e)
		
	def on_press_statio(self,event):
		self.wall.solve_stationnary()
		self.redraw()
		
	def on_press_reset(self,event):
		self.wall.remesh()
		self.redraw()

	def update_sim(self,event):

		self.wall.advance_time()
		self.redraw()

	
	def redraw(self):
		self.wall.draw()
		self.panelfig.LoadFigure(self.wall.figure)



		
		
if __name__ == '__main__':
	app = wx.App()
	frame = MainFrame()
	
	
  
	app.MainLoop()
	
