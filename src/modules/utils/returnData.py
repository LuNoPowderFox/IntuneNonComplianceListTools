from typing import List
from . import ReturnCodes

class ReturnData():
    """
    Contains data only needed for returning

    ReturnCode: an ReturnCodes value, indicating status
    returnValues: a dict containing the return values
    errorMessages: a dict containing error messages for each faulty argument that was given to the function
    """
    def __init__(self):
        self._returnCode: ReturnCodes = ReturnCodes.SUCCESS
        self._mode: str = ""
        self._returnValues: dict = {}
        self._errorMessages: dict = {}

    @property
    def returnCode(self) -> ReturnCodes:
        return self._returnCode

    def setReturnCode(self, code: ReturnCodes) -> None:
        self._returnCode = code

    @property
    def mode(self) -> str:
        return self._mode

    def setMode(self, mode: str) -> None:
        self._mode = mode

    @property
    def returnValues(self):
        return self._returnValues

    def getReturnValueList(self) -> List:
        return self._returnValues.keys()

    def isInReturnValues(self, name: str) -> bool:
        return name in self._returnValues.keys()

    def getReturnValue(self, name: str):
        if name in self._returnValues.keys():
            return self._returnValues[name]
        return None

    def setReturnValue(self, name: str, value) -> None:
        self._returnValues[name] = value

    @property
    def errorMessages(self):
        return self._errorMessages

    def getErrorMessageList(self) -> List:
        return self._errorMessages.keys()

    def isInErrorMessages(self, name: str) -> bool:
        return name in self._errorMessages.keys()

    def getErrorMessage(self, name: str):
        if name in self._errorMessages.keys():
            return self._errorMessages[name]
        return None

    def setErrorMessage(self, name: str, value, appendIfExists: bool = True, appendSeperator: str = " ") -> None:
        if self.isInErrorMessages(name) and appendIfExists:
            self._errorMessages[name] += appendSeperator + value
        else:
            self._errorMessages[name] = value