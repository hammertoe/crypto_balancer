class Order():
    def __init__(self, pair, direction, amount, price):
        if direction.upper() not in ['BUY', 'SELL']:
            raise ValueError("{} is not a valid direction".format(direction))
        self.pair = pair
        self.direction = direction
        self.amount = float(amount)
        self.price = float(price)
        self.type_ = None

    def __str__(self):
        return "{} {} {} @ {}".format(self.direction, self.amount,
                                      self.pair, self.price)

    def __repr__(self):
        return "Order('{}', '{}', {}, {})".format(self.pair, self.direction,
                                                  self.amount, self.price)

    def __eq__(self, other):
        return self.pair == other.pair and \
            self.direction == other.direction and \
            self.amount == other.amount and \
            self.price == other.price
    
    def __lt__(self, other):
        return str(self) < str(other)
