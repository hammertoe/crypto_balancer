class Order():
    def __init__(self, pair, direction, amount, price):
        if direction not in ['BUY', 'SELL']:
            raise ValueError("{} is not a valid direction".format(direction))
        self.pair = pair
        self.direction = direction
        self.amount = float(amount)
        self.price = float(price)

    def __str__(self):
        return "{} {} {} @ {}".format(self.direction, self.amount, self.pair, self.price)

    def __repr__(self):
        return "{} {} {} @ {}".format(self.direction, self.amount, self.pair, self.price)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return str(self) <  str(other)
