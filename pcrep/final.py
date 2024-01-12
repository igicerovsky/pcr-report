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
    idx = pd.IndexSlice
    if target_id:
        return df.loc[idx[samnple_num, target_id, :], :]
    else:
        return df.loc[idx[samnple_num, :, :], :]


def add_to(first, second, delim):
    if first:
        return first + delim + second
    elif second:
        return second
    else:
        return None


def isvalid_nc(s):
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
    # display(s)
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
