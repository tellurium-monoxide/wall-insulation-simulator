#!/usr/bin/env python3
# -*- coding: utf-8 -*-




from .materials import Material



class Layer:
    def __init__(self,e = 1, mat=Material()):
        self.e=e
        self.mat=mat

        self.Rth = e / mat.la







