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

