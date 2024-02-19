#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np


import matplotlib
matplotlib.use('WxAgg')

import matplotlib.backends.backend_wxagg
from matplotlib.figure import Figure


import matplotlib.cm
import matplotlib.colors as mplcolors


from .layers import Layer
from .materials import Material
from .layered_wall import Wall


NPOINT_PREFERRED_PER_LAYER=20
NPOINT_MINIMAL_PER_LAYER=10





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
# Layer = namedtuple('Layer', ['e', 'la', 'rho','Cp','dx'])

class SolverHeatEquation1dMultilayer:

    def __init__(self):
        self.figure = Figure()
        self.ax=self.figure.add_axes([0,0,1,1])


        self.wall=Wall()

        self.courant=0.4
        self.Tint=0
        self.Tout=0
        self.time=0
        self.dt=1

        self.phi_int_to_wall=0

        self.Tmin=-10
        self.Tmax=40

        self.vmaxabs=0

        self.text_inside=""
        self.text_inside=""


    def remesh(self):
        current_length=0
        self.time=0
        for i in range(len(self.wall.layers)):
            layer=self.wall.layers[i]

            dx = (layer.mat.D * self.dt / self.courant) ** 0.5

            layer.Npoints= max(int(layer.e / dx)+1,2)
            layer.xmesh=np.linspace(current_length,current_length+layer.e,layer.Npoints)

            layer.dx=layer.xmesh[1]-layer.xmesh[0]
            layer.Tmesh=np.zeros(layer.Npoints)

            current_length+=layer.e
            self.wall.layers[i]=layer
        self.time_to_statio=0
        self.steps_to_statio=0
        self.limiter_ratio=5
        if len(self.wall.layers)>0:
            self.time_to_statio=max([layer.e**2/layer.mat.D for layer in self.wall.layers])
            self.steps_to_statio = self.time_to_statio/self.dt
        self.vmaxabs=0


    def add_layer(self, layer):
        self.wall.add_layer(layer)

        dt= (layer.e/NPOINT_PREFERRED_PER_LAYER)**2 * self.courant / layer.mat.D
        self.set_time_step(dt)
        # layerNmax=max(self.wall.layers, key = lambda x:x.Npoints)
        layerNmin=min(self.wall.layers, key = lambda x:x.Npoints)
        if layerNmin.Npoints<5:
            dt= (layerNmin.e/NPOINT_MINIMAL_PER_LAYER)**2 * self.courant / layerNmin.mat.D
            self.set_time_step(dt)


    def remove_layer(self):
        self.wall.remove_layer()
        self.remesh()

    def change_layers(self, new_layers):
        while len(self.wall.layers):
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
    def get_formatted_time_step(self):
        return format_time(self.dt)


    def set_text_inside(self, text):
        self.text_inside=text
    def set_text_outside(self, text):
        self.text_outside=text

    def draw(self):
        self.ax.clear()

        self.ax.frame_on=False
        self.ax.axis("off")
        self.ax.margins(0)

        wl=self.wall.length
        hspace=wl/4
        self.ax.set_xlim([-hspace,wl+hspace])
        vspace=1
        self.ax.set_ylim([self.Tmin-vspace, self.Tmax+vspace])

        layer_name_height=self.Tmax-1
        x0=0
        self.ax.axvline(x=x0, color="k")
        for i in range(len(self.wall.layers)):
            layer=self.wall.layers[i]
            e=layer.e
            x0+=e
            self.ax.axvline(x=x0, color="k")
            self.ax.text(x0-e+0.002,layer_name_height,"%s" %(layer.mat.name),rotation=90,verticalalignment='top', fontsize=9)

        for T in range(self.Tmin, self.Tmax+1,5):
            self.ax.axhline(y=T, color="lightgrey", linestyle="--", linewidth=0.7)
            self.ax.text(-hspace,T+0.1,"%d" %(T), color="lightgrey", fontsize=9)
            self.ax.text(wl+hspace,T+0.1,"%d" %(T), color="lightgrey", fontsize=9,horizontalalignment='right')

        self.ax.text(-hspace,layer_name_height,self.text_inside)


        self.ax.text(wl,layer_name_height,self.text_inside)


        self.ax.plot([-hspace,0],[self.Tint,self.Tint],color="r")
        self.ax.plot([wl,wl+hspace],[self.Tout,self.Tout],color="cyan")


        vmin=np.inf
        vmax=-np.inf
        vmaxabs=0
        for i in range(len(self.wall.layers)):
            layer=self.wall.layers[i]
            T=layer.Tmesh
            grad=np.zeros(layer.Npoints)
            grad[1:-1]= (T[1:-1]-T[0:-2])/layer.dx
            grad[0]=(T[1]-T[0])/layer.dx
            grad[-1]=(T[-1]-T[-2])/layer.dx
            flux=layer.mat.la * grad
            self.wall.layers[i].flux=flux
            vmax=max(vmax, max(flux))
            vmin=min(vmin, min(flux))
            vmaxabs=max(vmaxabs, max(abs(flux)))
        
        self.vmaxabs=max(vmaxabs, self.vmaxabs)
        vmin-=0.0001
        vmax+=0.0001

        for i in range(len(self.wall.layers)):
            layer=self.wall.layers[i]
            x=layer.xmesh
            T=layer.Tmesh
            flux=layer.flux
            r=flux/(abs(flux)+0.00001)*(abs(flux)/(self.vmaxabs+0.00001))**(1/5)
            norm=mplcolors.Normalize(vmin=-1, vmax=1)
            
            # print(r)
            cmap=matplotlib.cm.get_cmap("coolwarm")
            self.ax.scatter(x,T, color=cmap(norm(r)))

