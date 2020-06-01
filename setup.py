#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="compprogutils",
    version=0.1,
    author="Dan Baterisna",
    author_email="dan.alden.baterisna@gmail.com",
    description="Utilities for streamlining common operations in programming contests.",

    packages = find_packages(include=["compprogutils", "compprogutils.*"]),
    install_requires = [
        "terminaltables"
    ],
    entry_points = {
        "console_scripts" : [
            "cpu = compprogutils.cpu:main"
        ]
    }
)
