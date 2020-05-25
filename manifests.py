""" Module for reading and writing manifests."""

# All manifest-managing code should be placed here
# Manifests are basically glorified dictionaries

# A contest manifest contains one (key, value) pair for each problem
# that is of the type (problem name, directory to problem

# A problem manifest contains five keys: (solutions, checkers, data-makers, generators, tests)
# Each of these keys is an array of Executable objects (in the tests key, it is made of Test objects)

import json, os

import executables, tests, solutions, checkers

import configuration

from contextlib import contextmanager

def checkForManifest():
    """ Return a list containing all types of manifests found. This list will contain 'contest'
    iff the file .cpu.contest_manifest exists in the directory where cpu was called. Similarly,
    the list will contain "problem" iff the file .cpu.problem_manifest exists. This list will be
    empty if neither are present. """
    manifestsFound = []
    for manifestType in ["contest", "problem"]:
        if os.path.isfile(os.path.join(os.getcwd(), f".cpu.{manifestType}_manifest.json")):
            manifestsFound.append(manifestType)
    return manifestsFound

def requireManifest(mtype):
    """ Raise a NotInCPUDirectory error if the manifest of type mtype
    cannot be found in the current working directory."""
    if mtype not in checkForManifest():
        raise NotInCPUDirectory(f"""cpu does not recognize the directory you are in. Make sure
you are in a cpu directory. Look for the .cpu.{mtype}_manifest file.""")

CUSTOM_CLASSES = [executables.Executable, tests.Test, executables.NonLocalExecutable, solutions.Solution,
                  checkers.Checker]
TYPE_NAMES = {cls.__name__: cls for cls in CUSTOM_CLASSES}

class ManifestEncoder(json.JSONEncoder):
    """ A JSON encoder that is aware of all the custom classes that may be in a manifest. """
    def default(self, obj):
        for customClass in CUSTOM_CLASSES:
            if isinstance(obj, customClass):
                return obj.__serialize__()
        return super(ManifestEncoder, self).default(obj)

class ManifestDecoder(json.JSONDecoder):
    """ A JSON decoder that is aware of all the custom classes that may be in a manifest. """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook = self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "_custom_type" not in obj:
            return obj
        for name in TYPE_NAMES:
            if obj["_custom_type"] == name:
                return TYPE_NAMES[name].__deserialize__(obj)
        return obj

EMPTY_MANIFEST = {}

def loadManifestFrom(fileName):
    """ Retrieve the encoded manifest from the file with the given filename. """
    with open(fileName, "r") as f:
        return json.load(f, cls=ManifestDecoder)

def saveManifestTo(m, fileName):
    """ Save the given manifest to a file with the given filename. """
    with open(fileName, "w") as f:
        return json.dump(m, f, cls=ManifestEncoder, indent=2)

def loadManifestType(mtype):
    """ Retrieve the manifest with the given type. If it is of the `problem` type,
    include the information in the global_manifest."""
    requireManifest(mtype)
    mret = loadManifestFrom(f".cpu.{mtype}_manifest.json")
    if mtype == "problem":
        globalManifest = loadManifestFrom(configuration.configFilePath("global_manifest.json"))
        or localKey in mret:
            if localKey not in globalManifest:
                continue
            for globalInKey in globalManifest[localKey]:
                if globalInKey in mret[localKey]:
                    continue
                mret[localKey][globalInKey] = globalManifest[localKey][globalInKey]
    return mret

@contextmanager
def modifyManifest(mtype):
    """ Context manager for manipulating a manifest file. """
    fileName = f".cpu.{mtype}_manifest.json"
    requireManifest(mtype)
    loadedM = loadManifestFrom(fileName)
    yield loadedM
    saveManifestTo(loadedM, fileName)

