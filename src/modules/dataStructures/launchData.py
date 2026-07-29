import argparse
import sys

from .utils import ProgramModes
from .returnCodes import ReturnCodes
from ..config import Config
# if 'returnData' in sys.modules:
from .returnData import ReturnData
if 'argumentData' in sys.modules:
    from .argumentData import ArgumentData

class LaunchData():
    _launchArgsRaw: argparse.Namespace = None
    _launchArgs: dict = None
    _correctedLaunchArgs: dict = None
    _usedSubCommand: str = "" # What subcommand was involved

    def __init__(self, launchArgsRaw: argparse.Namespace):
        self._launchArgsRaw = launchArgsRaw
        self._extractLaunchArgs()

    def _extractLaunchArgs(self) -> None:
        self._launchArgs = vars(self._launchArgsRaw)
        self._usedSubCommand = self.getLaunchArg("subCommand")
        #TODO: maybe move the extraction somewhere here and then just check them where they are currently getting extracted
        ...

    def runExtractFunc(self) -> ReturnData:
        """
        Tries to run the extraction function from the arguments
        
        :return: The result of the extract function for that module
        :rtype: ReturnData
        """
        rData = ReturnData()
        if not self.isInLaunchArgs("extractFunc"):
            rData.setReturnCode(ReturnCodes.ERROR)
            rData.setArgCode("extractFunc", ReturnCodes.MISSING_ARGS)
            rData.setErrorMessage("extractFunc", "No launch argument extraction function to run with launch args was set!")
            return rData
        return self.getLaunchArg("extractFunc")()

    def runModeFunc(self, args: ArgumentData) -> ReturnData:
        """
        Tries to run the method specified in the launch args for the specified module

        :return: The result of the run method for that module
        :rtype: ReturnData
        """
        rData = ReturnData()
        if not self.isInLaunchArgs("func"):
            rData.setReturnCode(ReturnCodes.ERROR)
            rData.setArgCode("func", ReturnCodes.MISSING_ARGS)
            rData.setErrorMessage("func", "No function to run with launch args was set!")
            return rData
        
        return self.getLaunchArg("func")(args)

    def isInLaunchArgs(self, argument: str) -> bool:
        if argument in self._launchArgs.keys():
            return True
        return False

    def getLaunchArg(self, name: str):
        """
        Returns the wanted launch argument.  
        If the wanted argument is not found, raise AttributeError() for now

        :param name: the name of the argument to return
        :type name: str
        """
        if self.isInLaunchArgs(name):
            return self._launchArgs[name]
        raise AttributeError()

    def getConfig(self) -> Config | None:
        if not self.isInLaunchArgs("config"):
            return None
        return self.getLaunchArg("config")

    def getMainMode(self) -> ProgramModes:
        """
        Returns the mode specified by the first subcommand in the launch args
        """
        if not self.isInLaunchArgs("subCommand"):
            return ProgramModes.UNSPECIFIED
        match self.getLaunchArg("subCommand"):
            case "Compile":
                return ProgramModes.COMPILE
            case "Merge":
                return ProgramModes.MERGE
            case "Help":
                return ProgramModes.HELP
            case "GUI":
                return ProgramModes.GUI
            case _:
                return ProgramModes.UNSPECIFIED