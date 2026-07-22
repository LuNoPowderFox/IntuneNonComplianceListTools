import argparse
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from typing import List
from .formatExcel import formatExcel # as fE
from . import utils
import validators
import re

# Merge a new Compliance List into an existing one, updating it

# just check if the data has the DeviceId column
def checkHasDeviceIdColumn(df: pd.DataFrame) -> bool:
    if not 'GeräteId' in df:
        return False
    return True

# Check if the linklist has either of the possible deviceIdLink columns
def checkLinksHaveDeviceIdColumns(linkList: pd.DataFrame) -> bool:
    if checkHasDeviceIdColumn(linkList) or 'Gerätename' in linkList:
        return True
    return True

# Im starting to realize that this is stupid...
# might be a bit better now, idk, too sleep deprived xd
# Takes the output of getDeviceIds()
def checkHasDeviceIds(df: pd.DataFrame) -> bool:
    #if hasDeviceIdColumn:
    if not checkHasDeviceIdColumn(df):
        print(df)
        print("No Device Id")
        return False
    # Check if df has any data except "NO_DEVICE_ID"
    if len(df.loc[~df['GeräteId'].isin(["NO_DEVICE_ID"]),:]) == 0:
        return False
    return True
    
#TODO: maybe add an check on whether there is an 'GeräteId' column in the dataset, even if there aren't any links
# should even be possible in this function
def getDeviceIds(linkList: pd.DataFrame) -> pd.DataFrame | None:
    print("Trying to extract device ids...")
    if not checkLinksHaveDeviceIdColumns(linkList=linkList):
        # print("getDeviceIds(): checkHasDeviceIds(): False")
        return pd.DataFrame()
    deviceIdList: List = []
    deviceIds: pd.DataFrame = pd.DataFrame()
    idColumn = "GeräteId"
    if not checkHasDeviceIdColumn(linkList):
        # We just assume that the column 'Gerätename' otherwise contains the links
        idColumn = "Gerätename"
    for rowId, link in linkList[['RowId', idColumn]].values:
        #TODO: change this so it checks if it's actually the device url and not just any url
        if not validators.url(link) or link == "" or link is None:
            # print(f"'{link}' is not a valid url")
            # If there is no deviceId found, still fill the data with "NO_DEVICE_ID" to keep comparision working
            deviceIdList.append({'rowId': rowId, 'GeräteId': "NO_DEVICE_ID"})
        else:
            deviceIdList.append({'rowId': rowId, 'GeräteId': link.rsplit('/')[-1]})
        
    deviceIds = pd.DataFrame(deviceIdList)
    return deviceIds

def getHyperlinks(sheet, columnList: List | None = None) -> pd.DataFrame | None:
    print("Trying to extract all hyperlinks from worksheet...")
    columns: dict = {}
    tmpList: List = []
    linkList: pd.DataFrame = pd.DataFrame()

    header = [cell.value for cell in sheet[1]]
    for i, colName in enumerate(header):
        if columnList is None or colName in columnList:
            columns[i] = colName

    for row in sheet.rows:
        tmpRow: dict = {}
        if row[0].row == 1:
            continue
        for column in columns.keys():
            tmpRow['RowId'] = row[0].row-2
            if row[column].style == "Link" or row[column].style == "Hyperlink":
                tmpRow[columns[column]] = f"{row[column].hyperlink.target}"
                tmpRow[columns[column]] += f"#{row[column].hyperlink.location}" if row[column].hyperlink.location != None else ""
            else:
                tmpRow[columns[column]] = row[column].value
        tmpList.append(tmpRow)

    linkList = pd.DataFrame(tmpList).fillna("")
    return linkList

def addDeviceIdColumn(df: pd.DataFrame, deviceIds: pd.DataFrame | None = None, hasDeviceIds: bool = False) -> pd.DataFrame | None:
    if checkHasDeviceIdColumn(df):
        # first make sure that no column is empty so comparision doesn't break
        df.loc[df['GeräteId'] == "", 'GeräteId'] = "NO_DEVICE_ID"
        return df

    print("Adding DeviceId column...")
    newDf: pd.DataFrame = df
    newDf.insert(loc=0, column='GeräteId', value="")
    for i, row in df.iterrows():
        if hasDeviceIds:
            newDf.loc[df.index[i], 'GeräteId'] = deviceIds.loc[deviceIds.index[i], 'GeräteId']

    newDf.loc[df['GeräteId'] == "", 'GeräteId'] = "NO_DEVICE_ID"
    return newDf

