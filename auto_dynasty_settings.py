import configparser
import json
import os
from pathlib import Path

import shutil
from sims.sim_info_types import Age
from relationships.relationship_enums import RelationshipType

from . import constants
from .utils.debug_logger import debug_log


class GlobalSettings:
    FILE_NAME = constants.CONFIG_FILE_NAME

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

        self.enforce_dynasty_name = False

        # Dynasty Roles
        self.heir_gender_priority = "none"
        self.familial_connections_become_heir = ["children","spouse","siblings","parents"]
        self.heir_minimum_age = "BABY"
        self.keep_existing_heir = True

        self.outcast_minimum_age = int(Age.CHILD)

        self.minimum_rel_heir_threshold = 10
        self.maximum_rel_blacksheep_threshold = -60
        self.minimum_rel_removeblacksheep_threshold = 0

        # Noble Inheritance
        self.minimum_rel_nobleinherit_threshold = 0

        self.nobleinherit_minimum_age = int(Age.TEEN)
        self.nobleinherit_career_req = "all"
        
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

        # Dynasty Auto Repair
        self.global_automatic_repair = True
        self.enable_repair_for_played = False
        self.enable_repair_for_unplayed = True
        
        self.add_which_roles = ["head","heir"]
        self.whitelist_head_relatives = [int(RelationshipType.DESCENDANT),int(RelationshipType.SPOUSE)] 
        self.whitelist_heir_relatives = [int(RelationshipType.DESCENDANT),int(RelationshipType.SPOUSE)] 
        self.whitelist_member_relatives = []
    
    @classmethod
    def migrate_old_config(cls):
        mod_folder_directory = Path(constants.MODS_FOLDER)
        destination = cls.get_file_path()
        existing_config = None

        if os.path.exists(destination):
            return

        for old_config_name in constants.OLD_CONFIG_NAMES:
            existing_config = next(
                (
                    file for file in mod_folder_directory.rglob("*.json")
                    if file.name.replace("[", "").replace("]", "") == old_config_name.replace("[", "").replace("]", "")
                ),
                None
            )
            if existing_config is not None:
                break

        if existing_config is not None:
            cls.load_json(existing_config)
            os.remove(existing_config)
            cls.save(cls)

    @classmethod
    def get_file_path(cls):
        config_folder = Path(constants.MODS_FOLDER)

        script_file = next(
            (
                file for file in config_folder.rglob("*.ts4script")
                if file.name.replace("[","").replace("]","") == constants.MOD_FILE_NAME.replace("[","").replace("]","")
            ),
            None
        )

        if script_file is not None:
            config_folder = script_file.parent
        else:
            config_file = next(
                (
                    file for file in config_folder.rglob("*.cfg")
                    if file.name.replace("[","").replace("]","") == constants.CONFIG_FILE_NAME.replace("[","").replace("]","")
                ),
                None
            )

            if config_file is not None:
                config_folder = config_file.parent

        config_folder.mkdir(parents=True, exist_ok=True)

        return str(config_folder / cls.FILE_NAME)

    @classmethod
    def apply_old_json_dict(cls, data):
        cls.global_dynasty_mod_enabler = data.get("global_dynasty_mod_enabler", True)
        cls.global_noble_mod_enabler = data.get("global_noble_mod_enabler", True)
        cls.global_dynasty_relations_enabler = data.get("global_dynasty_relations_enabler", False)

        cls.automatic_children_join = data.get("automatic_children_join", True)
        cls.automatic_spouse_join = data.get("automatic_spouse_join", True)
        cls.automatic_heir_selection = data.get("automatic_heir_selection", True)
        cls.automatic_blacksheep_selection = data.get("automatic_blacksheep_selection", True)

        cls.automatic_alliances = data.get("automatic_alliances", True)
        cls.automatic_rivalries = data.get("automatic_rivalries", True)
        cls.automatic_remove_alliances = data.get("automatic_remove_alliances", True)
        cls.automatic_remove_rivalries = data.get("automatic_remove_rivalries", True)

        cls.enforce_dynasty_name = data.get("enforce_dynasty_name", False)
        
        cls.heir_gender_priority = data.get("heir_gender_priority", "none")
        cls.familial_connections_become_heir = data.get("familial_connections_become_heir", ["children","spouse","siblings","parents"])
        cls.heir_minimum_age = data.get("heir_minimum_age", "BABY")
        cls.keep_existing_heir = data.get("keep_existing_heir", True)

        cls.outcast_minimum_age = data.get("outcast_minimum_age", Age.CHILD)

        cls.minimum_rel_heir_threshold = data.get("minimum_rel_heir_threshold", 10)
        cls.maximum_rel_blacksheep_threshold = data.get("maximum_rel_blacksheep_threshold", -60)
        cls.minimum_rel_removeblacksheep_threshold = data.get("minimum_rel_removeblacksheep_threshold", 0)

        cls.minimum_rel_nobleinherit_threshold = data.get("minimum_rel_nobleinherit_threshold", 0)
        cls.nobleinherit_minimum_age = data.get("nobleinherit_minimum_age", Age.TEEN)
        cls.nobleinherit_career_req = data.get("nobleinherit_career_req", "all")

        cls.add_dynasty_children = data.get("add_dynasty_children", "headheir")
        cls.add_dynasty_spouse = data.get("add_dynasty_spouse", "headheir")

        cls.minimum_head_rel_new_ally = data.get("minimum_head_rel_new_ally", 40)
        cls.minimum_average_rel_new_ally = data.get("minimum_average_rel_new_ally", 25)
        cls.maximum_level_gap_new_ally = data.get("maximum_level_gap_new_ally", 3)
        cls.maximum_head_rel_remove_ally = data.get("maximum_head_rel_remove_ally", 0)
        cls.maximum_average_rel_remove_ally = data.get("maximum_average_rel_remove_ally", 5)
        cls.maximum_head_rel_new_rival = data.get("maximum_head_rel_new_rival", -50)
        cls.maximum_average_rel_new_rival = data.get("maximum_average_rel_new_rival", -20)
        cls.minimum_head_rel_remove_rival = data.get("minimum_head_rel_remove_rival", 10)

    @classmethod
    def load_json(cls,json_file):
        if not os.path.exists(json_file):
            debug_log(f"Old JSON file not found")
            return
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            cls.apply_old_json_dict(data)
            debug_log(f"Loaded old JSON settings: {data}")
        except Exception as ex:
            debug_log(f"Failed to load settings: {ex}")

    def save(self):
        path = self.get_file_path()

        config = configparser.ConfigParser()

        config["Enablers"] = {
            "global_dynasty_mod_enabler": str(self.global_dynasty_mod_enabler),
            "global_noble_mod_enabler": str(self.global_noble_mod_enabler),
            "global_dynasty_relations_enabler": str(self.global_dynasty_relations_enabler),
            "automatic_children_join": str(self.automatic_children_join),
            "automatic_spouse_join": str(self.automatic_spouse_join),
            "automatic_heir_selection": str(self.automatic_heir_selection),
            "automatic_blacksheep_selection": str(self.automatic_blacksheep_selection),
            "automatic_alliances": str(self.automatic_alliances),
            "automatic_rivalries": str(self.automatic_rivalries),
            "automatic_remove_alliances": str(self.automatic_remove_alliances),
            "automatic_remove_rivalries": str(self.automatic_remove_rivalries),
            "enforce_dynasty_name": str(self.enforce_dynasty_name),
        }

        config["Dynasty Roles"] = {
            "heir_gender_priority": self.heir_gender_priority,
            "familial_connections_become_heir": ",".join(self.familial_connections_become_heir),
            "heir_minimum_age": self.heir_minimum_age,
            "keep_existing_heir": str(self.keep_existing_heir),
            "outcast_minimum_age": str(self.outcast_minimum_age),
            "add_dynasty_children": self.add_dynasty_children,
            "add_dynasty_spouse": self.add_dynasty_spouse,
        }

        config["Noble Inherit"] = {
            "nobleinherit_minimum_age": str(self.nobleinherit_minimum_age),
            "nobleinherit_career_req": self.nobleinherit_career_req,
        }

        config["Dynasty Relations"] = {
            "maximum_level_gap_new_ally": str(self.maximum_level_gap_new_ally),
        }

        config["Thresholds"] = {
            "minimum_rel_heir_threshold": str(self.minimum_rel_heir_threshold),
            "maximum_rel_blacksheep_threshold": str(self.maximum_rel_blacksheep_threshold),
            "minimum_rel_removeblacksheep_threshold": str(self.minimum_rel_removeblacksheep_threshold),
            "minimum_rel_nobleinherit_threshold": str(self.minimum_rel_nobleinherit_threshold),
            "minimum_head_rel_new_ally": str(self.minimum_head_rel_new_ally),
            "minimum_average_rel_new_ally": str(self.minimum_average_rel_new_ally),
            "maximum_head_rel_remove_ally": str(self.maximum_head_rel_remove_ally),
            "maximum_average_rel_remove_ally": str(self.maximum_average_rel_remove_ally),
            "maximum_head_rel_new_rival": str(self.maximum_head_rel_new_rival),
            "maximum_average_rel_new_rival": str(self.maximum_average_rel_new_rival),
            "minimum_head_rel_remove_rival": str(self.minimum_head_rel_remove_rival),
        }

        config["EA Repair"] = {
            "global_automatic_repair": str(self.global_automatic_repair),
            "enable_repair_for_played": str(self.enable_repair_for_played),
            "enable_repair_for_unplayed": str(self.enable_repair_for_unplayed),

            "add_which_roles": ",".join(self.add_which_roles),
            "whitelist_head_relatives": ",".join(str(x) for x in self.whitelist_head_relatives),
            "whitelist_heir_relatives": ",".join(str(x) for x in self.whitelist_heir_relatives),
            "whitelist_member_relatives": ",".join(str(x) for x in self.whitelist_member_relatives),
        }

        try:
            with open(path, "w") as file:
                config.write(file)
            debug_log(f"Saved settings to {path}")

        except Exception as ex:
            debug_log(f"Failed to save settings: {ex}")

    def load(self):
        self.migrate_old_config()
        path = self.get_file_path()

        if not os.path.exists(path):
            debug_log(f"Config not found, creating default at {path}")
            self.save()
            return

        config = configparser.ConfigParser()

        try:
            config.read(path)

            self.global_dynasty_mod_enabler = config.getboolean("Enablers", "global_dynasty_mod_enabler", fallback=True)
            self.global_noble_mod_enabler = config.getboolean("Enablers", "global_noble_mod_enabler", fallback=True)
            self.global_dynasty_relations_enabler = config.getboolean("Enablers", "global_dynasty_relations_enabler", fallback=False)

            self.automatic_children_join = config.getboolean("Enablers", "automatic_children_join", fallback=True)
            self.automatic_spouse_join = config.getboolean("Enablers", "automatic_spouse_join", fallback=True)
            self.automatic_heir_selection = config.getboolean("Enablers", "automatic_heir_selection", fallback=True)
            self.automatic_blacksheep_selection = config.getboolean("Enablers", "automatic_blacksheep_selection", fallback=True)

            self.automatic_alliances = config.getboolean("Enablers", "automatic_alliances", fallback=True)
            self.automatic_rivalries = config.getboolean("Enablers", "automatic_rivalries", fallback=True)
            self.automatic_remove_alliances = config.getboolean("Enablers", "automatic_remove_alliances", fallback=True)
            self.automatic_remove_rivalries = config.getboolean("Enablers", "automatic_remove_rivalries", fallback=True)

            self.enforce_dynasty_name = config.getboolean("Enablers", "enforce_dynasty_name", fallback=False)


            self.heir_gender_priority = config.get("Dynasty Roles", "heir_gender_priority", fallback="none")
            self.familial_connections_become_heir = config.get("Dynasty Roles","familial_connections_become_heir",fallback="children,spouse,siblings,parents").split(",")
            self.heir_minimum_age = config.get("Dynasty Roles", "heir_minimum_age", fallback="BABY")
            self.keep_existing_heir = config.getboolean("Dynasty Roles", "keep_existing_heir", fallback=True)
            self.outcast_minimum_age = config.getint("Dynasty Roles", "outcast_minimum_age", fallback=int(Age.CHILD))
            self.add_dynasty_children = config.get("Dynasty Roles", "add_dynasty_children", fallback="headheir")
            self.add_dynasty_spouse = config.get("Dynasty Roles", "add_dynasty_spouse", fallback="headheir")


            self.nobleinherit_minimum_age = config.getint("Noble Inherit", "nobleinherit_minimum_age", fallback=int(Age.TEEN))
            self.nobleinherit_career_req = config.get("Noble Inherit", "nobleinherit_career_req", fallback="all")


            self.minimum_rel_heir_threshold = config.getint("Thresholds", "minimum_rel_heir_threshold", fallback=10)
            self.maximum_rel_blacksheep_threshold = config.getint("Thresholds", "maximum_rel_blacksheep_threshold", fallback=-60)
            self.minimum_rel_removeblacksheep_threshold = config.getint("Thresholds", "minimum_rel_removeblacksheep_threshold", fallback=0)
            self.minimum_rel_nobleinherit_threshold = config.getint("Thresholds", "minimum_rel_nobleinherit_threshold", fallback=0)
            self.minimum_head_rel_new_ally = config.getint("Thresholds", "minimum_head_rel_new_ally", fallback=40)
            self.minimum_average_rel_new_ally = config.getint("Thresholds", "minimum_average_rel_new_ally", fallback=25)
            self.maximum_head_rel_remove_ally = config.getint("Thresholds", "maximum_head_rel_remove_ally", fallback=0)
            self.maximum_average_rel_remove_ally = config.getint("Thresholds", "maximum_average_rel_remove_ally", fallback=5)
            self.maximum_average_rel_new_rival = config.getint("Thresholds", "maximum_average_rel_new_rival", fallback=-20)
            self.minimum_head_rel_remove_rival = config.getint("Thresholds", "minimum_head_rel_remove_rival", fallback=10)

            self.global_automatic_repair = config.getboolean("EA Repair", "global_automatic_repair", fallback=True)
            self.enable_repair_for_played = config.getboolean("EA Repair", "enable_repair_for_played", fallback=False)
            self.enable_repair_for_unplayed = config.getboolean("EA Repair", "enable_repair_for_unplayed", fallback=True)

            self.add_which_roles = config.get("EA Repair","add_which_roles",fallback="head,heir").split(",")
            self.whitelist_head_relatives = [int(x) for x in config.get("EA Repair", "whitelist_head_relatives", fallback="9,12").split(",") if x]
            self.whitelist_heir_relatives = [int(x) for x in config.get("EA Repair", "whitelist_heir_relatives", fallback="9,12").split(",") if x]
            self.whitelist_member_relatives = [int(x) for x in config.get("EA Repair", "whitelist_member_relatives", fallback="9,12").split(",") if x]

            self.maximum_level_gap_new_ally = config.getint("Dynasty Relations", "maximum_level_gap_new_ally", fallback=3)

            self.save()
            debug_log("Loaded config settings")

        except Exception as ex:
            debug_log(f"Failed to load config settings: {ex}")

    def reset_to_defaults(self):
        self.__init__()
        self.save()


SETTINGS = GlobalSettings()
SETTINGS.load()