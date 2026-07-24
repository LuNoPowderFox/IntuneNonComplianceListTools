from typing import List
import argparse
import copy

from ..config import Config, ConfigTypes
from .utils import AttributeLocation
from .launchData import LaunchData

# I'm shitty at naming stuff...
class ArgumentData():
    """
    Contains data like arguments for functions, launch arguments & config
    should maybe replace the argparse.Namespace class/accept it as an argument and extract the data
    should have a function to create a new instance of this class with parameters from an existing one (would be useful for autocompiling)
    should have a function for setting new arguments (and maybe return it as a new instance)
    
    the _args dict should contain both determine whether each arg is "hardcoded" or a reference to the launch args and the actual value/reference

    launchData (static): the launch arguments & config
    args: a dict containing dictionaries for each argument and where it's stored
    """
    _launchData: LaunchData = None

    def __init__(self):
        self._args: dict = {}

    @classmethod
    def createFromExisting(cls, newArgs: dict | None = None):
        newData = copy.copy(cls)
        if newArgs is not None:
            newData._setArgs(newArgs=newArgs)
        return newData

    @property
    def args(self) -> dict:
        return self._args

    def getArgsList(self) -> List:
        return self._args.keys()

    def isInArgs(self, name: str) -> bool:
        return name in self._args.keys()

    def getArg(self, name):
        if not name in self._args.keys():
            #TODO: better error handling for this
            raise AttributeError()
        match self._args[name]["location"]:
            case AttributeLocation.NOT_A_REFERENCE:
                return self._args[name]["value"]
            case AttributeLocation.REFERENCE_TO_LAUNCH_ARGS:
                return self._launchData.getLaunchArg(name)
            case AttributeLocation.REFERENCE_TO_CONFIG:
                return self._launchData.getConfig(self._args[name]["value"])

    def setArg(self, name: str, value, location: AttributeLocation = AttributeLocation.NOT_A_REFERENCE):
        """
        Set an the argument [name] to the wanted value

        :param name: The name of the argument
        :param value: either the value or the internal location of the data. If it's referencing a config, it this stands for the ConfigType, the config Path will for now not be saved
        :param location: to determine, where the data is stored. If it is a reference to launch args, the data stored in, [name] must match to an existing entry for that attribute
        """
        newValue = value
        match location:
            case AttributeLocation.REFERENCE_TO_LAUNCH_ARGS:
                if not self._launchData.isInLaunchArgs(name):
                    raise AttributeError()
            case AttributeLocation.REFERENCE_TO_CONFIG:
                if not self._launchData.isInConfig(name):
                    raise AttributeError()
            case AttributeLocation.NOT_A_REFERENCE:
                if not self.isInArgs(name):
                    raise AttributeError()
        self._args[name] = {"location": location, "value": newValue}

    def _setArgs(self, newArgs):
        self._args = newArgs

    def _setLaunchArgs(self, launchArgs: argparse.Namespace | LaunchData):
        #TODO: make this extract the args properly
        if type(launchArgs) == LaunchData:
            self._launchData = launchArgs
        else:
            self._launchData = LaunchData(launchArgsRaw=launchArgs)

    