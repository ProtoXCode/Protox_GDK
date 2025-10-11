import json
import os
import logging


def load_config() -> dict:
    """ Load the config file, creates a new default one if it doesn't exist """

    config_file = os.path.join(os.path.dirname(__file__), 'config.json')

    try:
        with open(config_file, encoding='utf-8', mode='r') as json_data:
            config = json.load(json_data)

    except FileNotFoundError:
        config = {'app_width': 1575,
                  'app_height': 825}
        with open(config_file, encoding='utf-8', mode='w') as json_data:
            json.dump(config, json_data, indent=4)
        logging.info('Default config file created')

    return config
