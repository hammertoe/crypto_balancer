import argparse
import ccxt
import configparser
import logging
import sys

from crypto_balancer.simple_balancer import SimpleBalancer
from crypto_balancer.execute import execute_order

logger = logging.getLogger(__name__)


def main(args=None):
    config = configparser.ConfigParser()
    config.read('config.ini')

    def exchange_choices():
        return set(config.sections()) & set(ccxt.exchanges)

    parser = argparse.ArgumentParser(
        description='Balance holdings on an exchange.')
    parser.add_argument('--trade', action="store_true",
                        help='Actually place orders')
    parser.add_argument('--force', action="store_true",
                        help='Force rebalance')
    parser.add_argument('--valuebase', default='USDT',
                        help='Currency to value portfolio in')
    parser.add_argument('exchange', choices=exchange_choices())
    args = parser.parse_args()

    config = config[args.exchange]

    try:
        targets = [x.split() for x in config['targets'].split('\n')]
        targets = dict([[a, float(b)] for (a, b) in targets])
    except ValueError:
        logger.error("Targets format invalid")
        sys.exit(1)

    total_target = sum(targets.values())
    if total_target != 100:
        logger.error("Total target needs to equal 100, it is {}"
                     .format(total_target))
        sys.exit(1)

    exch = getattr(ccxt, args.exchange)({'nonce': ccxt.Exchange.milliseconds})
    exch.apiKey = config['api_key']
    exch.secret = config['api_secret']
    exch.load_markets()

    print("Connected to exchange: {}".format(exch.name))
    print()

    raw_balances = exch.fetch_balance()
    balances = {}
    print("Balances:")
    for cur in targets:
        balances[cur] = raw_balances[cur]['total']
        print("  {} {}".format(cur, balances[cur]))

    print()

    rates = fetch_rates(exch, targets.keys())
    balancer = SimpleBalancer(targets, args.valuebase,
                              threshold=float(config['threshold']))

    base_values = balancer.calc_base_values(balances, rates)
    total_base_value = sum(base_values.values())

    print("Porfolio value:")
    for cur in base_values:
        bv = base_values[cur]
        pc = (bv / total_base_value) * 100
        print("  {} {} ({:.2f} / {:.2f}%)".format(cur, bv, pc, targets[cur]))

    print("Total value: {:.2f} {}".format(total_base_value, args.valuebase))
    print()

    orders = balancer(balances, rates, force=args.force)

    if not orders['orders']:
        print("No balancing needed")
    else:
        print("Balancing needed:")
        for order in orders['orders']:
            print("  " + str(order))
        total_fee = '%s' % float('%.4g' % orders['total_fee'])
        print("Total fees to re-balance: {} {}".format(total_fee,
                                                       args.valuebase))

        print()
        if args.trade:
            for order in orders['orders']:
                limits = exch.markets[order.pair]['limits']
                if order.amount < limits['amount']['min'] \
                   or order.amount * order.price < limits['cost']['min']:
                    print("Order too small to process: {}".format(order))
                    continue
                try:
                    res = execute_order(exch, order)
                    print("Order placed: {} {} {} @ {} "
                          .format(res['symbol'], res['side'],
                                  res['amount'], res['price']))
                except Exception:
                    logger.error("Could not place order: {}".format(order))
        else:
            print("No trades placed, as '--trade' not given on command line")


def fetch_rates(exch, curs):
    pairs = []

    for i in curs:
        for j in curs:
            pair = "{}/{}".format(i, j)
            if pair in exch.markets:
                pairs.append(pair)

    rates = {}
    for pair in pairs:
        orderbook = exch.fetchOrderBook(pair)
        high = orderbook['asks'][0][0]
        low = orderbook['bids'][0][0]
        mid = (high + low)/2.0
        rates[pair] = mid

    return rates


if __name__ == '__main__':
    main()
