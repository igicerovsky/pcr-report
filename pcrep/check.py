"""Script containing method checks
"""

from enum import Enum

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


def check_limits(min, max, val, txt, ex=False):
    comment = None
    if val < min:
        if ex:
            comment = '{} {:.2f} < {}'.format(txt, val, min)
        else:
            comment = '<{}'.format(txt, val, min)
    elif val > max:
        if ex:
            comment = '{} {:.2f} > {}'.format(txt, val, max)
        else:
            comment = '>{}'.format(txt, val, max)
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
