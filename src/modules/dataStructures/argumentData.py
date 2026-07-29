from typing import List
import copy
import sys

from ..config import Config, ConfigTypes
from .utils import AttributeLocation, ProgramModes
from .launchData import LaunchData
from .globalData import GlobalData
from . import gData

# Nice point to rediscover that cirular imports are a thing...
# if "returnData" in sys.modules:
from .returnData import ReturnData

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
        #TODO: add better functionality for setting new args
        newData = copy.copy(cls)
        # newData = ArgumentData()
        # newData._setArgs(cls.args)
        # newData._setMode(cls.getMode())
        print(newData)
        if newArgs is not None:
            if type(newArgs) == ReturnData:
                newData.extractFromReturnData(rData=newArgs, replaceExisting=True)
            elif type(newArgs) == dict:
                for name in newArgs.keys():
                    if not "location" in newArgs[name] and not "value" in newArgs[name]:
                        #TODO: choose better error handling
                        raise AttributeError
                    newData.setArg(name=name, value=newArgs[name]["value"], location=newArgs[name]["location"])
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
                return gData.globData.launchData.getLaunchArg(self._args[name]["value"])
            case AttributeLocation.CONFIG:
                print(gData.globData.config.getConfig(self._args[name]["value"]["type"], self._args[name]["value"]["path"])[name])
                return gData.globData.config.getConfig(self._args[name]["value"]["type"], self._args[name]["value"]["path"])[name] # With this we just need to make sure that the config name is the same as [name] here

    def setArg(self, name: str, value, configPath: str = "", location: AttributeLocation = AttributeLocation.FUNC_ARGS) -> None:
        """
        Set an the argument [name] to the wanted value

        :param name: The name of the argument
        :type name: str
        :param value: either the value if location is FUNC_ARG or of ConfigTypes if location is CONFIG or the launch arg if location is LAUNCH_ARG
        :type value: Any | ConfigTypes
        :param configPath: In case location is set to CONFIG, store this alongside the ConfigTypes
        :type configPath: str
        :param location: The actual place where the value is stored
        :type location: AttributeLocation
        """
        newValue = value
        match location:
            case AttributeLocation.LAUNCH_ARGS:
                if not gData.globData.launchData.isInLaunchArgs(value):
                    raise AttributeError()
            case AttributeLocation.CONFIG:
                if not gData.globData.config.isInConfig(value, configPath):
                    raise AttributeError()
                newValue = { "type": value, "path": configPath }
            # case AttributeLocation.FUNC_ARGS:
                # Why? doesn't that break it?...
                #TODO: check this
                # if not self.isInArgs(name):
                #     raise AttributeError()
                pass
        self._args[name] = {"location": location, "value": newValue}
        del newValue

    def _setArgs(self, newArgs: dict) -> None:
        """
        Internal function to replace the args dict as a whole
        """
        self._args = newArgs

    def extractFromReturnData(self, rData: ReturnData, valueList: List | None = None, newMode: ProgramModes | None = None, extractMode: bool = False, replaceExisting: bool = False) -> None:
        """
        Extract the return values and save them as arguments. Extracts all values, unless valueList is set

        :param ReturnData rData: The ReturnData object to extract the values from
        :param valueList: If this is set, only extract the values mentioned in here
        :type valueList: List | None
        :param newMode: Manually set the new mode
        :type newMode: ProgramModes | None
        :param bool extractMode: If this is set, also extract the mode set in rData. Only has an effect if newMode is not set
        :param bool replaceExisting: If this is set, replace already existing values, if not, ignore that value
        """
        for arg in rData.getReturnValueList():
            if not valueList is None and arg not in valueList:
                continue
            if arg in self.getArgsList() and not replaceExisting:
                continue
            if rData.returnValues[arg]["location"] == AttributeLocation.RETURN_VAL:
                self._args[arg] = {"location": AttributeLocation.FUNC_ARGS, "value": rData.getReturnValue(arg)}
            else:
                self._args[arg] = {"location": rData.returnValues[arg]["location"], "value": rData.returnValues[arg]["value"]}

        if not newMode is None:
            self._setMode(newMode)
        if extractMode and newMode is None:
            self._setMode(rData.mode)

    def getMode(self) -> ProgramModes:
        """
        Returns the set mode

        :return: The mode
        :rtype: ProgramModes
        """
        return self._mode

    def _setMode(self, mode: ProgramModes) -> None:
        """
        Sets the mode

        :param ProgramModes mode: The mode to set
        """
        self._mode = mode