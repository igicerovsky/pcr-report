"""Script containing method checks
"""

from enum import Enum

METHOD_LIMIT_MULTIPLIER_NEGATIVE_CONTROL = 0.1
MIN_3S_NAME = 'lower 3s action'
MAX_3S_NAME = 'upper 3s action'
MIN_2S_NAME = 'lower 3s warning'
MAX_2S_NAME = 'upper 3s warning'
MIN_METHOD_NAME = 'Lower [vg/μl]'
MAX_METHOD_NAME = 'Upper [vg/μl]'
CV_THRESHOLD = 20.0  # in %


class CheckLevel(int, Enum):
    WARNING = 1
    ERROR = 0


class CheckType(str, Enum):
    METHOD = 'method'
    NEGATIVE_CONTROL = 'negative control'
    PLASMID_CONTROL = 'plasmid_control'
    CV = 'CV'


def check_limits(min, max, val, txt):
    comment = None
    if val < min:
        comment = '{} {:.2f} < {}'.format(txt, val, min)
    elif val > max:
        comment = '{} {:.2f} > {}'.format(txt, val, max)
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
    # TODO: add warming limits
    # r2s = check_limits(limits[MIN_2S_NAME], limits[MAX_2S_NAME], val, type)

    return r3s


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
    ret = None
    if type == 'rc':
        check_control(limitsdc['reference_control'].loc[target_id], val, type)
    elif type == 'pc':
        check_control(limitsdc['plasmid_control'].loc[target_id], val, type)

    return ret


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


def method_check_nc(thr, val):
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
        comment = 'nc {:.2f} > {}'.format(val, thr)
    return comment


def method_check_s(limits, val, type, txt=None):
    """Check sample
    """

    return check_limits(limits[MIN_METHOD_NAME],
                        limits[MAX_METHOD_NAME], val, txt + type)


def droplets_check(droplets_num: int, low_thr: int):
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
        comment = 'droplets {:.0f} < {}'.format(
            droplets_num, low_thr)
    return comment


def cv_check(val, thr=CV_THRESHOLD):
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
        comment = 'CV {:.1f} > {:.1f}'.format(val, thr)
    return comment
