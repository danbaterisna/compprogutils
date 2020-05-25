class CPUException(Exception):
    def __init__(self, message):
        self.message = message

class ContestAlreadyExists(CPUException):
    """ Exception raised when cpu make-contest is called, but
    cpu can already detect a manifest file in the current directory. """

class NotInCPUDirectory(CPUException):
    """ Exception raised when a command other than cpu make-contest is
    called outside of a recognized cpu contest. """

class UnknownProgramExtension(CPUException):
    """ Exception raised when a program file has an extension cpu
    does not recognize. """

class UnknownCompilationCommand(CPUException):
    """ Exception raised when the compilation command is not recognized. """

class ImproperCompilationCommand(CPUException):
    """ Exception raised when the compilation command is not recognized. """

class UnsuccessfulCompilation(CPUException):
    """ Exception raised when the compilation command is not recognized. """

class UncompiledRunAttempted(CPUException):
    """ Exception raised when an executable that has not been compiled is run."""

class UnknownProgram(CPUException):
    """ Exception raised when the program name is not recognized. """

class SolutionExecution(CPUException):
    """ Exception raised when the solution does not return an exit code of zero. """

class SolutionTimeout(CPUException):
    """ Exception raised when the solution times out. """

class MalformedDataDelimiter(CPUException):
    """ Exception raised when more than one DATA_ESCAPE sequence is read.
    when processing solution output."""

class UnexpectedEOF(CPUException):
    """ Exception raised when an unexpected EOF is read during parsing. """
