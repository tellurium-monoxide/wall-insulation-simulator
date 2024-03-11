import wx

import wx.lib.scrolledpanel as scrolled


import matplotlib.backends.backend_wxagg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from functools import partial


# local imports
from ...physics.solver import Layer, Material



from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal as PanelNumericInput
from ..controls_numeric_values.bounded_value import CtrlPositiveBoundedDecimal

from .controls_materials import DisplayMaterialProp, InputMaterialProp
from .layer_choice import PanelLayer

from ..events import *



class PanelLayerList(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)


        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.button_add_begin= wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_PLUS), style=wx.BU_EXACTFIT)
        self.button_add_begin.SetToolTip("add a layer right here on the left")
        self.button_add_begin.Bind(wx.EVT_BUTTON, self.on_press_add_begin)

        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.list_of_panel_layer=[]

        self.load_layers(self.solver.wall.layers)

        size=self.GetEffectiveMinSize()
        self.SetMinSize((-1,size[1]+20))

        self.Fit()




    def on_press_add(self, event, pos=None):
        self.add_layer(pos=pos)
    def on_press_remove(self, event, pos=None):
        self.remove_layer(pos=pos)
        
        
    def on_press_move_right(self, event, pos=None):
        self.swap_layer(pos, pos+1)


    def swap_layer(self,i,j):
        n=len(self.list_of_panel_layer)
        if i<n and j<n:
            l1=self.list_of_panel_layer[i].get_layer()
            l2=self.list_of_panel_layer[j].get_layer()
            self.list_of_panel_layer[i].set_layer(l2)
            self.list_of_panel_layer[j].set_layer(l1)

    def on_press_add_begin(self, event):
        self.add_layer(0)


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
            lay.button_move_right.Bind(wx.EVT_BUTTON, partial(self.on_press_move_right,pos=i))

        self.SetSizer(self.sizer_h, deleteOld=True)
        self.Fit()
        self.parent.Fit()
        self.parent.set_size()
        self.GetTopLevelParent().Layout()



    def add_layer(self, pos=None):
        if pos==None:
            pos=len(self.list_of_panel_layer)
        self.Freeze()
        lay= PanelLayer(self)
        self.list_of_panel_layer.insert(pos, lay)
        self.update_sizer()
        self.Thaw()

    def remove_layer(self, pos=None):
        if pos==None:
            pos=len(self.list_of_panel_layer)-1
        if len(self.list_of_panel_layer)>1:

            self.list_of_panel_layer.pop(pos).Destroy()
            self.update_sizer()
            return True
        return False

    def sanitize_layers(self):
        # we fuse consecutive layers of same material to reduce mesh size
        layer_id=0
        while layer_id<len(self.list_of_panel_layer)-1:
            layer=self.list_of_panel_layer[layer_id].get_layer()
            layer_next=self.list_of_panel_layer[layer_id+1].get_layer()
            if layer.mat.name==layer_next.mat.name:
                e=layer.e + layer_next.e
                layer_fused=Layer(e=e, mat=layer.mat)
                self.list_of_panel_layer[layer_id].set_layer(layer_fused)
                self.remove_layer(layer_id+1)
                
            else:
                layer_id+=1

    def gather_layers(self):
        self.sanitize_layers()
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
        self.set_layer_amount(len(layers))
        for i in range(len(layers)):
            self.list_of_panel_layer[i].set_layer(layers[i])


        self.Layout()
        self.Fit()

    def disable_input(self):
        self.button_add_begin.Hide()
        for i in range(len(self.list_of_panel_layer)):
            self.list_of_panel_layer[i].disable_input()
    def enable_input(self):
        self.button_add_begin.Show()
        for i in range(len(self.list_of_panel_layer)):
            self.list_of_panel_layer[i].enable_input()


class ScrolledLayerListWrapper(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent)

        self.parent=parent
        self.solver=parent.solver
        self.localizer=parent.localizer

        self.sizer=wx.BoxSizer(wx.VERTICAL)




        self.layer_list=PanelLayerList(self)
        self.sizer.Add(self.layer_list)

        self.SetSizer(self.sizer)
        self.sizer.SetSizeHints(self)


        self.set_size()

        self.SetupScrolling(scroll_x=True, scroll_y=False)


    def set_size(self):
        sizeh=self.GetParent().GetEffectiveMinSize()[0]
        sizev=self.GetEffectiveMinSize()[1]
        self.SetMinSize((sizeh,sizev))
        self.GetParent().Layout()

