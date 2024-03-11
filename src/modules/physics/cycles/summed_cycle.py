


from matplotlib.figure import Figure
from matplotlib import ticker


import numpy as np


from ..helpers.time_formatting import format_time_h_om
from .base_cycle import BaseCycle


class SummedCycle(BaseCycle):
    def __init__(self, cycle1, cycle2, name="SummedCycle"):
        BaseCycle(self, children=[cycle1, cycle2], name=name)


        self.length_days= max([c.length_days for c in self.children])
        self.length= max([c.length for c in self.children])
        
        if not(self.is_valid()):
            print("invalid cycle")
            


    def is_valid(self):
        # both cycles must have same length (maybe not needed actually, could automatically repeat
        return True
        

    def get_temp(self, time):
        
        time_r=time%self.length
        T=0
        for cycle in self.children:
            T+=cycle.get_temp(time_r)
        return T
        
    def plot_cycle(self,ax,  time=None):

        ax.clear()
        ax.axis("on")
        
        ax.set_title(self.name)
        
        times=np.array(self.times + [self.length])
        
        ax.plot(times, self.temperatures +  [self.temperatures[0]])
        
        formatter = lambda x, pos: format_time_h_om(x)
        
        if time!=None:
            time_r=time%self.length
            T=self.get_temp(time)
            ax.scatter([time_r], [T])
            ax.axvline(x=time_r)
        
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(ticker.FixedLocator(times))
        
        
        
        
    
