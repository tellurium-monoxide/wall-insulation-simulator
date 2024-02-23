#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

import numpy as np


import matplotlib
matplotlib.use('WxAgg')

from matplotlib.figure import Figure


import matplotlib.cm
import matplotlib.colors as mplcolors


from .layers import Layer
from .materials import Material
from .layered_wall import Wall


NPOINT_PREFERRED_PER_LAYER=10
NPOINT_MINIMAL_PER_LAYER=4

LIMITER_RATIO = 2



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

def format_time_hms(t):

    ts=int(t)
    d=ts//(24*3600)
    h=(ts - d * 24 * 3600) // 3600
    m=(ts - d * 24 * 3600 - h * 3600) // 60
    s=(ts - d * 24 * 3600 - h * 3600 - m * 60)

    return "%02dh%02dm%02ds" % (h,m,s)
def format_time_hm(t):

    ts=int(t)
    d=ts//(24*3600)
    h=(ts - d * 24 * 3600) // 3600
    m=(ts - d * 24 * 3600 - h * 3600) // 60

    return "%02dh%02dm" % (h,m)

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


        self.run_sim=False
        self.updates_since_redraw=0
        self.time_since_redraw=0
        self.time_last_redraw=time.perf_counter_ns()
        self.this_run_start=time.perf_counter_ns()

        self.Tint_is_variable=False
        self.needRedraw=False

        self.this_run_time=0
        self.this_run_updates=0

        self.method="implicit"

    def remesh(self):
        if self.method=="implicit":
            self.remesh_implicit()
        elif self.method=="explicit":
            self.remesh_explicit()
    def remesh_explicit(self):
        current_length=0
        self.time=0

        # best_dt=min(self.wall.layers, key = lambda x:x.Npoints)
        # if len(self.wall.layers)>0:
            # best_dt=max([ (layer.e/NPOINT_PREFERRED_PER_LAYER)**2 * self.courant / layer.mat.D for layer in self.wall.layers])
        # else:
            # best_dt=0
        # self.dt=best_dt

        if len(self.wall.layers)>0:
            worst_layer=min(self.wall.layers, key = lambda l: (l.e * (self.courant/l.mat.D)**0.5))
            self.dt = (worst_layer.e/NPOINT_MINIMAL_PER_LAYER)**2 * self.courant / worst_layer.mat.D
        else:
            self.dt=0

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

        self.solve_stationnary()


    def remesh_implicit(self):
        current_length=0
        self.time=0
        self.dt=60

        if len(self.wall.layers)>0:
            min_width= min([l.e for l in self.wall.layers])
        else:
            min_width=1

        for i in range(len(self.wall.layers)):
            layer=self.wall.layers[i]

            dx = self.dt



            layer.Npoints=  int(NPOINT_MINIMAL_PER_LAYER * (1+np.log(layer.e / min_width)))
            # print(layer.Npoints)
            # layer.Npoints=  NPOINT_PREFERRED_PER_LAYER
            # layer.Npoints=  NPOINT_MINIMAL_PER_LAYER

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
        self.solve_stationnary()



    def add_layer(self, layer):
        self.wall.add_layer(layer)
        self.remesh()



    def remove_layer(self):
        self.wall.remove_layer()
        self.remesh()

    def change_layers(self, new_layers):
        while len(self.wall.layers):
            self.remove_layer()
        for layer in new_layers:
            self.add_layer(layer)
        self.remesh()




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
        hspace=wl/5
        self.ax.set_xlim([-hspace,wl+hspace])
        vspace=1
        self.ax.set_ylim([self.Tmin-vspace, self.Tmax+vspace])

        layer_name_height=self.Tmax-2
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




        self.ax.text(wl+hspace/100,layer_name_height,self.text_outside)
        self.ax.text(wl+hspace/100,layer_name_height-2,format_time_hm(self.time))

        self.ax.plot([-hspace,0],[self.Tint,self.Tint],color="tab:green")
        self.ax.plot([wl,wl+hspace],[self.Tout,self.Tout],color="tab:green")

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
        phi= (T[0]-T[1]) /R
        return phi



    def solve_stationnary(self):
        Ts=np.zeros(len(self.wall.layers)+1)
        Ts[0]=self.Tint
        Ts[-1]=self.Tout

        M,d=self.stationnary_linear_system()
        Ts=np.linalg.solve(M,d)

        for i in range(len(self.wall.layers)):
            self.wall.layers[i].Tmesh=(self.wall.layers[i].xmesh-self.wall.layers[i].xmesh[0]) / self.wall.layers[i].e * (Ts[i+1]-Ts[i]) +Ts[i]






    def advance_time_explicit(self):
        self.update_Tint()
        self.time+=self.dt
        updated_temp=[]
        for i in range(len(self.wall.layers)):
            layer=self.wall.layers[i]
            T=layer.Tmesh
            laplaT=np.zeros(len(T))
            laplaT[1:-1]=(T[2:]+T[0:-2]-2*T[1:-1])/(layer.dx)**2

            laplaT[0] = (T[0] - 2 *T[1] + T[2]) / (layer.dx)**2
            laplaT[-1] = (T[-1] - 2 *T[-2] + T[-3]) / (layer.dx)**2



            Tup=T + self.dt *  (layer.mat.D * laplaT)

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

    def advance_time_implicit(self):

        alpha=0.5

        self.time+=self.dt
        updated_temp=[]
        nl=len(self.wall.layers)
        Ntot = sum([layer.Npoints for layer in self.wall.layers]) - nl+1 + 1
        M=np.zeros((Ntot,Ntot))
        Tglob=np.zeros(Ntot)

        l0=self.wall.layers[0]
        coef=self.Tint_is_variable * self.dt *  l0.mat.la/ l0.dx * self.wall.room.surface /self.wall.room.heat_capacity
        M[0,0]=1
        M[0,1]=  alpha *coef
        M[0,2]= - alpha *coef

        Tglob[0]=self.Tint + self.Tint_is_variable * self.dt * self.wall.room.heating_power /self.wall.room.heat_capacity
        Tglob[0]+= (1-alpha) * coef * (l0.Tmesh[1] - l0.Tmesh[0])

        M[1,0]=   -1

        lid=1
        for i in range(nl):
            layer=self.wall.layers[i]
            T=layer.Tmesh
            n=len(T)
            Kl=np.zeros((n,n))
            Tr=np.zeros(n)


            for p in range(1,n-1):
                Kl[p,p]=-2
                Kl[p,p-1]=1
                Kl[p,p+1]=1

            Ml= np.eye(n) - alpha * self.dt * layer.mat.D * Kl / layer.dx**2

            Trhs_loc=(np.eye(n) + (1-alpha) * self.dt * layer.mat.D * Kl / layer.dx**2).dot(T)

            Tr[1:-1]=Trhs_loc[1:-1]
            if i==0:
                Tr[0]=0
                Ml[0,0]=1
            else:
                # layerleft=self.wall.layers[i-1]
                Tr[0]=0
                # Ml[0,0]=-3/2 * layer.mat.la / layer.dx
                # Ml[0,1]=4/2 * layer.mat.la / layer.dx
                # Ml[0,2]=-1/2  * layer.mat.la / layer.dx
                Ml[0,0]=-1 * layer.mat.la / layer.dx
                Ml[0,1]=1  * layer.mat.la / layer.dx
            if i==nl-1:
                Tr[-1]=self.Tout
                Ml[-1,-1]=1
            else:
                Tr[-1]=0
                # Ml[-1,-3]=3/2 * layer.mat.la / layer.dx
                # Ml[-1,-2]=-4/2  * layer.mat.la / layer.dx
                # Ml[-1,-1]=1/2  * layer.mat.la / layer.dx
                Ml[-1,-2]=1  * layer.mat.la / layer.dx
                Ml[-1,-1]=-1  * layer.mat.la / layer.dx
            M[lid:lid+n,lid:lid+n] = M[lid:lid+n,lid:lid+n]+Ml
            Tglob[lid:lid+n] = Tglob[lid:lid+n]+Tr
            # Tup = np.linalg.solve(M,T)
            lid+=n-1


        Tup= np.linalg.solve(M, Tglob)


        self.Tint=Tup[0]
        lid=1
        for i in range(nl):
            layer=self.wall.layers[i]
            n=layer.Npoints
            self.wall.layers[i].Tmesh=Tup[lid:lid+n]
            lid+=n-1


    def advance_time(self):

        if self.method=="implicit":
            self.advance_time_implicit()
        elif self.method=="explicit":
            self.advance_time_explicit()



    def update_loop(self):
        time_new_redraw=time.perf_counter_ns()
        self.time_since_redraw=time_new_redraw-self.time_last_redraw
        while self.run_sim:
            time.sleep(0.00001)


            time_new_redraw=time.perf_counter_ns()
            self.time_since_redraw=time_new_redraw-self.time_last_redraw
#            needRedraw=self.time_since_redraw >= 30*1e6 # 50 is main_panel.timer_update_redraw.GetInterval()

            steps_per_sec= self.updates_since_redraw/self.time_since_redraw*1e9
            isTooFast=self.time_since_redraw > 0 and  steps_per_sec > self.steps_to_statio/LIMITER_RATIO
#            isTooFast=False
            if  not(self.needRedraw) and not(isTooFast):
                self.advance_time()
                self.updates_since_redraw+=1
            else:
                time.sleep(0.001)

            # elif isTooFast:
                # print("limiting updates per sec")



    def update_Tint(self):
        if self.Tint_is_variable:

            phi = self.compute_phi()

            dT= -self.dt * self.wall.room.compute_temperature_loss_rate(phi)

            newT= self.Tint + dT

            # if newT> self.Tmin and newT<self.Tmax :
                # self.Tint=newT
            self.Tint=newT

    def compute_heat_loss(self):
        phi = self.compute_phi()

        return self.wall.room.compute_heat_loss_rate(phi)

    def update_Tout(self):
        return

