


from matplotlib.figure import Figure
from matplotlib import ticker


import numpy as np


from ..helpers.time_formatting import format_time_h_om


class TemperatureCycle:
    def __init__(self,times, temperatures, name="default name"):
        self.times=times
        self.temperatures=temperatures
        self.name=name

        self.length_days= (self.times[-1]// (24*3600))+1
        self.length= self.length_days * 24 * 3600
        
        if not(self.is_valid()):
            print("invalid cycle")
            
        self.compute_rates()


    def is_valid(self):
        
        # times must be strictly increasing
        for i in range(len(self.times)-1):
            if self.times[i]>=self.times[i+1]:
                return False
        
        # 
        if len(self.times)!=len(self.temperatures):
            return False

            
        return True
        
    def compute_rates(self):
        self.rates=[]
        for i in range(len(self.times)-1):
            r=(self.temperatures[i+1]-self.temperatures[i])/(self.times[i+1]-self.times[i])
            self.rates.append(r)
        
        r = ( self.temperatures[0] - self.temperatures[-1]) / (self.length-self.times[-1])
        self.rates.append(r)

    def get_temp(self, time):
        
        time_r=time%self.length
        # print(time, time_r)
        if time_r>=self.times[-1]:
            r=self.rates[-1]
            T=self.temperatures[-1] + r * (time_r - self.times[-1])
            return T
        for i in range(len(self.times)-1):
            # print(i)
            if self.times[i] <= time_r and time_r <=self.times[i+1]:
                r=self.rates[i]
                T=self.temperatures[i] + r * (time_r - self.times[i])
                # print(T)
                return T
        print("could not find a temperature for the given time in the cycle")
        return False
        
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
        
        
        
        
    
