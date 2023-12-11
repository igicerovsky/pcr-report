import os
import sys
import argparse

from tkinter import *
from tkinter import filedialog, messagebox

from pcrep.config import init_config
from pcrep.parse_input import parse_analysis_filepath
from pcrep.constants import WELL_RESULT_NAME, SAMPLE_ID_NAME, MEAN_NAME, STDE_NAME, DIL_FINAL_FACTOR_NAME
from pcrep.constants import CONC_NAME, CV_COLNAME, SAMPLE_TYPE_NAME, DROPLET_CHECK_COLNAME, COMMENTS_NAME
from pcrep.constants import POSITIVES_NAME, NEGATIVES_NAME, SAMPLE_NAME
from pcrep.pcrep import init_data, process_data, read_limits, read_conc
from pcrep.check import concat_comments
from pcrep.xlswriter import analysis_to_excel, final_to_excel
from pcrep.final import make_final

# import outpy3


def main_report(analysis_filepath, config_dir):
    print(f'Analysis file {analysis_filepath}')
    print(f'Configuration directory {config_dir}')

    init_config(config_dir)

    parsedc = parse_analysis_filepath(analysis_filepath)
    base_filepath = os.path.join(
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


def browse_files():
    filename = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title="Select a PCR Analysis File",
                                          filetypes=[('CSV Files', '*.csv')])
    analysis_file.set(filename)
    entry_analysis.update()

    try:
        main_report(analysis_file.get(), config_folder.get())
    except Exception as e:
        messagebox.showerror("PCR Error", e)


def browse_folder():
    filename = filedialog.askdirectory(initialdir=config_folder,  # os.patrh.join(os.getcwd(), 'data'),
                                       title="Select a PCR Config Folder")
    analysis_file.set(filename)


def compute():
    main_report(analysis_file.get(), config_folder.get())


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, string):
        self.widget.configure(state="normal")
        self.widget.insert("end", string, (self.tag,))
        self.widget.yview(END)
        self.widget.configure(state="disabled")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', help="config and params directory",
                        default=None)
    args = parser.parse_args()

    window = Tk()
    window.title('PCR Analysis')
    window.geometry("800x400")
    window.config(background="white")

    analysis_file = StringVar()
    analysis_file.set('...')
    config_folder = StringVar()
    if args.cfg:
        config_folder.set(args.cfg)
    else:
        config_folder.set(os.path.join(os.getcwd(), 'data'))

    button_analysis = Button(window, text="Browse Analysis Files",
                             command=browse_files)
    button_analysis.grid(column=0, row=0)

    entry_analysis = Entry(textvariable=analysis_file,
                           state=DISABLED, width=110)
    entry_analysis.grid(row=0, column=1,
                        padx=10, pady=10)

    button_config = Button(window, text="Browse Config Folder",
                           command=browse_folder)
    button_config.grid(column=0, row=1)
    entry_config = Entry(textvariable=config_folder, state=DISABLED, width=110)
    entry_config.grid(row=1, column=1,
                      padx=10, pady=10)

    text = Text(window, wrap="word", width=80, height=16, state=DISABLED)
    text.grid(row=2, column=1, padx=10, pady=10)
    sys.stdout = TextRedirector(text, "stderr")
    sys.stdout = TextRedirector(text, "stdout")

    window.mainloop()