#        self.ax.set_xlabel("Position (m)")
        self.ax.axes.get_xaxis().set_visible(False)
        self.ax.set_ylabel("Temperature (°C)")

#        self.ax.set_title("Time = %s" % format_time(self.time))





    def stationnary_equation(self,Ts):
        d=np.zeros(len(Ts))
        d[0]=Ts[0]-self.Tint
        d[len(Ts)-1]=Ts[len(Ts)-1]-self.Tout
        for i in range(1,len(Ts)-1):
            d[i]=(Ts[i]-Ts[i-1])/self.wall.layers[i-1].Rth-(Ts[i+1]-Ts[i])/self.wall.layers[i].Rth
        return d

    def stationnary_linear_system(self):
        n=len(self.wall.layers)+1
        M=np.zeros((n,n))
        d=np.zeros(n)
        d[0]=self.Tint
        d[-1]=self.Tout
        M[0,0]=1
        M[-1,-1]=1
        for i in range(1,n-1):
            M[i, i-1] = - 1/self.wall.layers[i-1].Rth
            M[i, i  ] = 1/self.wall.layers[i].Rth + 1/self.wall.layers[i-1].Rth
            M[i, i+1] = -1/self.wall.layers[i].Rth

        return M,d

    def compute_phi(self):
        phi=0
