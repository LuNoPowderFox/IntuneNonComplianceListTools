import sys

# if 'launchData' in sys.modules:
from .launchData import LaunchData
from .utils import ProgramModes
from ..config import Config

import argparse

class GlobalData():
    """
    # GlobalData  
    Contains the launcharguments, the config data for the program and the main mode the program is running in  
    Should be accessible by every program-internal function using this data structure module
    """
    _launchData: LaunchData = None
    _config: Config = None
    _mode: ProgramModes = ProgramModes.UNSPECIFIED

    def __init__(self, launchData: argparse.Namespace | LaunchData | None = None):
        if not launchData is None:
            self._setLaunchData(launchData)
        self._loadConfig()
        self._setMode(self._launchData.getMainMode())

    @property
    def launchData(self) -> LaunchData | None:
        return self._launchData

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def config(self) -> Config | None:
        return self._config
    
    def _setLaunchData(self, launchArgs: argparse.Namespace | LaunchData) -> None:
            """
            Internal function to populate the launch data.  
            Could *technically* be run multiple times, but isn't recommended because the data *should* only be set on launch
            """
            #TODO: make this extract the args properly
            if type(launchArgs) == LaunchData:
                self._launchData = launchArgs
            else:
                self._launchData = LaunchData(launchArgsRaw=launchArgs)

    def _setMode(self, mode: ProgramModes) -> None:
        """
        Sets the main mode the program is launched in  
        Should not be called from outside the class

        :param mode: The main mode the program is running in
        :type mode: ProgramModes
        """
        self._mode = mode

    def _loadConfig(self, configPath: str | None = None) -> None:
        """
        Loads a (new) Config for the program

        :param configPath: if set, try to load the config from the given Path. If not set, try to load either the config specified in launchArgs or the default config
        :type configPath: str | None
        """
        self._config = self._launchData.getConfig()
        if configPath is None:
            self._config.loadConfig(self._launchData.getLaunchArg("settingsFile"))
        else:
            self._config.loadConfig(configPath)