# it's easier to just delete the column and recreate it later
def clearDeviceIdColumn(df: pd.DataFrame) -> pd.DataFrame:
    if not checkHasDeviceIdColumn(df):
        return df
    print("Dropping DeviceId column...")
    return df.drop('GeräteId', axis=1)

# add/rearange missing/missplaced columns, so they are in the wanted order for comparision
def prepareDfForComp(df: pd.DataFrame, columnList: List) -> pd.DataFrame:
    print("Removing unnecessary data...")
    for column in df.columns:
        #TODO: add an option to always keep one previous state and only remove it if the new state changed
        # Removes old data that was kept in previous file but is not needed (right now this still happens for both new and old data)
        df[column] = df[column].apply(lambda x: re.sub("\\s?\\[.*?\\]$", "", x) if re.search("\\s?\\[.*?\\]$", x) else x)
    print("Checking columns...")
    if df.columns.to_list() == columnList:
        print("Colums correct")
        return df
    print("Columns not yet correct, fixing...")
    fixedDf = pd.DataFrame(df, columns=columnList).fillna("")

    return fixedDf

# Compare both datasets to make sure they both have the same attributes, in the same order (otherwise comparision breaks)
def getNewColumnList(oldData: pd.DataFrame, newData: pd.DataFrame) -> List:
    print("Generating list of unique columns...")
    columnList: List = []
    columnListTmp: List = []
    oldColumns = oldData.columns
    newColumns = newData.columns
    for i in range(max(len(oldColumns), len(newColumns))):
        if not len(oldColumns) == len(newColumns):
            if len(oldColumns) > len(newColumns):
                columnListTmp.append(oldColumns[i])
                continue
            elif len(oldColumns) < len(newColumns):
                columnListTmp.append(newColumns[i])
                continue
        if oldColumns[i] == newColumns[i]:
            columnListTmp.append(oldColumns[i])
        else:
            columnListTmp.append(oldColumns[i])
            columnListTmp.append(newColumns[i])
    
    # Must have attributes, even if neither of the original datasets have them
    columnListTmp.append('GeräteId')
    columnListTmp.append('Gerätename')
    columnListTmp.append('Benutzer-E-Mail')
    columnListTmp.append('Verändert')

    [columnList.append(x) for x in columnListTmp if x not in columnList]
    return columnList

