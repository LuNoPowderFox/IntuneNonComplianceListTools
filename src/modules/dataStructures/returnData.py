import sys

from typing import List, Any
from .returnCodes import ReturnCodes
from .utils import AttributeLocation, ProgramModes
if 'argumentData' in sys.modules:
    from .argumentData import ArgumentData
# if 'gData' in sys.modules: # Circular imports are confusing...
from . import gData

class ReturnData():
    """
    Contains data only needed for returning

    ReturnCode: an ReturnCodes value, indicating status
    returnValues: a dict containing the return values
    errorMessages: a dict containing error messages for each faulty argument that was given to the function
    mode: The submode the program is running in (will be used, if main mode is GUI for example)
    funcArgs: a reference to the ArgumentData, the function was called with (maybe)
    """
    def __init__(self, funcArgs: ArgumentData | None = None, mode: ProgramModes = ProgramModes.UNSPECIFIED):
        self._returnCode: ReturnCodes = ReturnCodes.SUCCESS
        self._returnValues: dict = {}
        self._errorMessages: dict = {}
        self._funcArgs: ArgumentData = funcArgs
        self._argCodes: dict = {}
        self._mode: ProgramModes = mode

    @property
    def returnCode(self) -> ReturnCodes:
        return self._returnCode

    def setReturnCode(self, code: ReturnCodes) -> None:
        """
        Sets the return code

        :param ReturnCodes code: The code to set
        """
        self._returnCode = code

    @property
    def mode(self) -> str:
        return self._mode

    def setMode(self, mode: ProgramModes) -> None:
        """
        Sets the mode

        :param ProgramModes mode: The mode to set
        """
        self._mode = mode

    @property
    def funcArgs(self) -> ArgumentData:
        return self._funcArgs

    def getFuncArg(self, name: str) -> Any | None:
        """
        Returns the given function argument

        :param str name: the name of the argument
        :return: Either the value of the argument or None if non-existant
        :rtype: Any | None
        """
        if self._funcArgs is None:
            return None
        return self._funcArgs.getArg(name)

    def isInFuncArgs(self, name) -> bool:
        """
        Check whether the given value is existant within the function arguments
                
        :param str name: The name of the function argument
        :return: A boolean
        :rtype: bool
        """
        if self._funcArgs is None:
            return False
        return self._funcArgs.isInArgs(name)

    @property
    def returnValues(self):
        return self._returnValues

    def getReturnValueList(self) -> List:
        """
        Returns a list of all available return values
        """
        return self._returnValues.keys()

    def isInReturnValues(self, name: str) -> bool:
        """
        Check whether the given value is existant within the return values
        
        :param str name: The name of the return value
        :return: A boolean
        :rtype: bool
        """
        return name in self._returnValues.keys()

    def getReturnValue(self, name: str) -> Any | None:
        """
        Returns the wanted return value from the internal data  
        Return none if not found

        :param name: the name of the wanted return value
        :type name: str
        :return: The wanted return value or None if not found
        :rtype: Any | None
        """
        if not name in self._returnValues.keys():
            return None
        match self._returnValues[name]["location"]:
            case AttributeLocation.RETURN_VAL:
                return self._returnValues[name]["value"]
            case AttributeLocation.FUNC_ARGS:
                return self.getFuncArg(name)
            case AttributeLocation.LAUNCH_ARGS:
                return gData.globData.launchData.getLaunchArg(self._returnValues[name]["value"])
            case AttributeLocation.CONFIG:
                return gData.globData.config.getConfig(self._returnValues[name]["value"]["type"], self._returnValues[name]["value"]["path"], returnAsDict=False)

    def setReturnValue(self, name: str, value, configPath: str = "", location: AttributeLocation = AttributeLocation.RETURN_VAL) -> None:
        """
        Sets an return value  
        
        :param name: The name of the return value
        :type name: str
        :param value: either the value if location is RETURN_VAL or of ConfigTypes if location is CONFIG or the launch arg if locations is LAUNCH_ARG
        :type value: Any | ConfigTypes
        :param configPath: In case location is set to CONFIG, store this alongside the ConfigTypes
        :type configPath: str
        :param location: The actual place where the value is stored
        :type location: AttributeLocation
        """
        newValue = value
        match location:
                    case AttributeLocation.FUNC_ARGS:
                        if not self.isInFuncArgs(name):
                            raise AttributeError()
                    case AttributeLocation.LAUNCH_ARGS:
                        if not gData.globData.launchData.isInLaunchArgs(value):
                            raise AttributeError()
                    case AttributeLocation.CONFIG:
                        if not gData.globData.config.isInConfig(value, configPath):
                            raise AttributeError()
                        newValue = { "type": value, "path": configPath }

        self._returnValues[name] = { "location": location, "value": newValue }

    def extractFromOther(self, otherReturnData: ReturnData, extractMode: bool = False, inplace: bool = True) -> ReturnData | None:
        """
        Extract and merge the returnData attributes from otherReturnData to self  
        If duplicates are found, use the attributes from otherReturnData

        :param otherReturnData: the instance to extract the data from
        :type otherReturnData: RetunData
        :param bool extractMode: If this is set, also extract the mode fomr otherReturnData
        :param inplace: merge the data into self if set. otherwise return new instance (NOT IMPLEMENTED YET)
        :type inplace: bool
        :return: Either a new instance of ReturnData with the merged attributes or None
        :rtype: ReturnData | None
        """
        #TODO: make this actually work
        self._returnCode = otherReturnData._returnCode
        self._returnValues.update(otherReturnData._returnValues)
        self._argCodes.update(otherReturnData._argCodes)
        self._errorMessages.update(otherReturnData._errorMessages)

        if extractMode:
            self.setMode(otherReturnData.mode)

    def getArgCodeList(self) -> List:
        """
        Returns a list of all available arg codes
        """
        return self._argCodes.keys()

    def isInArgCodes(self, name: str) -> bool:
        """
        Checks whether the given argument is in the argcode list
        """
        return name in self.getArgCodeList()

    def getArgCode(self, name) -> ReturnCodes | None:
        """
        Returns the wanted argcode or None if not existant
        """
        if not self.isInArgCodes(name):
            return None
        return self._argCodes[name]

    def setArgCode(self, name: str, code: ReturnCodes) -> None:
        """
        Sets the return code for the specific argument
        """
        self._argCodes[name] = code

    @property
    def errorMessages(self):
        return self._errorMessages

    def getErrorMessageList(self) -> List:
        """
        Returns a list of all available entries from the error messages

        :return: A list of all error message entries
        :rtype: List
        """
        return self._errorMessages.keys()

    def isInErrorMessages(self, name: str) -> bool:
        """
        Check whether the given entry is existant within the error messages

        :param str name: The name of the entry
        :return: A boolean
        :rtype: bool
        """
        return name in self._errorMessages.keys()

    def getErrorMessage(self, name: str) -> str | None:
        """
        Return the error message for the given entry

        :param str name: The name of the entry of the error message
        :return: Either the error message or None if nonexistand
        :rtype: str | None 
        """
        if name in self._errorMessages.keys():
            return self._errorMessages[name]
        return None

    def setErrorMessage(self, name: str, value: str, appendIfExists: bool = True, appendSeperator: str = "") -> None:
        """
        Sets an error message for the specific argument

        :param str name: The name of the argument or error message
        :param str value: The error message to save
        :param bool appendIfExists: If this is set, append error messages to existing entries. If not, just replace the entry
        :param str appendSeperator: Determines, what will be put between the error messages if appended
        """
        if self.isInErrorMessages(name) and appendIfExists:
            self._errorMessages[name] += appendSeperator + value
        else:
            self._errorMessages[name] = value

    def __createArgumentData(self, argList: List | None = None, newMode: ProgramModes | None = None, extractMode: bool = True) -> ArgumentData:
        """
        Returns a new instance of ArgumentData generated from the ReturnData  
        Doesn't work yet because importing seems to be annoying...

        :params argList: If this is set, only extract the specified arguments
        :type argList: List | None
        :param newMode: Manually set the new mode
        :type newMode: ProgramModes | None
        :param extractMode: If this is set, also extract the mode set in rData. Only has an effect if newMode is not set
        :type extractMode: bool
        :return: A new instance of ArgumentData generated from the current instance of ReturnData
        :rtype: ArgumentData
        """
        newArgD = ArgumentData()
        return newArgD.extractFromReturnData(rData=self, valueList=argList, newMode=newMode, extractMode=extractMode)