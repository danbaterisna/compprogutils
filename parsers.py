
import os

from . import cpu_errors

WHITESPACE = "\n\r\t "

class StringParser:
    """Tool for extracting data from a string."""
    def __init__(self, strng):
        self.inString = strng
        self.curID = 0
    def readUntil(self, charSet = WHITESPACE, skipOver = True):
        """ Read until a character in charSet is found. By default, this is whitespace.
        Skip over this character, unless skipOver is false.
        Return the read string. """
        charsRead = []
        while self.curID < len(self.inString):
            cChar = self.inString[self.curID]
            if cChar in charSet:
                if skipOver:
                    self.curID += 1
                    break
            charsRead.append(cChar)
            self.curID += 1
        return ''.join(charsRead)
    def readDataFromString(self, dataType, charSet = WHITESPACE, skipOver = True):
        """ Read a single member of dataType from the string. dataType should have
        a constructor that accepts a string. Raises ValueError if it is not found. """
        possibleInt = self.readUntil(charSet, skipOver)
        return dataType(possibleInt)

