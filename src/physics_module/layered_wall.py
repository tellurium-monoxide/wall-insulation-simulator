#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from .layers import Layer
from .materials import Material, DefaultMaterials


class WallScenario:
    def __init__(self, layers):
        self.layers=[]
        for named_layer in layers:
            layer=Layer (named_layer[0], DefaultMaterials[named_layer[1]])
            self.layers.append(layer)


DefaultScenarios={}
def register_scenario(name, scenario):
    DefaultScenarios[name]=scenario


register_scenario("Isolation intérieur laine de bois", WallScenario([(0.15, "Laine de bois"), (0.4, "Béton")]))
register_scenario("Isolation intérieur laine de bois + BA13", WallScenario([(0.013, "BA13"),(0.15, "Laine de bois"), (0.4, "Béton")]))




class Wall:

    def __init__(self):
        
        self.layers=[]

        self.wall_length=0





    def add_layer(self, layer):
        self.layers.append(layer)
        self.wall_length+=layer.e


    def remove_layer(self):
        layer=self.layers.pop()
        self.wall_length-=layer.e


    def change_layers(self, new_layers):
        while len(self.layers):
            self.remove_layer()
        for layer in new_layers:
            self.add_layer(layer)




