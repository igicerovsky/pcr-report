"""
This script generates a PCR report based on an analysis file and configuration parameters.
The main_report function processes the analysis file, applies data transformations, and generates
the report. The Gui class provides a graphical user interface for selecting the analysis file and
configuration folder. The gui_fn function prompts for missing arguments using the GUI.
The main function parses command line arguments, calls the GUI if necessary, and invokes the
main_report function.

Usage:
    python pcr_report.py [--cfg CONFIG_DIR] [--analysis ANALYSIS_FILE] [--ifld INIT_FOLDER]

Arguments:
    --cfg CONFIG_DIR: The directory containing the configuration files and parameters. Default is
    './data'.
    --analysis ANALYSIS_FILE: The path to the analysis file. If not provided, the GUI will be used
    to select the file.
    --ifld INIT_FOLDER: The initial folder to open in the file dialog when selecting the analysis
    file.

Returns:
    None
"""
from os import path, getcwd
import argparse

from tkinter import StringVar, Button, Entry, Tk, DISABLED
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
from pcrep.typing import PathLikeOrNone


def main_report(analysis_filepath: PathLikeOrNone, config_dir: PathLikeOrNone):
    """
    Generates a PCR report based on the analysis file and configuration directory provided.

    Args:
        analysis_filepath (PathLikeOrNone): The path to the analysis file.
        config_dir (PathLikeOrNone): The path to the configuration directory.

    Returns:
        None
    """

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


class Gui:
    """ GUI class
    """

    def __init__(self, window, config_dir: PathLikeOrNone, init_folder: PathLikeOrNone) -> None:
        self.window = window
        self.window.title('HAMILTON Analysis')
        self.window.geometry("800x80")
        self.init_folder = init_folder

        self.analysis_file = StringVar()
        self.analysis_file.set('')
        self.config_folder = StringVar()
        if config_dir:
            self.config_folder.set(config_dir)
        else:
            self.config_folder.set(path.join(getcwd(), 'data'))

        button_analysis = Button(self.window, text="Browse Analysis File",
                                 command=lambda: self.browse_analysis())
        button_analysis.grid(column=0, row=0)

        self.entry_analysis = Entry(textvariable=self.analysis_file,
                                    state=DISABLED, width=110)
        self.entry_analysis.grid(row=0, column=1,
                                 padx=10, pady=10)

        button_config = Button(self.window, text="Browse Config Folder",
                               command=lambda: self.browse_config())
        button_config.grid(column=0, row=1)
        entry_config = Entry(textvariable=self.config_folder,
                             state=DISABLED, width=110)
        entry_config.grid(row=1, column=1,
                          padx=10, pady=10)

    def browse_analysis(self) -> None:
        """ Browse analysis file name
        """
        initialdir = getcwd()
        if self.init_folder:
            initialdir = self.init_folder
        filename = filedialog.askopenfilename(initialdir=initialdir,
                                              title="Select a PCR Analysis File",
                                              filetypes=[('CSV Files', '*.csv')])
        if filename:
            self.analysis_file.set(filename)
            self.entry_analysis.update()
            self.window.destroy()

    def browse_config(self) -> None:
        """ Browse config folder
        """
        dirname = filedialog.askdirectory(initialdir=self.config_folder.get(),
                                          title="Select a Config Folder")

        if dirname:
            self.config_folder.set(dirname)

    def res(self) -> None:
        """ Result
        """
        return self.analysis_file.get(), self.config_folder.get()


def gui_fn(config_dir: PathLikeOrNone, init_folder: PathLikeOrNone) -> PathLikeOrNone:
    """ GUI dialaog for data input
    """
    window = Tk()
    gui = Gui(window, config_dir, init_folder)
    window.mainloop()
    return gui.res()


def main():
    """
    This is the main function of the PCR report script.
    It parses command line arguments, prompts for missing arguments using a GUI,
    and calls the main_report function to generate the report.

    Returns:
        None
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', help="config and params directory",
                        default='./data')
    parser.add_argument(
        "--analysis", help="analysis file path", default=None)
    parser.add_argument('--ifld', help="initial analysis folder", default=None)

    args = parser.parse_args()
    analysis_filepath = args.analysis
    config_dir = args.cfg
    init_folder = args.ifld

    if not analysis_filepath:
        analysis_filepath, config_dir = gui_fn(config_dir, init_folder)
    if not analysis_filepath or not config_dir:
        print("Canceled.")
        return None

    try:
        main_report(analysis_filepath, config_dir)
    except (KeyError, ValueError, FileNotFoundError, ) as e:
        print(e)
        print('Failed!')


if __name__ == "__main__":
    main()