def compareOldData(oldData: pd.DataFrame, newData: pd.DataFrame, columnList: List, hasDeviceIds: bool = False) -> pd.DataFrame | None:
    print("Comparing Data...")
    resultData: pd.DataFrame = pd.DataFrame(columns=columnList)
    resultDataList: List = []
    #TODO: change compare to maybe ignore deviceId if not found
    # done by just filling the whole column with "NO_DEVICE_ID" during preperation 
    stillExistendDevices: List[tuple[int, int]] = [] # (oldIndex, newIndex)
    removedDevices: List[int] = [] # oldIndex
    newDevices: List[int] = [] # newIndex
    usedNewDevices: List[int] = [] # newIndex
    
    #TODO: fix the filtering, so that the compared values must not be different, even if they changed one of the attributes
    # if for example device name is the same but id and email not, save both seperately, email can be there multiple times tho
    # nvm, might already be the case
    for i, row in oldData.iterrows():
        deviceId, deviceName, userMail = row[['GeräteId', 'Gerätename', 'Benutzer-E-Mail']]
        #if newData.isin([deviceId, deviceName, userMail]).any().any():
        if  newData.index[(newData['GeräteId'] == deviceId) & (newData['Gerätename'] == deviceName) & (newData['Benutzer-E-Mail'] == userMail)].to_list() != []:
            newIndex = newData.index[(newData['GeräteId'] == deviceId) & (newData['Gerätename'] == deviceName) & (newData['Benutzer-E-Mail'] == userMail)].to_list()
            # it *should* usually never be empty, i think, i hope
            newIndex = newIndex[0] if len(newIndex) > 0 else None
            stillExistendDevices.append((i, newIndex))
            usedNewDevices.append(newIndex)
        else:
            removedDevices.append(i)

    for i, row in newData.iterrows():
        if i not in usedNewDevices:
            newDevices.append(i)

    print(f"Found {len(stillExistendDevices)} reaccuring datasets, " + 
          f"{len(newDevices)} new datasets and " + 
          f"{len(removedDevices)} removed datasets")

    tmpNewRow: dict

    print("Merging reacurring datasets...")
    for oldI, newI in stillExistendDevices:
        #TODO: add an asterix to changed columns
        # When there's an x in oldData it seems to be a str while newData is object
        # this seems to fix it by converting both into str it seems
        oldRow = oldData.loc[oldI].convert_dtypes()
        newRow = newData.loc[newI].convert_dtypes()

        tmpNewRow = oldRow.to_dict()
        
        if oldRow.loc[~(oldRow.index.isin(['Verändert', 'Notes']))].equals(newRow.loc[~(newRow.index.isin(['Verändert', 'Notes']))]):
        #if oldRow.loc[~oldRow.isin(['Verändert', 'Notes'])].eq(newRow.loc[~newRow.isin(['Verändert', 'Notes'])], fill_value="").all().all():
            if oldRow['Verändert'] != "Removed" and newRow['Verändert'] != "Removed":
                tmpNewRow['Verändert'] = ""
        else:
            tmpNewRow['Verändert'] = "X"
            if oldRow['Verändert'] == "Removed":
                tmpNewRow['Verändert'] = "New"
            diffs = oldRow.compare(newRow)
            
            for i, diff in diffs.iterrows():
                if diff.name in ('Notes', 'Verändert'):
                    continue
                tmpNewRow[diff.name] = f"{diff['other']} [{diff['self']}]"
            if oldRow['Notes'] and newRow['Notes']:
                tmpNewRow['Notes'] = f"{newRow['Notes']} [{oldRow['Notes']}]"
            elif oldRow['Notes'] and not newRow['Notes']:
                tmpNewRow['Notes'] = f"{oldRow['Notes']}"
            else:
                tmpNewRow['Notes'] = f"{newRow['Notes']}"
        resultDataList.append(tmpNewRow)

    print("Adding new datasets...")
    #TODO: maybe make the data stay longer (it'd currently get removed with the next merge)
    for newI in newDevices:
        newRow = newData.loc[newI]
        tmpNewRow = newRow.to_dict()
        tmpNewRow['Verändert'] = "New"
        resultDataList.append(tmpNewRow)

    print("Adding removed datasets...")
    # TODO: make sure that 'removed' stays in the columns
    for oldI in removedDevices:
        oldRow = oldData.loc[oldI]
        tmpNewRow = {'GeräteId': oldRow['GeräteId'], 'Gerätename': oldRow['Gerätename'], 'Benutzer-E-Mail': oldRow['Benutzer-E-Mail'], 'Verändert': "Removed", 'Notes': oldRow['Notes']}
        tmpColumnList = oldRow.index.to_list()
        tmpColumnList.remove("GeräteId")
        tmpColumnList.remove("Gerätename")
        tmpColumnList.remove("Benutzer-E-Mail")
        tmpColumnList.remove("Verändert")
        tmpColumnList.remove("Notes")
        for column in tmpColumnList:
            if oldRow[column] == "":
                continue
            # tmpNewRow[column] = f"[{oldRow[column]}]"
            tmpNewRow[column] = f"{oldRow[column]}"

        resultDataList.append(tmpNewRow)
    
    resultData = pd.DataFrame(resultDataList, columns=columnList)

    if not hasDeviceIds:
        resultData = clearDeviceIdColumn(resultData)

    return resultData

