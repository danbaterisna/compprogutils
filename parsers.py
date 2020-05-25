import os

import compprogutils.cpu_errors as cpu_errors

WHITESPACE = "\n\r\t "

class StringParser:
    """Tool for extracting data from a string."""
    def __init__(self, strng):
        self.inString = strng
        self.curID = 0
    def curChar(self, moveToNext = False):
        if self.curID < len(self.inString):
            retVal = self.inString[self.curID]
            if moveToNext:
                self.curID += 1
            return retVal
        else:
            raise cpu_errors.UnexpectedEOF(f"""EOF on attempted char find""")
    def readUntil(self, charSet = WHITESPACE, skipOver = True):
        """ Read until a character in charSet is found. By default, this is whitespace.
        Skip over this character, unless skipOver is false.
        Return the read string. """
        charsRead = []
        while self.curChar() is not None:
            cChar = self.curChar()
            if cChar in charSet:
                if skipOver:
                    self.curChar(moveToNext = True)
                break
            charsRead.append(self.curChar(moveToNext = True))
        return ''.join(charsRead)
    def readDataFromString(self, dataType, charSet = WHITESPACE, skipOver = True):
        """ Read a single member of dataType from the string. dataType should have
        a constructor that accepts a string. Raises ValueError if it is not found. """
        possibleInt = self.readUntil(charSet, skipOver)
        return dataType(possibleInt)

