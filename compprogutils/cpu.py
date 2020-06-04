# For automatic problem name generation
import itertools, functools
from string import ascii_uppercase
# For parsing cmdline args
import argparse as ap
# For processing manifest files
import json
import os, errno, shutil
# For table pretty printing
import terminaltables

from compprogutils import cpu_errors, manifests, executables, generators, tests, solutions, checkers, utilities, configuration

parser = ap.ArgumentParser(description = """Competitive programming utilities.

Use this to make setting up files for doing things in contests easier.""")

subparser = parser.add_subparsers(dest = "main_command", required = True)

def argument(*name_or_flags, **kwargs):
    """ Helper function to format data for decorating with `subcommand`. """
    return name_or_flags, kwargs

def subcommand(*sub_args, parent=subparser, aliases = []):
    # stolen from https://gist.github.com/mivade/384c2c41c3a29c637cb6c603d4197f9f
    """ Helper function to make declaring subcommands more sane. """
    def decorator(func):
        commandName = func.__name__.replace('_', '-')
        parser = parent.add_parser(commandName, description=func.__doc__, aliases = aliases)
        for args, kwargs in sub_args:
            parser.add_argument(*args, **kwargs)
        parser.set_defaults(handler=func)
        @functools.wraps(func)
        def decoratedFunc(**kwargs):
            return func(ap.Namespace(**kwargs))
        return decoratedFunc
    return decorator

def _add_problem(problemName):
    """ Adds a problem witht the given name to the contest. More specifically:
    - create a directory for the problem
    - create an empty manifest file for the problem
    - create the programs/ directory for the problem."""
    with manifests.modifyManifest("contest") as m:
        m[problemName] = os.path.join(problemName, "")
    os.mkdir(problemName)
    with utilities.cd(problemName):
        shutil.copyfile(os.path.join(configuration.CONF_DIRECTORY, "default_manifest.json"), \
                        ".cpu.problem_manifest.json")
        os.mkdir("programs")
        with utilities.cd("programs"):
            os.mkdir("solutions")
            os.mkdir("checkers")
            os.mkdir("generators")
        os.mkdir("tests")
        os.mkdir("outputs")
    print(f"Problem {problemName} created")


@subcommand(argument("name", type=str), aliases = ["ap"])
def add_problem(args):
    """Add a problem with the given name to the contest."""
    # This guy just exposes the _add_problem_ function to the outside.
    _add_problem(args.name)


@subcommand(argument("n", type=int), \
             argument("--by-name", type=str, nargs="+"))
def make_contest(args):
    """Creates a contest with n problems. The names from --by-name are used
    in order to name the problems. If names are not given, CPU will use
    A, B, C ..."""
    # Internally, creates the .cpu.contest_manifest file, which stores
    # a (problem_name, problem_directory) list in JSON.
    # Raise an error if there's already a manifest here:
    manifestsFound = manifests.checkForManifest()
    if manifestsFound:
        if "contest" in manifestsFound:
            raise cpu_errors.ContestAlreadyExists("""You are already in a cpu contest directory.
If this is a mistake, delete the file named .cpu.contest_manifest and try again.""")
        if "problem" in manifestsFound:
            raise cpu_errors.ContestAlreadyExists("""You are already in a cpu problem directory.
If this is a mistake, delete the file named .cpu.problem_manifest and try again.""")
    # Generate the problem names, if none were given:
    if args.by_name is None:
        def iterateAllStrings():
            for size in itertools.count(1):
                for charList in itertools.product(ascii_uppercase, repeat=size):
                    yield "".join(charList)
        args.by_name = list(itertools.islice(iterateAllStrings(), args.n))
    # Create an empty manifest file
    manifests.saveManifestTo(manifests.EMPTY_MANIFEST, ".cpu.contest_manifest.json")
    print("Contest created, now adding problems")
    # Add problems
    for problemName in args.by_name:
        _add_problem(problemName)
    print("Contest creation successful!")

@subcommand(argument("file_name", type=str), \
            argument("--name", "-n", type=str),
            aliases = ["as"])
