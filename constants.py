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
DEBUG_LOGGING_ENABLED = True

# **MOD**

# *RELATIONSHIP*

# Minimum friendly relationship score with the head to become a dynasty heir.
MINIMUM_REL_HEIR_THRESHOLD = 10

# Minimum friendly relationship score with the head to become a noble successor.
MINIMUM_REL_NOBLEINHERIT_THRESHOLD = 0

# Maximum friendly relationship with the head sim needed to be declared an outcast.
MAXIMUM_REL_BLACKSHEEP_THRESHOLD = -60

# Minimum friendly relationship with the head sim needed to have outcast status removed.
MINIMUM_REL_REMOVEBLACKSHEEP_THRESHOLD = 0
