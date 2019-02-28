from crypto_balancer.exceptions import OrderTooSmallException


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
    def fee(self):
        return self._fee
