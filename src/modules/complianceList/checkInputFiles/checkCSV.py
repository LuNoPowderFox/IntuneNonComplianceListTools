from ...dataStructures import ArgumentData, ReturnData, ReturnCodes, gData, AttributeLocation

from typing import List
import pandas as pd

def _getOSList(inputData: pd.DataFrame) -> List:
    # This assumes that _checkAttributes has been run already and that there are rows existing
    return inputData['OS'].unique()

def _checkAttributes(inputData: pd.DataFrame) -> ReturnData:
    rData = ReturnData()

    return rData

def checkCSV(args: ArgumentData) -> ReturnData:
    """
    Check the given .csv file for usability/validity

    Needed arguments (in argumentData):
    inputFile: str              - The name of the input file
    
    Given return values:
    canCompile: bool            - Is the data usable for compile or not
    possibleProblemsList: List  - A list of all found problems
    osList: List                - A list of all found OS's
    hasDeviceIDs: bool          - Does the data have an deviceID attribute (Intune device ID)

    :param args: The set of arguments
    :type args: ArgumentData
    :return: The set of return values
    :rtype: ReturnData
    """
    rData = ReturnData(funcArgs=ArgumentData)

    return rData