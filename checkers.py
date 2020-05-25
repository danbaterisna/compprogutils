""" Module for handling checkers """

import os, sys

import functools

import executables, tests

import parsers

import cpu_errors

class Checker(executables.Executable):
    """ A checker is an executable that validates test output. """
    def checkOutputFile(self, test, outputFile):
        """ Check the outputFile file against the given test. Return a (score, message) tuple. """
        checkerArgv = [test.getFilename(tests.TestFile.INPUT), test.getFilename(tests.TestFile.OUTPUT), \
                        test.getFilename(tests.TestFile.DATA), outputFile]

        checkerOutput, checkerTime = self.run(cmdArgs = [os.path.abspath(fileName) for fileName in checkerArgv])
        outputToParse = parsers.StringParser(checkerOutput)
        score = outputToParse.readData(float)
        remarks = outputToParse.readData(str, charSet = [])
        return (score, remarks)

def checkFromStreams(func):
    """ Decorator for writing cpu checkers. Takes in a function that
    expects 4 file stream arguments, and converts it into a function
    that takes filenames from sys.argv. """
    @functools.wraps(func)
    def decorated():
        argList = []
        for i in range(4):
            if os.path.isfile(sys.argv[i + 1]):
                argList.append(open(sys.argv[i + 1], "r"))
            else:
                argList.append(None)
        try:
            func(*argList)
        finally:
            for fileStream in argList:
                if fileStream is not None:
                    fileStream.close()
    return decorated