def add_solution(args):
    """ Register a solution with CPU. If --name is not given, use the
    file name after stripping extensions. """
    if args.name is None:
        args.name = os.path.splitext(args.file_name)[0]
    utilities.requireFileExists(args.file_name)
    with manifests.modifyManifest("problem") as m:
        m["solutions"][args.name] = solutions.Solution(args.name, args.file_name)
    print(f"Solution {args.name} added")

@subcommand(argument("sol_name", type=str), \
            argument("--custom-compile", "-c", type=str),
            aliases = ["cs"])
def compile_solution(args):
    """ Compile the registered solution. If -c is given, use the
        custom compilation command as stated in the config file. """
    with manifests.modifyManifest("problem") as m:
        utilities.requirePresentKey(m["solutions"], args.sol_name, "solution")
        m["solutions"][args.sol_name].compile(args.custom_compile, os.path.join("programs", "solutions"))

@subcommand(argument("sol_name", type=str),
            argument("--time-limit", "-t", type=int),
            argument("--input-test", "-i", type=str),
            argument("--silent", "-s", action="store_true"),
            aliases = ["rs"])
def run_solution(args):
    """ Run the registered solution. Receive input from STDIN (or the specified test)
    and output to STDOUT. Print additional information if -s is not given."""
    with manifests.modifyManifest("problem") as m:
        utilities.requirePresentKey(m["solutions"], args.sol_name, "solution")
        solExec = m["solutions"][args.sol_name]
        solResult = None
        if args.input_test is not None:
            utilities.requirePresentKey(m["tests"], args.input_test, "test")
            testOrigin = m["tests"][args.input_test]
            with testOrigin.getFileObject(tests.TestFile.INPUT) as inputFile:
                solResult = solExec.run(timeout = args.time_limit, fileInput = inputFile)
                print(solResult.output)
                if solResult.data is not None:
                    print("> Solution also gave the following data:")
                    print(solResult.data)
        else:
            try:
                solResult = solExec.run(timeout = args.time_limit, pipeToTerminal = True)
            except KeyboardInterrupt:
                if not args.silent:
                    print("<Solution interrupted>")
        if not args.silent and solResult is not None:
            print(f"Solution executed in {solResult.timeElapsed:.3f} seconds")

@subcommand(argument("sol_name", type=str))
def delete_solution(args):
    """ Delete the solution with the given name. """
    with manifests.modifyManifest("problem") as m:
        utilities.requirePresentKey(m["solutions"], args.sol_name, "solution")
        execToRemove = m["solutions"][args.sol_name]
        execToRemove.deleteExecutable()
        del m["solutions"][args.sol_name]
    print(f"Solution {args.sol_name} deleted!")

@subcommand(argument("file_name", type=str),
            argument("--name", "-n", type=str),
            aliases = ["ag"])
def add_generator(args):
    """ Add an input generator. If --name is not given, use file_name after stripping extensions."""
    utilities.requireFileExists(args.file_name)
    if args.name is None:
        args.name = os.path.splitext(args.file_name)[0]
    with manifests.modifyManifest("problem") as m:
        m["generators"][args.name] = executables.Executable(args.name, args.file_name)
    print(f"Generator {args.name} added!")

@subcommand(argument("file_name", type=str),
            argument("--name", "-n", type=str),
            aliases = ["ac"])
def add_checker(args):
    """ Add a test checker. If --name is not given, use file_name after stripping extensions. """
    utilities.requireFileExists(args.file_name)
    if args.name is None:
        args.name = os.path.splitext(args.file_name)[0]
    with manifests.modifyManifest("problem") as m:
        m["checkers"][args.name] = checkers.Checker(args.name, args.file_name)
    print(f"Checker {args.name} added!")

@subcommand(argument("check_name", type=str))
def set_checker(args):
    """ Set the default checker to the named checker. """
    mf = manifests.loadManifestType("problem")
    utilities.requirePresentKey(mf["checkers"], args.check_name, "checker")
    with manifests.modifyManifest("problem") as m:
        m["default_checker"] = args.check_name


@subcommand(argument("--with-gen", "-g", type=str),
            aliases = ["at"])
