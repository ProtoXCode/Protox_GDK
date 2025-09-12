import json


def load_config(config_file: str) -> dict:

    # TODO: Generate default file if no file found!

    with open(config_file, encoding='utf-8', mode='r') as json_data:
        config = json.load(json_data)

    return config
