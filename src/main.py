#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
N_THREADS=str(os.cpu_count())
N_THREADS_FREE=str(os.cpu_count()-1) # 1 thread is used for wx gui
N_THREADS_PHYSICAL=str(os.cpu_count()//2) # physical threads is half of logical threads
N_THREADS_SERIAL= '1' # used to disable parallel
os.environ["OMP_NUM_THREADS"] = N_THREADS_SERIAL
os.environ["OPENBLAS_NUM_THREADS"] = N_THREADS_SERIAL
os.environ["MKL_NUM_THREADS"] = N_THREADS_SERIAL
os.environ["VECLIB_MAXIMUM_THREADS"] = N_THREADS_SERIAL
os.environ["NUMEXPR_NUM_THREADS"] = N_THREADS_SERIAL

import psutil

import time
import copy
from threading import Thread

from functools import partial

import wx



# local imports
from modules.physics.solver import Layer, Material
from modules.physics.solver import SolverHeatEquation1dMultilayer as Solver

from modules.localizer.mylocalizer import MyLocalizer

# interface imports
from modules.gui.wall_customizer.panel_wall_customizer import PanelLayerMgr, StaticBoxWallCustomizerWrapper
from modules.gui.temperature_controller.controller_inside_temp import ControlInsideTemp
from modules.gui.temperature_controller.controller_outside_temp import ControlOutsideTemp
from modules.gui.events import *
from modules.gui.animated_figure import PanelAnimatedFigure

from modules.gui.sliders.slider_log import SliderLog
from modules.gui.sliders.slider_float import SliderFloat







class FigureWithTemperatureSliders(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.solver=parent.solver
        self.localizer=parent.localizer




        self.slider_Tint=wx.Slider(self,value=self.solver.Tint,minValue=self.solver.Tmin, maxValue=self.solver.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tint")
        self.panelfig = PanelAnimatedFigure(self, self.solver.figure)
        self.slider_Tout=wx.Slider(self,value=self.solver.Tout,minValue=self.solver.Tmin, maxValue=self.solver.Tmax, style=wx.SL_VALUE_LABEL | wx.SL_VERTICAL | wx.SL_LEFT | wx.SL_INVERSE| wx.SL_AUTOTICKS, name="Tout")

        self.ctrl_inside_temp = ControlInsideTemp(self, self.slider_Tint)
        self.ctrl_outside_temp = ControlOutsideTemp(self, self.slider_Tout)

        # create a FlexGridSizer to position the figure, sliders...
        sizer_grid = wx.FlexGridSizer(2,5,10,10)
        sizer_grid.AddGrowableRow(1, proportion=1)
        sizer_grid.AddGrowableCol(2, proportion=1)
        # sizer_h_fig_sliders.AddGrowableCol(3, proportion=1)

        # add content to the sizer
        sizer_grid.Add(wx.StaticText(self,label="Room heating"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(wx.StaticText(self,label="Tint (°C)"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(wx.StaticText(self,label="Temperature graph") ,1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(wx.StaticText(self,label="Text (°C)"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(wx.StaticText(self,label="Outside temp control"),1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_grid.Add(self.ctrl_inside_temp, 0,wx.EXPAND)
        sizer_grid.Add(self.slider_Tint, 0,wx.EXPAND)
        sizer_grid.Add(self.panelfig, 1,wx.EXPAND)
        sizer_grid.Add(self.slider_Tout, 0, wx.EXPAND)
        sizer_grid.Add(self.ctrl_outside_temp, 0, wx.EXPAND)

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
        self.info_ups=wx.StaticText(self,label="")
        self.sizer_v.Add(self.info_ups, 0, wx.LEFT, 3)
        



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
        limiter=(solver.simulation_time_per_sec)
        self.info_limit.SetLabel("sim speed = %g / %g" % (solver.simulation_time_per_sec/60, solver.max_simulation_time_per_sec/60))
        self.info_ups.SetLabel("ups = %g" % self.solver.steps_per_sec_redraw)
        self.Fit()
        self.Thaw()

class FrameSolverAdvancedSettings(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self,parent)
        self.parent=parent
        self.localizer=parent.localizer
        self.solver=parent.solver
        space=5
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        
        self.check_use_sparse = wx.CheckBox(self, label="sparse?")
        sizer_h.Add(self.check_use_sparse, 0, wx.ALL, space)
        
        self.SetSizer(sizer_h)
        self.Fit()
        self.check_use_sparse.Bind(wx.EVT_CHECKBOX, self.on_check_use_sparse)
        
    def on_check_use_sparse(self, event):
        
        self.solver.use_sparse=event.IsChecked()
class PanelSimulationControls(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.localizer=parent.localizer
        self.solver=parent.solver

        space=2
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
        self.localizer.link(self.button_reset.SetLabel, "button_reset", "button_reset", text="Reset")
        # self.localizer.link(self.button_statio.SetToolTip, "button_reset_tooltip", "button_reset_tooltip")
        sizer_h.Add(self.button_reset, 0, wx.ALL, space)
        
        self.button_advanced = wx.Button(self)
        self.localizer.link(self.button_advanced.SetLabel, "button_advanced", "button_advanced", text="Advanced settings")
        sizer_h.Add(self.button_advanced, 0, wx.ALL, space)
        

        
        self.slider_sim_speed = SliderLog(self,minValue=3600, maxValue=36000*3, nsteps=1000, orientation="h")
        self.slider_sim_speed.SetValue(self.solver.goal_simulation_time_per_sec)
        
        sizer_h.Add(self.slider_sim_speed,1,wx.EXPAND, 0)

        self.SetSizer(sizer_h)
        self.Fit()
        
        # Bindings
        self.button_statio.Bind(wx.EVT_BUTTON, self.on_press_statio)
        self.button_advanced.Bind(wx.EVT_BUTTON, self.on_press_advanced_settings)

        self.slider_sim_speed.Bind(wx.EVT_SLIDER, self.on_slide_sim_speed)
        

    def on_press_statio(self,event):
        self.solver.solve_stationnary()
        self.solver.time=0
        # self.redraw()
        
    def on_slide_sim_speed(self,event):
        v=self.slider_sim_speed.GetValue()
        self.solver.goal_simulation_time_per_sec=v
    def on_press_advanced_settings(self,event):
        f=FrameSolverAdvancedSettings(self)
        f.Show()

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
        
        self.panel_menu.button_reset.Bind(wx.EVT_BUTTON, self.on_press_reset)




        self.sizer_v.Add(self.panel_menu,0, wx.ALL| wx.EXPAND,2)
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

        self.timer_update_redraw= wx.Timer(self)
        self.timer_update_redraw.Start(40)
        self.Bind(wx.EVT_TIMER, self.on_timer_redraw, self.timer_update_redraw)





    def on_timer_redraw(self,event):
        self.solver.needRedraw=True
        self.update()
        self.solver.needRedraw=False
        
    def update(self):
        self.panel_info.update_info(self.solver)
        if self.solver.need_init_plot:
            self.solver.init_plot()
        else:
            self.solver.update_plot()
        # self.panel_fig_sliders.panelfig.LoadFigure(self.solver.figure)
        self.panel_fig_sliders.panelfig.Refresh()
        self.panel_fig_sliders.ctrl_inside_temp.update()
        self.panel_fig_sliders.ctrl_outside_temp.update()



    def on_press_run(self, event):
        self.solver.run_sim=not(self.solver.run_sim)
        if self.solver.run_sim:
            
            self.thread_update_loop = Thread(target=self.solver.update_loop)
            self.thread_update_loop.start()
            

            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button_pause", "run_button")
            self.panel_menu.button_adv.Disable()
        else:
            # self.timer_update_redraw.Stop()
            self.thread_update_loop.join()
            self.localizer.link(self.panel_menu.button_run.SetLabel, "run_button", "run_button")
            self.panel_menu.button_adv.Enable()
        self.panel_menu.Layout()





    def on_press_reset(self,event):
        self.solver.remesh()
        # self.redraw()






    def on_press_advance(self,event):
        self.solver.advance_time()
        # self.redraw()
        
    

       






        

class CustomStatusBar(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.localizer=parent.localizer
        # self.solver=parent.solver
        
        
        sizer_h=wx.BoxSizer(wx.HORIZONTAL)
        
        self.status_cpu=wx.StaticText(self)
        
        sizer_h.Add(self.status_cpu, 1, wx.EXPAND, 0)
        
        self.SetSizer(sizer_h)
        
    def update(self):
        print("status")
        self.set_status_cpu()
        print("done")
        
        
    def set_status_cpu(self):
        # load1, load5, load15 = psutil.getloadavg()
        # cpu_usage = (load15/os.cpu_count()) * 100
        cpu_usage = psutil.cpu_percent()
        # cpu_usage = 1
 
        self.status_cpu.SetLabel("CPU usage: %g" % cpu_usage)
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
        
        
        
        
        # self.status_bar=CustomStatusBar(self)
        self.status_bar=self.CreateStatusBar()
        


        self.main_panel=MainPanel(self)

        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

        self.sizer_v.Add(self.main_panel, 1, wx.EXPAND, 0)
        # self.sizer_v.Add(self.status_bar, 0, wx.EXPAND, 0)


        self.SetSizer(self.sizer_v)
        self.sizer_v.SetSizeHints(self)
        
        
        
        
        self.timer_update_status= wx.Timer(self)
        self.timer_update_status.Start(200)
        self.Bind(wx.EVT_TIMER, self.on_timer_status, self.timer_update_status)
# =============================================================================
# show the frame
# =============================================================================
        self.Bind(wx.EVT_CLOSE , self.on_close)
        self.localizer.set_lang("fr")
        self.Show()
        
        

        
    # def update(self):
        # self.main_panel.update()
        # wx.Yield()
        
    def on_timer_status(self, event):
        # self.status_bar.update()
        self.set_status_cpu()

        
    def set_status_cpu(self):
        # load1, load5, load15 = psutil.getloadavg()
        # cpu_usage = (load15/os.cpu_count()) * 100
        cpu_usage = psutil.cpu_percent()
        # cpu_usage = 1
 
        self.status_bar.SetStatusText("CPU usage: %g" % cpu_usage)


    def on_close(self,event):
        self.main_panel.timer_update_redraw.Stop()
        self.timer_update_status.Stop()
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
