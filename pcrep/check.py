"""Script containing method checks
"""

from enum import Enum
from .constants import (SAMPLE_TYPE_NAME, CONC_NAME, DROPLET_COLNAME,
                        DROPLET_THRESHOLD, MEAN_NAME)
from .constants import (CONTROL_CHECK_NAME, WARNING_CHECK_NAME, CV_CHECK_NAME,
                        DROPLET_CHECK_NAME, VALUE_CHECK_NAME)

METHOD_LIMIT_MULTIPLIER_NEGATIVE_CONTROL = 0.1
MIN_3S_NAME = 'lower 3s action'
MAX_3S_NAME = 'upper 3s action'
MIN_2S_NAME = 'lower 2s warning'
MAX_2S_NAME = 'upper 2s warning'
MIN_METHOD_NAME = 'Lower [vg/μl]'
MAX_METHOD_NAME = 'Upper [vg/μl]'
CV_THRESHOLD = 20.0  # in %
WARN_INFO = 'for information only'
MIN_METHOD_NAME_INFO = 'Lower info [vg/μl]'
MAX_METHOD_NAME_INFO = 'Upper info [vg/μl]'


class CheckLevel(int, Enum):
    """
    Enumeration representing the level of a check.

    Attributes:
        WARNING (int): Represents a warning level check.
        ERROR (int): Represents an error level check.
    """
    WARNING = 1
    ERROR = 0


class CheckType(str, Enum):
    """
    Enumeration class representing different types of checks.
    """

    METHOD = 'method'
    NEGATIVE_CONTROL = 'negative control'
    PLASMID_CONTROL = 'plasmid_control'
    CV = 'CV'


def check_limits(lmin: float, lmax: float, val: float, txt: str, ex=False):
    """
    Checks if a given value falls within the specified minimum and maximum limits.

    Args:
        min (float): The minimum limit.
        max (float): The maximum limit.
        val (float): The value to be checked.
        txt (str): A text description of the value.
        ex (bool, optional): If True, includes the value and limits in the comment. 
                             Defaults to False.

    Returns:
        str: A comment indicating if the value is below or above the limits.
    """
    comment = None
    if val < lmin:
        if ex:
            comment = f"{txt} {val:.2f} < {lmin}"
        else:
            comment = f"<{txt}"
    elif val > lmax:
        if ex:
            comment = f"{txt} {val:.2f} > {lmax}"
        else:
            comment = f">{txt}"
    return comment


def check_wlimits(min3s, min2s, max2s, max3s, val, txt, ex=False):
    """
    Check if a value falls within specified limits and return a comment.

    Args:
        min3s (float): The lower limit for the range.
        min2s (float): The upper limit for the lower range.
        max2s (float): The lower limit for the upper range.
        max3s (float): The upper limit for the range.
        val (float): The value to be checked.
        txt (str): The comment to be returned if the value falls within the limits.
        ex (bool, optional): Whether to include the actual values in the comment. Defaults to False.

    Returns:
        str: The comment if the value falls within the limits, otherwise None.
    """
    comment = None
    if min3s < val < min2s:
        if ex:
            comment = f"{txt} {min3s:.2f} < {val:.2f} < {min2s:.2f}"
        else:
            comment = txt
    elif max2s < val < max3s:
        if ex:
            comment = f"{txt} {max2s:.2f} < {val:.2f} < {max3s:.2f}"
        else:
            comment = txt
    return comment


def control_check_fn(s, dc_limits):
    """
    Perform a control check based on the given sample and dc_limits.

    Args:
        s (Sample): The sample to perform the control check on.
        dc_limits (dict): The dictionary containing the control limits.
    """
    c = control_check_routing(dc_limits, s[SAMPLE_TYPE_NAME],
                              s[MEAN_NAME], s.name[1])
    return c[0]


def warning_check_fn(s, dc_limits):
    """ Perform a warning check based on the given sample and dc_limits."""
    c = control_check_routing(dc_limits, s[SAMPLE_TYPE_NAME],
                              s[MEAN_NAME], s.name[1])
    return c[1]


def check_control(limits, val, sample_type):
    """Check control (reference or plasmid)

    Parameters:
    -----------
    limits: pandas.series
    val: float
        Value to check
    type: str
        Control type
    """
    r3s = check_limits(limits[MIN_3S_NAME],
                       limits[MAX_3S_NAME], val, sample_type)
    r2s = None
    USE_2S3S = False  # not using <2s, 3s> interval check now
    if not r3s and USE_2S3S:
        txt = WARN_INFO
        r2s = check_wlimits(limits[MIN_3S_NAME], limits[MIN_2S_NAME],
                            limits[MAX_2S_NAME], limits[MAX_3S_NAME],
                            val, txt)

    return (r3s, r2s)


