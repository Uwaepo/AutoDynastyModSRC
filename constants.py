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

# *SIM RELATIONSHIP THRESHOLDS*
# Dynasty Roles:
# Minimum friendly relationship score with the head to become a dynasty heir.
MINIMUM_REL_HEIR_THRESHOLD = 10

# Maximum friendly relationship with the head sim needed to be declared an outcast.
MAXIMUM_REL_BLACKSHEEP_THRESHOLD = -60

# Minimum friendly relationship with the head sim needed to have outcast status removed.
MINIMUM_REL_REMOVEBLACKSHEEP_THRESHOLD = 0

# Noble Ranks:
# Minimum friendly relationship score with the head to become a noble successor.
MINIMUM_REL_NOBLEINHERIT_THRESHOLD = 0

# *DYNASTY RELATIONS THRESHOLDS*
# Alliances:

# Global enabler for automatic dynasty relation changes.
AUTO_RELATIONS_ENABLED = False

# TO CREATE AN ALLIANCE, EITHER THE HEAD/AVERAGE CONDITION MUST BE MET
# Minimum relationship needed with the head of a dynasty to form an alliance. (x% or more)
MINIMUM_HEAD_REL_NEW_ALLY = 40

# Minimum average relationship with all members to form an alliance. (x% or more)
MINIMUM_AVERAGE_REL_NEW_ALLY = 25

# The maximum lower-bound level gap for an alliance to be considered between dynasties. 
MAXIMUM_LOWER_LEVEL_GAP_ALLY = 3

# TO REMOVE AN ALLIANCE, BOTH THE HEAD/AVERAGE CONDITIONS MUST BE MET
# The maximum relationship between two heads to consider removing an alliance. (x% or less)
MAXIMUM_HEAD_REL_REMOVE_ALLY = 0

# The maximum relationship between two heads to consider removing an alliance. (x% or less)
MAXIMUM_AVERAGE_REL_REMOVE_ALLY = 5

# Rivalries:

# TO CREATE A RIVALRY, EITHER THE HEAD/AVERAGE CONDITION MUST BE MET
# Maximum relationship needed with the head of a dynasty to form a rivalry. (x% or less)
MAXIMUM_HEAD_REL_NEW_RIVAL = -50

# Maximum average relationship with all members to form a rivalry. (x% or less)
MAXIMUM_AVERAGE_REL_NEW_RIVAL = -20

# RIVALS ARE ONLY REMOVED BASED ON RELATIONS WITH THE HEAD. IF THE HEAD HAS A GOOD RELATIONSHIP WITH A RIVAL DYNASTY HEAD, THE RIVALRY WILL BE REMOVED.
# The maximum relationship between two heads to consider removing an rivalry. (x% or more)
MINIMUM_HEAD_REL_REMOVE_RIVAL = 10