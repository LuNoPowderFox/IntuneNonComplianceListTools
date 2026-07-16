from modules import config, CompileComplianceList, MergeComplianceLists, clUtils, utils
import argparse

if __name__ == "__main__":
    mainParser = utils.createArgParser()

    argsP = mainParser.parse_args()
    result = argsP.func(argsP)
    # print(args)
    print(result)