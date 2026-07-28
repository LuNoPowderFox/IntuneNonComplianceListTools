import argparse

from .utils import ProgramModes
from ..config import Config

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

    def checkArgs(self, mode: ProgramModes) -> None:
        """
        Tries to run the function specified for the submodule, giving the launch args to it and receiving a fixed set of arguments
        """
        ...

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