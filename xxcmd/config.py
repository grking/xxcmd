# config.py


class Config():

    def __init__(self):

        # System default configuration
        self.config = {
            'echo-commands': True,
            'show-labels': True,
            'align-commands': True,
            'draw-window-border': True
        }

    # Provide an access helper
    def __getattr__(self, attr):
        return self.config[attr.replace('_', '-')]

    def __setattr__(self, attr, value):
        if attr != 'config':
            self.config[attr.replace('_', '-')] = value
        else:
            super().__setattr__(attr, value)
