#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 08:39:27 2024

@author: tb266682
"""



import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure


import scipy.optimize

from collections import namedtuple


class Material:
	
	def __init__(self,la=1, rho=1, Cp=1):
		self.rho=rho
		self.la=la
		self.Cp=Cp
		
		
		self.D=la / ( rho * Cp)
	

DefaultMaterials={}
def register_material(mat, name):
	DefaultMaterials[name]=mat
	
def DefaultMaterialList():
	return list(DefaultMaterials.keys())
	
mat1=Material(la=1,Cp=1, rho=1)
register_material(mat1, "mat1")

mat2=Material(la=0.5,Cp=1, rho=3)
register_material(mat2, "mat2")


class Layer:
	def __init__(self,e = 1, mat=Material()):
		self.e=e
		self.mat=mat
		
		self.Rth = e / mat.la
		


# ~ Layer = namedtuple('Layer', ['e', 'la', 'rho','Cp','dx'])

class Wall:
	
	def __init__(self):
		self.figure = Figure()
		self.axes = self.figure.add_subplot(111)
		self.ax=self.axes
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
		
		

	def remesh(self):
		self.wall_length=0
		for i in range(len(self.layers)):
			layer=self.layers[i]
			
			dx = (layer.mat.D * self.dt / self.courant) ** 0.5
			layer.dx=dx
			layer.Npoints= int(layer.e / dx)
			layer.xmesh=np.linspace(self.wall_length,self.wall_length+layer.e,layer.Npoints)
			layer.Tmesh=np.zeros(layer.Npoints)
			
			self.wall_length+=layer.e
			self.layers[i]=layer


	def add_layer(self, layer):
		self.layers.append(layer)
		self.remesh()
		
	def remove_layer(self):
		layer=self.layers.pop()
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

		
		
	
	def draw(self):
		self.ax.clear()
		x0=0
		self.ax.axvline(x=x0, color="k")
		for i in range(len(self.layers)):
			e=self.layers[i].e
			x0+=e
			self.ax.axvline(x=x0, color="k")
			self.ax.text(x0-e,self.Tint+1,"Layer %d" %(i+1))
			# ~ legend="D=%4.2f\n" %(self.diffs[i])
			# ~ legend+="Rth=%4.1f\n" % self.Rth[i]
			# ~ legend+="$\lambda$=%4.2f\n" % self.layers[i].la
			# ~ legend+="rhoCp=%4.1f" % (self.layers[i].rho*self.layers[i].Cp)
			# ~ self.ax.text(x0-e,-3,legend, va="top")
		
		
		self.ax.text(-x0/2,self.Tint+1,"Room")
		
		
		self.ax.text(x0,self.Tint+1,"Outside")
		self.ax.set_xlim([-x0/2,1.5*x0])
		self.ax.set_ylim([self.Tout-5, self.Tint+5])
		
		self.plot_Tint=self.ax.plot([-self.wall_length,0],[self.Tint,self.Tint],color="r")
		self.plot_Tout=self.ax.plot([self.wall_length,2*self.wall_length],[self.Tout,self.Tout],color="cyan")
		self.Tplots=[]
		for i in range(len(self.layers)):
			self.Tplots.append(self.ax.plot(self.layers[i].xmesh,self.layers[i].Tmesh))
			
		self.ax.set_ylabel("Temperature (°C)")
		
		phi_in_to_out=self.compute_phi()
		
		flux_text="Thermal flux\n %5.2f W/m²" % phi_in_to_out
		self.text_flux=self.ax.text(-self.wall_length/4,self.Tint-5,flux_text, ha="center")
		
			
	def draw_wall(self):
		x0=0
		self.ax.axvline(x=x0, color="k")
		for i in range(len(self.layers)):
			e=self.layers[i].e
			x0+=e
			self.ax.axvline(x=x0, color="k")
			self.ax.text(x0-e,self.Tint+1,"Layer %d" %(i+1))
			# ~ legend="D=%4.2f\n" %(self.diffs[i])
			# ~ legend+="Rth=%4.1f\n" % self.Rth[i]
			# ~ legend+="$\lambda$=%4.2f\n" % self.layers[i].la
			# ~ legend+="rhoCp=%4.1f" % (self.layers[i].rho*self.layers[i].Cp)
			# ~ self.ax.text(x0-e,-3,legend, va="top")
		
		
		self.ax.text(-x0/2,self.Tint+1,"Room")
		
		
		self.ax.text(x0,self.Tint+1,"Outside")
		self.ax.set_xlim([-x0/2,1.5*x0])
		self.ax.set_ylim([self.Tout-5, self.Tint+5])
		


	def init_plot_temp(self):
		self.plot_Tint=self.ax.plot([-self.wall_length,0],[self.Tint,self.Tint],color="r")
		self.plot_Tout=self.ax.plot([self.wall_length,2*self.wall_length],[self.Tout,self.Tout],color="cyan")
		self.Tplots=[]
		for i in range(len(self.layers)):
			self.Tplots.append(self.ax.plot(self.layers[i].xmesh,self.layers[i].Tmesh))
			
		self.ax.set_ylabel("Temperature (°C)")
		
		phi_in_to_out=self.compute_phi()
		
		flux_text="Thermal flux\n %5.2f W/m²" % phi_in_to_out
		# ~ flux_text+="\n%5.2f W/m²" % self.phi_int_to_wall
		self.text_flux=self.ax.text(-self.wall_length/4,self.Tint-5,flux_text, ha="center")
	
	def update_plot_temp(self):
#        self.ax.plot([-self.wall_length,0],[self.Tint,self.Tint],color="r")
		self.plot_Tout[0].set_data([self.wall_length,2*self.wall_length],[self.Tout,self.Tout])
		for i in range(self.Nlayer):
			self.Tplots[i][0].set_data(self.meshes[i],self.temp[i])
			
		phi_in_to_out=self.compute_phi()
		flux_text="Thermal flux\n %5.2f W/m²" % phi_in_to_out
		# ~ flux_text+="\n%5.2f W/m²" % self.phi_int_to_wall
		self.text_flux.set(text=flux_text)
			
			
	
	def stationnary_equation(self,Ts):
		d=np.zeros(len(Ts))
		d[0]=Ts[0]-self.Tint
		d[len(Ts)-1]=Ts[len(Ts)-1]-self.Tout
		for i in range(1,len(Ts)-1):
			d[i]=(Ts[i]-Ts[i-1])/self.layers[i-1].Rth-(Ts[i+1]-Ts[i])/self.layers[i].Rth
		return d
			
	
	def compute_phi(self):
		phi=0
		for i in range(len(self.layers)):
#            layer=self.layers[i]
			T=self.layers[i].Tmesh
			for j in range(1,len(T)):
				phi+= (T[j] - T[j-1])/self.layers[i].Rth * self.layers[i].dx
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
			phi+=(Ts[i+1]-Ts[i])/self.layers[i].Rth
		print("phi:",phi, "W/m2")
		
		
		
	
		
	def advance_time(self):
		
		self.time+=self.dt
		
		updated_temp=[]
		for i in range(len(self.layers)):
			layer=self.layers[i]
			T=layer.Tmesh
			x=layer.xmesh
			laplaT=np.zeros(len(T))
			laplaT[1:-1]=(T[2:]+T[0:-2]-2*T[1:-1])/(x[1:-1]-x[0:-2])**2
			
			flux_interfaces=np.zeros(len(T))
			
			if i==0:
				Tleft=self.Tint
				flux_interfaces[0]=-layer.mat.D *(T[0]-Tleft)/layer.dx
				self.phi_int_to_wall=flux_interfaces[0]
#                laplaT[0]=-(T[0]-Tleft)/(x[1]-x[0])
			else:
				layerleft=self.layers[i-1]
				F_loc=layer.mat.D * (T[1]-T[0])/layer.dx
				F_left=layerleft.mat.D * (layerleft.Tmesh[-1]-layerleft.Tmesh[-2]) / layerleft.dx
				flux_interfaces[0]=  F_loc - F_left
			if i==len(self.layers)-1:
				Tright=self.Tout
				flux_interfaces[-1]=layer.mat.D *(Tright-T[-1])/layer.dx
			else:
				layerright=self.layers[i+1]
				Tright=layerright.Tmesh[1]
				F_loc=layer.mat.D * (T[-1]-T[-2])/layer.dx
				F_right= layerright.mat.D * (layerright.Tmesh[1]-layerright.Tmesh[0])/layerright.dx
				flux_interfaces[-1]= F_right - F_loc
			
			
			Tup=T + self.dt *  (layer.mat.D * laplaT + flux_interfaces)
			updated_temp.append(Tup)
		
		for i in range(len(self.layers)):
			self.layers[i].Tmesh=updated_temp[i]
		
		# ~ phi=self.compute_phi()
		# ~ print("advance", phi)
		

	def update_anim(self,frame):
		for t in range(self.anim_plot_frequency):
			self.advance_time()
			
		self.update_plot_temp()
		self.ax.set_title("Time = %5.1f seconds"% self.time)
		





if __name__=="__main__":
	

	wall=Wall()

	
	dt=0.08
	wall.set_time_step(dt)
	
	mat1=Material(la=0.05,rho=1,Cp=1)
	mat2=Material(la=0.4,rho=3,Cp=1)
	
	layer1=Layer(e=1, mat=mat1)
	layer2=Layer(e=2, mat=mat2)
	wall.add_layer(layer1)
	# ~ wall.add_layer(layer2)
	
	# ~ wall.change_layers([layer2])
	
	print("la",wall.layers[0].mat.la)
	
	wall.set_inside_temp(19)
	wall.set_outside_temp(10)
	

	
	# ~ print(wall.courant)

	wall.solve_stationnary()
	wall.draw()
	
	# ~ wall.draw_wall()
	# ~ wall.init_plot_temp()
	# ~ plt.savefig("1.png")
# =============================================================================
# start animating
# =============================================================================
	
	# ~ wall.set_outside_temp(5)
	
	
	
	# ~ wall.ax.set_title("init")
	# ~ wall.draw_wall()
	# ~ wall.update_plot_temp()

 
	# ~ plt.savefig("2.png")

#    
	# ~ nframes=60
	
	# ~ wall.anim_plot_frequency=1
	# ~ ani = FuncAnimation(wall.figure, wall.update_anim, frames=range(nframes), blit=False)
	
	# ~ writer = animation.PillowWriter(fps=10,
									 # ~ metadata=dict(artist='Me'),
									 # ~ bitrate=1800)
	# ~ ani.save('3.gif', writer=writer)
	


	# ~ plt.show()
#    niter=1000
#    nout=100
#    for k in range(niter+1):
#        wall.advance_time()
#        if k%nout==0:
#            print(k/niter*100)
#
#            wall.ax.set_title(wall.time)
#            wall.draw_wall()
#            wall.plot_temp()
#            plt.savefig("anim/wall%d.png"%k)
#            ax.clear()
#            plt.close()
		

#    wall.solve_stationnary()
	
#    ax=plt.gca()
#    wall.ax.set_title("Last iter, %d seconds" % wall.time)
#    wall.draw_wall(ax)
#    wall.plot_temp(ax)
	
	
# =============================================================================
#     plot the stationnary solution for comparison
# =============================================================================
	fig2, ax2 = plt.subplots()
	wall.ax=ax2
	wall.solve_stationnary()

 
	wall.ax.set_title("Statio")
	wall.draw_wall()
	wall.init_plot_temp()



	
	

	plt.show()
