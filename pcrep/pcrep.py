"""PCR reporting script
"""
from os import path

import pandas as pd

from .constants import SAMPLE_ID_NAME, TARGET_ID_NAME
from .config import config


def well2idx(well_id):
    """Convert well id string to indices

    Parameters:
    -----------
    well_id : string
        Conatenated well identification

    Returns:
    tuple(string, int)
        Splitted row and column identification
    """
    wr = well_id[0]
    wc = int(well_id[1:])
    return wr, wc


def result_fn(conc, dil, a=20.0, b=2.0):
    """Compute results

    Parameters:
    conc : float
    dil : float
        final dilution factor of the sample
    a : float
        ddPCR Volume 20 µL
    b : float
        Sample volume in the ddPCR reaction 2 µL
    """
    return ((a * conc) * (1000.0 / b)) * dil


def multindex_dfi(df):
    """Create multindex dataframe from analysis data

    Parameters:
    df : original dataframe

    """
    df.reset_index(inplace=True)
    df.rename(columns={'Sample description 1': SAMPLE_ID_NAME}, inplace=True)
    df.set_index([SAMPLE_ID_NAME, 'Target', 'Well'], inplace=True)
    df.sort_index(inplace=True)
    df.sort_index(axis=1)
    df.drop(['Sample description 2', 'Sample description 3', 'Sample description 4',
            'TargetType', 'Supermix', 'Status', 'Experiment', 'SampleType'],
            axis=1, inplace=True)
    return df


def read_limits(config_dir):
    """Read limits from data files
    """
    palsmid_control_limits = pd.read_csv(
        path.join(config_dir, config['plasmid_control_limits_file']))
    palsmid_control_limits.set_index(['Target'], inplace=True)

    reference_control_limits = pd.read_csv(
        path.join(config_dir, config['reference_control_limits_file']))
    reference_control_limits.set_index(['Target'], inplace=True)

    method_limits = pd.read_csv(path.join(
        config_dir, config['method_limits_file']))
    method_limits.set_index([TARGET_ID_NAME], inplace=True)

    dc_limits = {'method': method_limits, 'reference_control': reference_control_limits,
                 'plasmid_control': palsmid_control_limits}

    return dc_limits
