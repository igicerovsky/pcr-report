"""Typing definitions for PCRep.
"""
import os
from typing import Union


PathLike = Union[
    str,
    os.PathLike
]

PathLikeOrNone = Union[PathLike, None]
