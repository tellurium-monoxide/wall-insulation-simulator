import wx
from wx.lib.masked import NumCtrl
import wx.lib.scrolledpanel as scrolled
import matplotlib.backends.backend_wxagg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from threading import Thread
import time
import copy
from functools import partial

# local imports
from physics_module.solver import Layer, Material
from physics_module.solver import SolverHeatEquation1dMultilayer as Solver
# ~ from physics_module.materials import Material, DefaultMaterials

from localizer.mylocalizer import MyLocalizer

# interface imports

from panel_input_physical_value import PanelNumericInput as PanelNumericInput
from panel_wall_creator import PanelLayerMgr, PanelMaterialCreator, EVT_WALL_SETUP_CHANGED






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


class PanelTempControl(wx.Panel):
    def __init__(self, parent, solver):
        wx.Panel.__init__(self, parent)

        sizer_h = wx.BoxSizer(wx.HORIZONTAL)


        self.slider_Tint=wx.Slider(self,value=solver.Tint,minValue=solver.Tmin, maxValue=solver.Tmax, style=wx.SL_LABELS, size=(300,-1), name="Tint")
        sizer_h.Add(self.slider_Tint, 5, wx.LEFT | wx.EXPAND, 5)

        self.slider_Tout=wx.Slider(self,value=solver.Tout,minValue=solver.Tmin, maxValue=solver.Tmax, style=wx.SL_LABELS, size=(300,-1))
        sizer_h.Add(self.slider_Tout, 5, wx.LEFT | wx.EXPAND, 5)

        self.SetSizer(sizer_h)

        self.Fit()

    def update(self,solver):
        self.slider_Tint.SetValue(solver.Tint)
        self.slider_Tout.SetValue(solver.Tout)
        self.Fit()



class PanelSolverInfo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

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

    def update_info(self,solver):
        self.Freeze()
        self.info_time.SetLabel("Time = %s" % solver.get_formatted_time())
        self.info_dt.SetLabel("Time step = %s" % solver.get_formatted_time_step())
        Rth=sum([l.Rth for l in solver.wall.layers])
        self.info_Rth.SetLabel("Total thermal resistance = %g K.m²/W" % Rth)
        phi_int_to_solver=solver.compute_phi()
        self.info_phi.SetLabel("Thermal flux from interior to solver = %g W/m²" % phi_int_to_solver)
        phi_int_to_out = (solver.Tout-solver.Tint) / Rth
        self.info_phi2.SetLabel("Thermal flux from interior to out  = %g W/m²" % phi_int_to_out)
        Nx= sum([layer.Npoints for layer in solver.wall.layers])
        self.info_Nx.SetLabel("Nx= %d" % Nx)
        limiter=(solver.steps_to_statio/solver.limiter_ratio)
        self.info_limit.SetLabel("limiter = %g" % limiter)
        self.Fit()
        self.Thaw()

class MainPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.localizer=parent.localizer
        self.solver=Solver()


        self.solver.set_inside_temp(19)
        self.solver.set_outside_temp(5)


        self.localizer.link(self.solver.set_text_inside, "plot_text_inside", "plot_text_inside")
        self.localizer.link(self.solver.set_text_inside, "plot_text_outside", "plot_text_outside")

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


        self.panel_menu.SetSizer(sizer_h)

        self.sizer_v.Add(self.panel_menu,0, wx.ALL,2)
# =============================================================================
# panel to manage layer
# =============================================================================
        # self.mat_creator=PanelMaterialCreator(self)
        self.layermgr=PanelLayerMgr(self)
        self.layermgr.panel_layer_list.load_layers(self.solver.wall.layers)

        sizer_h=wx.BoxSizer(wx.HORIZONTAL)
        # sizer_h.Add(self.mat_creator,0, wx.ALL | wx.EXPAND,2)
        sizer_h.Add(self.layermgr,0, wx.ALL,2)

        self.sizer_v.Add(sizer_h,0, wx.ALL | wx.ALL,2)
