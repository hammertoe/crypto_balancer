LIMITS = {'BNB/BTC': {'amount': {'max': 90000000.0, 'min': 0.01},
                      'cost': {'max': None, 'min': 0.001},
                      'price': {'max': None, 'min': None}},
          'BNB/ETH': {'amount': {'max': 90000000.0, 'min': 0.01},
                      'cost': {'max': None, 'min': 0.01},
                      'price': {'max': None, 'min': None}},
          'BNB/USDT': {'amount': {'max': 10000000.0, 'min': 0.01},
                       'cost': {'max': None, 'min': 10.0},
                       'price': {'max': None, 'min': None}},
          'BTC/USDT': {'amount': {'max': 10000000.0, 'min': 1e-06},
                       'cost': {'max': None, 'min': 10.0},
                       'price': {'max': None, 'min': None}},
          'ETH/BTC': {'amount': {'max': 100000.0, 'min': 0.001},
                      'cost': {'max': None, 'min': 0.001},
                      'price': {'max': None, 'min': None}},
          'ETH/USDT': {'amount': {'max': 10000000.0, 'min': 1e-05},
                       'cost': {'max': None, 'min': 10.0},
                       'price': {'max': None, 'min': None}},
          'XRP/BNB': {'amount': {'max': 90000000.0, 'min': 0.1},
                      'cost': {'max': None, 'min': 1.0},
                      'price': {'max': None, 'min': None}},
          'XRP/BTC': {'amount': {'max': 90000000.0, 'min': 1.0},
                      'cost': {'max': None, 'min': 0.001},
                      'price': {'max': None, 'min': None}},
          'XRP/ETH': {'amount': {'max': 90000000.0, 'min': 1.0},
                      'cost': {'max': None, 'min': 0.01},
                      'price': {'max': None, 'min': None}},
          'XRP/USDT': {'amount': {'max': 90000000.0, 'min': 0.1},
                       'cost': {'max': None, 'min': 1.0},
                       'price': {'max': None, 'min': None}},
          'XLM/USDT': {'amount': {'max': 90000000.0, 'min': 0.1},
                       'cost': {'max': None, 'min': 1.0},
                       'price': {'max': None, 'min': None}},
          'XLM/XRP': {'amount': {'max': 90000000.0, 'min': 0.1},
                      'cost': {'max': None, 'min': 1.0},
                      'price': {'max': None, 'min': None}}}


class DummyExchange():

    def __init__(self, currencies, balances, rates=None, fee=0.001):
        self.name = 'DummyExchange'
        self._currencies = currencies
        self._balances = balances
        self._rates = rates
        self._fee = fee

    @property
    def balances(self):
        return self._balances

    @property
    def pairs(self):
        _pairs = []
        for i in self._currencies:
            for j in self._currencies:
                pair = "{}/{}".format(i, j)
                _pairs.append(pair)
        return _pairs

    @property
    def rates(self):
        if self._rates:
            return self._rates

        _rates = {}
        for pair in self.pairs:
            _rates[pair] = 1.0

        return _rates

    @property
    def limits(self):
        return LIMITS

    @property
    def fee(self):
        return self._fee

    def preprocess_order(self, order):
        try:
            limits = self.limits[order.pair]
        except KeyError:
            return None
        if order.amount < limits['amount']['min'] \
           or order.amount * order.price < limits['cost']['min']:
            return None

        base, quote = order.pair.split('/')
        if order.direction.upper() == 'BUY':
            if order.amount * order.price > self._balances[quote]:
                return None

        if order.direction.upper() == 'SELL':
            if order.amount > self._balances[base]:
                return None

        order.type_ = 'LIMIT'
        return order

    def execute_order(self, order):
        base, quote = order.pair.split('/')
        if order.direction.upper() == 'BUY':
            if order.amount * order.price > self._balances[quote]:
                raise ValueError("Can't overdraw")
            self._balances[base] += order.amount
            self._balances[base] -= order.amount * self.fee
            self._balances[quote] -= order.amount * order.price

        if order.direction.upper() == 'SELL':
            if order.amount > self._balances[base]:
                raise ValueError("Can't overdraw")
            self._balances[base] -= order.amount
            self._balances[quote] += order.amount * order.price
            self._balances[quote] -= order.amount * order.price * self.fee

        return {'symbol': order.pair,
                'side': order.direction.upper(),
                'amount': order.amount,
                'price': order.price}
