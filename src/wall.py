#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 08:39:27 2024

@author: tb266682
"""



import numpy as np


import matplotlib
matplotlib.use('WxAgg')

import matplotlib.backends.backend_wxagg
from matplotlib.figure import Figure


import scipy.optimize




NPOINT_PREFERRED_PER_LAYER=20
NPOINT_MINIMAL_PER_LAYER=10

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

# ~ mat1=Material(la=1,Cp=1, rho=1)
# ~ register_material(mat1, "mat1")

# ~ mat2=Material(la=0.5,Cp=1, rho=1)
# ~ register_material(mat2, "mat2")

default=Material(la=1,Cp=1, rho=1, name="default")
register_material(default)


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




def format_time(t):
    if t>1:
        s=int(t)
        d=s//(24*3600)
        h=(s - d * 24 * 3600) // 3600
        m=(s - d * 24 * 3600 - h * 3600) // 60
        s=(s - d * 24 * 3600 - h * 3600 - m * 60)
        if d>0:
            return "%dd%dh%dm%ds" % (d,h,m,s)
        elif h>0:
            return "%dh%dm%ds" % (h,m,s)
        elif m>0:
            return "%dm%ds" % (m,s)
        else:
            return "%ds" % (s)
    else:
        return "%dms" % (t*1000)
# ~ Layer = namedtuple('Layer', ['e', 'la', 'rho','Cp','dx'])

class Wall:

    def __init__(self):
        self.figure = Figure()
        self.ax=self.figure.add_axes([0,0,1,1])


        self.layers=[]
        self.meshes=[]
        self.temp=[]
        self.diffs=[]
        # ~ self.dx=[]
        self.courant=0.4
        self.Tint=0
        self.Tout=0
        self.time=0
        self.dt=1

        self.phi_int_to_wall=0

        self.wall_length=0

        self.Tmin=-10
        self.Tmax=40


    def remesh(self):
        self.wall_length=0
        self.time=0
        for i in range(len(self.layers)):
            layer=self.layers[i]

            dx = (layer.mat.D * self.dt / self.courant) ** 0.5

            layer.Npoints= max(int(layer.e / dx)+1,2)
            layer.xmesh=np.linspace(self.wall_length,self.wall_length+layer.e,layer.Npoints)

            layer.dx=layer.xmesh[1]-layer.xmesh[0]
            layer.Tmesh=np.zeros(layer.Npoints)

            self.wall_length+=layer.e
            self.layers[i]=layer


    def add_layer(self, layer):
        self.layers.append(layer)

        dt= (layer.e/NPOINT_PREFERRED_PER_LAYER)**2 * self.courant / layer.mat.D
        self.set_time_step(dt)
        # ~ layerNmax=max(self.layers, key = lambda x:x.Npoints)
        layerNmin=min(self.layers, key = lambda x:x.Npoints)
        if layerNmin.Npoints<5:
            dt= (layerNmin.e/NPOINT_MINIMAL_PER_LAYER)**2 * self.courant / layerNmin.mat.D
            self.set_time_step(dt)


    def remove_layer(self):
        self.layers.pop()
        self.remesh()

    def change_layers(self, new_layers):
        while len(self.layers):
            self.remove_layer()
        for layer in new_layers:
            self.add_layer(layer)



    def set_inside_temp(self,Tint):
        self.Tint=Tint

    def set_outside_temp(self,Tout):
        self.Tout=Tout

    def set_time_step(self,dt):
        self.dt=dt
        self.remesh()


    def get_formatted_time(self):
        return format_time(self.time)


    def draw(self):
        self.ax.clear()

        self.ax.frame_on=False
        self.ax.axis("off")
        self.ax.margins(0)

        wl=self.wall_length
        hspace=wl/3
        self.ax.set_xlim([-hspace,wl+hspace])
        vspace=1
        self.ax.set_ylim([self.Tmin-vspace, self.Tmax+vspace])

        layer_name_height=self.Tmax-1
        x0=0
        self.ax.axvline(x=x0, color="k")
        for i in range(len(self.layers)):
            layer=self.layers[i]
            e=layer.e
            x0+=e
            self.ax.axvline(x=x0, color="k")
            self.ax.text(x0-e+0.002,layer_name_height,"%s" %(layer.mat.name),rotation=90,verticalalignment='top', fontsize=9)

        for T in range(self.Tmin, self.Tmax+1,5):
            self.ax.axhline(y=T, color="lightgrey", linestyle="--", linewidth=0.7)
            self.ax.text(-hspace,T+0.1,"%d" %(T), color="lightgrey", fontsize=9)
            self.ax.text(wl+hspace,T+0.1,"%d" %(T), color="lightgrey", fontsize=9,horizontalalignment='right')

        self.ax.text(-hspace,layer_name_height,"Room")


        self.ax.text(wl,layer_name_height,"Outside")


        self.ax.plot([-hspace,0],[self.Tint,self.Tint],color="r")
        self.ax.plot([self.wall_length,self.wall_length+hspace],[self.Tout,self.Tout],color="cyan")

        for i in range(len(self.layers)):
            self.ax.plot(self.layers[i].xmesh,self.layers[i].Tmesh)

#        self.ax.set_xlabel("Position (m)")
        self.ax.axes.get_xaxis().set_visible(False)
        self.ax.set_ylabel("Temperature (°C)")

#        self.ax.set_title("Time = %s" % format_time(self.time))





    def stationnary_equation(self,Ts):
        d=np.zeros(len(Ts))
        d[0]=Ts[0]-self.Tint
        d[len(Ts)-1]=Ts[len(Ts)-1]-self.Tout
        for i in range(1,len(Ts)-1):
            d[i]=(Ts[i]-Ts[i-1])/self.layers[i-1].Rth-(Ts[i+1]-Ts[i])/self.layers[i].Rth
        return d


    def compute_phi(self):
        phi=0
#        for i in range(len(self.layers)):
#            layer=self.layers[i]
#            T=layer.Tmesh
#            for j in range(1,len(T)):
#                phi+= (T[j] - T[j-1])/layer.Rth * layer.dx
        layer=self.layers[0]
        T=layer.Tmesh
        R=layer.dx/layer.mat.la
        phi= (T[1]-T[0]) /R
        return phi



    def solve_stationnary(self):
        Ts=np.zeros(len(self.layers)+1)
        Ts[0]=self.Tint
        Ts[-1]=self.Tout

#        fun = lambda T : self.stationnary_equation(T,self.Rth)
        sol=scipy.optimize.root(self.stationnary_equation, x0=Ts)
        Ts=sol.x

        for i in range(len(self.layers)):
            self.layers[i].Tmesh=(self.layers[i].xmesh-self.layers[i].xmesh[0]) / self.layers[i].e * (Ts[i+1]-Ts[i]) +Ts[i]

        phi=0
        for i in range(len(self.layers)):
            phi+=(Ts[i+1]-Ts[i])/self.layers[i].Rth*self.layers[i].e
        print("phi:",phi, "W/m2")





    def advance_time(self):

        self.time+=self.dt

        updated_temp=[]
        for i in range(len(self.layers)):
            layer=self.layers[i]
            T=layer.Tmesh
            laplaT=np.zeros(len(T))
            laplaT[1:-1]=(T[2:]+T[0:-2]-2*T[1:-1])/(layer.dx)**2

            laplaT[0] = (T[0] - 2 *T[1] + T[2]) / (layer.dx)**2
            laplaT[-1] = (T[-1] - 2 *T[-2] + T[-3]) / (layer.dx)**2
            flux_interfaces=np.zeros(len(T))

            # ~ if i==0:
                # ~ flux_interfaces[0]=0*-layer.mat.D *(T[0]-self.Tint)/layer.dx
            # ~ else:
                # ~ layerleft=self.layers[i-1]
                # ~ Tleft=layerleft.Tmesh
                # ~ F_loc=layer.mat.D * (T[1] -2*T[0] + layerleft.Tmesh[-2])/layer.dx**2
                # ~ F_left=layerleft.mat.D * (layerleft.Tmesh[-1]-2*layerleft.Tmesh[-2]+layerleft.Tmesh[-3]) / layerleft.dx**2
                # ~ flux_interfaces[0]= ( F_loc + 0* F_left)
                # ~ beta=layerleft.mat.D * (Tleft[-1]-Tleft[-2]) / layerleft.dx
                # ~ flux_interfaces[0]= -((T[1]-T[0]) - layerleft.mat.rhoCp/layer.mat.rhoCp * (Tleft[-1]-Tleft[-2]))/self.dt
            # ~ if i==len(self.layers)-1:
                # ~ flux_interfaces[-1]=0*layer.mat.D *(self.Tout-T[-1])/layer.dx**2
            # ~ else:
                # ~ layerright=self.layers[i+1]
                # ~ Tright=layerright.Tmesh
                # ~ F_loc=layer.mat.D * (T[-2]-2*T[-1]+layerright.Tmesh[1])/layer.dx
                # ~ F_right= layerright.mat.D * (layerright.Tmesh[0]-2*layerright.Tmesh[1]+layerright.Tmesh[2])/layerright.dx**2
                # ~ flux_interfaces[-1]= ( 0*F_right +  F_loc)
                # ~ flux_interfaces[-1]= -((T[-1]-T[-2]) - layerright.mat.rhoCp/layer.mat.rhoCp * (Tright[1]-Tright[0]))/self.dt


            Tup=T + self.dt *  (layer.mat.D * laplaT + flux_interfaces)

# =============================================================================
#             apply boundary conditions
# =============================================================================
            if i==0:
                Tup[0] = self.Tint
            else:
                layerleft=self.layers[i-1]
                Tleft=layerleft.Tmesh

                r = (layerleft.mat.la/layerleft.dx) / (layer.mat.la/layer.dx)
                Tup[0]=1 / (1+r) * ( T[1] + r * Tleft[-2])

            if i==len(self.layers)-1:
                Tup[-1] = self.Tout
            else:
                layerright=self.layers[i+1]
                Tright=layerright.Tmesh

                r = (layerright.mat.la/layerright.dx) / (layer.mat.la/layer.dx)
                Tup[-1] = 1 / (1+r) * (T[-2] + r * Tright[1])



            updated_temp.append(Tup)

        for i in range(len(self.layers)):
            self.layers[i].Tmesh=updated_temp[i]

        # ~ for i in range(len(self.layers)):
            # ~ layer=self.layers[i]
            # ~ if i>0:
                # ~ layerleft=self.layers[i-1]
                # ~ Tleft=layerleft.Tmesh

                # ~ r = layerleft.mat.la / layer.mat.la
                # ~ self.layers[i].Tmesh[0]=1 / (1+r) * ( self.layers[i].Tmesh[1] + r * Tleft[-2])
            # ~ if i<len(self.layers)-1:
                # ~ layerright=self.layers[i+1]
                # ~ Tright=layerright.Tmesh

                # ~ r = layerright.mat.la / layer.mat.la
                # ~ self.layers[i].Tmesh[-1] = 1 / (1+r) * (self.layers[i].Tmesh[-2] + r * Tright[1])








# =============================================================================
# basic testing
# =============================================================================
if __name__=="__main__":

    wall=Wall()


    mat1=Material(la=0.05,rho=1,Cp=1)
    mat2=Material(la=0.4,rho=3,Cp=1)

    layer1=Layer(e=1, mat=mat1)
    layer2=Layer(e=2, mat=mat2)
    wall.add_layer(layer1)

    wall.change_layers([layer2])

    wall.set_inside_temp(19)
    wall.set_outside_temp(10)



    wall.solve_stationnary()
    wall.draw()


