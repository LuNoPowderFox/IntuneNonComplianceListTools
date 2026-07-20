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
        }
    }
   
    Configs for columns and which to keep
    dir: {
        (name of the sheet/OS to apply this to; '*' for all as fallback/default): {
            "keepColumns": (list of column Names),
            "excludeColumns": (list of column Names),
            "keepRest": (bool to determine whether columns, that haven't been mentioned yet, should be kept as well or not),
            "extraColumns": (list of columns to add at the end if not present, for example Notes),
            "columnOrderStart": (list of the columns in the wanted order at the start),
            "columnOrderEnd": (list of the columns in the wanted order at the end)
        }
    }

    Configs for merge behaviour
    dir: {
        "oldValues": { (settings around old values)
            "keepOldValues": (bool to determine whether to display previous values),
            "oldValuesCount": (how many versions of old versions to keep before removal)
        }
    }
    
    Configs for value generation behaviour
    dir: {
        (operationName; '*' for all as fallback/default): {
            (argName): (ruleset for generation (not sure how yet))
        }
    }
    
    Configs for links
    dir: {
        (linkName): {
            "link": (hyperlink with placeholder if needed),
            "fillValuePattern": (pattern for value to replace the placeholder or magic Value, indicating the cell value to be used),
            "applyTo": (columnName/maybe pattern for specific cells (later); can be a list),
            "exclude": (columName/maybe pattern for specific cells(later); can be a list; Used if "applyTo" is left empty)
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
        self.configProfileName: str = ""
        self._configPath: str = ""
        self._conf: dir = {}
        self._format: dir = {}
        self._columns: dir = {}
        self._mergeBehaviour: dir = {}
        self._valueGen: dir = {}
        self._links: dir = {}
        self._standartgVals: dir = {}


    def _loadConfig(self, pConf: dir | None = None) -> None:
        if pConf is None:
            self._conf = utils._standartConf
        else:
            self._conf = pConf

        self.configProfileName = self._conf["configProfileName"]
        self._format = self._conf["formating"]
        self._columns = self._conf["columns"]
        self._mergeBehaviour = self._conf["mergeBehaviour"]
        self._valueGen = self._conf["valueGen"]
        self._links = self._conf["links"]
        self._standartgVals = self._conf["standartVals"]
        ...
    
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
        # return

        with open(configFile, "r") as file:
            conf = json.load(file)
        
        self._loadConfig(pConf=conf)

    def loadConfig(self, args: argparse.Namespace) -> None:
        if args is None or args.settingsFile is None:
            self._configPath = _standartConfigPath
        else:
            self._configPath = args.settingsFile

        # print(self._configPath)
        self._loadConfigFromFile()

    def getConfig(self, configName: ConfigTypes, configValue: str | None = None) -> dict | None:
        match configName:
            case ConfigTypes.Formating:
                return self._format
            case ConfigTypes.Columns:
                return self._columns
            case ConfigTypes.MergeBehaviour:
                return self._mergeBehaviour
            case ConfigTypes.ValueGen:
                return self._valueGen
            case ConfigTypes.Links:
                return self._links
            case ConfigTypes.StandartVals:
                return self._standartgVals
        ...