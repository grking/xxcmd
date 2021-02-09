import os
import unittest
import tempfile
from xxcmd.config import Config


class ConfigTests(unittest.TestCase):

    def test_basic(self):
        config = Config()
        self.assertIsInstance(config, Config)

    def test_save(self):
        config = Config()
        self.assertEqual(config.show_labels, True)
        # Save to temp file
        config.show_labels = 'no'
        filename = tempfile.mktemp()
        Config.DEFAULT_CONFIG_FILE = filename
        result = config.save()
        self.assertTrue(result)
        # Save again should fail
        result = config.save()
        self.assertFalse(result)
        # Load
        config = Config()
        self.assertEqual(config.show_labels, False)
        os.unlink(filename)