# =============================================================================
# panel to show animated figure
# =============================================================================


        self.panel_fig_sliders=wx.Panel(self)
        self.panel_fig_sliders.solver=self.solver
        self.panel_fig_sliders.localizer=self.localizer

        self.slider_Tint=wx.Slider(self.panel_fig_sliders,value=self.solver.Tint,minValue=self.solver.Tmin, maxValue=self.solver.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tint")
        self.panelfig = PanelAnimatedFigure(self.panel_fig_sliders, self.solver.figure)
        self.slider_Tout=wx.Slider(self.panel_fig_sliders,value=self.solver.Tout,minValue=self.solver.Tmin, maxValue=self.solver.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_LEFT | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tout")

        self.panel_info=PanelSolverInfo(self.panel_fig_sliders)
        self.panel_info.update_info(self.solver)

        # create a FlexGridSizer to position the figure, sliders...
        sizer_h_fig_sliders = wx.FlexGridSizer(2,4,10,10)
        sizer_h_fig_sliders.AddGrowableRow(1, proportion=1)
        sizer_h_fig_sliders.AddGrowableCol(1, proportion=1)
        sizer_h_fig_sliders.AddGrowableCol(3, proportion=1)

        # add content to the sizer
        sizer_h_fig_sliders.Add(wx.StaticText(self.panel_fig_sliders,label="Tint (°C)"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_h_fig_sliders.Add(wx.StaticText(self.panel_fig_sliders,label="Temperature in the solver") ,1, wx.ALIGN_CENTER_HORIZONTAL)
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
        self.updates_since_redraw=0
        self.time_since_redraw=0
        self.time_last_redraw=time.perf_counter_ns()

        self.this_run_time=0
        self.this_run_updates=0

#        self.thread_update_loop = Thread(target=self.update_loop_thread)
        self.timer_update_redraw= wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer_redraw, self.timer_update_redraw)



        self.Bind(EVT_WALL_SETUP_CHANGED, self.on_receive_layers)

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
            self.this_run_start=time.perf_counter_ns()
            self.thread_update_loop = Thread(target=self.update_loop_thread)
            self.thread_update_loop.start()
            self.timer_update_redraw.Start(50)
            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button_pause", "run_button")
            self.panel_menu.button_adv.Disable()
        else:
            self.timer_update_redraw.Stop()
            self.thread_update_loop.join()
            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button", "run_button")
            self.panel_menu.button_adv.Enable()
            self.this_run_time=0
            self.this_run_updates=0


    def on_receive_layers(self, event):
        # ~ layers=event.GetLayers()
        # ~ self.solver.change_layers(layers)
        self.redraw()

    def on_press_statio(self,event):
        self.solver.solve_stationnary()
        self.solver.time=0
        self.redraw()

    def on_press_reset(self,event):
        self.solver.remesh()
        self.redraw()


    def on_slide_Tint(self,event):
        Tint= self.slider_Tint.GetValue()
        self.solver.set_inside_temp(Tint)
        if not(self.run_sim):
            self.redraw()

    def on_slide_Tout(self,event):
        Tout= self.slider_Tout.GetValue()
        self.solver.set_outside_temp(Tout)
        if not(self.run_sim):
            self.redraw()



    def on_press_advance(self,event):
        self.solver.advance_time()
        self.redraw()

    def on_timer_redraw(self,event):

        self.redraw()
        # ~ print("updates since last redraw ",self.updates_since_redraw)

        time_new_redraw=time.perf_counter_ns()
        self.time_since_redraw=time_new_redraw-self.time_last_redraw
        # ~ print("time since last redraw ",self.time_since_redraw/1e6, 'ms')

        self.this_run_time=time_new_redraw-self.this_run_start
        self.this_run_updates+=self.updates_since_redraw
        # ~ print("updates per seconds :",1e9*self.this_run_updates/self.this_run_time)
        # ~ print("progression to statio :",self.solver.time_to_statio/(self.solver.time+self.solver.dt))

        self.time_last_redraw=time.perf_counter_ns()

        self.updates_since_redraw=0


    def update_loop_thread(self):
        time_new_redraw=time.perf_counter_ns()
        self.time_since_redraw=time_new_redraw-self.time_last_redraw
        while self.run_sim:
            time.sleep(0.00001)
            time_new_redraw=time.perf_counter_ns()
            self.time_since_redraw=time_new_redraw-self.time_last_redraw
            needRedraw=self.time_since_redraw < self.timer_update_redraw.GetInterval()*1000000

            isTooFast=self.time_since_redraw > 0 and self.updates_since_redraw/self.time_since_redraw*1e9 > self.solver.steps_to_statio/self.solver.limiter_ratio
            if  needRedraw and not(isTooFast):
                self.solver.advance_time()
                self.updates_since_redraw+=1
            # ~ elif isTooFast:
                # ~ print("limiting updates per sec")



    def redraw(self):
        self.panel_info.update_info(self.solver)
        self.solver.draw()
        self.panelfig.LoadFigure(self.solver.figure)




class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='wall-simulator', style=wx.DEFAULT_FRAME_STYLE)

        self.localizer=MyLocalizer()

        menubar = wx.MenuBar()


        menu_file=wx.Menu()


        self.menu_item_save=menu_file.Append(-1, "Save config", '')
        self.localizer.link(self.menu_item_save.SetItemLabel, "menu_file_save", "menu_file_save")
        self.menu_item_load=menu_file.Append(-1, "Load config", '')
        self.localizer.link(self.menu_item_load.SetItemLabel, "menu_file_load", "menu_file_load")

        menu_file.Bind(wx.EVT_MENU,  self.on_file_menu)


        menubar.Append(menu_file, 'File')

        self.contentSaved=False




        menu_lang=wx.Menu()
        for lang in self.localizer.langs:
            menu_lang.Append(-1, lang.upper(), '')

        menu_lang.Bind(wx.EVT_MENU,  self.on_lang_change)
        menubar.Append(menu_lang, 'Language')



        menu_help=wx.Menu()
        self.menu_item_help=menu_help.Append(-1, "Help", '')
        self.menu_item_website=menu_help.Append(-1, "Website", '')
        self.menu_item_about=menu_help.Append(-1, "About", '')

        menubar.Append(menu_help, 'Help')


        self.localizer.link(partial(menubar.SetMenuLabel,0), "menu_file", "menu_file")
        self.localizer.link(partial(menubar.SetMenuLabel,1), "menu_lang", "menu_lang")
        self.localizer.link(partial(menubar.SetMenuLabel,2), "menu_help", "menu_help")
        self.SetMenuBar(menubar)



        self.main_panel=MainPanel(self)

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
        # ~ self.Maximize(True)
        self.Show()


    def on_lang_change(self,event):
        self.localizer.set_lang(event.GetEventObject().FindItemById(event.GetId()).GetItemLabel().lower())
        self.main_panel.redraw()
        self.Layout()


    def on_file_menu(self,event):
        eventId=event.GetId()
        if eventId==self.menu_item_save.GetId():
            self.menu_action_save()
        if eventId==self.menu_item_load.GetId():
            self.menu_action_load()
        # print(event.GetEventObject().FindItemById(event.GetId()).GetItemLabel())
        # print(event.GetId())
        # print(self.menu_item_save.GetId())


    def menu_action_save(self):
        with wx.FileDialog(self, "Save WallConfig file", wildcard="WALLCONFIG files (*.wall)|*.wall",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'wb') as file:
                    self.main_panel.solver.wall.config.write_to_file(pathname, file)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)
            else:
                self.contentSaved=True

    def menu_action_load(self):
        if not(self.contentSaved):
            if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open WallConfig file", wildcard="WALLCONFIG files (*.wall)|*.wall",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'rb') as file:
                    self.main_panel.solver.wall.config.load_from_file(pathname, file)
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)
            else:
                self.main_panel.layermgr.update_after_config_change()
                self.contentSaved=True

if __name__ == '__main__':
    app = wx.App()

    frame = MainFrame()





    app.MainLoop()

