"""Script containing method checks
"""

METHOD_LIMIT_MULTIPLIER_NEGATIVE_CONTROL = 0.1
MIN_3S_NAME = 'lower 3s action'
MAX_3S_NAME = 'upper 3s action'
MIN_2S_NAME = 'lower 3s warning'
MAX_2S_NAME = 'upper 3s warning'
MIN_METHOD_NAME = 'Lower [vg/ml]'
MAX_METHOD_NAME = 'Upper [vg/ml]'


def check_routing(limitsdc, type, val, target_id):
    """Routing of checks

    Parameters:
    -----------
    limitsdc: disctionary
        Dictionary with limits
    type: str
        Sample type one of 'nc', 'rc', 's'
    val: float
        Value to check
    target_id: str
        Method target one of target_id from method_limits.csv
    """
    ret = None
    if type == 'nc':
        t = limitsdc['method'].loc[:, 'Lower [vg/ml]'][target_id] * \
            METHOD_LIMIT_MULTIPLIER_NEGATIVE_CONTROL
        ret = check_nc(t, val)
    elif type == 'rc':
        ret = check_control(
            limitsdc['reference_control'].loc[target_id], val, type)
    elif type == 'pc':
        ret = check_control(limitsdc['plasmid_control'][target_id], val, type)
    elif type == 's':
        ret = None
    else:
        ret = check_s(limitsdc['method'].loc[target_id], val, type)
        raise Exception(f'Invalid sample type {type} in check_routing!')

    return ret


def check_nc(thr, val):
    """Check negative control

    Parameters:
    -----------
    thr: float
        Lower limit threshold
    val: float
        Value to check
    """

    return (val < thr, f'nc > threshold ({val} > {t})')


def check_limits(min, max, val, type):
    comment = None
    if val < min:
        comment = f'{type} {val} < {min}'
    elif val > max:
        comment = f'{type} {val} > {max}'
    return (comment == None, comment)


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


def check_s(limits, val, type):
    """Check sample
    """

    return check_limits(limits[MIN_METHOD_NAME],
                        limits[MAX_METHOD_NAME], val, type)
