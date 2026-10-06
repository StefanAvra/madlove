"""The base class of all scenes."""


class Scene:
    def __init__(self, game):
        self.game = game

    def render(self, screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError
