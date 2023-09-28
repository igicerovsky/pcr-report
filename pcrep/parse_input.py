"""Parsing input filenme routines
"""

import re


def parse_inputname(filename):
    result = re.split(r"[_.]", filename)
    names = ['date', 'gn', 'dateex', 'time', 'n', 'ext']
    return dict(zip(names, result))
