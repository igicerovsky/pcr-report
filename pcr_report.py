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

from pcrep.parse_input import parse_analysis_filepath
from pcrep.xlswriter import analysis_to_excel, final_to_excel
from pcrep.typing import PathLikeOrNone
from pcrep.pcrep import analyse


def main_report(analysis_filepath: PathLikeOrNone, config_dir: PathLikeOrNone):
    """
    Generates a PCR report based on the analysis file and configuration directory provided.

    Args:
        analysis_filepath (PathLikeOrNone): The path to the analysis file.
        config_dir (PathLikeOrNone): The path to the configuration directory.

    Returns:
        None
    """

    parsedc = parse_analysis_filepath(analysis_filepath)
    base_filepath = path.join(
        parsedc['analysis_dir'], f"{parsedc['date']}_{parsedc['gn']}")

    df, dff = analyse(analysis_filepath, config_dir)

    xls_file = base_filepath + '-data_analysis.xlsx'
    analysis_to_excel(df, xls_file)

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

        def analysis_fn():
            self.browse_analysis()
        button_analysis = Button(self.window, text="Browse Analysis File",
                                 command=analysis_fn)
        button_analysis.grid(column=0, row=0)

        self.entry_analysis = Entry(textvariable=self.analysis_file,
                                    state=DISABLED, width=110)
        self.entry_analysis.grid(row=0, column=1,
                                 padx=10, pady=10)

        def browse_fn():
            self.browse_config()
        button_config = Button(self.window, text="Browse Config Folder",
                               command=browse_fn)
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

    return None


if __name__ == "__main__":
    main()
