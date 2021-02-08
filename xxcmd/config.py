# config.py
import os
import configparser


class Config():

    DEFAULT_CONFIG_FILE = '~/.xxcmdrc'

    def __init__(self):

        # System default configuration
        self.config = {
            'echo-commands': True,
            'show-labels': True,
            'align-commands': True,
            'draw-window-border': True,
            'label-padding': 2
        }

        # If there is a config file merge that in too
        filename = os.path.expanduser(Config.DEFAULT_CONFIG_FILE)
        if os.path.isfile(filename):
            parser = configparser.ConfigParser()
            parser.read(filename)
            if parser.has_section('xxcmd'):
                for key, value in parser.items('xxcmd'):
                    self.__setattr__(key, value)

    # Provide an access helper
    def __getattr__(self, attr):
        return self.config[attr.replace('_', '-')]

    def __setattr__(self, attr, value):
        if attr != 'config':
            if type(value) is str:
                if value.lower() in ['no', 'false']:
                    value = False
                elif value.lower() in ['yes', 'true']:
                    value = True
                elif value.isdigit():
                    value = int(value)
            self.config[attr.replace('_', '-')] = value
        else:
            super().__setattr__(attr, value)