def _mergeComplianceLists(oldListPath: str, newListPath: str, wantedOS: str | List[str] = "Windows") -> dict | None:
    # 1. check which devices from oldData are also still in newData
    # 1.1 compare the problem columns, using newData as the newer state and update accordingly
    # 1.2 compare the notes from those devices and keep the new ones + maybe the old notes in brackets [] after that
    # 2. check which devices from oldData are not in newData
    # 2.1 set those devices from oldData to no problems (problem columns empty)
    # 2.2 keep the specific notes from those devices from oldData
    # 3. check which new Devices are found in newData
    # 3.1 keep those devices as is from newData
    # 3.2 keep the notes from those devices from newData^
    # 4 create column showing if the data changed
    result = {
        "ReturnCode": utils.ReturnCodes.SUCCESS,
        "returnValues": {

        },
        "args": {

        },
        "errorMessages": {
            
        }
    }
    mergedData: pd.DataFrame = None
    print(f"Merging data for OS '{wantedOS}'...")
    
    oldWb = load_workbook(oldListPath)
    newWb = load_workbook(newListPath)
    
    if wantedOS in oldWb:
        oldData = pd.read_excel(oldListPath, sheet_name=wantedOS, engine="openpyxl").fillna('')
    if wantedOS in newWb:
        newData = pd.read_excel(newListPath, sheet_name=wantedOS, engine="openpyxl").fillna('')
    
    if wantedOS not in oldWb and wantedOS in newWb:
        print(f"OS '{wantedOS}' only found in new data...")
        result["returnValues"]["mergedData"] = newData
        return result
    if wantedOS not in newWb and wantedOS in oldWb:
        print(f"OS '{wantedOS}' only found in old data...")
        result["returnValues"]["mergedData"] = oldData
        return result
    if wantedOS not in oldWb and wantedOS not in newWb:
        result["ReturnCode"] = utils.ReturnCodes.COMPLIANCE_LIST_INVALID_OS
        return result
    
    oldSheet = oldWb[wantedOS]
    newSheet = newWb[wantedOS]

    oldLinks = getHyperlinks(sheet=oldSheet)
    newLinks = getHyperlinks(sheet=newSheet)

    oldDeviceIds = getDeviceIds(linkList=oldLinks)
    newDeviceIds = getDeviceIds(linkList=newLinks)

    hasDeviceIds = (checkHasDeviceIds(oldDeviceIds) & checkHasDeviceIds(newDeviceIds))

    if not hasDeviceIds:
        oldData = clearDeviceIdColumn(oldData)
        newData = clearDeviceIdColumn(newData)

    oldData = addDeviceIdColumn(oldData, deviceIds=oldDeviceIds, hasDeviceIds=hasDeviceIds)
    newData = addDeviceIdColumn(newData, deviceIds=newDeviceIds, hasDeviceIds=hasDeviceIds)

    columnList = getNewColumnList(oldData=oldData, newData=newData)

    oldData = prepareDfForComp(oldData, columnList=columnList)
    newData = prepareDfForComp(newData, columnList=columnList)

    mergedData = compareOldData(oldData=oldData, newData=newData, columnList=columnList, hasDeviceIds=hasDeviceIds)

    result["returnValues"]["mergedData"] = mergedData

    return result

def mergeComplianceLists(pArgs: argparse.Namespace) -> dict | None:
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

    args = utils.extractMergeArgs(pArgs=pArgs)

    neededArgs: set = {"oldFile", "newFile", "mergedFile", "compileCSV", "wantedOS", "deviceLinkSkip", "emailLinks", "keepDeviceIds"}
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

    if not "args" in args:
        result["ReturnCode"] = utils.ReturnCodes.NO_ARGS_GIVEN
        return result
    elif not any(arg in neededArgs for arg in args["args"].keys()):
        result["ReturnCode"] = utils.ReturnCodes.MISSING_ARGS
        return result

    oldListPath: str = args["args"]["oldFile"]
    newListPath: str = args["args"]["newFile"]
    outputPath: str = args["args"]["mergedFile"]
    wantedOS: List[str] = args["args"]["wantedOS"]
    makeDeviceLinks: bool = not args["args"]["deviceLinkSkip"]
    makeEmailLinks: bool = args["args"]["emailLinks"]
    keepDeviceIdColumn: bool = args["args"]["keepDeviceIds"]
    
    tmp = {}

    for os in wantedOS:
        tmpResult = _mergeComplianceLists(oldListPath=oldListPath, newListPath=newListPath, wantedOS=os)
        print("")

        if tmpResult["ReturnCode"] == utils.ReturnCodes.COMPLIANCE_LIST_INVALID_OS:
            result["ReturnCode"] = utils.ReturnCodes.PARTIAL_SUCCESS
            result["args"]["wantedOS"] = utils.ReturnCodes.COMPLIANCE_LIST_INVALID_OS
            if "wantedOS" not in result["errorMessages"].keys():
                result["errorMessages"]["wantedOS"] = f"The following OS's are not valid: {os}"
            else:
                result["errorMessages"]["wantedOS"] += f", {os}"
        else:
            tmp[os] = tmpResult["returnValues"]["mergedData"]

    if len(tmp.keys()) == 0:
        result["ReturnCode"] = utils.ReturnCodes.ERROR
        return result

    with pd.ExcelWriter(outputPath) as oFile:
        for os in tmp.keys():
            tmp[os].to_excel(oFile, index=False, sheet_name=os)
    for os in tmp.keys():
        formatExcel(outputPath, createDeviceLinks=makeDeviceLinks, createEmailLinks=makeEmailLinks, keepDeviceIdColumn=keepDeviceIdColumn, sheetName=os)
        print("")
    
    #TODO: add more error handling during the compile
    result["returnValues"]["mergedFile"] = outputPath
    return result
