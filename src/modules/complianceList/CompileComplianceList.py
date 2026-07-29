import argparse
import pandas as pd
from .formatExcel import formatExcel
from . import utils
from typing import List
import sys
import copy

from ..dataStructures import gData, ArgumentData, ReturnData, ReturnCodes

def addToColumnOder(columnOrder, problemList, problem):
    if problem in problemList and problem not in columnOrder:
        columnOrder.append(problem)

def processInput(pDF: pd.DataFrame, wantedOS: str) -> dict | ReturnData | pd.DataFrame:
    # to not remove stuff from the original df
    df = copy.deepcopy(pDF)
    processedList: List = []
    processedData: pd.DataFrame
    hasDeviceID: bool = False
    rData = ReturnData()
    result = {
        "ReturnCode": utils.ReturnCodes.SUCCESS,
        "returnValues": {

        },
        "args": {

        },
        "errorMessages": {
            
        }
    }

    if wantedOS not in pDF['OS'].values:
        result["ReturnCode"] = utils.ReturnCodes.COMPLIANCE_LIST_INVALID_OS
        rData.setReturnCode(ReturnCodes.COMPLIANCE_LIST_INVALID_OS)
        return rData
        return result

    for x in df.index:
        if wantedOS not in df.loc[x, "OS"]:
            df.drop(x, inplace=True)

    if df.shape[0] == 0:
        sys.exit(f"No entries for the OS '{wantedOS}' found. Exiting...")

    if 'DeviceId' in df:
        print("DeviceId column found, trying to add overview links...")
        hasDeviceID = True
    else:
        print("No Device Id column found")
        df['DeviceId'] = ""
    

    # There seem to be 2 devices with neither a DeviceName nor UserMail but with an DeviceId
    # This seems to fix it
    df.fillna({'UserEmail': "NO_EMAIL", 'DeviceName': 'NO_DEVICE_NAME'}, inplace=True)

    problems = df["SettingNm_loc"].unique()
    for (deviceName, userEmail, deviceId), group in df.groupby(['DeviceName', 'UserEmail', 'DeviceId']):
        if hasDeviceID:
            row = {'GeräteId': deviceId,'Gerätename': deviceName, 'Benutzer-E-Mail': userEmail, 'Verändert': ""}
        else:
            row = {'Gerätename': deviceName, 'Benutzer-E-Mail': userEmail, 'Verändert': ""}
        #deviceProblems = set(group['SettingNm_loc'])
        deviceProblems = group.groupby('SettingNm_loc')['ErrorCodeString'].apply(list).to_dict()

        for problem in problems:
            if problem in deviceProblems.keys():
                if not pd.isna(deviceProblems[problem]):
                    row[problem] = f"Fehler ({int(deviceProblems[problem][0])})"
                else:
                    row[problem] = "Fehler"
            else:
                row[problem] = ""
        processedList.append(row)

    #TODO: Maybe make this look better and make customisation better
    # Custom order stuff, not needed
    if hasDeviceID:
        columnOrder = ['GeräteId', 'Gerätename', 'Benutzer-E-Mail', 'Verändert']
    else:
        columnOrder = ['Gerätename', 'Benutzer-E-Mail', 'Verändert']

    # Windows stuff
    addToColumnOder(columnOrder, problemList=problems, problem='BitLocker')
    addToColumnOder(columnOrder, problemList=problems, problem='Encryption of data storage on device')
    addToColumnOder(columnOrder, problemList=problems, problem='Trusted Platform Module (TPM)')
    addToColumnOder(columnOrder, problemList=problems, problem='Minimum OS version')
    addToColumnOder(columnOrder, problemList=problems, problem='Firewall')
    addToColumnOder(columnOrder, problemList=problems, problem='Antivirus')
    addToColumnOder(columnOrder, problemList=problems, problem='Real-time protection')
    addToColumnOder(columnOrder, problemList=problems, problem='Microsoft Defender Antimalware security intelligence up-to-date')
    addToColumnOder(columnOrder, problemList=problems, problem='Enrolled user exists')
    addToColumnOder(columnOrder, problemList=problems, problem='Has a compliance policy assigned')


    # Add the remaining problems
    for problem in problems:
        if problem == 'Is active':
            continue
        addToColumnOder(columnOrder=columnOrder, problemList=problems, problem=problem)

    # So this column is the last
    addToColumnOder(columnOrder, problemList=problems, problem='Is active')

    processedData = pd.DataFrame(processedList)
    processedData = processedData[columnOrder]
    result["returnValues"]["processedData"] = processedData
    rData.setReturnValue(name="processedData", value=processedData)
    return rData
    return result

