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





DefaultMaterials={}
def register_material(mat):
    DefaultMaterials[mat.name]=mat

def DefaultMaterialList():
    return list(DefaultMaterials.keys())


# taken from http://meteo.re.free.fr/thermo.php :
register_material(Material(la=0.038,Cp=2100, rho=55, name="Laine de bois"))
register_material(Material(la=0.024,Cp=1400, rho=32, name="Polyurethane PUR"))
register_material(Material(la=0.330,Cp=792, rho=790, name="BA13"))
register_material(Material(la=0.032,Cp=1450, rho=15, name="polystyrene gris EPS"))
register_material(Material(la=1.050,Cp=648, rho=1300, name="parpaing"))
register_material(Material(la=0.032,Cp=1030, rho=29, name="Laine de verre GR32"))
register_material(Material(la=0.040,Cp=1030, rho=15, name="Laine de verre"))
register_material(Material(la=0.038,Cp=1860, rho=60, name="Ouate de cellulose"))

# others:
register_material(Material(la=2,Cp=840, rho=2200, name="Béton"))

class MaterialList:
    
    def __init__(self):
        self.list=DefaultMaterials
        
    def add_material(self,mat):
        self.list[mat.name]=mat
        
        


# =============================================================================
# basic testing
# =============================================================================
if __name__=="__main__":

    print("materials")


