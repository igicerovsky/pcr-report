""" PCR testing module
"""
import os
import hashlib

import pandas as pd

from pcrep.config import init_config
from pcrep.parse_input import parse_analysis_filepath
from pcrep.pcrep import init_data, process_data, read_limits, read_conc
from pcrep.check import concat_comments
from pcrep.final import make_final
from pcrep.constants import (
    WELL_RESULT_NAME, SAMPLE_ID_NAME, MEAN_NAME, STDE_NAME, DIL_FINAL_FACTOR_NAME,
    CONC_NAME, CV_COLNAME, SAMPLE_TYPE_NAME, DROPLET_COLNAME, COMMENTS_NAME,
    POSITIVES_NAME, NEGATIVES_NAME, SAMPLE_NAME
)


def e2e(analysis_filepath, config_dir):
    """Test end-to-end runner."""
    init_config(config_dir)

    parsedc = parse_analysis_filepath(analysis_filepath)
    base_filepath = os.path.join(
        parsedc['analysis_dir'], f"{parsedc['date']}_{parsedc['gn']}")
    input_concentration_data = base_filepath + '_conc.xlsx'

    df = init_data(analysis_filepath,
                   read_conc(input_concentration_data))
    dc_limits = read_limits(config_dir)
    df = process_data(df, dc_limits)

    dfc = df.copy()
    df = df.assign(comments=df.apply(lambda x: concat_comments(x), axis=1))
    col_order = [SAMPLE_NAME, DIL_FINAL_FACTOR_NAME, CONC_NAME,
                 WELL_RESULT_NAME, MEAN_NAME, STDE_NAME, CV_COLNAME, COMMENTS_NAME,
                 DROPLET_COLNAME, POSITIVES_NAME, NEGATIVES_NAME, SAMPLE_TYPE_NAME]
    df = df.loc[:, col_order]

    ha = hashlib.sha1(pd.util.hash_pandas_object(df).values).hexdigest()
    hash_a = '3ca81c35872dea1e17ea883a04d1bfbbc59832ee'
    if ha != hash_a:
        raise RuntimeError(f'Analysis hash failed! {hash_a} != {ha}')

    samples = dfc.index.get_level_values(SAMPLE_ID_NAME).unique().values
    samples.sort()
    dff = make_final(dfc, samples)
    hf = hashlib.sha1(pd.util.hash_pandas_object(dff).values).hexdigest()
    hash_f = '2bacb9237ee2b3bc143c595e22aa0da2717ebb6c'
    if hf != hash_f:
        raise RuntimeError(f'Final hash faiuled !{hash_f} != {hf}')


def test_e2e():
    """Test end-to-end process."""
    analysis_filepath = ('./example/231128_GN005006-013_IDT-ITR_HT2/'
                         '231128_GN005006-013_20231128_123248_019.csv')
    config_dir = './data'

    e2e(analysis_filepath, config_dir)
