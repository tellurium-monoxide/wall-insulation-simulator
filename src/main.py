import wx

# import wx.lib.analogclock as wxclock

import matplotlib.backends.backend_wxagg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
# from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg

from threading import Thread
import time
import copy
from functools import partial

# local imports
from modules.physics.solver import Layer, Material
from modules.physics.solver import SolverHeatEquation1dMultilayer as Solver
# ~ from physics_module.materials import Material, DefaultMaterials

from modules.localizer.mylocalizer import MyLocalizer

# interface imports

from modules.gui.wall_customizer.panel_wall_customizer import PanelLayerMgr, StaticBoxWallCustomizerWrapper
from modules.gui.temperature_controller.controller_inside_temp import ControlInsideTemp

from modules.gui.events import *




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
        canvas = FigureCanvasWxAgg(self, -1, figure)
        canvas.SetMinSize(self.fixed_min_size)
        canvas.draw_idle()


        # self.canvas.Destroy()

        # self.Enable()
        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.sizer.Add(canvas, 1, wx.BOTTOM|wx.EXPAND,0)
        self.sizer.Replace(self.canvas, canvas)

        self.canvas.Destroy()
        self.canvas=canvas
        self.SetSizer(self.sizer)
        self.Thaw()


class FigureWithTemperatureSliders(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.solver=parent.solver
        self.localizer=parent.localizer




        self.slider_Tint=wx.Slider(self,value=self.solver.Tint,minValue=self.solver.Tmin, maxValue=self.solver.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tint")
        self.panelfig = PanelAnimatedFigure(self, self.solver.figure)
        self.slider_Tout=wx.Slider(self,value=self.solver.Tout,minValue=self.solver.Tmin, maxValue=self.solver.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_LEFT | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tout")

        self.ctrl_inside_temp = ControlInsideTemp(self, self.slider_Tint)

        # create a FlexGridSizer to position the figure, sliders...
        sizer_grid = wx.FlexGridSizer(2,4,10,10)
        sizer_grid.AddGrowableRow(1, proportion=1)
        sizer_grid.AddGrowableCol(2, proportion=1)
        # sizer_h_fig_sliders.AddGrowableCol(3, proportion=1)

        # add content to the sizer
        sizer_grid.Add(wx.StaticText(self,label="Room heating"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(wx.StaticText(self,label="Tint (°C)"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(wx.StaticText(self,label="Temperature graph") ,1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(wx.StaticText(self,label="Text (°C)"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(self.ctrl_inside_temp, 0,wx.EXPAND)
        sizer_grid.Add(self.slider_Tint, 0,wx.EXPAND)
        sizer_grid.Add(self.panelfig, 1,wx.EXPAND)
        sizer_grid.Add(self.slider_Tout, 0, wx.EXPAND)

        self.SetSizer(sizer_grid)


        # Bindings
        self.slider_Tint.Bind(wx.EVT_SLIDER, self.on_slide_Tint)
        self.slider_Tout.Bind(wx.EVT_SLIDER, self.on_slide_Tout)

    def on_slide_Tint(self,event):
        Tint= self.slider_Tint.GetValue()
        self.solver.set_inside_temp(Tint)


    def on_slide_Tout(self,event):
        Tout= self.slider_Tout.GetValue()
        self.solver.set_outside_temp(Tout)


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
        self.info_phi.SetLabel("Thermal flux from interior to wall = %g W/m²" % phi_int_to_solver)
        phi_int_to_out = -(solver.Tout-solver.Tint) / Rth
        self.info_phi2.SetLabel("Thermal flux at equilibrium = %g W/m²" % phi_int_to_out)
        Nx= sum([layer.Npoints for layer in solver.wall.layers])
        text_nx="Nx= %d (" % Nx + str([layer.Npoints for layer in solver.wall.layers]) + ")"
        self.info_Nx.SetLabel(text_nx)
        limiter=(solver.steps_to_statio/solver.limiter_ratio)
        self.info_limit.SetLabel("limiter = %g" % limiter)
        self.Fit()
        self.Thaw()



class PanelSimulationControls(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.localizer=parent.localizer
        self.solver=parent.solver

        space=5
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)

        self.button_run = wx.Button(self)
        self.localizer.link(self.button_run.SetLabel, "run_button", "run_button")
        self.localizer.link(self.button_run.SetToolTip, "run_button_tooltip", "run_button_tooltip")

        sizer_h.Add(self.button_run, 0, wx.ALL, space)

        self.button_adv = wx.Button(self)
        self.localizer.link(self.button_adv.SetLabel, "button_advance", "button_advance")

        sizer_h.Add(self.button_adv, 0, wx.ALL, space)

        self.button_statio = wx.Button(self)
        self.localizer.link(self.button_statio.SetLabel, "button_statio", "button_statio", text="aa")
        self.localizer.link(self.button_statio.SetToolTip, "button_statio_tooltip", "button_statio_tooltip")

        sizer_h.Add(self.button_statio, 0, wx.ALL, space)

        self.button_reset = wx.Button(self)
        self.localizer.link(self.button_reset.SetLabel, "button_reset", "button_reset", text="")
        # self.localizer.link(self.button_statio.SetToolTip, "button_reset_tooltip", "button_reset_tooltip")
        sizer_h.Add(self.button_reset, 0, wx.ALL, space)

        self.SetSizer(sizer_h)
        self.Fit()

class MainPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.localizer=parent.localizer
        self.solver=Solver()


        self.solver.set_inside_temp(19)
        self.solver.set_outside_temp(5)


        self.localizer.link(self.solver.set_text_inside, "plot_text_inside", "plot_text_inside")
        self.localizer.link(self.solver.set_text_outside, "plot_text_outside", "plot_text_outside")



        # main vertical sizer
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)



# =============================================================================
# panel to manage layers
# =============================================================================
        # self.layermgr=PanelLayerMgr(self)
        self.layermgr=StaticBoxWallCustomizerWrapper(self)

        self.sizer_v.Add(self.layermgr.sizer,0, wx.ALL | wx.EXPAND,2)

# =============================================================================
# panel with main actions
# =============================================================================
        self.panel_menu = PanelSimulationControls(self)


        self.panel_menu.button_run.Bind(wx.EVT_BUTTON, self.on_press_run)
        self.panel_menu.button_adv.Bind(wx.EVT_BUTTON, self.on_press_advance)
        self.panel_menu.button_statio.Bind(wx.EVT_BUTTON, self.on_press_statio)
        self.panel_menu.button_reset.Bind(wx.EVT_BUTTON, self.on_press_reset)




        self.sizer_v.Add(self.panel_menu,0, wx.ALL,2)
# =============================================================================
# panel to show animated figure
# =============================================================================


        self.panel_fig_sliders=FigureWithTemperatureSliders(self)


        self.panel_info=PanelSolverInfo(self)
        self.panel_info.update_info(self.solver)

        # sizer_h_fig_sliders.Add(self.panel_info, 1, wx.EXPAND)



        sizer_h = wx.BoxSizer(wx.HORIZONTAL)

        # sizer_h.Add(self.ctrl_inside_temp, 0, wx.EXPAND, 0)
        sizer_h.Add(self.panel_fig_sliders, 1, wx.EXPAND, 0)
        sizer_h.Add(self.panel_info)





        self.sizer_v.Add(sizer_h, 1, wx.ALL | wx.EXPAND, 2)



# =============================================================================
# set the main sizer
# =============================================================================
        self.SetSizer(self.sizer_v)
        self.sizer_v.SetSizeHints(parent)



# =============================================================================
# bindings
# =============================================================================
        # manage main update


#        self.thread_update_loop = Thread(target=self.update_loop_thread)
        self.timer_update_redraw= wx.Timer(self)
        self.timer_update_redraw.Start(30)


        self.Bind(wx.EVT_TIMER, self.on_timer_redraw, self.timer_update_redraw)

        self.Bind(EVT_WALL_SETUP_CHANGED, self.on_wall_setup_change)







    def on_press_run(self, event):
        self.solver.run_sim=not(self.solver.run_sim)
        if self.solver.run_sim:
            self.solver.this_run_start=time.perf_counter_ns()
            self.thread_update_loop = Thread(target=self.solver.update_loop)
            self.thread_update_loop.start()

            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button_pause", "run_button")
            self.panel_menu.button_adv.Disable()
        else:
            # self.timer_update_redraw.Stop()
            self.thread_update_loop.join()
            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button", "run_button")
            self.panel_menu.button_adv.Enable()
            self.solver.this_run_time=0
            self.solver.this_run_updates=0


    def on_wall_setup_change(self, event):
        # self.redraw()
        return

    def on_press_statio(self,event):
        self.solver.solve_stationnary()
        self.solver.time=0
        # self.redraw()

    def on_press_reset(self,event):
        self.solver.remesh()
        # self.redraw()






    def on_press_advance(self,event):
        self.solver.advance_time()
        self.redraw()

    def on_timer_redraw(self,event):

        self.solver.needRedraw=True
        self.redraw()
        self.solver.needRedraw=False

        time_new_redraw=time.perf_counter_ns()

        self.solver.time_since_redraw=time_new_redraw-self.solver.time_last_redraw
        self.solver.this_run_time=time_new_redraw-self.solver.this_run_start
        self.solver.this_run_updates+=self.solver.updates_since_redraw
        # ~ print("updates since last redraw ",self.updates_since_redraw)
        # ~ print("time since last redraw ",self.time_since_redraw/1e6, 'ms')
        # ~ print("updates per seconds :",1e9*self.this_run_updates/self.this_run_time)
        # ~ print("progression to statio :",self.solver.time_to_statio/(self.solver.time+self.solver.dt))

        self.solver.time_last_redraw=time.perf_counter_ns()
        self.solver.updates_since_redraw=0





    def redraw(self):
        self.panel_info.update_info(self.solver)
        self.solver.draw()
        self.panel_fig_sliders.panelfig.LoadFigure(self.solver.figure)
        self.panel_fig_sliders.ctrl_inside_temp.update()




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
        self.Bind(wx.EVT_CLOSE , self.on_close)
        self.localizer.set_lang("fr")
        self.Show()



    def on_close(self,event):
        self.main_panel.timer_update_redraw.Stop()
        if self.main_panel.solver.run_sim:

            self.main_panel.solver.run_sim=False
        print(self.localizer.missing)
        event.Skip()

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
