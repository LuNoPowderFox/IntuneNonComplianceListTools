from modules.dataStructures import ArgumentData, ReturnData, ReturnCodes, LaunchData, gData, GlobalData
from modules import config, CompileComplianceList, MergeComplianceLists, clUtils, utils

def handleResult(result: ReturnData) -> None:
    if result.returnCode == ReturnCodes.SUCCESS:
        print(f"Operation '{result.mode}' was successful\n")
        if result.mode == "Help":
            exit(0)
        
        print("Outputed file to: ", end="")
        if result.isInReturnValues("outputFile"):
            print(f"'{result.getReturnValue("outputFile")}'")
        elif result.isInReturnValues("mergedFile"):
            print(f"'{result.getReturnValue("mergedFile")}'")
        else:
            print("Error, output file path not found!")
        print("")
        exit(0)
    elif result.returnCode == ReturnCodes.PARTIAL_SUCCESS:
        print(f"Operation '{result.mode}' was partially successful\n")
        if result.mode == "Help":
            exit(0)
        
        print("Outputed file to: ", end="")
        if result.isInReturnValues("outputFile"):
            print(f"'{result.getReturnValue("outputFile")}'")
        elif result.isInReturnValues("mergedFile"):
            print(f"'{result.getReturnValue("mergedFile")}'")
        else:
            print("Error, output file path not found!")
        print("")

        print("Error Messages")
        for arg in result.getArgCodeList():
            if not isinstance(result.getArgCode(arg), ReturnCodes):
                continue
            print(f"For argument '{arg}':")
            print(f"{result.getErrorMessage(arg)}\n")
        print("")
        exit(0)
    else:
        print(f"Operation '{result.mode}' failed!\n")

        print("Error Messages")
        for arg in result.getArgCodeList():
            if not isinstance(result.getArgCode(arg), ReturnCodes):
                continue
            print(f"For argument '{arg}':")
            print(f"{result.getErrorMessage(arg)}\n")

        exit(1)

if __name__ == "__main__":
    #TODO: make the output cleaner, displaying proper status messages
    mainParser = utils.createArgParser()

    argsP = mainParser.parse_args()

    gData.globData = GlobalData(launchData=argsP)
    args = ArgumentData()
    extractedResult = gData.globData.launchData.runExtractFunc()
    if not extractedResult.returnCode == ReturnCodes.SUCCESS:
        handleResult(extractedResult)
    args.extractFromReturnData(rData=extractedResult, extractMode=True, replaceExisting=True)
    print(args.args)

    result = gData.globData.launchData.runModeFunc(args=args)
    
    handleResult(result=result)

    # Will be removed in cleanup
    exit(0)

    result = argsP.func(argsP)
    if result["ReturnCode"] == clUtils.ReturnCodes.SUCCESS:
        print(f"Operation '{result["Mode"]}' was successful\n")
        if result["Mode"] == "Help":
            exit(0)
        
        print("Outputed file to: ", end="")
        if "outputFile" in result["returnValues"].keys():
            print(f"'{result["returnValues"]["outputFile"]}'")
        elif "mergedFile" in result["returnValues"].keys():
            print(f"'{result["returnValues"]["mergedFile"]}'")
        else:
            print("Error, output file path not found!")
        print("")
        exit(0)
    elif result["ReturnCode"] == clUtils.ReturnCodes.PARTIAL_SUCCESS:
        print(f"Operation '{result["Mode"]}' was partially successful\n")
        if result["Mode"] == "Help":
            exit(0)
        
        print("Outputed file to: ", end="")
        if "outputFile" in result["returnValues"].keys():
            print(f"'{result["returnValues"]["outputFile"]}'")
        elif "mergedFile" in result["returnValues"].keys():
            print(f"'{result["returnValues"]["mergedFile"]}'")
        else:
            print("Error, output file path not found!")
        print("")

        print("Error Messages")
        for arg in result["args"].keys():
            if not isinstance(result["args"][arg], clUtils.ReturnCodes):
                continue
            print(f"For argument '{arg}':")
            print(f"{result["errorMessages"][arg]}\n")
        print("")
        exit(0)
    else:
        print(f"Operation '{result["Mode"]}' failed!\n")

        print("Error Messages")
        for arg in result["args"].keys():
            if not isinstance(result["args"][arg], clUtils.ReturnCodes):
                continue
            print(f"For argument '{arg}':")
            print(f"{result["errorMessages"][arg]}\n")

        exit(1)