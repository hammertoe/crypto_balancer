import argparse
import configparser
import logging
import sys

from crypto_balancer.simple_balancer import SimpleBalancer
from crypto_balancer.ccxt_exchange import CCXTExchange, exchanges
from crypto_balancer.executor import Executor
from crypto_balancer.portfolio import Portfolio

logger = logging.getLogger(__name__)


def main(args=None):
    config = configparser.ConfigParser()
    config.read('config.ini')

    def exchange_choices():
        return set(config.sections()) & set(exchanges)

    parser = argparse.ArgumentParser(
        description='Balance holdings on an exchange.')
    parser.add_argument('--trade', action="store_true",
                        help='Actually place orders')
    parser.add_argument('--force', action="store_true",
                        help='Force rebalance')
    parser.add_argument('--valuebase', default='USDT',
                        help='Currency to value portfolio in')
    parser.add_argument('--cancel', action="store_true",
                        help='Cancel open orders first')
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

    exchange = CCXTExchange(args.exchange,
                            targets.keys(),
                            config['api_key'],
                            config['api_secret'])

    print("Connected to exchange: {}".format(exchange.name))
    print()

    if args.cancel:
        print("Cancelling open orders...")
        for order in exchange.cancel_orders():
            print("Cancelled order:", order['symbol'], order['id'])
        print()

    threshold = float(config['threshold'])
    portfolio = Portfolio.make_portfolio(targets, exchange, threshold)

    print("Balances:")
    for cur, bal in portfolio.balances.items():
        print("  {} {}".format(cur, bal))

    print()

    print("Porfolio value:")
    for cur, pct in portfolio.balances_pct.items():
        print("  {} ({:.2f} / {:.2f}%)".format(cur, pct, targets[cur]))

    print("Total value: {:.2f} {}".format(portfolio.valuation_quote,
                                          portfolio.quote_currency))
    print()

    balancer = SimpleBalancer()
    executor = Executor(portfolio, exchange, balancer)
    res = executor.run(force=args.force, trade=args.trade)

    print("Initial Portfolio balance error: {:.2g} / {:.2g} {}".format(
        res['initial_portfolio'].balance_rmse,
        threshold,
        "[FORCE]" if args.force else ""))

    if not res['proposed_portfolio']:
        print("No balancing needed")
    else:
        print("Balancing needed:")
        print("Proposed Portfolio balance error: {:.2g}".format(
            res['proposed_portfolio'].balance_rmse))
        print("Orders:")
        for order in res['orders']:
            print("  " + str(order))
        total_fee = '%s' % float('%.4g' % res['total_fee'])
        print("Total fees to re-balance: {} {}"
              .format(total_fee,
                      portfolio.quote_currency))

        print()
        if args.trade:
            for order in res['success']:
                print("Success: {}".format(order))

            for order in res['errors']:
                print("Failed: {}".format(order))


if __name__ == '__main__':
    main()
