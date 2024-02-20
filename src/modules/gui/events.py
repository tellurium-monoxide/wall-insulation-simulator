
import wx
import wx.lib.newevent



# events to be propagated to the main panel when simulation parameters changes
eventWallSetupChanged, EVT_WALL_SETUP_CHANGED = wx.lib.newevent.NewCommandEvent()
eventWallMaterialListChanged, EVT_WALL_MATERIALS_CHANGED = wx.lib.newevent.NewCommandEvent()
