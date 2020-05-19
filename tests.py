""" Module for managing cpu test objects. """

import itertools
import enum
import shutil, os

import textwrap, terminaltables

import utilities, configuration

TEST_PATH = "tests"

class TestFile(enum.Enum):
    """ Enum for managing the three files that can be created in
    a test. """
    INPUT = 1
    OUTPUT = 2
    DATA = 3

class Test:
    """ A test contains a set of data a solution is expected to process
    correctly. It is composed of three files, an input file, an
    output file, and a data file in case the checker needs any
    auxilliary information. Only the input file is given upon
    constuction; the output and data files must be generated
    through other means.
    """
    def __init__(self, ID):
       self.fileTable = {typ: os.path.join(TEST_PATH, f"{ID}.{suffix}") for typ, suffix in
                zip(TestFile, ["in", "out", "data"])}
       self.ID = ID

    def writeToTestFile(self, testFile, contents):
        """ Writes contents to the given testFile. testFile must be
        a member of the TestFile enum. """
        with open(self.fileTable[testFile], "w") as f:
            f.write(contents)

    def getFilename(self, testFile):
        """ Return the filename of the given testFile. testFile must be
        a member of the TestFile enum. """
        return self.fileTable[testFile]

    def checkFileExists(self, testFile):
        """ Return True iff the given testFile exists. """
        return os.path.isfile(self.fileTable[testFile])

    def getFileObject(self, testFile, *args, **kwargs):
        """ Calls `open` on the specified testFile. All other arguments are passed to `open`. """
        return open(self.fileTable[testFile], *args, **kwargs)

    def getFileContents(self, testFile, default = "[None]", maxLines = None):
        """ Returns a string with the contents of the file's first `maxLines` lines. If the file does not exist, return
        default. """
        fileContents = default
        try:
            with self.getFileObject(testFile, "r") as fl:
                if maxLines is not None:
                    fileContents = '\n'.join(itertools.islice(fl, maxLines))
                else:
                    fileContents = fl.read()
        except FileNotFoundError:
            pass
        return fileContents

    def __serialize__(self):
        """ Return a JSON-serializable dict which decodes to an equivalent test. """
        return {"_custom_type" : "Test",
                "ID" : self.ID}

    def __repr__(self):
        return f"Test({self.ID})"

    def __str__(self):
        inputSizeBytes = os.path.getsize(self.getFilename(TestFile.INPUT))
        outputSizeBytes = None
        try:
            outputSizeBytes = os.path.getsize(self.getFilename(TestFile.OUTPUT))
        except OSError: # this will be raised if the output file does not exist yet
            pass
        inputSizeRepr = utilities.humanizeFileSize(inputSizeBytes)
        outputSizeRepr = "None" if outputSizeBytes is None else utilities.humanizeFileSize(outputSizeBytes)
        return f"Test {self.ID} [{inputSizeRepr} | {outputSizeRepr}]"

    def testDisplayTable(self, maxLines):
        """ Return a terminaltables.SingleTable representing the truncated contents of this test. """
        table = terminaltables.SingleTable([])
        table.title = str(self)
        if configuration.getConfig()["display_io_side_by_side"]:
            colWidth = (shutil.get_terminal_size().columns // 2) - 4
            table.table_data.append(["Input".ljust(colWidth), "Output".ljust(colWidth)])
            inputLines = utilities.wrapStringList(self.getFileContents(TestFile.INPUT, maxLines = maxLines),
                                              colWidth, maxLines)
            outputLines = utilities.wrapStringList(self.getFileContents(TestFile.OUTPUT, maxLines = maxLines),
                                                         colWidth, maxLines)
            tableHeight = max(len(inputLines), len(outputLines))
            inputLines = utilities.padListRight(inputLines, tableHeight, "")
            outputLines = utilities.padListRight(outputLines, tableHeight, "")
            table.table_data += [[il, ol] for il, ol in zip(inputLines, outputLines)]
            return table
        else:
            colWidth = shutil.get_terminal_size().columns - 5
            table.inner_row_border = True
            table.table_data.append(["Input".ljust(colWidth)])
            table.table_data.append([utilities.wrapString(self.getFileContents(TestFile.INPUT, maxLines = maxLines),
                                                         colWidth, maxLines)])
            table.table_data.append(["Output".ljust(colWidth)])
            table.table_data.append([utilities.wrapString(self.getFileContents(TestFile.OUTPUT, maxLines = maxLines),
                                                         colWidth, maxLines)])
            return table

    def deleteFiles(self):
        """ Deletes all the files this test contains. """
        for fileName in self.fileTable.values():
            try:
                os.remove(fileName)
            except FileNotFoundError:
                pass

    @classmethod
    def __deserialize__(cls, obj):
        result = Test(obj["ID"])
        return result

def getUnusedTest(testList):
    """ Get an unused test from the provided test manifest
    in testList. """
    for i in itertools.count(1):
        if str(i) not in testList:
            return Test(str(i))


