from modules.dataStructures import ArgumentData, ReturnData, ReturnCodes, gData, GlobalData, ProgramModes
from modules import utils

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

        print("Error Messages:")
        for arg in result.getArgCodeList():
            if not isinstance(result.getArgCode(arg), ReturnCodes):
                continue
            print(f"For argument '{arg}':")
            print(f"{result.getErrorMessage(arg)}\n")
        print("")
        exit(0)
    else:
        print(f"Operation '{result.mode}' failed!\n")

        print("Error Messages:")
        for arg in result.getArgCodeList():
            if not isinstance(result.getArgCode(arg), ReturnCodes):
                print(arg)
                print(result.getArgCode(arg))
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
    if extractedResult.returnCode == ReturnCodes.WARNING:
        if extractedResult.getArgCode("newFile") == ReturnCodes.NEEDS_COMPILE_INPUT_FILES or extractedResult.getArgCode("oldFile") == ReturnCodes.NEEDS_COMPILE_INPUT_FILES:
            extractedResult.setReturnCode(ReturnCodes.SUCCESS)
            tmpR = gData.globData.launchData.runFunc("autoCompileFunc", ArgumentData().createFromExisting(extractedResult, ProgramModes.COMPILE))
            for file in extractedResult.getReturnValue("compileFilesList"):
                if tmpR.returnCode == ReturnCodes.SUCCESS:
                    extractedResult.setReturnValue(name=file, value=tmpR.getReturnValue(file))
                else:
                    extractedResult.extractFromOther(tmpR)
    if not extractedResult.returnCode == ReturnCodes.SUCCESS:
        handleResult(extractedResult)
    args.extractFromReturnData(rData=extractedResult, extractMode=True, replaceExisting=True)

    result = gData.globData.launchData.runModeFunc(args=args)
    
    handleResult(result=result)
