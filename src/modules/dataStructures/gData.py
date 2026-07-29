import sys

if 'globalData' in sys.modules:
    from .globalData import GlobalData

# The shared instance of GlobalData, needs to be set at the beginning of the program with the launch args
# Has be in seperate file because it breaks otherwise
globData: GlobalData = None