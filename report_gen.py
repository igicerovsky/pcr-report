import os
import argparse

import pandas as pd

from pcrep.config import init_config
from pcrep.parse_input import parse_analysis_filepath
from pcrep.constants import CONC_NAME, DIL_FINAL_FACTOR_NAME, DIL_TYPE_NAME, DIL_SAMPLE_DESCRIPTION_NAME
from pcrep.constants import FDL_NAME, SAMPLE_NAME, SAMPLE_TYPE_NAME, CV_COLNAME
from pcrep.constants import SAMPLE_NUM_NAME, WELL_RESULT_NAME, TARGET_ID_NAME, SAMPLE_ID_NAME
from pcrep.constants import VALUE_CHECK_NAME, DROPLET_CHECK_NAME
from pcrep.constants import CONTROL_CHECK_NAME, WARNING_CHECK_NAME, CV_CHECK_NAME
from pcrep.pcrep import result_fn, multindex_dfi, read_limits
from pcrep.config import config
from pcrep.check import cv_fn, method_check_fn, droplets_check_fn
from pcrep.check import control_check_fn, warning_check_fn, cv_check, concat_comments
from pcrep.xlswriter import analysis_to_excel, final_to_excel
from pcrep.final import make_final


def main_report(analysis_filepath, config_dir):
    print(f'Analysis file {analysis_filepath}')
    print(f'Configuration directory {config_dir}')

    dc = parse_analysis_filepath(analysis_filepath)
    init_config(config_dir)

    df = pd.read_csv(analysis_filepath, delimiter=';', decimal=',')
    df[CONC_NAME] = df[CONC_NAME].astype('Float64')

    parsedc = parse_analysis_filepath(analysis_filepath)
    analysis_dir = parsedc['analysis_dir']
    base_filepath = os.path.join(
        analysis_dir, '{}_{}'.format(parsedc['date'], parsedc['gn']))
    input_concentration_data = base_filepath + '_conc.csv'
    df_conc = pd.read_csv(input_concentration_data, sep=";", decimal=',')
    df_conc.set_index([SAMPLE_ID_NAME], inplace=True)

    df.loc[:, [FDL_NAME]] = df[SAMPLE_NUM_NAME].map(
        df_conc[DIL_FINAL_FACTOR_NAME], na_action='ignore')
    df.loc[:, [SAMPLE_NAME]] = df[SAMPLE_NUM_NAME].map(
        df_conc[DIL_SAMPLE_DESCRIPTION_NAME], na_action='ignore')
    df.loc[:, [SAMPLE_TYPE_NAME]] = df[SAMPLE_NUM_NAME].map(
        df_conc[DIL_TYPE_NAME], na_action='ignore')
    df = df.dropna(subset=[SAMPLE_TYPE_NAME])

    targets = df['Target'].unique()
    samples = df['Sample description 1'].unique()
    samples.sort()
    df.loc[:, [WELL_RESULT_NAME]] = df.apply(lambda x: result_fn(
        x['Conc(copies/µL)'], x['final dilution factor']), axis=1)

    dc_limits = read_limits(config_dir)

    dfi = multindex_dfi(df)
    dfi.loc[:, ['mean [vg/ml]']
            ] = dfi.groupby(level=["sample_id", 'Target']).apply(lambda x: x['vg/ml'].mean())
    dfi.loc[:, ['STDE']] = dfi.groupby(level=["sample_id", 'Target']).apply(
        lambda x: x['vg/ml'].std(ddof=0))
    dfi.loc[:, [CV_COLNAME]] = dfi.apply(lambda x: cv_fn(
        x['mean [vg/ml]'], x['STDE'], x['sample type']), axis=1)

    dfi.loc[:, [VALUE_CHECK_NAME]] = dfi.apply(
        lambda x: method_check_fn(x, dc_limits), axis=1)
    dfi.loc[:, [DROPLET_CHECK_NAME]] = dfi.apply(
        lambda x: droplets_check_fn(x), axis=1)

    dfi.loc[:, [CONTROL_CHECK_NAME]] = dfi.apply(
        lambda x: control_check_fn(x, dc_limits), axis=1)
    dfi.loc[:, [WARNING_CHECK_NAME]] = dfi.apply(
        lambda x: warning_check_fn(x, dc_limits), axis=1)

    dfi.loc[:, [CV_CHECK_NAME]] = dfi.apply(
        lambda x: cv_check(x[CV_COLNAME]), axis=1)

    dfc = dfi.copy()
    dfi = dfi.assign(comments=dfi.apply(lambda x: concat_comments(x), axis=1))
    col_order = ['Sample', 'final dilution factor', 'Conc(copies/µL)',
                 'vg/ml', 'mean [vg/ml]', 'STDE', 'CV [%]', 'comments',
                 'Accepted Droplets', 'Positives', 'Negatives', 'sample type']
    dfi = dfi.loc[:, col_order]

    xls_file = base_filepath + '-data_analysis.xlsx'
    analysis_to_excel(df, xls_file)

    dff = make_final(dfc, samples)
    final_file = base_filepath + '-final.xlsx'
    final_to_excel(dff, final_file)

    print('Done.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "analysis", help="analysis file path", default=None)
    parser.add_argument('--cfg', help="config and params directory",
                        default='./data')

    args = parser.parse_args()
    analysis_filepath = args.analysis.rstrip("/\\")
    config_dir = args.cfg

    main_report(analysis_filepath, config_dir)


if __name__ == "__main__":
    main()
