from enum import Enum

class AttributeLocation(Enum):
    """
    This will be internally used to determine, where a value is stored
    """
    LAUNCH_ARGS = 0
    CONFIG = 1 # Maybe not needed
    FUNC_ARGS = 2
    RETURN_VAL = 3

class ProgramModes(Enum):
    """
    Used to indicate the modes of the program
    """
    UNSPECIFIED = -1
    HELP = 0
    COMPILE = 1
    MERGE = 2
    GUI = 3