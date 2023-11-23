import os
import argparse

import pandas as pd

from pcrep.config import init_config
from pcrep.parse_input import parse_analysis_filepath
from pcrep.constants import CONC_NAME, DIL_FINAL_FACTOR_NAME, DIL_TYPE_NAME, DIL_SAMPLE_DESCRIPTION_NAME
from pcrep.constants import FDL_NAME, SAMPLE_NAME, SAMPLE_TYPE_NAME, SAMPLE_NUM_NAME, WELL_RESULT_NAME
from pcrep.pcrep import result_fn


DATA_DIR = './data'
PARAMS_FILENAME = 'params.json'


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
    df_conc.set_index(['sample_id'], inplace=True)

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