def control_check_routing(limitsdc, sample_type, val, target_id):
    """Routing of CONTROL checks

    Parameters:
    -----------
    limitsdc: disctionary
        Dictionary with limits
    type: str
        Sample type, valid for 'pc', 'rc' otherwise skipped
    val: float
        Value to check
    target_id: str
        Method target one of target_id from method_limits.csv
    """
    ret = (None, None)
    if sample_type == 'rc':
        ret = check_control(
            limitsdc['reference_control'].loc[target_id], val, sample_type)
    elif sample_type == 'pc':
        ret = check_control(
            limitsdc['plasmid_control'].loc[target_id], val, sample_type)

    return ret


def method_check_nc(thr, val, ex=False):
    """Check negative control

    Parameters:
    -----------
    thr: float
        Lower limit threshold
    val: float
        Value to check
    """
    comment = None
    if val > thr:
        if ex:
            comment = f'nc {val:.2f} > {thr}'
        else:
            comment = f'nc > {thr}'
    return comment


def check_limits_i(val: float,
                   min: float, max: float,
                   min_i: float, max_i: float,
                   txt: str, ex=False):
    """ Check limits
    """
    comment = None
    if min_i and val > min_i and val < min:
        comment = f'{WARN_INFO}'
    elif val < min:
        if ex:
            comment = f'{txt} {val:.2f} < {min}'
        else:
            comment = f'<{txt}'
    elif max_i and val < max_i and val > max:
        comment = f'{WARN_INFO}'
    elif val > max:
        if ex:
            comment = f'{txt} {val:.2f} > {max}'
        else:
            comment = f'>{txt}'
    return comment


def method_check_s(limits, val, txt=None):
    """Check sample
    """

    return check_limits_i(val,
                          limits[MIN_METHOD_NAME], limits[MAX_METHOD_NAME],
                          limits[MIN_METHOD_NAME_INFO], limits[MAX_METHOD_NAME_INFO],
                          txt)


def method_check_fn(s, dc_limits: dict):
    """Method check callable

    Parameters:
    -----------
    s:
        sample
    dc_limits: dict
        limits dictionary
    """
    return method_check_routing(dc_limits['method'], s[SAMPLE_TYPE_NAME],
                                s[CONC_NAME], s.name[1])


def method_check_routing(limits, sample_type, val, target_id):
    """Routing of METHOD checks

    Parameters:
    -----------
    limitsdc: disctionary
        Dictionary with limits
    type: str
        Sample type one of 'nc', 'pc', 'rc', 's'
    val: float
        Value to check
    target_id: str
        Method target one of target_id from method_limits.csv
    """
    ret = None
    if sample_type in ['nc']:
        # order of magnitude lower than negative control limits
        t = limits.loc[target_id][MIN_METHOD_NAME] * \
            METHOD_LIMIT_MULTIPLIER_NEGATIVE_CONTROL
        ret = method_check_nc(t, val)
    elif sample_type in ['rc', 'pc', 's']:
        ret = method_check_s(limits.loc[target_id], val, 'LOQ')
    else:
        raise Exception(f'Invalid sample type {sample_type} in check_routing!')

    return ret


def droplets_check_fn(s):
    """Droplets check callable

    Parameters:
    -----------
    s:
        sample
    """
    return droplets_check(s[DROPLET_COLNAME], DROPLET_THRESHOLD)


def droplets_check(droplets_num: int, low_thr: int, ex: bool = False):
    """Check number of droplets

    Parameters:
    -----------
    low_thr: int
        Minumum droplets available
    droplets_num: int
        Actual number of droplets
    """

    comment = None
    if droplets_num < low_thr:
        if ex:
            comment = 'droplets {:.0f} < {}'.format(
                droplets_num, low_thr)
        else:
            comment = 'droplets < {}'.format(low_thr)
    return comment


def cv_check(val, thr=CV_THRESHOLD, ex=False):
    """Coefficient of variation check

    Parameters:
    -----------
    val: float
        Value to check
    thr: float
        CV threshold in %
    """
    comment = None
    if val > thr:
        if ex:
            comment = 'CV {:.1f} > {:.1f}'.format(val, thr)
        else:
            comment = 'CV>{:.0f}%'.format(thr)
    return comment


def cv_fn(mean_val: float, std_val: float, sample_type: str):
    """Compute Coefficient of variation

    Parameters:
    -----------
    mean_val: float
        mean
    std_val: float
        standard deviation
    stype: str
        sample type
    """
    cv = float("nan")
    # cv is not applied to negative samples
    if sample_type == 'nc':
        return cv

    if isinstance(mean_val, float) and mean_val != 0.0:
        cv = 100.0 * std_val / mean_val
    return cv


def add_comment(s, n):
    """Add comment to string"""
    if s and n:
        s += ', ' + n
    elif not s and n:
        s = n
    return s


def concat_comments(x):
    """Concatenate comments"""
    s = None
    s = add_comment(s, x[VALUE_CHECK_NAME])
    s = add_comment(s, x[DROPLET_CHECK_NAME])
    s = add_comment(s, x[CONTROL_CHECK_NAME])
    s = add_comment(s, x[CV_CHECK_NAME])
    s = add_comment(s, x[WARNING_CHECK_NAME])
    return s
