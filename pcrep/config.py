"""Configuration modole for the pcrep package
"""
import os  # type: ignore
import json

CONFIG_FILENAME: str = 'config.json'


config: dict = {}


def init_config(config_dir):
    """
    Initialize the configuration by reading the config file.

    Args:
        config_dir (str): The directory path where the config file is located.
    """
    read_config(os.path.join(config_dir, CONFIG_FILENAME))


def read_config(filename):
    """
    Read the configuration from the specified JSON file.

    Args:
        filename (str): The path to the JSON config file.

    Returns:
        dict: The configuration dictionary.

    Raises:
        KeyError: If a key in the config file is not valid.
        Exception: If a required config key is missing.
    """
    keys = ['pandoc_bin', 'pdflatex_bin', 'reference_docx',
            'params_filename', 'plasmid_control_limits_file',
            'reference_control_limits_file', 'method_limits_file']
    k_type = ['AAV8', 'AAV9', 'default']
    with open(filename, encoding="utf-8") as json_config:
        items = json.load(json_config).items()
        key, value = (None, None)
        for key, value in items:
            if key in keys:
                config[key] = value
            elif not key in k_type:
                raise KeyError(key)
        if not key in keys:
            raise (KeyError(
                f"Missing config for {key}."))

    return config
