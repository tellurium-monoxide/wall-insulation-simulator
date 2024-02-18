#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Material:

    def __init__(self,la=1, rho=1, Cp=1, name="default mat"):
        self.rho=rho
        self.la=la
        self.Cp=Cp

        self.name=name

        self.D=la / ( rho * Cp)
        self.rhoCp= rho*Cp
        self.effusivity= (la * rho * Cp) **0.5







# taken from http://meteo.re.free.fr/thermo.php :


# others:




