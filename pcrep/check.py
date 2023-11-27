"""Script containing method checks
"""

from enum import Enum
from .constants import SAMPLE_TYPE_NAME, CONC_NAME, DROPLET_CHECK_COLNAME, DROPLET_THRESHOLD, CONTROL_CHECK_COLNAME_ORIG  # type: ignore


METHOD_LIMIT_MULTIPLIER_NEGATIVE_CONTROL = 0.1
MIN_3S_NAME = 'lower 3s action'
MAX_3S_NAME = 'upper 3s action'
MIN_2S_NAME = 'lower 2s warning'
MAX_2S_NAME = 'upper 2s warning'
MIN_METHOD_NAME = 'Lower [vg/μl]'
MAX_METHOD_NAME = 'Upper [vg/μl]'
CV_THRESHOLD = 20.0  # in %
WARN_INFO = 'for information'


class CheckLevel(int, Enum):
    WARNING = 1
    ERROR = 0


class CheckType(str, Enum):
    METHOD = 'method'
    NEGATIVE_CONTROL = 'negative control'
    PLASMID_CONTROL = 'plasmid_control'
    CV = 'CV'


def check_limits(min: float, max: float, val: float, txt: str, ex=False):
    comment = None
    if val < min:
        if ex:
            comment = '{} {:.2f} < {}'.format(txt, val, min)
        else:
            comment = '<{}'.format(txt)
    elif val > max:
        if ex:
            comment = '{} {:.2f} > {}'.format(txt, val, max)
        else:
            comment = '>{}'.format(txt)
    return comment


def check_wlimits(min3s, min2s, max2s, max3s, val, txt, ex=False):
    comment = None
    if val > min3s and val < min2s:
        if ex:
            comment = '{} {:0.2f} < {:.2f} < {:.2f}'.format(
                txt, min3s, val, min2s)
        else:
            comment = txt
    elif val > max2s and val < max3s:
        if ex:
            comment = '{} {:.2f} < {:.2f} < {:.2f}'.format(
                txt, max2s, val, max3s)
        else:
            comment = txt
    return comment


def control_check_fn(s, dc_limits):
    c = control_check_routing(dc_limits, s[SAMPLE_TYPE_NAME],
                              s[CONTROL_CHECK_COLNAME_ORIG], s.name[1])
    return c[0]


def warning_check_fn(s, dc_limits):
    c = control_check_routing(dc_limits, s[SAMPLE_TYPE_NAME],
                              s[CONTROL_CHECK_COLNAME_ORIG], s.name[1])
    return c[1]


def check_control(limits, val, type):
    """Check control (reference or plasmid)

    Parameters:
    -----------
    limits: pandas.series
    val: float
        Value to check
    type: str
        Control type
    """
    r3s = check_limits(limits[MIN_3S_NAME], limits[MAX_3S_NAME], val, type)
    r2s = None
    if not r3s:
        r2s = check_wlimits(limits[MIN_3S_NAME], limits[MIN_2S_NAME],
                            limits[MAX_2S_NAME], limits[MAX_3S_NAME],
                            val, WARN_INFO)

    return (r3s, r2s)


def control_check_routing(limitsdc, type, val, target_id):
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
    if type == 'rc':
        ret = check_control(
            limitsdc['reference_control'].loc[target_id], val, type)
    elif type == 'pc':
        ret = check_control(
            limitsdc['plasmid_control'].loc[target_id], val, type)

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
            comment = 'nc {:.2f} > {}'.format(val, thr)
        else:
            comment = 'nc > {}'.format(thr)
    return comment


def method_check_s(limits, val, type, txt=None):
    """Check sample
    """

    return check_limits(limits[MIN_METHOD_NAME],
                        limits[MAX_METHOD_NAME], val, txt)


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


def method_check_routing(limits, type, val, target_id):
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
    if type == 'nc':
        # order of magnitude lower than negative control limits
        t = limits.loc[target_id][MIN_METHOD_NAME] * \
            METHOD_LIMIT_MULTIPLIER_NEGATIVE_CONTROL
        ret = method_check_nc(t, val)
    elif type == 'rc' or type == 'pc' or type == 's':
        ret = method_check_s(limits.loc[target_id], val, type, 'LOQ')
    else:
        raise Exception(f'Invalid sample type {type} in check_routing!')

    return ret


def droplets_check_fn(s):
    """Droplets check callable

    Parameters:
    -----------
    s:
        sample
    """
    return droplets_check(s[DROPLET_CHECK_COLNAME], DROPLET_THRESHOLD)


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


def cv_fn(mean_val: float, std_val: float, stype: str):
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
    if stype == 'nc':
        return cv

    if isinstance(mean_val, float) and mean_val != 0.0:
        cv = 100.0 * std_val / mean_val
    return cv


def add_comment(s, n):
    if s and n:
        s += ', ' + n
    elif not s and n:
        s = n
    return s


def concat_comments(x):
    s = None
    s = add_comment(s, x['method_check'])
    s = add_comment(s, x['droplet_check'])
    s = add_comment(s, x['control_check'])
    s = add_comment(s, x['cv_check'])
    s = add_comment(s, x['warning_check'])
    return s
