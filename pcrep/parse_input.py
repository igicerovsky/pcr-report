"""Parsing input filenme routines
"""

from os import path
import re
from datetime import datetime


def parse_analysis_filepath(file_path):
    """Parses analysis filename

    Parameters
    ----------
        file_path: path_like

    Returns
    -------
    dictionary
        dictionary containing parsed `datetime`, `plate` number and `protocol name`

    Raises
    ------
    Exception
        If pathname isn't a file exception is raised.
    """
    if not path.isfile(file_path):
        raise FileExistsError('Not an analysis file!')
    split = path.split(file_path)
    s = re.split(r"[_.]", split[1])
    names = ['date', 'gn', 'dateex', 'time', 'n', 'ext']
    dc = dict(zip(names, s))
    dc['datetime'] = datetime.strptime(s[2]+s[3], "%Y%m%d%H%M%S")
    dc['analysis_dir'] = split[0]

    return dc
