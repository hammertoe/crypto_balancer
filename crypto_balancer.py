import argparse
import ccxt
import configparser
import logging
import sys

logger = logging.getLogger(__name__)

class SimpleBalancer():
    def __init__(self, targets, base):
        self.targets = targets
        self.base = base
        self.rounds = 3

    def __call__(self, amounts, rates):
#        import pdb; pdb.set_trace()
        orders = []
        for i in range(self.rounds):
            differences = self.calc_base_differences(amounts, rates)
            sorted_by_diff = sorted(tuple(differences.items()), key=lambda x: x[1])
            highest_cur, highest_amount = sorted_by_diff[0]
            lowest_cur, lowest_amount = sorted_by_diff[-1]

            symbol = '{}/{}'.format(lowest_cur, highest_cur)
            direction = None

            if symbol in rates:
                direction = 'BUY'
            else:
                symbol = '{}/{}'.format(highest_cur, lowest_cur)
                if symbol in rates:
                    direction = 'SELL'
                else:
                    raise ValueError("Invalid symbol")
            rate = rates[symbol]    
#            print(symbol, direction, sorted_by_diff)
            highest_amount = -highest_amount

            if direction == 'BUY':
                # BUY
                leftover = highest_amount - lowest_amount
                to_use = lowest_amount

                if to_use == 0:
                    break

                orders.append(Order(symbol, 'BUY', to_use / rate))
                amounts[highest_cur] -= to_use 
                amounts[lowest_cur] += to_use / rate

            else:
                # SELL
                leftover = lowest_amount - highest_amount
                to_use = highest_amount

                if to_use == 0:
                    break

                orders.append(Order(symbol, 'SELL', to_use / rate))
                amounts[highest_cur] -= to_use / rate
                amounts[lowest_cur] += to_use
                

        return orders

    def calc_differences(self, amounts, rates):
        current_percentages = self.calc_cur_percentage(amounts, rates)
        differences = {}
        for cur in self.targets:
            differences[cur] = self.targets[cur] - current_percentages[cur]
        return differences

    def calc_cur_percentage(self, amounts, rates):
        # first convert the amounts into their base value
        base_values = {}
        current_percentages = {}
        for cur,amount in amounts.items():
            if cur == self.base:
                base_values[cur] = amount
            else:
                symbol = "{}/{}".format(cur, self.base)
                base_values[cur] = amount * rates[symbol]

        total_base_value = sum(base_values.values())
        for cur,base_value in base_values.items():
            current_percentages[cur] = (base_value/total_base_value) * 100
            
        return current_percentages

    def calc_base_differences(self, amounts, rates):
        # first convert the amounts into their base value
        base_values = {}
        differences = {}
        for cur,amount in amounts.items():
            if cur == self.base:
                base_values[cur] = amount
            else:
                symbol = "{}/{}".format(cur, self.base)
                base_values[cur] = amount * rates[symbol]

        total_base_value = sum(base_values.values())
        for cur in base_values:
            differences[cur] = (total_base_value*(self.targets[cur]/100.0)) - base_values[cur]
        return differences
    
class Order():
    def __init__(self, symbol, direction, amount):
        if direction not in ['BUY', 'SELL']:
            raise ValueError("{} is not a valid direction".format(direction))
        self.symbol = symbol
        self.direction = direction
        self.amount = float(amount)

    def __str__(self):
        return "{} {} {}".format(self.direction, self.amount, self.symbol)

    def __repr__(self):
        return "{} {} {}".format(self.direction, self.amount, self.symbol)

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return str(self) <  str(other)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    def exchange_choices():
        return set(config.sections()) & set(ccxt.exchanges)

    parser = argparse.ArgumentParser(description='Balance holdings on an exchange.')
    parser.add_argument('--dry', action='store_true', help='dry run. Do not actually place trades')
    parser.add_argument('--valuebase', default='USDT', help='currency to value portfolio in')
    parser.add_argument('exchange', choices=exchange_choices())
    args = parser.parse_args()

    config = config[args.exchange]

    try:
        targets = [ x.split() for x in config['targets'].split('\n') ]
        targets = dict([ [a,float(b)] for (a,b) in targets ])
    except:
        logger.error("Targets format invalid")
        sys.exit(1)

    total_target = sum(targets.values())
    if total_target != 100:
        logger.error("Total target needs to equal 100, it is {}".format(total_target))
        sys.exit(1)

    exch = getattr(ccxt, args.exchange)({'nonce': ccxt.Exchange.milliseconds})
    exch.apiKey = config['api_key']
    exch.secret = config['api_secret']
    markets = exch.load_markets()

    raw_balances = exch.fetch_balance()
    balances = {}
    for cur in targets:
        balances[cur] = raw_balances[cur]['total']

    print(balances)