def add_test(args):
    """ Add a new test, reading data from stdin. Use an EOF signal (Ctrl-D) to
    separate test input and test output, and to end test output. If --with-gen
    is provided, use the stdout of the given generator program as input.

    As a function, return the test ID."""
    with manifests.modifyManifest("problem") as m:
        newTest = tests.getUnusedTest(m["tests"])
        if args.with_gen is None:
            print(f"Test {newTest.ID} created. Now reading input...")
            newTest.writeToTestFile(tests.TestFile.INPUT, generators.fetchInputUntilEOF())
            print(f"Now reading output...")
            newTest.writeToTestFile(tests.TestFile.OUTPUT, generators.fetchInputUntilEOF())
            print(f"Test created successfully!")
        else:
            genExec = generators.getGen(args.with_gen)
            print(f"Test {newTest.ID} created. Calling generator...")
            genExec.run(fileToWrite = newTest.getFileObject(tests.TestFile.INPUT, "wb"))
            print(f"Test generated successfully!")
        m["tests"][newTest.ID] = newTest
        return newTest.ID

@subcommand(argument("sol_name", type=str),
            argument("--timeout", "-t", type=int),
            argument("tests", type=str, nargs="*"),
            aliases = ["mo"])
def make_output(args):
    """ Use the sol in sol_name to generate the output for the tests listed. If no tests are listed,
    the output generator is run for all tests. If --timeout is given, stop running the solution after
    -t seconds. """
    mf = manifests.loadManifestType("problem")
    if args.tests == []:
        args.tests = list(mf["tests"].keys())
    for testName in args.tests:
        utilities.requirePresentKey(mf["tests"], testName, "test")
    utilities.requirePresentKey(mf["solutions"], args.sol_name, "solution")
    testsToGenerate = {testName: mf["tests"][testName] for testName in args.tests}
    solExec = mf["solutions"][args.sol_name]
    for testGName, testg in testsToGenerate.items():
        print(f"Generating output for test {testGName}...")
        with testg.getFileObject(tests.TestFile.INPUT, "rb") as inputFile:
            with testg.getFileObject(tests.TestFile.OUTPUT, "wb") as outputFile:
                solExec.run(fileInput = inputFile, fileToWrite = outputFile, timeout = args.timeout)
        print(f"Output generated!")

@subcommand(argument("sol_name", type=str),
            argument("--timeout", "-t", type=int),
            argument("tests", type=str, nargs="*"),
            aliases = ["ts"])
def test_solution(args):
    """ Run `tests` on the given solution. If tests is not given, use all tests.
    If --timeout is given, stop running the solution after -t seconds.
    As a function, return the minimum score given by the checker for any of the tests.
    """
    mf = manifests.loadManifestType("problem")
    args.checker = mf["default_checker"]
    if args.tests == []:
        args.tests = list(mf["tests"].keys())
    for testName in args.tests:
        utilities.requirePresentKey(mf["tests"], testName, "test")
    utilities.requirePresentKey(mf["solutions"], args.sol_name, "solution")
    utilities.requirePresentKey(mf["checkers"], args.checker, "checker")
    testsToRun = {testName: mf["tests"][testName] for testName in args.tests}
    solExec = mf["solutions"][args.sol_name]
    checkerExec = mf["checkers"][args.checker]
    if not checkerExec.precompiled:
        checkerExec.compile(outputDirectory = os.path.join("programs", "checkers"))
    print(f"All info ready. Running tests:")
    extraVerdicts = set()
    totalScore = 1
    for testName, testPackage in testsToRun.items():
        print(testPackage.testDisplayTable(maxLines = 3).table)
        if not testPackage.checkFileExists(tests.TestFile.OUTPUT):
            print(f"!!! Test has no output to check, skipping")
            continue
        outputCheckName = os.path.join("outputs", f"{args.sol_name}_out.txt")
        with open(outputCheckName, "w") as outputToCheck:
            with testPackage.getFileObject(tests.TestFile.INPUT, "r") as testInput:
                try:
                    solutionRunData = solExec.run(timeout = args.timeout, fileInput = testInput,
                                fileToWrite = outputToCheck)
                    print(f"Solution executed in {solutionRunData.timeElapsed:.3f} seconds")
                except cpu_errors.SolutionTimeout as ce:
                    print(f"Solution exceeded time limit. Skipping.")
                    extraVerdicts.add("TLE")
                    totalScore = 0
                    continue
                except cpu_errors.SolutionExecution as ce:
                    print(f"Runtime error: {ce.message}")
                    extraVerdicts.add("RTE")
                    print(f"Skipping.")
                    totalScore = 0
                    continue
        print("Output:")
        print(*utilities.wrapFileContentsList(outputCheckName, shutil.get_terminal_size()[1], 5), sep="\n")
        score, notes = checkerExec.checkOutputFile(testPackage, outputCheckName)
        print(f"Checker notes: {notes.rstrip()}")
        print("Checker verdict:", checkers.getVerdictString(score), end="\n\n")
        totalScore = min(totalScore, score)
    print("Minimum score received:", checkers.getVerdictString(totalScore))
    if len(extraVerdicts) > 0:
        print("Additionally, it received the following errors:", *extraVerdicts)
    return totalScore

