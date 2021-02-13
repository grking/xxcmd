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
            'show-commands': True,
            'align-commands': True,
            'draw-window-border': True,
            'label-padding': 2,
            'bracket-labels': False,
            'bold-labels': True,
            'whole-line-selection': True,
            'search-labels-only': False,
            'search-labels-first': True,
            'shell': 'default',
            'sort-by-label': True,
            'sort-by-command': False,
            'sort-case-sensitive': True,
            'display-help-footer': True,
            'load-global-database': True,
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
                if value.lower() in ['no', 'false', 'off']:
                    value = False
                elif value.lower() in ['yes', 'true', 'on']:
                    value = True
                elif value.isdigit():
                    value = int(value)
            self.config[attr.replace('_', '-')] = value
        else:
            super().__setattr__(attr, value)

    def save(self, overwrite=False):

        # Sanity check the file
        filename = os.path.expanduser(Config.DEFAULT_CONFIG_FILE)
        if os.path.isfile(filename) and not overwrite:
            return False

        # Make it prettier
        config = {'xxcmd': {}}
        for key, value in self.config.items():
            if value is True:
                value = 'yes'
            elif value is False:
                value = 'no'
            config['xxcmd'][key] = value

        # Write out our config
        parser = configparser.ConfigParser()
        parser.read_dict(config)
        with open(filename, 'w') as outfile:
            parser.write(outfile)
        return filename
