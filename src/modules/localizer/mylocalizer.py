
from .localizer import Localizer

class MyLocalizer(Localizer):

    def __init__(self):
        Localizer.__init__(self)

        self.add_lang("en")
        self.add_lang("fr")

        self.texts["en"]["menu_file"]="File"
        self.texts["fr"]["menu_file"]="Fichier"

        self.texts["en"]["menu_file_save"]="Save config"
        self.texts["fr"]["menu_file_save"]="Save config"

        self.texts["en"]["menu_file_load"]="Load config"
        self.texts["fr"]["menu_file_load"]="Load config"

        self.texts["en"]["menu_lang"]="Language"
        self.texts["fr"]["menu_lang"]="Langue"

        self.texts["en"]["menu_help"]="Help"
        self.texts["fr"]["menu_help"]="Aide"

        self.texts["en"]["plot_text_inside"]="Inside"
        self.texts["fr"]["plot_text_inside"]="Intérieur"

        self.texts["en"]["plot_text_outside"]="Outside"
        self.texts["fr"]["plot_text_outside"]="Extérieur"

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

        self.texts["en"]["button_reset"]="Reset"
        self.texts["fr"]["button_reset"]="Réinitialiser"



        # wall customizer
        self.texts["en"]["button_edit"]="Edit"
        self.texts["fr"]["button_edit"]="Editer"

        self.texts["en"]["button_edit_confirm"]="Confirm"
        self.texts["fr"]["button_edit_confirm"]="Confirmer"

        self.texts["en"]["button_load"]="Load ->"
        self.texts["fr"]["button_load"]="Charger ->"

        self.texts["en"]["button_load_tooltip"]="Load the preset wall selected in the dropdown menu"
        self.texts["fr"]["button_load_tooltip"]="Charge le mur prédéfini sélectionner dans le menu déroulant à droite."

        self.texts["en"]["button_save"]="Save"
        self.texts["fr"]["button_save"]="<- Enregistrer"

        self.texts["en"]["button_save_tooltip"]="Save the current wall configuration to the list of presets."
        self.texts["fr"]["button_save_tooltip"]="Enregistre la configuration de mur actuelle avec le nom indiqué ci-contre, ou remplace la configuration actuelle si aucun nom n'est renseigné."

        self.texts["en"]["button_create_material"]="Edit materials"
        self.texts["fr"]["button_create_material"]="Modifier les matériaux"

        self.texts["fr"]["button_collapse_list"]="> Réduire <"


        # material creator
        self.texts["en"]["button_save_mat"]="Save"
        self.texts["fr"]["button_save_mat"]="Enregistrer"

        self.texts["en"]["button_save_mat_tooltip"]="Save the material."
        self.texts["fr"]["button_save_mat_tooltip"]="Enregistre le matériau avec les paramètres renseignés ci-dessous."

        self.texts["en"]["button_save_as_mat"]="Save as"
        self.texts["fr"]["button_save_as_mat"]="Enregistrer sous"

        self.texts["en"]["button_save_as_mat_tooltip"]="Does nothing yet."
        self.texts["fr"]["button_save_as_mat_tooltip"]="Ne fait rien pour l'instant."

        self.texts["en"]["button_delete_mat"]="Delete"
        self.texts["fr"]["button_delete_mat"]="Supprimer"

        self.texts["en"]["button_delete_mat_tooltip"]="Does nothing yet."
        self.texts["fr"]["button_delete_mat_tooltip"]="Ne fait rien pour l'instant."

        self.texts["en"]["dialog_overwrite_name"]="This will overwrite the material, please confirm."
        self.texts["fr"]["dialog_overwrite_name"]="Confirmez le changement des propriétés du matériau."


