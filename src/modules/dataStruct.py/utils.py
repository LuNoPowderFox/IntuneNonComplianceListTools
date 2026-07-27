from enum import Enum

class AttributeLocation(Enum):
    """
    This will be internally used to determine, where a value is stored
    """
    REFERENCE_TO_LAUNCH_ARGS = 0
    REFERENCE_TO_CONFIG = 1 # Maybe not needed
    NOT_A_REFERENCE = 2