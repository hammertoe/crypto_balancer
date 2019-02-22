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
        orders = []
        rates["{}/{}".format(self.base, self.base)] = 1.0
        for i in range(self.rounds):
            differences = self.calc_base_differences(amounts, rates)
            sorted_by_diff = sorted(tuple(differences.items()), key=lambda x: x[1])

            to_sell_cur, to_sell_amount_base = sorted_by_diff[0]
            to_buy_cur, to_buy_amount_base = sorted_by_diff[-1]

            to_sell_amount_base = abs(to_sell_amount_base)
            to_buy_amount_base = abs(to_buy_amount_base)

            if not (to_sell_amount_base and to_buy_amount_base):
                break
            
            trade_amount_base = min(to_buy_amount_base, to_sell_amount_base)
            trade_pair = "{}/{}".format(to_buy_cur, to_sell_cur)

            to_sell_pair_base = "{}/{}".format(to_sell_cur, self.base)
            to_sell_amount_cur = trade_amount_base / rates[to_sell_pair_base]

            to_buy_pair_base = "{}/{}".format(to_buy_cur, self.base)
            to_buy_amount_cur = trade_amount_base / rates[to_buy_pair_base]
                        
            if trade_pair in rates:
                trade_direction = 'BUY'
                trade_rate = rates[trade_pair]
                trade_amount = to_buy_amount_cur
            else:
                trade_pair = "{}/{}".format(to_sell_cur, to_buy_cur)
                if trade_pair in rates:
                    trade_direction = 'SELL'
                    trade_rate = rates[trade_pair]
                    trade_amount = to_sell_amount_cur
                else:
                    raise ValueError("Invalid pair")
                
            orders.append(Order(trade_pair, trade_direction, trade_amount))

            amounts[to_sell_cur] -= to_sell_amount_cur
            amounts[to_buy_cur] += to_buy_amount_cur

        return {'orders':orders, 'amounts': amounts}

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
                pair = "{}/{}".format(cur, self.base)
                base_values[cur] = amount * rates[pair]

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
                pair = "{}/{}".format(cur, self.base)
                base_values[cur] = amount * rates[pair]

        total_base_value = sum(base_values.values())
        for cur in base_values:
            differences[cur] = (total_base_value*(self.targets[cur]/100.0)) - base_values[cur]
        return differences
    
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

