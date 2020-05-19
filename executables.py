""" Module for working with executable files """
# For manipulating path extensions
import os
# For accessing commands stored in the config file
import configuration
# For raising errors
import cpu_errors
# For running commands
import subprocess, shutil
# For timing
import time

import utilities

class Executable:
    """ An executable is something cpu can run. Each executable is composed of:
        - its name,
        - the name of the file where its code is stored.

        After compilation, exec_loc is computed, which is the location of the executable code.
        """
    def __init__(self, name, src):
        self.name = name
        self.src = src
        self.exec_loc = None
        self.ext = os.path.splitext(src)[1][1:]

    def getCompileCommand(self, commandKey = None):
        """ Retrieve the executable's compile command from the cpu config file, without
        filling in template parameters. Use the given commandKey if available. """
        cfg = configuration.getConfig()["commands"]
        if self.ext not in cfg or "compile" not in cfg[self.ext]:
            raise cpu_errors.UnknownProgramExtension(f"""cpu does not know how to compile
{self.src}. Check that a key corresponding to the file extension exists in ~/.cpu/.config.""")
        if commandKey is None:
            commandKey = "__default__"
        commandsAvailable = cfg[self.ext]["compile"]
        if commandKey not in commandsAvailable:
            raise cpu_errors.UnknownCompilationCommand(f"""cpu does not recognize the
compilation command {compileCommand} used. Make sure the corresponding key exists in the config file.""")
        return commandsAvailable[commandKey]

    def getRunCommand(self):
        """ Retrieve the executable's run command from the cpu config file, without filling in
        template parameters."""
        cfg = configuration.getConfig()["commands"]
        if self.ext not in cfg or "run" not in cfg[self.ext]:
            raise cpu_errors.UnknownProgramExtension(f"""cpu does not know how to run
{self.src}. Check that a key corresponding to the file extension exists in ~/.cpu/.config.""")
        return cfg[self.ext]["run"]

    def compile(self, commandKey = None, outputDirectory = ""):
        """ Run the compilation command stored in the config file, and store the output in outputDirectory.
        Use the given commandKey if given."""
        currentWorkingDir = os.getcwd()
        with utilities.cd(outputDirectory):
            @utilities.mapOverInputList
            def expandTemplate(s):
                return s.format(name = self.name, file = os.path.join(os.path.relpath(currentWorkingDir), self.src))
            # run the compilation command
            try:
                commandString, compilationOutput = map(expandTemplate, self.getCompileCommand())
                compileComplete = subprocess.run(commandString)
                if compileComplete.returncode != 0:
                    raise cpu_errors.UnsuccessfulCompilation(f"""Compilation return code is {compileComplete.returncode}""")
                self.exec_loc = os.path.join(outputDirectory, compilationOutput[0])
            except KeyError as e:
                raise cpu_errors.ImproperCompilationCommand(f"""cpu does not recognize the
    shortcut {e}. Make sure it is properly spelled.""")

    def run(self, cmdArgs = [], fileInput = None, fileToWrite = subprocess.PIPE, timeout = None, pipeToTerminal = False):
        """ Run the executable using the command stored in the config file. .compile() must have been called on the
        executable. If fileToWrite is supplied, and it is a binary file-like object, pipe stdout to the given file.
        cmdArgs is a list that is appended to the run command. If fileInput is given, and it is a binary file-like
        object, pipe the file to stdin. If pipeToTerminal is true, send both stdin and stdout to the terminal.

        Return a list with two elements. The first is the output of the executable if output is not piped anywhere,
        or None if it is. The second is the time in seconds the execution took, which is computed using time.time()
        """
        if self.exec_loc is None:
            raise cpu_errors.UncompiledRunAttempted(f"""The program {self.name} has not been compiled yet. """)
        @utilities.mapOverInputList
        def expandTemplate(s):
            return s.format(name = self.name, file = self.exec_loc)
        exec_cmd = expandTemplate(self.getRunCommand())
        returnValue = [None, None]
        try:
            timeStarted = time.time()
            runComplete = subprocess.run(exec_cmd + cmdArgs, check = True,
                                         stdin = fileInput, stdout = None if pipeToTerminal else fileToWrite, timeout = timeout)
            returnValue[1] = time.time() - timeStarted
        except subprocess.TimeoutExpired as e:
            raise cpu_errors.SolutionTimeout(f"""Your code could not finish in {e.timeout} seconds.""")
        except subprocess.CalledProcessError as e:
            raise cpu_errors.SolutionExecution(f"""Your code exited with return code {e.returncode}.""")
        if fileToWrite == subprocess.PIPE and not pipeToTerminal:
            returnValue[0] = runComplete.stdout.decode('utf-8')
        return returnValue

    def deleteExecutable(self):
        """ Deletes the file pointed to in exec_loc. """
        if not (self.exec_loc is None):
            os.remove(self.exec_loc)

    def __serialize__(self):
        """ Return a JSON-serializable dict which decodes to an equivalent executable. """
        return {"_custom_type" : "Executable",
                "name" : self.name,
                "src" : self.src,
                "exec_loc" : self.exec_loc}
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, '{self.src}', exec_loc = {self.exec_loc})"

    @classmethod
    def __deserialize__(cls, obj):
        result =  Executable(obj["name"], obj["src"])
        result.exec_loc = obj["exec_loc"]
        return result


# TODO: non local executables
# for these, you just give it a fixed exec_loc so we don't have to compile it every time we use it

class NonLocalExecutable(Executable):
    """ A NonLocalExecutable is an Executable whose source file is not expected to be in the current folder.
    Useful for default programs, etc. """
    def __init__(self, name, src, exec_loc):
        super().__init__(name, src)
        self.exec_loc = exec_loc

    def __serialize__(self):
        result = super().__serialize__()
        result["_custom_type"] = "NonLocalExecutable"
        return result

    @classmethod
    def __deserialize__(cls, obj):
        result = NonLocalExecutable(obj["name"], obj["src"], obj["exec_loc"])
        return result

