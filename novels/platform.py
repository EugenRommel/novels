import sys


def get_platform():
    platform=''
    if sys.platform.startswith('win'):
        platform = 'win'
    elif sys.platform.startswith('linux'):
        platform = 'linux'
    return platform
