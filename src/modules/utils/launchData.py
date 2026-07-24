import argparse

from ..config import Config, ConfigTypes

class LaunchData():
    _launchArgsRaw: argparse.Namespace = None
    _launchArgs: dict = None
    _config: Config = None

    def __init__(self, launchArgsRaw: argparse.Namespace | None):
        self._launchArgsRaw = launchArgsRaw
        self._loadConfig()
        self._extractLaunchArgs()

    def _extractLaunchArgs(self) -> None:
        #TODO
        ...

    def isInLaunchArgs(self, argument: str) -> bool:
        if argument in self._launchArgs.keys():
            return True
        return False

    def getLaunchArg(self, name: str):
        if self.isInLaunchArgs(name):
            return self._launchArgs[name]
        raise AttributeError()

    def _loadConfig(self):
        self._config.loadConfig(self._launchArgsRaw)

    # IDK, isn't implemented in Config yet
    def __isInConfig(self, configType: ConfigTypes, config: str) -> bool:
        # return self._config.
        ...

    def getConfig(self, configName: ConfigTypes, configValue: str | None = None) -> dict | None:
        return self._config.getConfig(configName=configName, configValue=configValue)