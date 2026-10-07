import pytest

from madlove import config, storage
from madlove.scores import HighScores


class FakeLocalStorage:
    """the part of the browser's localStorage that the game uses"""

    def __init__(self):
        self.items = {}

    def getItem(self, key):
        return self.items.get(key)

    def setItem(self, key, value):
        self.items[key] = str(value)


@pytest.fixture
def local_storage():
    return FakeLocalStorage()


def test_file_store_creates_its_folder(tmp_path):
    store = storage.FileStore(str(tmp_path / 'new' / 'highscores.json'))
    store.write('[]')
    assert store.read() == '[]'


def test_file_store_without_a_file(tmp_path):
    with pytest.raises(OSError):
        storage.FileStore(str(tmp_path / 'highscores.json')).read()


def test_browser_store(local_storage):
    store = storage.BrowserStore('madlove.test', local_storage)
    store.write('[]')
    assert store.read() == '[]'
    assert local_storage.items == {'madlove.test': '[]'}


def test_browser_store_without_an_entry(local_storage):
    with pytest.raises(FileNotFoundError):
        storage.BrowserStore('madlove.test', local_storage).read()


def test_high_scores_in_the_browser(local_storage):
    # the first start saves the default list, the next one loads it
    first = HighScores(storage.BrowserStore(storage.HIGHSCORES_KEY, local_storage))
    first.load()
    first.add('NEW', 5000, free_mode=True)
    first.save()
    second = HighScores(storage.BrowserStore(storage.HIGHSCORES_KEY, local_storage))
    second.entries = []
    second.load()
    assert second.entries == first.entries
    assert second.entries[0].name == 'NEW'


def test_highscores_store_on_desktop(settings):
    store = storage.highscores_store(settings)
    assert isinstance(store, storage.FileStore)
    assert store.path.startswith(settings.data_dir)


def test_highscores_store_in_the_browser(settings, monkeypatch, local_storage):
    monkeypatch.setattr(config, 'WEB', True)
    monkeypatch.setattr(storage, 'BrowserStore', lambda key: (key, local_storage))
    assert storage.highscores_store(settings) == (storage.HIGHSCORES_KEY, local_storage)
