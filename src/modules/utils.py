from typing import List

from modules import clUtils, MergeComplianceLists, CompileComplianceList
from modules.complianceList import compileComplianceList, mergeCompileList
from modules.config import Config
from .dataStructures import ReturnData, ArgumentData, AttributeLocation, ReturnCodes, gData, ProgramModes
import argparse

def emptyFunc(tmp: Any | None = None) -> None | ReturnData:
    return ReturnData()
    ...

def createHelpParser(parser: argparse.ArgumentParser | None = None) -> None:
    #TODO: make the help list better
    parser.add_argument(
                        dest="helpMode", 
                        choices=["Tools", "Help", "Compile", "Merge", "GUI"],
                        nargs="?",
                        default="Help"
                        )

def handleHelp(args: ArgumentData | None = None) -> ReturnData | None:
    # args = vars(pArgs)
    parserList = None
    helpMode = ""

    #TODO: fix this properly

    # if args.isInArgs("parserList"):
    if gData.globData.launchData.isInLaunchArgs("parserList"):
        # parserList = args.getArg("parserList")
        parserList = gData.globData.launchData.getLaunchArg("parserList")
    # if args.isInArgs("helpMode"):
    if gData.globData.launchData.isInLaunchArgs("helpMode"):
        # helpMode = args.getArg("helpMode")
        helpMode = gData.globData.launchData.getLaunchArg("helpMode")

    if helpMode in parserList.keys():
        parserList[helpMode].print_help()
    else:
        parserList["Help"].print_help()

    return ReturnData(mode=ProgramModes.HELP)

def createGuiParser(parser: argparse.ArgumentParser | None = None) -> None:
    ...

def createArgParser() -> argparse.ArgumentParser | None:
    mainParser = argparse.ArgumentParser(
                            prog="ComplianceListTools", 
                            description="A set of tools to process exported .csv lists of Intune's noncompliant devices report into a more usable format and be able to merge lists together.",
                            epilog="Created by LuNoPowderFox https://github.com/LuNoPowderFox/IntuneNonComplianceListTools",
                            allow_abbrev=False,
                            add_help=False
                            )
    mainParser.add_argument(
                            "-h", "--help",
                            action="help",
                            help="Show help message and exit the program"
                            )
    
    mainParser.set_defaults(config=Config())

    commonOptions = argparse.ArgumentParser("General options", description="Options, that are for setting the general behaviour of the program")
    generalOptions = commonOptions.add_argument_group("General options", description="Options, that are for setting the general behaviour of the program")
    #TODO: only add -s to GUI mode
    generalOptions.add_argument(
                            "-s", "--SettingsFile", 
                            dest="settingsFile",
                            help="Use non-default path for settings file (Default is '...')"
                            )
    
    generalOptions.add_argument(
                            "-g", "--GUI",
                            dest="useGUI",
                            action="store_true",
                            help="Launch the program as a GUI if needed modules are found and parse the rest of the arguments"
                            )
    
    sharedListOptions = commonOptions.add_argument_group("Shared list options", description="Options, that are both used for Compiling and for Merging")
    sharedListOptions.add_argument(
                        "-w", "--WantedOs",
                        dest="wantedOS",
                        nargs="+",
                        action="extend",
                        help="The OS you want to compile the data for. Default is 'Windows'"
                        )
    sharedListOptions.add_argument(
                        "-d", "--DeviceLinkSkip",
                        dest="deviceLinkSkip",
                        action="store_true",
                        help="Skip the creation of the device overview links"
                        )
    sharedListOptions.add_argument(
                        "-e", "--EmailLinks",
                        dest="emailLinks",
                        action="store_true",
                        help="Convert Emails into teams chat links"
                        )
    sharedListOptions.add_argument(
                        "-k", "--KeepDeviceIds",
                        dest="keepDeviceIds",
                        action="store_true",
                        help="Keep the Device Id column"
                        )
    
    subParsers = mainParser.add_subparsers(
                            title="Modes",
                            description="The available modes, the program can run in",
                            help="Mode help",
                            dest="subCommand" #To be able to see, which subcommand was invoked
                            )
    
    compileParser = subParsers.add_parser(
                            "Compile",
                            description="A list of all available options for Compiling",
                            help="Try to run a Compile with the rest of the given arguments",
                            add_help=False,
                            parents=[commonOptions]
                            )
    clUtils.createCompileParser(pParser=compileParser)
    compileParser.set_defaults(func=CompileComplianceList.compileComplianceList)
    compileParser.set_defaults(extractFunc=clUtils.extractCompileArgs)
    compileParser.set_defaults(autoCompileFunc=emptyFunc)

    mergeParser = subParsers.add_parser(
                            "Merge",
                            description="A list of all available options for Merging",
                            help="Try to run a Merge with the rest of the given arguments",
                            add_help=False,
                            parents=[commonOptions]
                            )
    clUtils.createMergeParser(pParser=mergeParser)
    mergeParser.set_defaults(func=MergeComplianceLists.mergeCompileList)
    mergeParser.set_defaults(extractFunc=clUtils.extractMergeArgs)
    mergeParser.set_defaults(autoCompileFunc=clUtils.autocompileInput)

    helpParser = subParsers.add_parser(
                            "Help", 
                            description="A list of all available help pages",
                            help="Display usage help for the main script and exit",
                            )
    createHelpParser(parser=helpParser)
    helpParser.set_defaults(func=handleHelp)
    helpParser.set_defaults(extractFunc=emptyFunc)
    helpParser.set_defaults(autoCompileFunc=emptyFunc)

    guiParser = subParsers.add_parser(
                            "GUI",
                            description="A list of all available options for lauching in GUI mode",
                            help="Launch program in GUI mode if needed modules are found",                            
                            add_help=False
                            )
    createGuiParser(parser=guiParser)
    guiParser.set_defaults(func=emptyFunc)
    guiParser.set_defaults(extractFunc=emptyFunc)
    guiParser.set_defaults(autoCompileFunc=emptyFunc)

    parserList = {"Tools": mainParser, "Compile": compileParser, "Merge": mergeParser, "Help": helpParser, "GUI": guiParser}
    # so that the help function can access the parsers
    helpParser.set_defaults(parserList=parserList)

    return mainParser