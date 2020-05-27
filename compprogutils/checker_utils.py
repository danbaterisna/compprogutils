""" Module for checker utilities. This should contain all code users could use to streamline
writing checkers, while checkers.py contains all code cpu needs to deal with checkers. """

import sys, functools, os

def checkFromStreams(func):
    """ Decorator for writing cpu checkers. Takes in a function that
    expects 4 file stream arguments and returns a (score, message) list,
    and converts it into a function that takes filenames from sys.argv. """
    @functools.wraps(func)
    def decorated():
        argList = []
        for i in range(4):
            if os.path.isfile(sys.argv[i + 1]):
                argList.append(open(sys.argv[i + 1], "r"))
            else:
                argList.append(None)
        try:
            print(*func(*argList), sep = "\n")
        finally:
            for fileStream in argList:
                if fileStream is not None:
                    fileStream.close()
    return decorated
