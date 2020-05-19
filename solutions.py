""" Module for managing solutions. """

import executables

import cpu_errors

class SolutionResult:
    """ Object that holds teh result of a solution. Has 3 members:
        the output, the generated data, and the time elapsed. """
    def __init__(self, output, data, timeElapsed):
        self.output = output
        self.data = data
        self.timeElapsed = timeElapsed
    def __repr__(self):
        return f"SolutionResult(output = {self.output}, data = {self.data}, timeElapsed = {self.timeElapsed})"

DATA_ESCAPE = "\xDA\x7A\xF0\x11\x05"

class Solution(executables.Executable):
    """ Represents solution executables. Adds the ability to
    split a solution's output, and extra data it may generate."""
    def run(self, pipeToTerminal = False, *args, **kwargs):
        """ Runs the solution, sending all arguments to the parent
        executable. """
        runResult = super().run(pipeToTerminal = pipeToTerminal, *args, **kwargs)
        if runResult[0] is None:
            return SolutionResult(None, None, runResult[1])
        outputSplit = runResult[0].split(DATA_ESCAPE)
        result = SolutionResult(outputSplit[0], None, runResult[1])
        if len(outputSplit) > 2:
            raise cpu_errors.MalformedDataDelimiter("""You printed more than one data delimiter in your solution. """)
        if len(outputSplit) == 2:
            result.data = outputSplit[1]
        return result

    def __serialize__(self):
        result = super().__serialize__()
        result["_custom_type"] = "Solution"
        return result

    @classmethod
    def __deserialize__(self, obj):
        result = Solution(obj["name"], obj["src"])
        result.exec_loc = obj["exec_loc"]
        return result
