#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Room:

    def __init__(self, name="room", shape=(1,1,2.5), heating_power=0):
        self.shape=shape
        self.heating_power=heating_power

        self.name=name

        self.update_prop()



    def update_prop(self):
        shape=self.shape
        self.surface= 0*shape[0] * shape[1] * 2 + shape[2] * (shape[0]+shape[1]) * 2

        self.volume= shape[0] * shape[1] * shape[2]

        self.rhoCp = 1.2 * 1000 # rhoCp (volumic heat capacity) of air, maybe I can allow custom values

        self.heat_capacity = self.volume * self.rhoCp

        self.heating_rate = self.heating_power / (self.heat_capacity)

    def compute_temperature_loss_rate(self, phi):

        # we want to return the temperature loss over time in K/s
        # phi is W/m2, heat_capa is J/K
        return (phi * self.surface - self.heating_power) / ( self.heat_capacity)
    def compute_heat_loss_rate(self, phi):

        # we want to return the temperature loss over time in W of J/s
        return (phi * self.surface)


    def set_shape(self, shape):
        self.shape=shape
        self.update_prop()














