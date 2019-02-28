import logging
import sys

from crypto_balancer.exceptions import OrderTooSmallException

logger = logging.getLogger(__name__)

class Executor():

    def __init__(self, portfolio, exchange, balancer):
        self.portfolio = portfolio
        self.exchange = exchange
        self.balancer = balancer
        
    def run(self, force=False, trade=False):

        rates = self.exchange.rates
        balances = self.portfolio.balances

        res = {'orders': [],
               'success': [],
               'errors': [],
               'balances': balances,
               'total_fee': 0.0,
               'portfolio_value': self.portfolio.valuation_quote, }

        if self.portfolio.needs_balancing or force:
            orders = self.balancer.balance(self.portfolio, self.exchange)
        
            if orders['orders']:
                res['total_fee'] = orders['total_fee']
                res['orders'] = orders['orders']

                if trade:
                    for order in orders['orders']:
                        try:
                            r = self.exchange.execute_order(order)
                            res['success'].append(Order(r['symbol'], r['side'],
                                                       r['amount'], r['price']))
                        except OrderTooSmallException:
                            res['errors'].append(order)
                            logger.error("Order too small to place: {}".format(order))
                        except Exception:
                            res['errors'].append(order)
                            logger.error("Could not place order: {}".format(order))

        return res


