from os import path
import argparse
import warnings
import json

from zlib import crc32

from pcrep.pcrep import foo


DATA_DIR = './data'
PARAMS_FILENAME = 'params.json'


def main_report(data_file, raw_input):
    print(f'Processing data {data_file}')

    foo()

    print('Done.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "datafile", help="data file with measurements", default=None)
    parser.add_argument('--csv', action='store_true',
                        help="use csv files as input")
    # TODO: maybe process the raw PCR data
    # parser.add_argument('--raw', help="use raw csv data as input",
    #                     default='./data/config.json')

    args = parser.parse_args()
    data_file = args.datafile
    raw_input = not args.csv

    main_report(data_file, raw_input)


if __name__ == "__main__":
    main()
