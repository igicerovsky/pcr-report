from os import path, getcwd
import argparse

from tkinter import *
from tkinter import filedialog

from pcrep.config import init_config
from pcrep.parse_input import parse_analysis_filepath
from pcrep.constants import WELL_RESULT_NAME, SAMPLE_ID_NAME, MEAN_NAME, STDE_NAME, DIL_FINAL_FACTOR_NAME
from pcrep.constants import CONC_NAME, CV_COLNAME, SAMPLE_TYPE_NAME, DROPLET_COLNAME, COMMENTS_NAME
from pcrep.constants import POSITIVES_NAME, NEGATIVES_NAME, SAMPLE_NAME
from pcrep.pcrep import init_data, process_data, read_limits, read_conc
from pcrep.check import concat_comments
from pcrep.xlswriter import analysis_to_excel, final_to_excel
from pcrep.final import make_final


def main_report(analysis_filepath, config_dir):
    print(f'Analysis file {analysis_filepath}')
    print(f'Configuration directory {config_dir}')

    init_config(config_dir)

    parsedc = parse_analysis_filepath(analysis_filepath)
    base_filepath = path.join(
        parsedc['analysis_dir'], '{}_{}'.format(parsedc['date'], parsedc['gn']))
    input_concentration_data = base_filepath + '_conc.xlsx'
    df_conc = read_conc(input_concentration_data)

    df = init_data(analysis_filepath, df_conc)
    dc_limits = read_limits(config_dir)
    df = process_data(df, dc_limits)

    dfc = df.copy()
    df = df.assign(comments=df.apply(lambda x: concat_comments(x), axis=1))
    col_order = [SAMPLE_NAME, DIL_FINAL_FACTOR_NAME, CONC_NAME,
                 WELL_RESULT_NAME, MEAN_NAME, STDE_NAME, CV_COLNAME, COMMENTS_NAME,
                 DROPLET_COLNAME, POSITIVES_NAME, NEGATIVES_NAME, SAMPLE_TYPE_NAME]
    df = df.loc[:, col_order]

    xls_file = base_filepath + '-data_analysis.xlsx'
    analysis_to_excel(df, xls_file)

    samples = dfc.index.get_level_values(SAMPLE_ID_NAME).unique().values
    samples.sort()
    dff = make_final(dfc, samples)
    final_file = base_filepath + '-final.xlsx'
    final_to_excel(dff, final_file)

    print('Done.')


def browse_analysis():
    filename = filedialog.askopenfilename(initialdir=getcwd(),
                                          title="Select a PCR Analysis File",
                                          filetypes=[('CSV Files', '*.csv')])
    global analysis_file, entry_analysis
    analysis_file.set(filename)
    entry_analysis.update()
    global window
    window.destroy()


def browse_config(config_folder):
    filename = filedialog.askdirectory(initialdir=config_folder,
                                       title="Select a Config Folder")
    global analysis_file
    analysis_file.set(filename)


def gui(config_dir):
    global window
    window = Tk()
    window.title('PCR Analysis')
    window.geometry("800x100")

    global analysis_file
    analysis_file = StringVar()
    analysis_file.set('...')
    global config_folder
    config_folder = StringVar()
    if config_dir:
        config_folder.set(config_dir)
    else:
        config_folder.set(path.join(getcwd(), 'data'))

    button_analysis = Button(window, text="Browse Analysis File",
                             command=browse_analysis)
    button_analysis.grid(column=0, row=0)

    global entry_analysis
    entry_analysis = Entry(textvariable=analysis_file,
                           state=DISABLED, width=110)
    entry_analysis.grid(row=0, column=1,
                        padx=10, pady=10)

    button_config = Button(window, text="Browse Config Folder",
                           command=browse_config)
    button_config.grid(column=0, row=1)
    entry_config = Entry(textvariable=config_folder, state=DISABLED, width=110)
    entry_config.grid(row=1, column=1,
                      padx=10, pady=10)
    window.mainloop()

    main_report(analysis_file.get(), config_folder.get())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', help="config and params directory",
                        default='./data')
    parser.add_argument(
        "--analysis", help="analysis file path", default=None)
    parser.add_argument('--gui', action='store_true',
                        help="use calc files as input")

    args = parser.parse_args()
    analysis_filepath = args.analysis
    config_dir = args.cfg

    if args.analysis:
        main_report(analysis_filepath, config_dir)
    else:
        gui(config_dir)


if __name__ == "__main__":
    main()
