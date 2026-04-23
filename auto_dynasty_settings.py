import json
import os

from . import constants

from .utils.debug_logger import debug_log


class GlobalSettings:
    FILE_NAME = (f"[{constants.MOD_AUTHOR}]-{constants.MOD_NAME}-CONFIG.json")

    def __init__(self):
        # Enablers
        self.global_dynasty_mod_enabler = True
        self.global_noble_mod_enabler = True
        self.global_dynasty_relations_enabler = False

        self.automatic_children_join = True
        self.automatic_spouse_join = True
        self.automatic_heir_selection = True
        self.automatic_blacksheep_selection = True

        self.automatic_alliances = True
        self.automatic_rivalries = True
        self.automatic_remove_alliances = True
        self.automatic_remove_rivalries = True

        # Dynasty Roles
        self.minimum_rel_heir_threshold = 10
        self.maximum_rel_blacksheep_threshold = -60
        self.minimum_rel_removeblacksheep_threshold = 0

        # Noble Inheritance
        self.minimum_rel_nobleinherit_threshold = 0
        
        # Dynasty Family Changes
        self.add_dynasty_children = "headheir"
        self.add_dynasty_spouse = "headheir"

        # Alliances/Rivalries
        self.minimum_head_rel_new_ally = 40
        self.minimum_average_rel_new_ally = 25
        self.maximum_level_gap_new_ally = 3
        self.maximum_head_rel_remove_ally = 0
        self.maximum_average_rel_remove_ally = 5
        self.maximum_head_rel_new_rival = -50
        self.maximum_average_rel_new_rival = -20
        self.minimum_head_rel_remove_rival = 10


    @classmethod
    def get_file_path(cls):
        base = os.path.join(
            constants.SIMS4_DOCUMENTS_PATH,
            "Mods"
        )

        return os.path.join(base, cls.FILE_NAME)

    def to_dict(self):
        return {
            "global_dynasty_mod_enabler": self.global_dynasty_mod_enabler,
            "global_noble_mod_enabler": self.global_noble_mod_enabler,
            "global_dynasty_relations_enabler": self.global_dynasty_relations_enabler,

            "automatic_children_join": self.automatic_children_join,
            "automatic_spouse_join": self.automatic_spouse_join,
            "automatic_heir_selection": self.automatic_heir_selection,
            "automatic_blacksheep_selection": self.automatic_blacksheep_selection,

            "automatic_alliances": self.automatic_alliances,
            "automatic_rivalries": self.automatic_rivalries,
            "automatic_remove_alliances": self.automatic_remove_alliances,
            "automatic_remove_rivalries": self.automatic_remove_rivalries,

            "minimum_rel_heir_threshold": self.minimum_rel_heir_threshold,
            "minimum_rel_blacksheep_threshold": self.minimum_rel_blacksheep_threshold,
            "minimum_rel_removeblacksheep_threshold": self.minimum_rel_removeblacksheep_threshold,

            "minimum_rel_nobleinherit_threshold": self.minimum_rel_nobleinherit_threshold,

            "add_dynasty_children": self.add_dynasty_children,
            "add_dynasty_spouse": self.add_dynasty_spouse,

            "minimum_head_rel_new_ally": self.minimum_head_rel_new_ally,
            "minimum_average_rel_new_ally": self.minimum_average_rel_new_ally,
            "maximum_level_gap_new_ally": self.maximum_level_gap_new_ally,
            "maximum_head_rel_remove_ally": self.maximum_head_rel_remove_ally,
            "maximum_average_rel_remove_ally": self.maximum_average_rel_remove_ally,
            "maximum_head_rel_new_rival": self.maximum_head_rel_new_rival,
            "maximum_average_rel_new_rival": self.maximum_average_rel_new_rival,
            "minimum_head_rel_remove_rival": self.minimum_head_rel_remove_rival,
        }

    def apply_dict(self, data):
        self.global_dynasty_mod_enabler = data.get("global_dynasty_mod_enabler", True)
        self.global_noble_mod_enabler = data.get("global_noble_mod_enabler", True)
        self.global_dynasty_relations_enabler = data.get("global_dynasty_relations_enabler", False)

        self.automatic_children_join = data.get("automatic_children_join", True)
        self.automatic_spouse_join = data.get("automatic_spouse_join", True)
        self.automatic_heir_selection = data.get("automatic_heir_selection", True)
        self.automatic_blacksheep_selection = data.get("automatic_blacksheep_selection", True)

        self.automatic_alliances = data.get("automatic_alliances", True)
        self.automatic_rivalries = data.get("automatic_rivalries", True)
        self.automatic_remove_alliances = data.get("automatic_remove_alliances", True)
        self.automatic_remove_rivalries = data.get("automatic_remove_rivalries", True)

        self.minimum_rel_heir_threshold = data.get("minimum_rel_heir_threshold", 10)
        self.minimum_rel_blacksheep_threshold = data.get("minimum_rel_blacksheep_threshold", -60)
        self.minimum_rel_removeblacksheep_threshold = data.get("minimum_rel_removeblacksheep_threshold", 0)

        self.minimum_rel_nobleinherit_threshold = data.get("minimum_rel_nobleinherit_threshold", 0)

        self.add_dynasty_children = data.get("add_dynasty_children", "headheir")
        self.add_dynasty_spouse = data.get("add_dynasty_spouse", "headheir")

        self.minimum_head_rel_new_ally = data.get("minimum_head_rel_new_ally", 40)
        self.minimum_average_rel_new_ally = data.get("minimum_average_rel_new_ally", 25)
        self.maximum_level_gap_new_ally = data.get("maximum_level_gap_new_ally", 3)
        self.maximum_head_rel_remove_ally = data.get("maximum_head_rel_remove_ally", 0)
        self.maximum_average_rel_remove_ally = data.get("maximum_average_rel_remove_ally", 5)
        self.maximum_head_rel_new_rival = data.get("maximum_head_rel_new_rival", -50)
        self.maximum_average_rel_new_rival = data.get("maximum_average_rel_new_rival", -20)
        self.minimum_head_rel_remove_rival = data.get("minimum_head_rel_remove_rival", 10)
        

    def load(self):
        path = self.get_file_path()

        if not os.path.exists(path):
            debug_log(f"Settings file not found, creating default at {path}")
            self.save()
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.apply_dict(data)
            debug_log(f"Loaded settings: {data}")

        except Exception as ex:
            debug_log(f"Failed to load settings: {ex}")


    def save(self):
        path = self.get_file_path()

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=4)

            debug_log(f"Saved settings to {path}")

        except Exception as ex:
            debug_log(f"Failed to save settings: {ex}")


    def reset_to_defaults(self):
        debug_log("Resetting settings to default values")

        self.__init__()

        self.save()


SETTINGS = GlobalSettings()
SETTINGS.load()