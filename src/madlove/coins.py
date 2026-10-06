"""Credits and lives. A coin buys a credit, and starting a game or continuing turns a credit into lives."""

LIVES_PER_CREDIT = 3


class Wallet:
    def __init__(self):
        self.credit = 0
        self.lives = 0

    def add_coin(self):
        self.credit += 1

    def consume_coin(self):
        """turns a credit into a full set of lives"""
        if self.credit > 0:
            self.lives = LIVES_PER_CREDIT
            self.credit -= 1

    def add_life(self, add=1):
        self.lives += add

    def lose_life(self):
        self.lives = max(self.lives - 1, 0)

    def give_free_credit(self):
        """in free play there is always a credit"""
        if self.credit <= 0:
            self.credit = 1
