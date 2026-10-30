from pathlib import Path

from .utils import file_helper

# CONSTANTS
# These values are static and maintain their values through runtime.
# Whilst Python does not offer built-in constant support, anything in this file won't be updated, only read.

# MOD INFORMATION

OLD_CONFIG_NAMES = [
    "[Uwaepo]-AutoDynastyMod-CONFIG.json",
    "[Uwaepo]-AutoDynastyInheritance-CONFIG.json",
]

MOD_AUTHOR = "Uwaepo"
MOD_NAME = "AutoDynastyInheritance"
MOD_FILE_NAME = (f"[{MOD_AUTHOR}]-{MOD_NAME}.ts4script")
CONFIG_FILE_NAME = (f"[{MOD_AUTHOR}]-{MOD_NAME}-CONFIG.cfg")

# **FILE PATHS**

SIMS4_DOCUMENTS_PATH = file_helper.get_sims4_documents_folder()

MODS_FOLDER = SIMS4_DOCUMENTS_PATH / "Mods"
CONFIG_FOLDER = MODS_FOLDER

# **GAMEPLAY**

PARENT_NOBLE_TRAIT_IDS = {
    1: 3791951303619634378,
    2: 3791951303619634377,
    3: 3791951303619634376,
    4: 3791951303619634383,
    5: 3791951303619634382,
    6: 3791951303619634381,
    7: 3791951303619634380,
    8: 3791951303619634371,
    9: 3791951303619634370,
    10: 4560401178722943758,
}

COMPOUND_MAIDEN_NAME_LEFT_TRAIT_ID = 4630667655733169750
COMPOUND_MAIDEN_NAME_RIGHT_TRAIT_ID = 9412910719029212693

# **DEBUG CONSTANTS**
#*LOGGING*

# Global enabler for debug logging.
DEBUG_LOGGING_ENABLED = False