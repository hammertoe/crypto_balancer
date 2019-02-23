class Order():
    def __init__(self, pair, direction, amount):
        if direction not in ['BUY', 'SELL']:
            raise ValueError("{} is not a valid direction".format(direction))
        self.pair = pair
        self.direction = direction
        self.amount = float(amount)

    def __str__(self):
        return "{} {} {}".format(self.direction, self.amount, self.pair)

    def __repr__(self):
        return "{} {} {}".format(self.direction, self.amount, self.pair)

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return str(self) <  str(other)
