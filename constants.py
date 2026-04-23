from pathlib import Path

# CONSTANTS
# These values are static and maintain their values through runtime.
# Whilst Python does not offer built-in constant support, anything in this file won't be updated, only read.

# MOD INFORMATION

MOD_NAME = "AutoDynastyMod"
MOD_AUTHOR = "Uwaepo"

# **FILE PATHS**

HOME_PATH = Path.home()
DOCUMENTS_PATH = DOCUMENTS = HOME_PATH / "Documents"

SIMS4_DOCUMENTS_PATH = DOCUMENTS_PATH / "Electronic Arts" / "The Sims 4"

# **DEBUG CONSTANTS**
#*LOGGING*

# Global enabler for debug logging.
DEBUG_LOGGING_ENABLED = False