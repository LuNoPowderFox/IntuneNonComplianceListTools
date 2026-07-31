#TODO: config stuff

import argparse, json, os
from . import _standartConfigPath, utils
from .ConfigTypes import ConfigTypes


class Config:
    #TODO: maybe make a function that generates a config preset based on existing compiled lists
    """
    Still WIP

    Configs for formating
    dir: {
        "tablePresetName": (name of the table preset to use; None or empty for standart),
        "colors": {
            (column name; '*' for all as fallback/default): {
                "headerBackgroundColor": (color to use in the header row; None or empty for no color),
                "attributeBackgroundColor": (color to use in the attribute rows; None or empty for no color),
                headerForegroundColor: (color to use in the header row; None or empty for no color),
                "attributeForegroundColor": (color to use in the attribute rows; None or empty for no color)
            }
        },
        "fonts": {
            (column name; '*' for all as fallback/default): {
                "font": (font name; None or empty for standart),
                "fontSize": (font size; None for standart),
                "headerStyle": (style to apply to header row (italic, bold, cursive); None or empty for standart),
                "attributeStyle": (style to apply to attribute rows (italic, bold, cursive); None or empty for standart)
            }
        },
        "rules": { (conditional rules)
            (formatRuleName): {
                "applyTo": (list of columns to apply this rule to),
                "exclude": (columName/maybe pattern for specific cells(later); can be a list; Used if "applyTo" is left empty),
                "range": (range for the rule to apply to, empty for all rows excluding header)
                "dynamicArgs": { (Some rule types might or might not use different args. those would be put here)
                    (argName): (Value)
                },
                "actions": { (For all possible actions/rules)
                    (actionName): {
                        "ruleType": (what rule this is, probably enum value),
                        "condition": {
                            "operator": (operator if needed),
                            "formula": (formula if needed)
                        },
                        "fill": (the color to fill the cell with) (will probably be changed to be more dynamic)
                    }
                }
            }
        },
        "links": {
        (linkName): {
            "link": (hyperlink with placeholder if needed),
            "valueSource": {
                    "sourceType": (Indicate, whether 'value' is a hardcoded value or for example a column name),
                    "value": (hardcoded value or column name),
                    "keepSourceColumn": (indicate whether the source column should be removed or not)
            },
            "applyTo": (columnName/maybe pattern for specific cells (later); can be a list),
            "exclude": (columName/maybe pattern for specific cells(later); can be a list; Used if "applyTo" is left empty)
        }
    }
   
    Configs for columns and which to keep
    dir: {
        (name of the sheet/OS to apply this to; '*' for all as fallback/default): {
            "keepColumns": (list of column Names),
            "excludeColumns": (list of column Names),
            "keepRest": (bool to determine whether columns, that haven't been mentioned yet, should be kept as well or not; if yes, they will be put between the columns specified in 'columnOrderStart' and 'columnOrderEnd'),
            "extraColumns": (list of columns to add at the end if not present, for example Notes),
            "columnOrderStart": (list of the columns in the wanted order at the start),
            "columnOrderEnd": (list of the columns in the wanted order at the end)
        }
    }

    Configs for merge behaviour
    dir: {
        "oldValues": { (settings around old values)
            "keepOldValues": (bool to determine whether to display previous values),
            "removeOldValuesWhenNoChange": (bool to determine whether to remove the old value when there wasn't a change),
            "oldValuesCount": (how many versions of old versions to keep before removal)
        },
        "autoCompile": { (settings involving auto compilation of .csv files)
            "ask4CompileWhenNotAuto": (If this is true and the program was not launched with autocompile active, ask the user if they want to compile)
        }
    }
    
    Configs for value generation behaviour
    dir: {
        (operationName; '*' for all as fallback/default): {
            (argName): (ruleset for generation (not sure how yet))
        }
    }

    Configs for standart values
    dir: {
        "args": {
            (argName): (either the wanted Value or a magic value indicating dynamic generation)
        }
    }
    """

    def __init__(self):
        self._isEditable: bool = False
        self.configProfileName: str = ""
        self._configPath: str = ""
        self._conf: dir = {}
        self._format: dir = {}
        self._columns: dir = {}
        self._mergeBehaviour: dir = {}
        self._valueGen: dir = {}
        self._standartgVals: dir = {}

    def _loadConfig(self, pConf: dir | None = None) -> None:
        if pConf is None:
            self._conf = utils._standartConf
        else:
            self._conf = pConf

        self._isEditable = False
        self.configProfileName = self._conf["configProfileName"]
        self._format = self._conf["formating"]
        self._columns = self._conf["columns"]
        self._mergeBehaviour = self._conf["mergeBehaviour"]
        self._valueGen = self._conf["valueGen"]
        self._standartgVals = self._conf["standartVals"]
    
    def _loadConfigFromFile(self, pConfigFile: str | None = None) -> None:
        configFile = self._configPath
        if pConfigFile is not None:
            configFile = pConfigFile
        
        if not os.path.exists(configFile):
            print(f"{configFile} does not exist!")
            self._loadConfig()
            with open(configFile, 'w') as json_file:
                json.dump(self._conf, json_file, indent=4)
            return

        # only for saving the file
        # self._loadConfig()
        # with open(configFile, 'w') as json_file:
        #     json.dump(self._conf, json_file, indent=4)
        # exit(0)
        # return

        with open(configFile, "r") as file:
            conf = json.load(file)
        
        self._loadConfig(pConf=conf)

    def loadConfig(self, settingFile: argparse.Namespace | str) -> None:
        #TODO: change this to not need Namespace
        if type(settingFile) == argparse.Namespace:
            if settingFile is None or settingFile.settingsFile is None: #temp, to prevent stuff breaking during testing
                self._configPath = _standartConfigPath
            else:
                self._configPath = settingFile.settingsFile
        elif type(settingFile) == str:
            if settingFile is None or settingFile == "":
                #TODO: this currently often breaks, fix this properly
                self._configPath = _standartConfigPath
            else:
                self._configPath = settingFile
        self._loadConfigFromFile()

    def __getConfigValue(self, configDir: dir, configName: str, returnAsDict: bool = False, checkExists: bool = False) -> dict | bool | None:
        # if valuePath is empty it might be a problem (just realized it shouldn't even be called with config name as empty, so doesn't matter)
        valuePath = configName.split("/")
        result = configDir
        tmp = result
        for i, value in enumerate(valuePath):
            if type(tmp) == dict and value in tmp.keys():
                tmp = tmp[value]
            else:
                #WARNING: with the way this is handled, the actual config dir is not allowed to have any None values
                tmp = None
                break

        if checkExists and tmp is not None:
            return True
        elif checkExists and tmp is None:
            return False
        if tmp is not None and type(tmp) != dict and returnAsDict:
            result = {valuePath[-1]: tmp}
        elif tmp is not None and type(tmp) != dict and not returnAsDict:
            result = tmp
        elif tmp is not None and type(tmp) == dict and returnAsDict:
            result = {valuePath[-1]: tmp}
        elif tmp is not None and type(tmp) == dict and not returnAsDict:
            result = tmp
        return result

    def getConfig(self, configName: ConfigTypes, configValue: str | None = None, returnAsDict: bool = False, checkExists: bool = False) -> dict | bool | None:
        """
        Get values from the config

        :param configName: The part of the config to retrieve
        :type configName: ConfigTypes
        :param configValue: the name/path of the config to get, separated by '/' (for example in Formating: "colors/*/headerBackgroundColor" for just the value 'headerBackgroundColor' or "colors/*" for all values of that config) [Optional]
        :type configValue: str | None
        :param returnAsDict: If this is False, try to return the config value itself. If true, return the entry packaged in a dict with the entryname as its key
        :type returnAsDict: bool
        :param checkExists: Tells the function to only check if the config exists. Should only be set by internal functions
        :type checkExists: bool
        :return: The wanted config either by itself or packaged in a dict | bool if checkExists is set or None if not found
        :rtype: dict | bool | None
        """
        returnDir = None
        match configName:
            case ConfigTypes.All:
                returnDir = self._conf
            case ConfigTypes.Formating:
                returnDir = self._format
            case ConfigTypes.Columns:
                returnDir = self._columns
            case ConfigTypes.MergeBehaviour:
                returnDir = self._mergeBehaviour
            case ConfigTypes.ValueGen:
                returnDir = self._valueGen
            case ConfigTypes.StandartVals:
                returnDir = self._standartgVals
        if returnDir is not None and configValue is not None:
            returnDir = self.__getConfigValue(returnDir, configValue, returnAsDict=returnAsDict, checkExists=checkExists)
        return returnDir
    
    def isInConfig(self, configName: ConfigTypes, configValue: str | None = None) -> bool:
        """
        Checks whether the wanted config is set or not
        """
        return self.getConfig(configName=configName, configValue=configValue)