class Localizer:

    def __init__(self):
        self.langs=["en","fr"]
        self.lang="en"

        self.setters={}
        self.texts={}
        for lang in self.langs:
            self.texts[lang]={}
            # ~ self.setters[lang] = lambda event : print(dir(event))
            # ~ self.setters[lang] = lambda event : print(event.GetId())
            # ~ self.setters[lang] = lambda event : print(event.GetEventObject().FindItemById(event.GetId()).GetItemLabel())
            self.setters[lang] = lambda event : self.set_lang(event.GetEventObject().FindItemById(event.GetId()).GetItemLabel())
        # ~ for lang in self.langs:

            # ~ self.setters[lang](1)
        self.texts["en"]["run_button"]="Start"
        self.texts["fr"]["run_button"]="Démarrer"

        self.texts["en"]["run_button_pause"]="Stop"
        self.texts["fr"]["run_button_pause"]="Arrêter"

        self.texts["en"]["run_button_tooltip"]="Start simulating the diffusion of heat in the wall."
        self.texts["fr"]["run_button_tooltip"]="Démarre la simulation de diffusion de la température dans le mur."

        self.texts["en"]["button_advance"]="Advance one step"
        self.texts["fr"]["button_advance"]="Avance un pas de temps"

        self.texts["en"]["button_statio"]="Stationnary"
        self.texts["fr"]["button_statio"]="Stationnaire"

        self.texts["en"]["button_statio_tooltip"]="Go directly to the temperature profile established after a long time "
        self.texts["fr"]["button_statio_tooltip"]="Avance la simulation jusqu'à l'état stationnaire."

        self.texts["en"]["button_edit"]="Edit"
        self.texts["fr"]["button_edit"]="Editer"

        self.texts["en"]["button_edit_confirm"]="Confirm"
        self.texts["fr"]["button_edit_confirm"]="Confirmer"

        self.texts["en"]["button_add"]="Add layer"
        self.texts["fr"]["button_add"]="Ajouter couche"

        self.texts["en"]["button_remove"]="Remove layer"
        self.texts["fr"]["button_remove"]="Retirer couche"

        self.texts["en"]["button_load"]="Load ->"
        self.texts["fr"]["button_load"]="Charger ->"

        self.texts["en"]["button_load_tooltip"]="Load the preset wall selected in the dropdown menu"
        self.texts["fr"]["button_load_tooltip"]="Charge le mur prédéfini sélectionner dans le menu déroulant à droite."

        self.texts["en"]["button_save"]="Save"
        self.texts["fr"]["button_save"]="Enregistrer"

        self.texts["en"]["button_save_tooltip"]="Does nothing yet."
        self.texts["fr"]["button_save_tooltip"]="Ne fait rien pour l'instant."

        self.texts["en"]["button_create_mat"]="Create"
        self.texts["fr"]["button_create_mat"]="Créer"

        self.texts["en"]["button_create_mat_tooltip"]="Does nothing yet."
        self.texts["fr"]["button_create_mat_tooltip"]="Ne fait rien pour l'instant."

        self.texts["en"]["button_delete_mat"]="X"
        self.texts["fr"]["button_delete_mat"]="X"

        self.texts["en"]["button_delete_mat_tooltip"]="Does nothing yet."
        self.texts["fr"]["button_delete_mat_tooltip"]="Ne fait rien pour l'instant."


        self.links={}
    def get_text(self, text_id):
        if text_id in self.texts[self.lang]:
            return self.texts[self.lang][text_id]
        else:
            return "missing text"
    def link(self,setter, text_id, link_name):

        setter(self.get_text(text_id))
        self.links[link_name]=(setter,text_id)

    def set_lang(self,lang):
        self.lang=lang
        for key, link in self.links.items():
            setter,text_id=link
            setter(self.get_text(text_id))
            # ~ print(text_id)
