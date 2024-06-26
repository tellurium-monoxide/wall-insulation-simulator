#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle


from .materials import Material
from .layers import Layer
from .room import Room
from .temperature_cycle import TemperatureCycle






class WallConfigData:
    def __init__(self):
        self.materials={}
        self.presets={}
        self.rooms={}
        self.temp_cycles={}


    def add_material(self,mat):
        self.materials[mat.name]=mat


    def remove_material(self,name_to_be_del,force_delete=False):
        if len(self.get_material_list())==1:
            return False
        name_list=self.get_list_presets_using_material(name_to_be_del)
        if len(name_list)>0:
            if not(force_delete) or len(name_list)==len(self.get_preset_list()):
                return False
            else:
                for preset_name in name_list:
                    print("Deleting preset:", preset_name)
                    self.remove_preset_wall(preset_name)
                return self.__remove_material__(name_to_be_del)
        else:
            return self.__remove_material__(name_to_be_del)

    def __remove_material__(self, name_to_be_del):
        if (name_to_be_del in self.get_material_list()):
            self.materials.pop(name_to_be_del)
            print("Deleting material:", name_to_be_del)
            return True
        else:
            return False






    def get_material(self,name):
        return self.materials[name]
    def get_material_list(self):
        return list(self.materials.keys())




    def add_preset_wall(self,name, named_layers):
        layers=[]
        for named_layer in named_layers:

            if not(named_layer[1] in self.materials):
                print("preset has unknown material")
                return False
            else:
                layers.append(Layer(e=named_layer[0], mat = self.get_material(named_layer[1])))


        self.presets[name]=layers
        return True


    def remove_preset_wall(self,name):
        self.presets.pop(name)

    def get_preset(self,name):
        return self.presets[name]


    def get_preset_list(self):
        return list(self.presets.keys())


    def get_list_presets_using_material(self, mat_name):
        list_presets_using_mat=[]
        for preset_name, layers in self.presets.items():
            if mat_name in [l.mat.name for l in layers]:
                list_presets_using_mat.append(preset_name)
        return list_presets_using_mat

    def get_default_preset(self):
        return self.presets[self.get_preset_list()[0]]



    def add_preset_room(self, room):
        self.rooms[room.name]=room

    def remove_preset_room(self, room_name):
        try:
            self.rooms.pop(room_name)
        except ValueError:
            return False
        else:
            return True

    def get_room(self, room_name):
        return self.rooms[room_name]

    def get_room_names_list(self):
        return list(self.rooms.keys())

    def get_default_room(self):
        return self.rooms[self.get_room_names_list()[0]]

    def add_temp_cycle(self, cycle):
        self.temp_cycles[cycle.name]=cycle

    def remove_temp_cycle(self, cycle_name):
        try:
            self.temp_cycles.pop(cycle_name)
        except ValueError:
            return False
        else:
            return True
            
    def get_temp_cycle_names_list(self):
        return list(self.temp_cycles.keys())
        
    def get_temp_cycle(self, cycle_name):
        return self.temp_cycles[cycle_name]
    def get_default_temp_cycle(self):
        return self.temp_cycles[self.get_temp_cycle_names_list()[0]]
        
        
        
    def write_to_file(self, pathname, file):
        print("Writing config to %s" % pathname)
        # for name, mat in self.materials.items():
            # line="material,"+name+","
            # line+=str(mat.la)+","
            # line+=str(mat.rho)+","
            # line+=str(mat.Cp)+"\n"
            # file.write(line)
        # for name, preset in self.presets.items():
            # line="preset,"+name+","
            # for layer in preset:
                # line+=str(layer.e)+","
                # line+=str(layer.mat.name)+","
            # line=line[:-1]
            # line+="\n"
            # file.write(line)
        pickle.dump(self,file, protocol=pickle.DEFAULT_PROTOCOL)
    def load_from_file(self, pathname, file):
        print("Loading config from %s" % pathname)
        # lines=file.readlines()
        config=pickle.load(file)
        self.materials=config.materials
        self.presets=config.presets



        
        
DefaultConfig=WallConfigData()


# taken from http://meteo.re.free.fr/thermo.php :
DefaultConfig.add_material(Material(la=0.038,Cp=2100, rho=55, name="Laine de bois"))
DefaultConfig.add_material(Material(la=0.024,Cp=1400, rho=32, name="Polyurethane PUR"))
DefaultConfig.add_material(Material(la=0.330,Cp=792, rho=790, name="BA13"))
DefaultConfig.add_material(Material(la=0.032,Cp=1450, rho=15, name="polystyrene gris EPS"))
DefaultConfig.add_material(Material(la=1.050,Cp=648, rho=1300, name="parpaing"))
DefaultConfig.add_material(Material(la=0.032,Cp=1030, rho=29, name="Laine de verre GR32"))
DefaultConfig.add_material(Material(la=0.040,Cp=1030, rho=15, name="Laine de verre"))
DefaultConfig.add_material(Material(la=0.038,Cp=1860, rho=60, name="Ouate de cellulose"))

# others:
DefaultConfig.add_material(Material(la=2,Cp=840, rho=2200, name="Béton"))
DefaultConfig.add_material(Material(la=0.024,Cp=1000, rho=1.2, name="Air"))


DefaultConfig.add_preset_wall("Isolation intérieur laine de bois", [(0.15, "Laine de bois"), (0.4, "Béton")])
DefaultConfig.add_preset_wall("Isolation intérieur laine de verre", [(0.15, "Laine de verre"), (0.4, "Béton")])
DefaultConfig.add_preset_wall("Isolation intérieur laine de bois + BA13", [(0.013, "BA13"),(0.15, "Laine de bois"), (0.4, "Béton")])
DefaultConfig.add_preset_wall("Isolation intérieur laine de bois + BA13 + air", [(0.013, "BA13"),(0.01, "Air"),(0.15, "Laine de bois"), (0.4, "Béton")])
DefaultConfig.add_preset_wall("Béton seul", [(0.4, "Béton")])



DefaultConfig.add_preset_room(Room(shape=(10,5, 2.5), heating_power=0, name="Pièce par défault"))



DefaultConfig.add_temp_cycle(TemperatureCycle([0, 6*3600, 12*3600, 16*3600, 20*3600], [4, 6, 15, 18, 15], name="Cycle par défaut"))




