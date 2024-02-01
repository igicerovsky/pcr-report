""" PCR testing module
"""
import os
import hashlib

import pandas as pd

from pcrep.config import init_config
from pcrep.pcrep import analyse


def e2e_ex(analysis_filepath, config_dir):
    """Test end-to-end runner."""
    init_config(config_dir)

    df, dff = analyse(analysis_filepath, config_dir)

    ha = hashlib.sha1(pd.util.hash_pandas_object(df).values).hexdigest()
    hash_a = '3ca81c35872dea1e17ea883a04d1bfbbc59832ee'
    if ha != hash_a:
        raise RuntimeError(f'Analysis hash failed! {hash_a} != {ha}')

    hf = hashlib.sha1(pd.util.hash_pandas_object(dff).values).hexdigest()
    hash_f = '2bacb9237ee2b3bc143c595e22aa0da2717ebb6c'
    if hf != hash_f:
        raise RuntimeError(f'Final hash faiuled !{hash_f} != {hf}')


def test_e2e():
    """Test end-to-end process."""
    analysis_filepath = ('./example/231128_GN005006-013_IDT-ITR_HT2/'
                         '231128_GN005006-013_20231128_123248_019.csv')
    config_dir = './data'

    e2e_ex(analysis_filepath, config_dir)
