"""Final report generation.
"""
from functools import reduce
import pandas as pd

from .constants import SAMPLE_ID_NAME, TARGET_NAME  # type: ignore
from .check import WARN_INFO


DC_CONTROLS = {'IDT': {True: 'valid', False: 'not valid'},
               'ITR': {True: 'fulfill assay criteria', False: 'does not fulfill assay criteria'},
               'HT2': {True: 'valid', False: 'not valid'},
               'FVIII': {True: 'valid', False: 'not valid'},
               'FIX': {True: 'valid', False: 'not valid'}}


def get_sample(df, samnple_num, target_id=None):
    """
    Get a sample from a DataFrame based on the sample number and target ID.

    Parameters:
        df (DataFrame): The input DataFrame.
        samnple_num (int): The sample number.
        target_id (str, optional): The target ID. Defaults to None.

    Returns:
        DataFrame: The selected sample from the DataFrame.
    """
    idx = pd.IndexSlice
    if target_id:
        return df.loc[idx[samnple_num, target_id, :], :]
    else:
        return df.loc[idx[samnple_num, :, :], :]


def add_to(first, second, delim):
    """
    Concatenates two strings with a delimiter in between.

    Args:
        first (str): The first string.
        second (str): The second string.
        delim (str): The delimiter to be placed between the strings.

    Returns:
        str: The concatenated string with the delimiter.

    """
    if first:
        return first + delim + second
    elif second:
        return second
    return None


def isvalid_nc(s):
    """
    Check if the given data is valid for the specified sample.

    Args:
        s (pandas.DataFrame): The input data.

    Returns:
        tuple: A tuple containing the validity status, the corresponding value, and any comments.
    """
    comment = None
    val = s['mean [vg/ml]'].values[0]
    target = s.index.get_level_values(TARGET_NAME)[0]
    valid = not any(x is not None for x in s['droplet_check'].values)
    if any(x is not None for x in s['droplet_check'].values):
        comment = reduce(lambda s1, s2: s1 or s2, s['droplet_check'].values)
        valid = False
    if any(x is not None for x in s['method_check'].values):
        comment = add_to(comment, reduce(
            lambda s1, s2: s1 or s2, s['method_check'].values), '; ')
        valid = False
    # valid &= not any(x is not None for x in s['method_check'].values)
    val = DC_CONTROLS[target][valid]

    return (valid, val, comment)


def isvalid_prs(s):
    """
    Check if the given data is valid for plasmid, reference, sample).

    Args:
        s (pandas.DataFrame): The input data containing the following columns:
            - mean [vg/ml]: The mean value in vg/ml.
            - droplet_check: The droplet check result.
            - method_check: The method check result.
            - cv_check: The CV check result.
            - warning_check: The warning check result.
    Returns:
        tuple: A tuple containing the following elements:
            - valid (bool): True if the data is valid, False otherwise.
            - ret: The mean value in vg/ml.
            - comment: Any comment or additional information regarding the validity of the data.
    """
    ret = s['mean [vg/ml]'].values[0]
    comment = None
    valid = True
    if any(x is not None for x in s['droplet_check'].values):
        comment = reduce(lambda s1, s2: s1 or s2, s['droplet_check'].values)
        valid = False
    if any(x is not None for x in s['method_check'].values):
        comment = add_to(comment, reduce(
            lambda s1, s2: s1 or s2, s['method_check'].values), '; ')
        valid = False
    if any(x is not None for x in s['cv_check'].values):
        comment = add_to(comment, reduce(
            lambda s1, s2: s1 or s2, s['cv_check'].values), '; ')
        valid = False
    if any(x is not None for x in s['warning_check'].values):
        comment = add_to(comment, reduce(
            lambda s1, s2: s1 or s2, s['warning_check'].values), '; ')

    return (valid, ret, comment)


def process_sample(s):
    """
    Process a sample and return a dictionary containing the sample information and results.

    Args:
        s (pd.DataFrame): The sample data as a pandas DataFrame.

    Returns:
        dict: A dictionary containing the processed sample information and results.
            The dictionary has the following keys:
            - 'id': The sample ID.
            - 'target': The target(s) of the sample.
            - 'type': The sample type.
            - 'name': The sample name.
            - 'result {target} [vg/ml]': The result value for each target.
            - 'comment {target}': The comment for each target.

    """
    idxs = pd.IndexSlice
    targets = s.index.get_level_values(TARGET_NAME).unique()
    target = '/'.join(targets)
    id = int(s.index.get_level_values(SAMPLE_ID_NAME).unique()[0])
    stype = s['sample type'].array[0]
    dc = {'id': id,
          'target': target,
          'type': stype,
          'name': s['Sample'].array[0]
          }
    for t in targets:
        comment = None
        k = f'result {t} [vg/ml]'
        kc = f'comment {t}'
        if stype == 'nc':
            v = isvalid_nc(s.loc[idxs[:, [t], :], :])
            if not v[0]:
                comment = DC_CONTROLS[t][v[0]] + '; ' + v[2]
            # else:
            #     comment = DC_CONTROLS[t][v[0]]
        elif stype == 'pc' or stype == 'rc':
            v = isvalid_prs(s.loc[idxs[:, [t], :], :])
            comment = DC_CONTROLS[t][v[0]]
        elif stype == 's':
            v = isvalid_prs(s.loc[idxs[:, [t], :], :])
            if v[2] and WARN_INFO in v[2]:
                comment = v[2]
            elif v[2]:
                v = (v[0], v[2], v[1])  # nasty hack
            # if not v[0]:
            #     v = (v[0], v[2])
        dc[k] = v[1]
        dc[kc] = comment
    return dc


def make_final(df, samples):
    """
    Create a final DataFrame containing processed sample results.

    Args:
        df (pandas.DataFrame): The original DataFrame containing the samples.
        samples (list): A list of sample names to process.

    Returns:
        pandas.DataFrame: The final DataFrame with processed sample results.
    """
    dff = pd.DataFrame()
    for n in samples:
        s = get_sample(df, n)
        r = process_sample(s)
        dff = pd.concat([dff, pd.DataFrame([r])], ignore_index=True)
    dff.set_index(['id'], inplace=True)

    targets = df.index.get_level_values(TARGET_NAME).unique()
    col_order = ['target', 'name']
    col_order += [f'result {x} [vg/ml]' for x in targets]
    col_order += [f'comment {x}' for x in targets]
    dff = dff.loc[:, col_order]

    return dff