@subcommand(argument("stress_sol_name", type=str),
            argument("ac_sol_name", type=str),
            argument("gen_name", type=str),
            argument("-r", "--rounds", type=int, default=-1))
def stress_test(args):
    """ Writes a test for which stress_sol_name is marked wrong, using ac_sol_name to generate
    correct output. Performs (--rounds) attempts (by default, infinite) """
    # recompile the generator
    failedRounds = 0
    while args.rounds == -1 or failedRounds < args.rounds:
        print(f"Attempt {failedRounds + 1}:")
        attemptTest = add_test(with_gen = args.gen_name)
        make_output(sol_name = args.ac_sol_name, tests = [attemptTest], timeout = None)
        if test_solution(sol_name = args.stress_sol_name, timeout = None, tests = [attemptTest]) < 1:
            print(f"Solution {args.stress_sol_name} breaks under test {attemptTest}")
            break
        else:
            delete_tests(tests = [attemptTest])
        failedRounds += 1
    else:
        print(f"Failed to break solution {args.stress_sol_name}")

@subcommand(argument("--summary", "-s", action="store_true"),
            argument("--truncate", "-t", type=int, default=5),
            argument("tests", type=str, nargs="*"),
            aliases = ["lt"])
def list_tests(args):
    """ List down the tests in `tests` for this problem. Only show up to TRUNCATE lines (default 3).
    If -s is enabled, do not show test contents. If no `tests` are given, output all tests. """
    mf = manifests.loadManifestType("problem")
    if args.tests == []:
        args.tests = list(mf["tests"].keys())
    for testName in args.tests:
        utilities.requirePresentKey(mf["tests"], testName, "test")
    for testName in args.tests:
        if args.summary:
            print(str(mf["tests"][testName]))
        else:
            print(mf["tests"][testName].testDisplayTable(args.truncate).table)

@subcommand(argument("tests", type=str, nargs="*"))
def delete_tests(args):
    """ Delete the tests in `tests`. """
    with manifests.modifyManifest("problem") as m:
        if args.tests == []:
            if utilities.confirmPrompt("You are about to delete all tests. Proceed? (y/n) "):
                args.tests = list(m["tests"].keys())
            else:
                return
        for testName in args.tests:
            utilities.requirePresentKey(m["tests"], testName, "test")
        for testName in args.tests:
            m["tests"][testName].deleteFiles()
            del m["tests"][testName]
            print(f"Test {testName} deleted")

def main():
    args = parser.parse_args()
    if args.main_command is None:
        args.print_help()
    else:
        try:
            args.handler(args)
        except cpu_errors.CPUException as e:
            print(f"A {e.__class__.__name__} error occured while processing this command!\n")
            print("Details:", e.message)
        except KeyboardInterrupt:
            print("<Execution interrupted>")
        except Exception as e:
            print(f"An internal error occured while processing this command! Re-raising...")
            raise e
