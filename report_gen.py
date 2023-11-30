import os
import argparse

from pcrep.config import init_config
from pcrep.parse_input import parse_analysis_filepath
from pcrep.constants import WELL_RESULT_NAME, SAMPLE_ID_NAME, MEAN_NAME, STDE_NAME, DIL_FINAL_FACTOR_NAME
from pcrep.constants import CONC_NAME, CV_COLNAME, SAMPLE_TYPE_NAME, DROPLET_CHECK_COLNAME, COMMENTS_NAME
from pcrep.constants import POSITIVES_NAME, NEGATIVES_NAME, SAMPLE_NAME
from pcrep.pcrep import init_data, process_data, read_limits, read_conc
from pcrep.check import concat_comments
from pcrep.xlswriter import analysis_to_excel, final_to_excel
from pcrep.final import make_final


def main_report(analysis_filepath, config_dir):
    print(f'Analysis file {analysis_filepath}')
    print(f'Configuration directory {config_dir}')

    dc = parse_analysis_filepath(analysis_filepath)
    init_config(config_dir)

    parsedc = parse_analysis_filepath(analysis_filepath)
    analysis_dir = parsedc['analysis_dir']
    base_filepath = os.path.join(
        analysis_dir, '{}_{}'.format(parsedc['date'], parsedc['gn']))
    input_concentration_data = base_filepath + '_conc.xlsx'
    df_conc = read_conc(input_concentration_data)

    df = init_data(analysis_filepath, df_conc)
    dc_limits = read_limits(config_dir)
    df = process_data(df, dc_limits)

    dfc = df.copy()
    df = df.assign(comments=df.apply(lambda x: concat_comments(x), axis=1))
    col_order = [SAMPLE_NAME, DIL_FINAL_FACTOR_NAME, CONC_NAME,
                 WELL_RESULT_NAME, MEAN_NAME, STDE_NAME, CV_COLNAME, COMMENTS_NAME,
                 DROPLET_CHECK_COLNAME, POSITIVES_NAME, NEGATIVES_NAME, SAMPLE_TYPE_NAME]
    df = df.loc[:, col_order]

    xls_file = base_filepath + '-data_analysis.xlsx'
    analysis_to_excel(df, xls_file)

    samples = dfc.index.get_level_values(SAMPLE_ID_NAME).unique().values
    samples.sort()
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
