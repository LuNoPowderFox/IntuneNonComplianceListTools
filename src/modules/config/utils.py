from enum import Enum

class ConfigMagicValues(Enum):
    USE_CELL_VALUE = 9999
    GENERATE_VALUE = 9998

_standartConf: dir = {
    "configProfileName": "DefaultNonCompliance",
    "formating" : {
        "tablePresetName": "TableStyleLight15",
        "colors": {           
            "Notes": {
                "headerBackgroundColor": "D9D9D9",
                "attributeBackgroundColor": "",
                "headerForegroundColor": "",
                "attributeForegroundColor": ""
            },
            "*": {
                "headerBackgroundColor": "A6A6A6",
                "attributeBackgroundColor": "",
                "headerForegroundColor": "",
                "attributeForegroundColor": ""
            }
        },
        "fonts": {
            "*": {
                "font": "",
                "fontSize": "",
                "headerStyle": "",
                "attributeStyle": ""
                }
            },
        "rules": {
            "ErrorColoring": {
                "applyTo": [],
                "exclude": ["GeräteId", "Gerätename", "Benutzer-E-Mail", "Verändert", "Notes"],
                "range": "",
                "dynamicArgs": {
                    "colors": {
                        "green": "33CC33",
                        "red": "FF0000",
                        "NO_COLOR": None
                    }
                },
                "actions": {
                    "forNoError": {
                        "ruleType": "CellIsRule",
                        "condition": {
                            "operator": "equal",
                            "formula": '""'
                        },
                        "fill": "green"
                    },
                    "forNoActiveError": {
                        "ruleType": "FormulaRule",
                        "condition": {
                            "formula": '_xlfn.REGEXTEST(INDIRECT(ADDRESS(ROW(), COLUMN({colLetter}1))), "^\\s?\\[.*?\\]$")'
                        },
                        "fill": "green"
                    },
                    "forError": {
                        "ruleType": "CellIsRule",
                        "condition": {
                            "operator": "notEqual",
                            "formula": '""'
                        },
                        "fill": "red"
                    }
                }
            },
            "RowChangedIndicator": {
                "applyTo": ["Verändert"],
                "exclude": [],
                "range": "",
                "dynamicArgs": {
                    "colors": {
                        "green": "33CC33",
                        "red": "FF0000",
                        "blue": "00B0F0",
                        "NO_COLOR": None
                    }
                },
                "actions": {
                    "forNew": {
                        "ruleType": "CellIsRule",
                        "condition": {
                            "operator": "equal",
                            "formula": '"New"'
                        },
                        "fill": "green"
                    },
                    "forRemoved": {
                        "ruleType": "CellIsRule",
                        "condition": {
                            "operator": "equal",
                            "formula": '"Removed"'
                        },
                        "fill": "red"
                    },
                    "forChanged": {
                        "ruleType": "CellIsRule",
                        "condition": {
                            "operator": "notEqual",
                            "formula": '""'
                        },
                        "fill": "blue"
                    },
                    "forNone": {
                        "ruleType": "CellIsRule",
                        "condition": {
                            "operator": "equal",
                            "formula": '""'
                        },
                        "fill": "NO_COLOR"
                    }
                }
            }
        },
        "links": {
            "Device Overview": {
                "link": "https://intune.microsoft.com/#view/Microsoft_Intune_Devices/DeviceSettingsMenuBlade/~/properties/mdmDeviceId/{value}",
                "fillValuePattern": ConfigMagicValues.USE_CELL_VALUE.value, #TODO: maybe add an encoder for json for this https://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json/24482806#24482806
                "applyTo": ["Gerätename"],
                "exclude": []
            },
            "Email Shortcut": {
                "link": "https://teams.microsoft.com/l/chat/0/0?users={value}",
                "fillValuePattern": ConfigMagicValues.USE_CELL_VALUE.value,
                "applyTo": ["Benutzer-E-Mail"],
                "exclude": []
            }
        },
    },
    "columns": {
        "Windows": {
            "keepColumns": ['Gerätename', 'Benutzer-E-Mail', 'Verändert'],
            "excludeColumns": [],
            "keepRest": True,
            "extraColumns": ["Notes"],
            "columnOrderStart": ['GeräteId', 'Gerätename', 'Benutzer-E-Mail', 'Verändert', 'BitLocker', 'Encryption of data storage on device', 'Trusted Platform Module (TPM)', 'Minimum OS version', 'Firewall', 'Antivirus', 'Real-time protection', 'Microsoft Defender Antimalware security intelligence up-to-date', 'Enrolled user exists', 'Has a compliance policy assigned'],
            "columnOrderEnd": ['Is Active', 'Notes']
        },
        "*": {
            "keepColumns": [],
            "excludeColumns": [],
            "keepRest": True,
            "extraColumns": [],
            "columnOrderStart": [],
            "columnOrderEnd": []
        }
    },
    "mergeBehaviour": {
        "oldValues": {
            "keepOldValues": True,
            "oldValuesCount": 1
        }
    },
    "valueGen": {

    },
    "standartVals": {
        "wantedOS": ["Windows"],
        "deviceLinkSkip": False,
        "emailLinks": True,
        "keepDeviceIds": True,
        "compileCSV": False
    }
}