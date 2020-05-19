""" Module for handling checkers """

import os

import executables, tests

import parsers

import cpu_errors

class Checker(executables.Executable):
    """ A checker is an executable that validates test output. """
    def checkOutputFile(self, test, outputFile):
        """ Check the outputFile file against the given test. Return a (score, message) tuple. """
        checkerOutput = self.run(cmdArgs = [test.getFilename(tests.TestFile.INPUT), test.getFilename(tests.TestFile.OUTPUT), \
                        test.getFilename(tests.TestFile.DATA), outputFile])
        outputToParse = parsers.StringParser(checkerOutput)
        score = outputToParse.readDataFromString(float)
        remarks = outputToParse.readDataFromString(str, charSet = [])
        return (score, remarks)





