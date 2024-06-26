#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from .layers import Layer
from .materials import Material
from .presets import WallConfigData, DefaultConfig


from copy import deepcopy




class Wall:

    def __init__(self):



        self.length=0

        self.config=DefaultConfig


        self.layers=deepcopy(self.config.get_default_preset())

        self.room=deepcopy(self.config.get_default_room())
        self.temp_cycle=deepcopy(self.config.get_default_temp_cycle())

        self.compute_length()


    def add_layer(self, layer):
        self.layers.append(layer)
        self.length+=layer.e


    def remove_layer(self):
        if len(self.layers)>0:
            layer=self.layers.pop()
            self.length-=layer.e


    def change_layers(self, new_layers):
        while len(self.layers):
            self.remove_layer()
        for layer in new_layers:
            self.add_layer(layer)


    def change_room(self, room):
        self.room=deepcopy(room)
        
    def change_temp_cycle(self, temp_cycle):
        self.temp_cycle=deepcopy(temp_cycle)


    def compute_length(self):
        wl=0
        for layer in self.layers:
            wl+=layer.e
        self.length=wl
        return wl


