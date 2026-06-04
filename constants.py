from pathlib import Path

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

HOME_PATH = Path.home()
DOCUMENTS_PATH = DOCUMENTS = HOME_PATH / "Documents"

SIMS4_DOCUMENTS_PATH = DOCUMENTS_PATH / "Electronic Arts" / "The Sims 4"

MODS_FOLDER = SIMS4_DOCUMENTS_PATH / "Mods"
CONFIG_FOLDER = MODS_FOLDER

# TUNABLE REFERENCES

MARRIAGE_RELBIT_GUID = 15822

# **DEBUG CONSTANTS**
#*LOGGING*

# Global enabler for debug logging.
DEBUG_LOGGING_ENABLED = False