from os import path
import json

CONFIG_FILENAME = 'config.json'


config = dict()


def init_config(config_dir):
    read_config(path.join(config_dir, CONFIG_FILENAME))


def read_config(filename):
    keys = ['pandoc_bin', 'pdflatex_bin', 'reference_docx', 'params_filename']
    k_type = ['AAV8', 'AAV9', 'default']
    with open(filename) as json_config:
        items = json.load(json_config).items()
        for key, value in items:
            if key in keys:
                config[key] = value
            elif not (key in k_type):
                raise KeyError(key)
        dc = dict(items)
        if not (key in keys):
            raise (Exception(
                f"Missing config for {key}."))

    return config
