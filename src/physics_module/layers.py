#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np


import matplotlib
matplotlib.use('WxAgg')

import matplotlib.backends.backend_wxagg
from matplotlib.figure import Figure


from .materials import Material, DefaultMaterials



class Layer:
    def __init__(self,e = 1, mat=Material()):
        self.e=e
        self.mat=mat

        self.Rth = e / mat.la


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




