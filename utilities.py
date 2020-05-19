import os, errno
from contextlib import contextmanager

import cpu_errors

import functools

@contextmanager
def cd(newDir):
    """ Context manager for performing operations in another directory."""
    prevDir = os.getcwd()
    os.chdir(newDir)
    try:
        yield
    finally:
        os.chdir(prevDir)

def requireFileExists(fileName):
    """ Raises a FileNotFound error if fileName does not exist."""
    if not os.path.isfile(fileName):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), fileName)

def requirePresentKey(dct, keyName, keyType):
    """ Raise a UnknownProgram error if keyName is not in dct.
    keyType is a parameter that goes into the displayed error message. """
    if keyName not in dct:
        raise cpu_errors.UnknownProgram(f""" cpu does not know the {keyType} name {keyName}. """)

def humanizeFileSize(num, suffix='B'):
    # Ripped from https://gist.github.com/cbwar/d2dfbc19b140bd599daccbe0fe925597, 
    # figured this was too trivial to get a dependency for
    # Updated to use more modern string formatting
    """Readable file size. Takes in an integer, and the suffix to place on the value
    ('B' by default). Returns a string.
    """
    for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            if unit == "":
                return f"{num} {unit}{suffix}"
            else:
                return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"

def padListRight(lst, n, default = None):
    """ Return lst with exactly n elements. If there are more, slice them off.
    If there are less, pad with default."""
    return lst[:n] + [default] * max(0, n - len(lst))

def wrapString(s, maxWidth, maxLines, indent = ">", placeholder="[...]"):
    """ Wrap s into a series of lines, each at most maxWidth long. Append indent
    to the start of continuation of previous lines. There will be at most maxLines lines in
    the result.  If it exceeds this length, it will be truncated, with placeholder alone
    on the last line.
    """
    wrapped = []
    widthNext = maxWidth - len(indent)
    for longLine in s.split('\n'):
        toPlaceHere, nextSection = longLine[:maxWidth], longLine[maxWidth:]
        wrapped.append(toPlaceHere)
        while nextSection:
            toPlaceHere, nextSecton = longLine[:maxWidth], longLine[maxWidth:]
            wrapped.append(indent + toPlaceHere)
    if len(wrapped) > maxLines:
        wrapped = wrapped[:maxLines - 1] + [placeholder]
    return '\n'.join(wrapped)

def wrapStringList(*args, **kwargs):
    """ Returns wrapString's individual lines as a list. """
    return wrapString(*args, **kwargs).split("\n")

def confirmPrompt(prompt):
    """ Displays a y/n confirmation prompt to the user. Returns True iff
    the user inputs y. This accepts y, n, yes, no, and is case insensitive. """
    responseTable = {"y" : True, "n" : False, "yes" : True, "no" : False}
    result = input(prompt).lower()
    while result not in responseTable:
        print("Please enter a y/n response.")
        result = input(prompt).lower()
    return responseTable[result]

def mapOverInputList(f):
    @functools.wraps(f)
    def decorated(lst):
        return list(map(f, lst))
    return decorated