def convertDataToExcel(inputFile: str, outputFile: str, wantedOS: List, makeDeviceLinks: bool = True, 
                       makeEmailLinks: bool = False, keepDeviceIdColumn: bool = False) -> dict | ReturnData | None:
    df = pd.read_csv(inputFile)
    rData = ReturnData()
    result = {
        "ReturnCode": utils.ReturnCodes.SUCCESS,
        "args": {

        },
        "errorMessages": {

        }
    }
    tmp = {}

    for os in wantedOS:
        tmpResult = processInput(df, os)

        if tmpResult.returnCode == ReturnCodes.COMPLIANCE_LIST_INVALID_OS:
            result["ReturnCode"] = utils.ReturnCodes.PARTIAL_SUCCESS
            rData.setReturnCode(ReturnCodes.PARTIAL_SUCCESS)
            result["args"]["wantedOS"] = utils.ReturnCodes.COMPLIANCE_LIST_INVALID_OS
            rData.setArgCode("wantedOS", ReturnCodes.COMPLIANCE_LIST_INVALID_OS)
            if not rData.isInErrorMessages("wantedOS"):
                rData.setErrorMessage("wantedOS", f"The following OS's are not valid: {os}")
                result["errorMessages"]["wantedOS"] = f"The following OS's are not valid: {os}"
            else:
                rData.setErrorMessage("wantedOS", f", {os}")
                result["errorMessages"]["wantedOS"] += f", {os}"
        else:
            tmp[os] = tmpResult.getReturnValue("processedData")
            # tmp[os] = tmpResult["returnValues"]["processedData"]

    if len(tmp.keys()) == 0:
        result["ReturnCode"] = utils.ReturnCodes.ERROR
        rData.setReturnCode(ReturnCodes.ERROR)
        return rData
        return result

    with pd.ExcelWriter(outputFile) as oFile:
        for os in tmp.keys():
            tmp[os].to_excel(oFile, index=False, sheet_name=os)
    for os in tmp.keys():
        formatExcel(outputFile, createDeviceLinks=makeDeviceLinks, createEmailLinks=makeEmailLinks, keepDeviceIdColumn=keepDeviceIdColumn, sheetName=os)

    return rData
    return result

def compileComplianceList(args: ArgumentData) -> ReturnData:
    rData = ReturnData(funcArgs=args, mode=args.getMode())
    neededArgs: set = {"inputFile", "outputFile", "wantedOS", "deviceLinkSkip", "emailLinks", "keepDeviceIds"}

    # if not any(args.isInArgs(arg) for arg in args.getArgsList()):
    if not any(args.isInArgs(arg) for arg in neededArgs):
        rData.setReturnCode = ReturnCodes.MISSING_ARGS
        return rData

    inputFile: str = args.getArg("inputFile")
    outputFile: str = args.getArg("outputFile")
    wantedOS: List[str] = args.getArg("wantedOS")
    makeDeviceLinks: bool = not args.getArg("deviceLinkSkip")
    makeEmailLinks: bool = args.getArg("emailLinks")
    keepDeviceIdColumn: bool = args.getArg("keepDeviceIds")

    tmp = convertDataToExcel(inputFile=inputFile, outputFile=outputFile, wantedOS=wantedOS, makeDeviceLinks=makeDeviceLinks, makeEmailLinks=makeEmailLinks, keepDeviceIdColumn=keepDeviceIdColumn)
    rData.extractFromOther(tmp)
    print(tmp)
    
    #TODO: add more error handling during the compile
    if rData.returnCode == ReturnCodes.SUCCESS:
        rData.setReturnValue(name="outputFile", value=outputFile)

    return rData

def compileComplianceListOld(pArgs: argparse.Namespace | dict | ArgumentData | None) -> dict | ReturnData | None:
    """Return dictionary structure:
    {
        "ReturnCode": (ReturnCode),
        "Mode": (Mode, the program is running in),
        "returnValues": {
            (Value): (Value or ReturnCode)        
        },
        "args": { (if needed)
            (Argname): (ReturnCode)
        },
        "errorMessages": { (if needed)
            (Argname): (Error message)
        }    
    }
    """
    if not type(pArgs) == dict:
        args = utils.extractCompileArgs(pArgs=pArgs)
    else:
        args = pArgs

    neededArgs: set = {"inputFile", "outputFile", "wantedOS", "deviceLinkSkip", "emailLinks", "keepDeviceIds"}
    result = {
        "ReturnCode": utils.ReturnCodes.SUCCESS,
        "Mode": args["Mode"],
        "returnValues": {},
        "args": {},
        "errorMessages": {}
    }

    if not args["ReturnCode"] == utils.ReturnCodes.SUCCESS:
        result["ReturnCode"] = args["ReturnCode"]
        result["args"] = args["args"]
        result["errorMessages"] = args["errorMessages"]
        return result

    # print(f"args: {args}")

    if not "args" in args:
        result["ReturnCode"] = utils.ReturnCodes.NO_ARGS_GIVEN
        return result
    elif not any(arg in neededArgs for arg in args["args"].keys()):
        result["ReturnCode"] = utils.ReturnCodes.MISSING_ARGS
        return result

    inputFile: str = args["args"]["inputFile"]
    outputFile: str = args["args"]["outputFile"]
    wantedOS: List[str] = args["args"]["wantedOS"]
    makeDeviceLinks: bool = not args["args"]["deviceLinkSkip"]
    makeEmailLinks: bool = args["args"]["emailLinks"]
    keepDeviceIdColumn: bool = args["args"]["keepDeviceIds"]
    
    tmp = convertDataToExcel(inputFile=inputFile, outputFile=outputFile, wantedOS=wantedOS, makeDeviceLinks=makeDeviceLinks, makeEmailLinks=makeEmailLinks, keepDeviceIdColumn=keepDeviceIdColumn)
    result = result | tmp
    
    #TODO: add more error handling during the compile
    if result["ReturnCode"] == utils.ReturnCodes.SUCCESS:
        result["returnValues"]["outputFile"] = outputFile
    return result
