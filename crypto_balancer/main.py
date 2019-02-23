import argparse
import ccxt
import configparser
import logging
import sys

from order import Order
from simple_balancer import SimpleBalancer

logger = logging.getLogger(__name__)

def main(args=None):
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

if __name__ == '__main__':
    main()
