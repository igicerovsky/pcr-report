"""PCR reporting script
"""
from os import path

import pandas as pd

from .constants import SAMPLE_ID_NAME, TARGET_ID_NAME  # type: ignore
from .config import config  # type: ignore
from .constants import CONC_NAME, DIL_FINAL_FACTOR_NAME, DIL_TYPE_NAME, DIL_SAMPLE_DESCRIPTION_NAME
from .constants import FDL_NAME, SAMPLE_NAME, SAMPLE_TYPE_NAME, CV_COLNAME, TARGET_NAME
from .constants import SAMPLE_NUM_NAME, WELL_RESULT_NAME
from .constants import VALUE_CHECK_NAME, DROPLET_CHECK_NAME, MEAN_NAME, STDE_NAME
from .constants import CONTROL_CHECK_NAME, WARNING_CHECK_NAME, CV_CHECK_NAME
from .check import cv_fn, method_check_fn, droplets_check_fn
from .check import control_check_fn, warning_check_fn, cv_check
from .typing import PathLike


def read_conc(input_concentration_data: PathLike):
    """
    Read concentration data from an Excel file.

    Args:
        input_concentration_data (str): Path to the Excel file containing the concentration data.

    Returns:
        pandas.DataFrame: DataFrame containing the concentration data with the sample ID as the index.
    """
    df_conc = pd.read_excel(input_concentration_data)
    df_conc.set_index([SAMPLE_ID_NAME], inplace=True)
    return df_conc


def init_data(analysis_filepath: str, df_conc: pd.DataFrame):
    """Read and preprocess analysis data

    Parameters:
    -----------
    analysis_filepath : path_like
    df_conc : pandas.DataFrame
    """
    df = pd.read_csv(analysis_filepath, delimiter=';', decimal=',')
    df[CONC_NAME] = df[CONC_NAME].astype('Float64')
    df.loc[:, [FDL_NAME]] = df[SAMPLE_NUM_NAME].map(
        df_conc[DIL_FINAL_FACTOR_NAME], na_action='ignore')
    df.loc[:, [SAMPLE_NAME]] = df[SAMPLE_NUM_NAME].map(
        df_conc[DIL_SAMPLE_DESCRIPTION_NAME], na_action='ignore')
    df.loc[:, [SAMPLE_TYPE_NAME]] = df[SAMPLE_NUM_NAME].map(
        df_conc[DIL_TYPE_NAME], na_action='ignore')
    df = df.dropna(subset=[SAMPLE_TYPE_NAME])
    df.loc[:, [WELL_RESULT_NAME]] = df.apply(lambda x: result_fn(
        x[CONC_NAME], x[FDL_NAME]), axis=1)

    df = multindex_dfi(df)
    level = [SAMPLE_ID_NAME, TARGET_NAME]
    df.loc[:, [MEAN_NAME]] = df.groupby(level=level).apply(
        lambda x: x[WELL_RESULT_NAME].mean())
    df.loc[:, [STDE_NAME]] = df.groupby(level=level).apply(
        lambda x: x[WELL_RESULT_NAME].std(ddof=0))
    df.loc[:, [CV_COLNAME]] = df.apply(lambda x: cv_fn(
        x[MEAN_NAME], x[STDE_NAME], x['sample type']), axis=1)

    return df


def process_data(df: pd.DataFrame, dc_limits: dict):
    """Process analysis data

    Parameters:
    -----------
    df : pandas.DataFrame
    dc_limits : dict
        dictionary with data limits
    """
    df.loc[:, [VALUE_CHECK_NAME]] = df.apply(
        lambda x: method_check_fn(x, dc_limits), axis=1)
    df.loc[:, [DROPLET_CHECK_NAME]] = df.apply(droplets_check_fn, axis=1)

    df.loc[:, [CONTROL_CHECK_NAME]] = df.apply(
        lambda x: control_check_fn(x, dc_limits), axis=1)
    df.loc[:, [WARNING_CHECK_NAME]] = df.apply(
        lambda x: warning_check_fn(x, dc_limits), axis=1)

    df.loc[:, [CV_CHECK_NAME]] = df.apply(
        lambda x: cv_check(x[CV_COLNAME]), axis=1)

    return df


def well2idx(well_id: str):
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


def result_fn(conc: float, dil: float, a=20.0, b=2.0):
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


def multindex_dfi(df: pd.DataFrame):
    """Create multindex dataframe from analysis data

    Parameters:
    df : original dataframe

    """
    df.reset_index(inplace=True)
    df.rename(columns={'Sample description 1': SAMPLE_ID_NAME}, inplace=True)
    df.set_index([SAMPLE_ID_NAME, TARGET_NAME, 'Well'], inplace=True)
    df.sort_index(inplace=True)
    df.sort_index(axis=1)
    df.drop(['Sample description 2', 'Sample description 3', 'Sample description 4',
            'TargetType', 'Supermix', 'Status', 'Experiment', 'SampleType'],
            axis=1, inplace=True)
    return df


def read_limits(config_dir: PathLike):
    """Read limits from data files
    """
    palsmid_control_limits = pd.read_csv(
        path.join(config_dir, config['plasmid_control_limits_file']))
    palsmid_control_limits.set_index([TARGET_NAME], inplace=True)

    reference_control_limits = pd.read_csv(
        path.join(config_dir, config['reference_control_limits_file']))
    reference_control_limits.set_index([TARGET_NAME], inplace=True)

    method_limits = pd.read_csv(path.join(
        config_dir, config['method_limits_file']))
    method_limits.set_index([TARGET_ID_NAME], inplace=True)

    dc_limits = {'method': method_limits, 'reference_control': reference_control_limits,
                 'plasmid_control': palsmid_control_limits}

    return dc_limits
