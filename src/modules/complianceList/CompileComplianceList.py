import argparse
import pandas as pd
from .formatExcel import formatExcel #as fE
from . import utils
from typing import List
import getopt, sys
import re, copy

def addToColumnOder(columnOrder, problemList, problem):
    if problem in problemList and problem not in columnOrder:
        columnOrder.append(problem)

def processInput(pDF: pd.DataFrame, wantedOS: str) -> dict | pd.DataFrame:
    # to not remove stuff from the original df
    df = copy.deepcopy(pDF)
    processedList: List = []
    processedData: pd.DataFrame
    hasDeviceID: bool = False
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
    #TODO: if deviceName/ID/email are empty, also add an index number to the string to leave them unique, so they don't get grouped
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
    return result

# TODO: return false if compile fails
def convertDataToExcel(inputFile: str, outputFile: str, wantedOS: List, makeDeviceLinks: bool = True, 
                       makeEmailLinks: bool = False, keepDeviceIdColumn: bool = False) -> dict | None:
    df = pd.read_csv(inputFile)
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

        if tmpResult["ReturnCode"] == utils.ReturnCodes.COMPLIANCE_LIST_INVALID_OS:
            result["ReturnCode"] = utils.ReturnCodes.PARTIAL_SUCCESS
            result["args"]["wantedOS"] = utils.ReturnCodes.COMPLIANCE_LIST_INVALID_OS
            if "wantedOS" not in result["errorMessages"].keys():
                result["errorMessages"]["wantedOS"] = f"The following OS's are not valid: {os}"
            else:
                result["errorMessages"]["wantedOS"] += f", {os}"
        else:
            tmp[os] = tmpResult["returnValues"]["processedData"]

    if len(tmp.keys()) == 0:
        result["ReturnCode"] = utils.ReturnCodes.ERROR
        return result

    with pd.ExcelWriter(outputFile) as oFile:
        for os in tmp.keys():
            tmp[os].to_excel(oFile, index=False, sheet_name=os)
    for os in tmp.keys():
        formatExcel(outputFile, createDeviceLinks=makeDeviceLinks, createEmailLinks=makeEmailLinks, keepDeviceIdColumn=keepDeviceIdColumn, sheetName=os)

    return result

# # Check the args and run the compile
# # Return output File path
# def checkArgs(inputFilePath: str, outputFilePath: str, wantedOS: str | List[str] | None, makeDeviceLinks: bool = True, 
#                        makeEmailLinks: bool = False, keepDeviceIdColumn: bool = False) -> str | bool | None:
    
#     inputFile = inputFilePath
#     outputFile = outputFilePath

#     if inputFile is None:
#         sys.exit("Error, no input file given! Please set the input file with '-i' or '--InputFile'. \nFor more help use '-h' or '--Help'")
#         inputFile = "TestInput\\NoncompliantDevicesAndSettingsV3_6453c22b-7b10-4194-adc9-8ee459d924bf.csv"
#     elif not inputFile.endswith(".csv"):
#         sys.exit("Error, given input file is possibly not correct file type!\nPlease give a file with the '.csv' extension")
#     if outputFile is None:
#         outputFile = re.sub(".csv$", ".xlsx", inputFile)
#         print(f"Set output file to '{outputFile}'")
#     if wantedOS is None:
#         #TODO: allow multiple OS's
#         wantedOS = "Windows"

#     convertDataToExcel(inputFile=inputFile, outputFile=outputFile, wantedOS=wantedOS, makeDeviceLinks=makeDeviceLinks, makeEmailLinks=makeEmailLinks, keepDeviceIdColumn=keepDeviceIdColumn)
#     if outputFilePath is None:
#         return outputFile

def compileComplianceList(pArgs: argparse.Namespace) -> dict | None:
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

    args = utils.extractCompileArgs(pArgs=pArgs)

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

# if __name__ == "__main__":
#     args = sys.argv[1:]
#     options = "hi:o:w:dek"
#     long_options = ["Help", "InputFile=", "OutputFile=", "WantedOS=", "DeviceLinksSkip", "EmailLinks", "KeepDeviceIds"]

#     inputFilePath: str = None
#     outputFilePath: str = None
#     wantedOS: str = None
#     makeDeviceLinks = True
#     makeEmailLinks = False
#     keepDeviceIdColumn = False

#     try:
#         arguments, values = getopt.getopt(args, options, long_options)
#         if len(arguments) == 0:
#             print("No arguments given, displaying help and exiting...")
#             utils.showCompileHelp()
#             exit(0)
#         for currentArg, currentVal in arguments:
#             if currentArg in ("-h", "--Help"):
#                 print("Showing Help")
#                 utils.showCompileHelp()
#                 exit(0)
#             elif currentArg in ("-i", "--InputFile"):
#                 inputFilePath = currentVal
#             elif currentArg in ("-o", "--Output"):
#                 outputFilePath = currentVal
#             elif currentArg in ("-w", "--WantedOS"):
#                 wantedOS = currentVal
#             elif currentArg in ("-d", "--DeviceLinkSkip"):
#                 makeDeviceLinks = False
#             elif currentArg in ("-e", "--EmailLinks"):
#                 makeEmailLinks = True
#             elif currentArg in ("-k", "--KeepDeviceIds"):
#                 keepDeviceIdColumn = True
#     except getopt.error as err:
#         print(str(err))

#     # if inputFilePath is None:
#     #     sys.exit("Error, no input file given! Please set the input file with '-i' or '--InputFile'. \nFor more help use '-h' or '--Help'")
#     #     inputFilePath = "TestInput\\NoncompliantDevicesAndSettingsV3_6453c22b-7b10-4194-adc9-8ee459d924bf.csv"
#     # elif not inputFilePath.endswith(".csv"):
#     #     sys.exit("Error, given input file is possibly not correct file type!\nPlease give a file with the '.csv' extension")
#     # if outputFilePath is None:
#     #     outputFilePath = re.sub(".csv$", ".xlsx", inputFilePath)
#     #     print(f"Set output file to '{outputFilePath}'")
#     # if wantedOS is None:
#     #     wantedOS = "Windows"

#     # convertDataToExcel(inputFilePath, outputFilePath, wantedOS=wantedOS, makeDeviceLinks=makeDeviceLinks, makeEmailLinks=makeEmailLinks, keepDeviceIdColumn=keepDeviceIdColumn)
    
#     checkArgs(inputFilePath, outputFilePath, wantedOS=wantedOS, makeDeviceLinks=makeDeviceLinks, makeEmailLinks=makeEmailLinks, keepDeviceIdColumn=keepDeviceIdColumn)