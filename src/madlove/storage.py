"""Where saved data goes: a file on desktop, the browser's localStorage in the web build."""

import os

from madlove import config

HIGHSCORES_FILE = 'highscores.json'
HIGHSCORES_KEY = 'madlove.highscores'


class FileStore:
    """a text file. read() raises OSError when it doesn't exist yet"""

    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path, encoding='utf-8') as f:
            return f.read()

    def write(self, text):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(text)


class BrowserStore:
    """an entry in the browser's localStorage. read() raises FileNotFoundError when it doesn't exist yet"""

    def __init__(self, key, local_storage=None):
        if local_storage is None:
            from platform import window  # pygbag adds the browser's window object to this module

            local_storage = window.localStorage
        self.key = key
        self.local_storage = local_storage

    def read(self):
        text = self.local_storage.getItem(self.key)
        if text is None:
            raise FileNotFoundError(f'nothing saved in localStorage under {self.key!r}')
        return text

    def write(self, text):
        self.local_storage.setItem(self.key, text)


def highscores_store(settings):
    if config.WEB:
        return BrowserStore(HIGHSCORES_KEY)
    return FileStore(os.path.join(settings.data_dir, HIGHSCORES_FILE))
