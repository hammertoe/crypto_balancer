import glob
import json
import pandas as pd

from crypto_balancer.dummy_exchange import DummyExchange


LIMITS = {'BNB/BTC': {'amount': {'max': 90000000.0, 'min': 0.01},
                      'cost': {'max': None, 'min': 0.001},
                      'price': {'max': None, 'min': None}},
          'BNB/ETH': {'amount': {'max': 90000000.0, 'min': 0.01},
                      'cost': {'max': None, 'min': 0.01},
                      'price': {'max': None, 'min': None}},
          'BNB/USD': {'amount': {'max': 10000000.0, 'min': 0.01},
                       'cost': {'max': None, 'min': 10.0},
                       'price': {'max': None, 'min': None}},
          'BTC/USD': {'amount': {'max': 10000000.0, 'min': 1e-06},
                       'cost': {'max': None, 'min': 10.0},
                       'price': {'max': None, 'min': None}},
          'ETH/BTC': {'amount': {'max': 100000.0, 'min': 0.001},
                      'cost': {'max': None, 'min': 0.001},
                      'price': {'max': None, 'min': None}},
          'ETH/USD': {'amount': {'max': 10000000.0, 'min': 1e-05},
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
          'XRP/USD': {'amount': {'max': 90000000.0, 'min': 0.1},
                       'cost': {'max': None, 'min': 1.0},
                       'price': {'max': None, 'min': None}},
          'XLM/USD': {'amount': {'max': 90000000.0, 'min': 0.1},
                       'cost': {'max': None, 'min': 1.0},
                       'price': {'max': None, 'min': None}},
          'XLM/XRP': {'amount': {'max': 90000000.0, 'min': 0.1},
                      'cost': {'max': None, 'min': 1.0},
                      'price': {'max': None, 'min': None}}}


class BacktestExchange(DummyExchange):
    
    def __init__(self, filenames, balances, fee=0.001):
        self.name = 'BacktestExchange'
        self._currencies = balances.keys()

        final_df = pd.DataFrame()
        for path in glob.glob(filenames):
            filename = path.split('/')[-1]
            pair = filename.split('.')[0]
            pair = pair.replace('-','/')
            self.pairs.append(pair)
            data = json.load(open(path, 'r'))#['Data']
            df = pd.DataFrame(data)
            df.set_index(pd.to_datetime(df['time'], unit='s'), inplace=True)
            df = df[~df.index.duplicated()]
            final_df[pair] = df['close']
#            print('loaded', pair)

        final_df.fillna(method='ffill', inplace=True)
#        self._iter = final_df['2018-01-08':].iterrows()
#        self._iter = final_df['2017-09-11':].iterrows()
#        self._iter = final_df[:'2018-12-30'].iterrows()
#        self._iter = final_df['2018-09-11':'2018-12-30'].iterrows()
        self._iter = final_df.iterrows()
        self._rates = {}
        
        self._balances = balances
        self._fee = fee

        self.tick()

    def tick(self):
        self._rates = dict(next(self._iter)[1])

    @property
    def limits(self):
        return LIMITS
