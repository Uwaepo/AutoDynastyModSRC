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

# **DEBUG CONSTANTS**
#*LOGGING*

# Global enabler for debug logging.
DEBUG_LOGGING_ENABLED = False