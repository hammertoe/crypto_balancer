import ccxt
import configparser

exchanges = ccxt.exchanges

class CCXTExchange():

    def __init__(self, name, api_key, api_secret):
        self.name = name
        self.exch = getattr(ccxt, name)({'nonce': ccxt.Exchange.milliseconds})
        self.exch.apiKey = api_key
        self.exch.secret = api_secret
        self.exch.load_markets()

    def balance(self):
        return self.exch.fetch_balance()

    def rates(self, curs):
        pairs = []

        for i in curs:
            for j in curs:
                pair = "{}/{}".format(i, j)
                if pair in self.exch.markets:
                    pairs.append(pair)

        rates = {}
        for pair in pairs:
            orderbook = self.exch.fetchOrderBook(pair)
            high = orderbook['asks'][0][0]
            low = orderbook['bids'][0][0]
            mid = (high + low)/2.0
            rates[pair] = mid

        return rates

    def limits(self, pair):
        return exch.markets[pair]['limits']

    def fees(self):
        return self.exch.fees['trading']['maker']
    
    def execute_order(self, order):
        direction = order.direction.lower()
        return self.exch.create_order(order.pair,
                                      'limit',
                                      direction,
                                      order.amount,
                                      order.price)



        
