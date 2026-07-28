from typing import List
import argparse
import copy
import sys

from ..config import Config, ConfigTypes
from .utils import AttributeLocation, ProgramModes
from .launchData import LaunchData
from .globalData import GlobalData

# Nice point to rediscover that cirular imports are a thing...
if "returnData" in sys.modules:
    from .returnData import ReturnData
if 'globData' in sys.modules:
    from . import globData

# I'm shitty at naming stuff...
class ArgumentData():
    """
    Contains data like arguments for functions and the sub mode of the program
    should maybe replace the argparse.Namespace class/accept it as an argument and extract the data
    should have a function to create a new instance of this class with parameters from an existing one (would be useful for autocompiling)
    should have a function for setting new arguments (and maybe return it as a new instance)
    
    the _args dict should contain both determine whether each arg is "hardcoded" or a reference to the launch args and the actual value/reference

    args: a dict containing dictionaries for each argument and where it's stored
    mode: The submode the program is running in (will be used, if main mode is GUI for example)
    """

    def __init__(self, mode: ProgramModes = ProgramModes.UNSPECIFIED):
        self._args: dict = {}
        self._mode: ProgramModes = mode

    @classmethod
    def createFromExisting(cls, newArgs: dict | ReturnData | None = None, newMode: ProgramModes | None = None, keepUnchangedArgs: bool = False) -> ArgumentData:
        """
        Creates and returns a new ArgumentData intance that is initially a copy of the intance this was invoked on

        :param newArgs: The new data to fill the new intance with. Can be just a dictionary or a ReturnData instance to extract from
        :type newArgs: dict | ReturnData | None 
        :param newMode: If set, set the sub mode in the new instance to the given value
        :type newMode: ProgramModes
        :param bool keepUnchangedArgs: Decides whether to keep arguments not specified in newArgs and leave them in the new intance
        :return: The new ArgumentData instance
        :rtype: ArgumentData
        """
        newData = copy.copy(cls)
        if newArgs is not None:
            if type(newArgs) == ReturnData:
                newData.extractFromReturnData(newArgs)
            else:
                newData._setArgs(newArgs=newArgs)
        if newMode is not None:
            newData._setMode(newMode)
        return newData

    @property
    def args(self) -> dict:
        """
        Returns the entire argument attribute  
        Not recommended, unless specifically needed as this does not ensure proper checking for validity  
        Might be removed later
        """
        return self._args

    def getArgsList(self) -> List:
        """
        Just returns a list of all aguments
        """
        return self._args.keys()

    def isInArgs(self, name: str) -> bool:
        """
        Checks if the wanted argument is found in Data
        """
        return name in self._args.keys()

    def getArg(self, name):
        """
        Returns the wanted Argument  
        If the argument is not found, raise AttributeError() for now
        """
        if not name in self._args.keys():
            #TODO: better error handling for this
            raise AttributeError()
        match self._args[name]["location"]:
            case AttributeLocation.FUNC_ARGS:
                return self._args[name]["value"]
            case AttributeLocation.LAUNCH_ARGS:
                return globData.launchData.getLaunchArg(name)
            case AttributeLocation.CONFIG:
                return globData.config.getConfig(self._args[name]["value"]["type"], self._args[name]["value"]["path"])

    def setArg(self, name: str, value, configPath: str = "", location: AttributeLocation = AttributeLocation.LAUNCH_ARGS) -> None:
        """
        Set an the argument [name] to the wanted value

        :param name: The name of the argument
        :type name: str
        :param value: either the value if location is FUNC_ARG or of ConfigTypes if location is CONFIG
        :type value: Any | ConfigTypes
        :param configPath: In case location is set to CONFIG, store this alongside the ConfigTypes
        :type configPath: str
        :param location: The actual place where the value is stored
        :type location: AttributeLocation
        """
        newValue = value
        match location:
            case AttributeLocation.LAUNCH_ARGS:
                if not globData.launchData.isInLaunchArgs(name):
                    raise AttributeError()
            case AttributeLocation.CONFIG:
                #TODO: Config needs a isInConfig() function
                if not globData.config.isInConfig(value, configPath):
                    raise AttributeError()
                newValue = { "type": value, "path": configPath }
            # case AttributeLocation.FUNC_ARGS:
                # Why? doesn't that break it?...
                #TODO: check this
                # if not self.isInArgs(name):
                #     raise AttributeError()
                pass
        self._args[name] = {"location": location, "value": newValue}

    def _setArgs(self, newArgs: dict) -> None:
        """
        Internal function to replace the args dict as a whole
        """
        self._args = newArgs

    def extractFromReturnData(self, rData: ReturnData, valueList: List | None = None, replaceExisting: bool = False) -> None:
        """
        Extract the return values and save them as arguments. Extracts all values, unless valueList is set
        """
        for value in rData.getReturnValueList():
            if not valueList is None and value not in valueList:
                continue
            if value in self.getArgsList() and not replaceExisting:
                continue
            self._args[value] = {"location": AttributeLocation.FUNC_ARGS, "value": rData.returnValues[value]}

    def getMode(self) -> ProgramModes:
        return self._mode

    def _setMode(self, mode: ProgramModes) -> None:
        self._mode = mode