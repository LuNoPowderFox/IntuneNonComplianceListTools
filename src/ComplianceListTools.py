from modules import config, CompileComplianceList, MergeComplianceLists, clUtils, utils
from modules.dataStructures import ArgumentData, ReturnData, ReturnCodes, LaunchData, globData, GlobalData

if __name__ == "__main__":
    #TODO: make the output cleaner, displaying proper status messages
    mainParser = utils.createArgParser()

    argsP = mainParser.parse_args()

    # args = ArgumentData(launchData=argsP)
    # args = LaunchData(launchArgsRaw=argsP)
    globData = GlobalData(launchData=argsP)
    print(globData)
    exit(1)
    # print(args)
    #TODO: make the arg extraction
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