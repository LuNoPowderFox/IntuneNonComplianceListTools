from enum import Enum
import argparse

#TODO: add more codes if needed
class ReturnCodes(Enum):
    SUCCESS = 0
    ERROR = -1
    INVALID_ARGS = -2
    INVALID_INPUT_FILE = -3
    
    ...

# extract the needed arguments into a dict to be given to the actual module
def extractCompileArgs(parentParser: argparse.ArgumentParser | None = None) -> dict | None:
    ...

def extractMergeArgs(parentParser: argparse.ArgumentParser | None = None) -> dict | None:
    ...
