


from matplotlib.figure import Figure
from matplotlib import ticker


import numpy as np
import copy

from ..helpers.time_formatting import format_time_h_om


class BaseCycle:
    def __init__(self,children=None,  name="default name"):
        self.name=name
        self.children=copy.deepcopy(children if children else [])


    def is_valid(self):
        raise NotImplementedError('You need to define a is_valid method!')
        

    def get_temp(self, time):
        raise NotImplementedError('You need to define a get_temp method!')
        

        
        
        
        
    
