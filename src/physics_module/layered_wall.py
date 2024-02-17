#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from .layers import Layer
from .materials import Material, DefaultMaterials


class WallScenario:
    def __init__(self,name,  layers):
        self.name=name
        self.layers=[]
        for named_layer in layers:
            layer=Layer (named_layer[0], DefaultMaterials[named_layer[1]])
            self.layers.append(layer)


DefaultScenarios={}
def register_scenario(scenario):
    DefaultScenarios[scenario.name]=scenario


register_scenario(WallScenario("Isolation intérieur laine de bois", [(0.15, "Laine de bois"), (0.4, "Béton")]))
register_scenario(WallScenario("Isolation intérieur laine de bois + BA13", [(0.013, "BA13"),(0.15, "Laine de bois"), (0.4, "Béton")]))




class Wall:

    def __init__(self):



        self.length=0

        self.preset_materials=DefaultMaterials
        self.preset_walls=DefaultScenarios

        self.layers=DefaultScenarios[list(DefaultScenarios.keys())[0]].layers


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


    def compute_length(self):
        wl=0
        for layer in self.layers:
            wl+=layer.e
        self.length=wl
        return wl


