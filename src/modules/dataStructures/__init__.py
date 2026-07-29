from .returnCodes import ReturnCodes as ReturnCodes
from .utils import ProgramModes as ProgramModes
from .utils import AttributeLocation as AttributeLocation
from .returnData import ReturnData as ReturnData
from .globalData import GlobalData as GlobalData
from .launchData import LaunchData as LaunchData
from .argumentData import ArgumentData as ArgumentData
# from .globData import globData as globData
from . import gData as gData

# This is probably very stupid but I don't care
# it should just like make handling arguments, returndata, launchargs and config earsier. also for easily implementing different front ends
# it should at first load one static/global LaunchData object with all launcharguments saved
# it should also then try to load the config according to the launch args
# LaunchData and Config should be stored in a GlobalData class that should be accessable by all project internal functions
# ArgumentData should be used to package args to send to functions
# it stores the arguments, or if specified, points to a specific attribute of either the launchdata or the config
# ReturnData is the same, except it also contains returnCodes and error messages (if needed)
# ArgumentData, and maybe also ReturnData, should also be able to extract data from a given ReturnData object