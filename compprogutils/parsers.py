import os

import compprogutils.cpu_errors as cpu_errors

WHITESPACE = "\n\r\t "

class StringParser:
    """Tool for extracting data from a string."""
    def __init__(self, strng):
        self.inString = strng
        self.curID = 0
    def curChar(self, moveToNext = False, exceptionOnEOF = False):
        if self.curID < len(self.inString):
            retVal = self.inString[self.curID]
            if moveToNext:
                self.curID += 1
            return retVal
        else:
            if exceptionOnEOF:
                raise cpu_errors.UnexpectedEOF(f"""EOF on attempted char find""")
            else:
                return None
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
    def readData(self, dataType, charSet = WHITESPACE, skipOver = True):
        """ Read a single member of dataType from the string. dataType should have
        a constructor that accepts a string. Raises ValueError if it is not found. """
        possibleInt = self.readUntil(charSet, skipOver)
        return dataType(possibleInt)

class FileParser(StringParser):
    """ Tool for extracting data from a file. """
    def __init__(self, byteStream):
        self.byteStream = byteStream
        self.streamHead = None
    def curChar(self, moveToNext = False):
        if self.streamHead is None:
            self.streamHead = self.byteStream.read(1)
        retVal = self.streamHead
        if retVal == "":
            raise cpu_errors.UnexpectedEOF(f"""EOF on attempted char find""")
        if moveToNext:
            self.streamHead = self.byteStream.read(1)
        return retVal

def tokenize(fileStream, removeEmptyTokens = True):
    """ Return all the whitespace-separated tokens of the file in fileStream. If removeEmptyTokens
    is true, all empty tokens are deleted from the final list."""
    fp = FileParser(fileStream)
    tokensRead = []
    while True:
        try:
            tokensRead.append(fp.readData(str))
        except cpu_errors.UnexpectedEOF as e:
            break
    if removeEmptyTokens:
        tokensRead = [token for token in tokensRead if token != ""]
    return tokensRead

