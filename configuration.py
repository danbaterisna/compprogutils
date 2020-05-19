""" Module for managing the cpu configuration file, and loading files from the configuration folder. """

# For path manipulation
import os
# The config file is JSON
import json

CONF_DIRECTORY = os.path.join(os.path.expanduser("~"), ".cpu")

def getConfig():
    """ Return a dict object with the config file."""
    with open(os.path.join(CONF_DIRECTORY, "config.json")) as configFile:
        return json.load(configFile)

