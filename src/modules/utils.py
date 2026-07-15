from typing import List

from modules import clUtils
import argparse

def emptyFunc(tmp) -> None:
    ...

def createHelpParser(parser: argparse.ArgumentParser | None = None) -> None:
    #TODO: make the help list better
    parser.add_argument(
                        dest="helpMode", 
                        # choices=["All", "Tools", "Help", "Compile", "Merge", "GUI"],
                        choices=["Tools", "Help", "Compile", "Merge", "GUI"],
                        nargs="?",
                        default="Help"
                        )

def handleHelp(pArgs: argparse.Namespace | None = None) -> None:
    args = vars(pArgs)
    parserList = None
    helpMode = ""
    if pArgs is None:
        return

    if "parserList" in args.keys():
        parserList = args["parserList"]
    if "helpMode" in args.keys():
        helpMode = args["helpMode"]

    if helpMode in parserList.keys():
        parserList[helpMode].print_help()
    else:
        parserList["Help"].print_help()

    ...

def createGuiParser(parser: argparse.ArgumentParser | None = None) -> None:
    
    ...

def createArgParser() -> None:
    mainParser = argparse.ArgumentParser(
                            prog="ComplianceListTools", 
                            description="A set of tools to process exported .csv lists of Intune's noncompliant devices report into a more usable format and be able to merge lists together.",
                            allow_abbrev=False,
                            add_help=False
                            )
    mainParser.add_argument(
                            "-h", "--help",
                            action="help",
                            help="Show help message and exit the program"
                            )
    
    commonOptions = argparse.ArgumentParser("General options", description="Options, that are for setting the general behaviour of the program")
    # generalOptions = mainParser.add_argument_group("General options", description="Options, that are for setting the general behaviour of the program")
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
    
    # sharedListOptions = mainParser.add_argument_group("Shared list options", description="Options, that are both used for Compiling and for Merging")
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
                            )
    
    compileParser = subParsers.add_parser(
                            "Compile",
                            description="A list of all available options for Compiling",
                            help="Try to run a Compile with the rest of the given arguments",
                            #TODO: add the shared options as well
                            add_help=False,
                            parents=[commonOptions]
                            )
    clUtils.createCompileParser(pParser=compileParser)
    compileParser.set_defaults(func=clUtils.extractCompileArgs)

    mergeParser = subParsers.add_parser(
                            "Merge",
                            description="A list of all available options for Merging",
                            help="Try to run a Merge with the rest of the given arguments",
                            #TODO: add the shared options as well
                            add_help=False,
                            parents=[commonOptions]
                            )
    clUtils.createMergeParser(pParser=mergeParser)
    mergeParser.set_defaults(func=clUtils.extractMergeArgs)

    helpParser = subParsers.add_parser(
                            "Help", 
                            description="A list of all available help pages",
                            help="Display usage help for the main script and exit",
                            )
    createHelpParser(parser=helpParser)
    helpParser.set_defaults(func=handleHelp)

    guiParser = subParsers.add_parser(
                            "GUI",
                            description="A list of all available options for lauching in GUI mode",
                            help="Launch program in GUI mode if needed modules are found",                            
                            add_help=False
                            )
    createGuiParser(parser=guiParser)
    guiParser.set_defaults(func=emptyFunc)

    # parserList = [mainParser, commonOptions, compileParser, mergeParser, helpParser, guiParser]
    parserList = {"Tools": mainParser, "Compile": compileParser, "Merge": mergeParser, "Help": helpParser, "GUI": guiParser}
    # so that the help function can access the parsers
    helpParser.set_defaults(parserList=parserList)

    args = mainParser.parse_args()
    # print(args)
    print(args.func(args))
