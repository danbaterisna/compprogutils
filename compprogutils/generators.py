import manifests, cpu_errors, utilities

import os

def getGen(name):
    """ Fetches the generator with the given name from the manifest,
    after recompiling it. """
    manifests.requireManifest("problem")
    mf = manifests.loadManifestFrom(".cpu.problem_manifest.json")
    utilities.requirePresentKey(mf["generators"], name, "generator")
    genExec = mf["generators"][name]
    genExec.compile(outputDirectory = os.path.join("programs", "generators"))
    return genExec

def fetchInputUntilEOF():
    """ Read stdin until an EOF is given. """
    lines = []
    try:
        while True:
            lines.append(input())
    except EOFError:
        pass
    return ''.join(s + '\n' for s in lines)