#        for i in range(len(self.wall.layers)):
#            layer=self.wall.layers[i]
#            T=layer.Tmesh
#            for j in range(1,len(T)):
#                phi+= (T[j] - T[j-1])/layer.Rth * layer.dx
        layer=self.wall.layers[0]
        T=layer.Tmesh
        R=layer.dx/layer.mat.la
        phi= (T[1]-T[0]) /R
        return phi



    def solve_stationnary(self):
        Ts=np.zeros(len(self.wall.layers)+1)
        Ts[0]=self.Tint
        Ts[-1]=self.Tout

        M,d=self.stationnary_linear_system()
        Ts=np.linalg.solve(M,d)

        for i in range(len(self.wall.layers)):
            self.wall.layers[i].Tmesh=(self.wall.layers[i].xmesh-self.wall.layers[i].xmesh[0]) / self.wall.layers[i].e * (Ts[i+1]-Ts[i]) +Ts[i]

        phi=0
        for i in range(len(self.wall.layers)):
            phi+=(Ts[i+1]-Ts[i])/self.wall.layers[i].Rth*self.wall.layers[i].e
        print("phi:",phi, "W/m2")





    def advance_time(self):

        self.time+=self.dt

        updated_temp=[]
        for i in range(len(self.wall.layers)):
            layer=self.wall.layers[i]
            T=layer.Tmesh
            laplaT=np.zeros(len(T))
            laplaT[1:-1]=(T[2:]+T[0:-2]-2*T[1:-1])/(layer.dx)**2

            laplaT[0] = (T[0] - 2 *T[1] + T[2]) / (layer.dx)**2
            laplaT[-1] = (T[-1] - 2 *T[-2] + T[-3]) / (layer.dx)**2
            flux_interfaces=np.zeros(len(T))

            # ~ if i==0:
                # ~ flux_interfaces[0]=0*-layer.mat.D *(T[0]-self.Tint)/layer.dx
            # ~ else:
                # ~ layerleft=self.wall.layers[i-1]
                # ~ Tleft=layerleft.Tmesh
                # ~ F_loc=layer.mat.D * (T[1] -2*T[0] + layerleft.Tmesh[-2])/layer.dx**2
                # ~ F_left=layerleft.mat.D * (layerleft.Tmesh[-1]-2*layerleft.Tmesh[-2]+layerleft.Tmesh[-3]) / layerleft.dx**2
                # ~ flux_interfaces[0]= ( F_loc + 0* F_left)
                # ~ beta=layerleft.mat.D * (Tleft[-1]-Tleft[-2]) / layerleft.dx
                # ~ flux_interfaces[0]= -((T[1]-T[0]) - layerleft.mat.rhoCp/layer.mat.rhoCp * (Tleft[-1]-Tleft[-2]))/self.dt
            # ~ if i==len(self.wall.layers)-1:
                # ~ flux_interfaces[-1]=0*layer.mat.D *(self.Tout-T[-1])/layer.dx**2
            # ~ else:
                # ~ layerright=self.wall.layers[i+1]
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
                layerleft=self.wall.layers[i-1]
                Tleft=layerleft.Tmesh

                r = (layerleft.mat.la/layerleft.dx) / (layer.mat.la/layer.dx)
                Tup[0]=1 / (1+r) * ( T[1] + r * Tleft[-2])

            if i==len(self.wall.layers)-1:
                Tup[-1] = self.Tout
            else:
                layerright=self.wall.layers[i+1]
                Tright=layerright.Tmesh

                r = (layerright.mat.la/layerright.dx) / (layer.mat.la/layer.dx)
                Tup[-1] = 1 / (1+r) * (T[-2] + r * Tright[1])



            updated_temp.append(Tup)

        for i in range(len(self.wall.layers)):
            self.wall.layers[i].Tmesh=updated_temp[i]

        # ~ for i in range(len(self.wall.layers)):
            # ~ layer=self.wall.layers[i]
            # ~ if i>0:
                # ~ layerleft=self.wall.layers[i-1]
                # ~ Tleft=layerleft.Tmesh

                # ~ r = layerleft.mat.la / layer.mat.la
                # ~ self.wall.layers[i].Tmesh[0]=1 / (1+r) * ( self.wall.layers[i].Tmesh[1] + r * Tleft[-2])
            # ~ if i<len(self.wall.layers)-1:
                # ~ layerright=self.wall.layers[i+1]
                # ~ Tright=layerright.Tmesh

                # ~ r = layerright.mat.la / layer.mat.la
                # ~ self.wall.layers[i].Tmesh[-1] = 1 / (1+r) * (self.wall.layers[i].Tmesh[-2] + r * Tright[1])









