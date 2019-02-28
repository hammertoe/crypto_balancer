import ccxt

from functools import lru_cache

exchanges = ccxt.exchanges


class CCXTExchange():

    def __init__(self, name, currencies, api_key, api_secret):
        self.name = name
        self.currencies = currencies
        self.exch = getattr(ccxt, name)({'nonce': ccxt.Exchange.milliseconds})
        self.exch.apiKey = api_key
        self.exch.secret = api_secret
        self.exch.load_markets()

    @property
    @lru_cache(maxsize=None)
    def balances(self):
        bals = self.exch.fetch_balance()['total']
        return {k: bals[k] for k in self.currencies}

    @property
    @lru_cache(maxsize=None)
    def pairs(self):
        _pairs = []
        for i in self.currencies:
            for j in self.currencies:
                pair = "{}/{}".format(i, j)
                if pair in self.exch.markets:
                    _pairs.append(pair)
        return _pairs

    @property
    @lru_cache(maxsize=None)
    def rates(self):
        _rates = {}
        for pair in self.pairs:
            orderbook = self.exch.fetchOrderBook(pair)
            high = orderbook['asks'][0][0]
            low = orderbook['bids'][0][0]
            mid = (high + low)/2.0
            _rates[pair] = mid

        return _rates

    @property
    @lru_cache(maxsize=None)
    def limits(self):
        return {pair: self.exch.markets[pair]['limits']
                for pair in self.pairs}

    @property
    @lru_cache(maxsize=None)
    def fee(self):
        return self.exch.fees['trading']['maker']

    def validate_order(self, order):
        try:
            limits = self.limits[order.pair]
        except KeyError:
            return False
        if order.amount < limits['amount']['min'] \
           or order.amount * order.price < limits['cost']['min']:
            return False
        return True

    def execute_order(self, order):
        return self.exch.create_order(order.pair,
                                      'limit',
                                      order.direction,
                                      order.amount,
                                      order.price)
