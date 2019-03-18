import unittest

from crypto_balancer.simple_balancer import SimpleBalancer
from crypto_balancer.portfolio import Portfolio
from crypto_balancer.dummy_exchange import DummyExchange
from crypto_balancer.executor import Executor
from crypto_balancer.order import Order

import sys
sys.path.append('..')      # XXX Probably needed to import your code


class test_Order(unittest.TestCase):

    def test_createOrder(self):
        order = Order('XRP/USDT', 'BUY', 10, 0.32)
        self.assertEqual(order.pair, 'XRP/USDT')
        self.assertEqual(order.direction, 'BUY')
        self.assertEqual(order.amount, 10)
        self.assertEqual(order.price, 0.32)

        order = Order('XRP/BTC', 'SELL', 20, 0.0001)
        self.assertEqual(order.pair, 'XRP/BTC')
        self.assertEqual(order.direction, 'SELL')
        self.assertEqual(order.amount, 20)
        self.assertEqual(order.price, 0.0001)

    def test_createOrderBadDirection(self):
        with self.assertRaises(ValueError):
            Order('XRP/USDT', 'FOO', 10, 0.001)

    def test_compareOrders(self):
        a = Order('XRP/USDT', 'BUY', 10, 0.32)
        b = Order('XRP/USDT', 'BUY', 10, 0.32)
        self.assertEqual(a, b)

        c = Order('XRP/BTC', 'SELL', 20, 0.0001)
        self.assertNotEqual(a, c)

        self.assertLess(a, c)
        self.assertGreater(c, a)

    def test_ReprStrOrder(self):
        a = Order('XRP/USDT', 'BUY', 10, 0.32)
        self.assertEqual(str(a), 'BUY 10.0 XRP/USDT @ 0.32')
        self.assertEqual(repr(a), "Order('XRP/USDT', 'BUY', 10.0, 0.32)")

    def test_HashOrder(self):
        a = Order('XRP/USDT', 'BUY', 10, 0.32)
        b = Order('XRP/USDT', 'BUY', 10, 0.32)
        c = Order('XLM/USDT', 'BUY', 10, 0.32)
        d = Order('XLM/USDT', 'SELL', 10, 0.32)
        e = Order('XLM/USDT', 'SELL', 100, 0.32)
        f = Order('XLM/USDT', 'SELL', 100, 0.1)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(f))
        self.assertNotEqual(hash(b), hash(c))
        self.assertNotEqual(hash(c), hash(d))
        self.assertNotEqual(hash(d), hash(e))
        self.assertNotEqual(hash(e), hash(f))


class test_Portfolio(unittest.TestCase):
    targets = {'XRP': 45,
               'XLM': 45,
               'USDT': 10, }

    targets2 = {'XRP': 40,
                'XLM': 40,
                'USDT': 20, }

    balances = {'XRP': 450,
                'XLM': 450,
                'USDT': 100, }

    zero_balances = {'XRP': 0,
                     'XLM': 0,
                     'USDT': 0, }

    def test_create_portfolio_defaults(self):
        exchange = DummyExchange(self.targets.keys(), self.targets)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        self.assertEqual(portfolio.threshold, 1.0)
        self.assertEqual(portfolio.quote_currency, 'USDT')
        self.assertEqual(portfolio.exchange, exchange)
        self.assertEqual(portfolio.targets, self.targets)

    def test_create_portfolio_custom(self):
        exchange = DummyExchange(self.targets.keys(), self.targets)
        portfolio = Portfolio.make_portfolio(self.targets,
                                             exchange, 2.0, 'BTC')

        self.assertEqual(portfolio.threshold, 2.0)
        self.assertEqual(portfolio.quote_currency, 'BTC')
        self.assertEqual(portfolio.exchange, exchange)
        self.assertEqual(portfolio.targets, self.targets)

    def test_create_portfolio_balances_quote(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        self.assertEqual(portfolio.balances_quote, self.balances)

    def test_create_portfolio_valuation_quote(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        self.assertEqual(portfolio.valuation_quote, 1000)

    def test_create_portfolio_balances_pct(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        self.assertEqual(portfolio.balances_pct, self.targets)
        self.assertNotEqual(portfolio.balances_pct, self.targets2)

    def test_create_portfolio_balances_pct_zero(self):
        exchange = DummyExchange(self.targets.keys(), self.zero_balances)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        self.assertEqual(portfolio.balances_pct, self.zero_balances)
        self.assertNotEqual(portfolio.balances_pct, self.targets)

    def test_create_portfolio_metric1(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        self.assertEqual(portfolio.balance_rms_error, 0)

    def test_create_portfolio_metric2(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets2, exchange)

        self.assertAlmostEqual(portfolio.balance_rms_error, 7.071067, 5)

    def test_create_portfolio_metric_zero(self):
        exchange = DummyExchange(self.targets.keys(), self.zero_balances)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        self.assertEqual(portfolio.balance_rms_error, 0)

    def test_create_portfolio_differences_quote1(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        expected = {'XRP': 0,
                    'XLM': 0,
                    'USDT': 0, }

        self.assertEqual(portfolio.differences_quote, expected)

    def test_create_portfolio_differences_quote2(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets2, exchange)

        expected = {'XRP': -50,
                    'XLM': -50,
                    'USDT': 100, }

        self.assertEqual(portfolio.differences_quote, expected)

    def test_create_portfolio_needs_balancing1(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets, exchange)

        self.assertFalse(portfolio.needs_balancing)

    def test_create_portfolio_needs_balancing2(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets2, exchange)

        self.assertTrue(portfolio.needs_balancing)

    def test_create_portfolio_needs_balancing3(self):
        exchange = DummyExchange(self.targets.keys(), self.balances)
        portfolio = Portfolio.make_portfolio(self.targets2,
                                             exchange, threshold=20)

        self.assertFalse(portfolio.needs_balancing)

    def test_base_differences_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }

        exchange = DummyExchange(targets.keys(), current, rates)
        portfolio = Portfolio.make_portfolio(targets, exchange)

        expected = {'XRP': 40,
                    'XLM': 0,
                    'USDT': -40, }
        self.assertEqual(portfolio.differences_quote,
                         expected)

    def test_base_differences_start_xrp_xlm_usdt_rates2(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4,
                 'USDT/USDT': 1.0, }

        exchange = DummyExchange(targets.keys(), current, rates)
        portfolio = Portfolio.make_portfolio(targets, exchange)

        expected = {'XRP': 40,
                    'XLM': 0,
                    'USDT': -40, }
        self.assertEqual(portfolio.differences_quote,
                         expected)

        final_base = {}
        final_targets = {}
        total_base = 0
        for cur in current:
            symbol = "{}/{}".format(cur, portfolio.quote_currency)
            final_base[cur] = current[cur] * exchange.rates[symbol]['mid']
            final_base[cur] += portfolio.differences_quote[cur]
            total_base += final_base[cur]

        for cur in final_base:
            final_targets[cur] = (final_base[cur] / total_base) * 100

        self.assertEqual(targets, final_targets)

    def test_base_differences_start_xrp_xlm_usdt_rates3(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 40,
                   'XLM': 40,
                   'USDT': 20, }
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5,
                 'USDT/USDT': 1.0, }

        exchange = DummyExchange(targets.keys(), current, rates)
        portfolio = Portfolio.make_portfolio(targets, exchange)

        expected = {'XRP': 7,
                    'XLM': 7,
                    'USDT': -14,
                    }
        self.assertEqual(portfolio.differences_quote,
                         expected)

        final_base = {}
        final_targets = {}
        total_base = 0
        for cur in current:
            symbol = "{}/{}".format(cur, portfolio.quote_currency)
            final_base[cur] = current[cur] * exchange.rates[symbol]['mid']
            final_base[cur] += portfolio.differences_quote[cur]
            total_base += final_base[cur]

        for cur in final_base:
            final_targets[cur] = (final_base[cur] / total_base) * 100

        self.assertEqual(targets, final_targets)


class test_SimpleBalancer(unittest.TestCase):

    def execute(self, targets, current, rates, fee=0.001, max_orders=5, mode='mid'):
        exchange = DummyExchange(targets.keys(), current, rates, fee)
        portfolio = Portfolio.make_portfolio(targets, exchange)

        balancer = SimpleBalancer()
        return balancer.balance(portfolio, exchange, max_orders=max_orders, mode=mode)

    def test_noop(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 450,
                   'XLM': 450,
                   'USDT': 100, }
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0, }

        res = self.execute(targets, current, rates)
        self.assertEqual(res['orders'], [])

    def test_start_all_usdt(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000, }
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }

        res = self.execute(targets, current, rates)

        expected = [Order('XLM/USDT', 'BUY', 400, 1.0),
                    Order('XRP/USDT', 'BUY', 500, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_start_all_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000, }
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5, }

        res = self.execute(targets, current, rates)

        expected = [Order('XRP/USDT', 'BUY', 1000, 0.5),
                    Order('XLM/USDT', 'BUY', 800, 0.5), ]
        self.assertEqual(res['orders'], expected)

    def test_start_all_xrp(self):
        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 1000,
                   'XLM': 0,
                   'USDT': 0, }
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0, }
        res = self.execute(targets, current, rates)

        expected = [Order('XLM/XRP', 'BUY', 400, 1.0),
                    Order('XRP/USDT', 'SELL', 100, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }
        res = self.execute(targets, current, rates)

        expected = [Order('XRP/USDT', 'BUY', 400, 0.1), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed1(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }
        res = self.execute(targets, current, rates)
        expected = [Order('XRP/USDT', 'BUY', 400, 0.1), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed2a(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 400,
                   'XLM': 400,
                   'USDT': 200, }
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0, }
        res = self.execute(targets, current, rates)
        expected = [Order('XLM/USDT', 'BUY', 50, 1.0),
                    Order('XRP/USDT', 'BUY', 50, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed2b(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 800,
                   'XLM': 800,
                   'USDT': 200, }
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5,
                 }
        res = self.execute(targets, current, rates)
        expected = [Order('XLM/USDT', 'BUY', 100, 0.5),
                    Order('XRP/USDT', 'BUY', 100, 0.5), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed3a(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 500,
                   'XLM': 500,
                   'USDT': 0, }
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }

        res = self.execute(targets, current, rates)
        expected = [Order('XLM/USDT', 'SELL', 50, 1.0),
                    Order('XRP/USDT', 'SELL', 50, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed3b(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 1000,
                   'XLM': 1000,
                   'USDT': 0, }
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5,
                 }

        res = self.execute(targets, current, rates)
        expected = [Order('XLM/USDT', 'SELL', 100, 0.5),
                    Order('XRP/USDT', 'SELL', 100, 0.5), ]
        self.assertEqual(res['orders'], expected)

    def test_real1a(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 6703.45,
                   'XLM': 0,
                   'USDT': 243.31, }
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'USDT/USDT': 1.0,
                 }

        res = self.execute(targets, current, rates)
        # Test the orders we get are correct
        expected = [Order('XLM/XRP', 'BUY', 11691.753411492733, 0.283366),
                    Order('XLM/USDT', 'BUY', 165.12549537648613, 0.09084),
                    Order('XRP/USDT', 'SELL', 34.42094463150016, 0.32076)]
        self.assertEqual(res['orders'], expected)

        # Test that the final amounts are in proportion to the targets
        base_amounts = {}
        for cur in res['proposed_portfolio'].currencies:
            pair = "{}/{}".format(cur, base)
            base_amounts[cur] = \
                res['proposed_portfolio'].balances[cur] * rates[pair]
        total_base = sum(base_amounts.values())
        for cur in targets:
            self.assertAlmostEqual(targets[cur],
                                   (base_amounts[cur] / total_base) * 100)

    def test_real2a(self):

        targets = {'XRP': 40,
                   'XLM': 20,
                   'BTC': 20,
                   'ETH': 10,
                   'USDT': 10, }
        current = {'XRP': 3402.24,
                   'XLM': 6009.74,
                   'BTC': 0.14,
                   'ETH': 1.82,
                   'USDT': 270.82}
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 'BTC/USDT': 3968.13,
                 'ETH/USDT': 147.81,
                 'USDT/USDT': 1.0,
                 }

        res = self.execute(targets, current, rates)
        # Test the orders we get are correct
        expected = [Order('XRP/USDT', 'BUY', 39.15710063598936, 0.32076),
                    Order('XLM/XRP', 'BUY', 6.551686481727605, 0.283366),
                    Order('BTC/USDT', 'SELL', 0.0037801180908891593, 3968.13),
                    Order('XRP/ETH', 'SELL', 13.236589350291911, 0.00217366),
                    Order('XRP/BTC', 'SELL', 18.648636987155573, 8.102e-05)]
        self.assertEqual(res['orders'], expected)

        # Test that the final amounts are in proportion to the targets
        base_amounts = {}
        for cur in res['proposed_portfolio'].currencies:
            pair = "{}/{}".format(cur, base)
            base_amounts[cur] = \
                res['proposed_portfolio'].balances[cur] * rates[pair]
        total_base = sum(base_amounts.values())
        for cur in targets:
            self.assertAlmostEqual(targets[cur],
                                   (base_amounts[cur] / total_base) * 100)

    def test_real2a_cheap(self):

        targets = {'XRP': 40,
                   'XLM': 20,
                   'BTC': 20,
                   'ETH': 10,
                   'USDT': 10, }
        current = {'XRP': 3402.24,
                   'XLM': 6009.74,
                   'BTC': 0.14,
                   'ETH': 1.82,
                   'USDT': 270.82}
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 'BTC/USDT': 3968.13,
                 'ETH/USDT': 147.81,
                 'USDT/USDT': 1.0,
                 }

        res = self.execute(targets, current, rates, mode='cheap')
        # Test the orders we get are correct
        
        expected = [Order('XRP/BTC', 'BUY', 28.11529866566897, 8.102e-05),
                    Order('XLM/XRP', 'BUY', 6.551686481727605, 0.283366),
                    Order('XRP/ETH', 'SELL', 13.236589350292975, 0.00217366)]
        self.assertEqual(res['orders'], expected)

    def test_real2a_cheaper(self):

        targets = {'XRP': 40,
                   'XLM': 20,
                   'BTC': 20,
                   'ETH': 10,
                   'USDT': 10, }
        current = {'XRP': 3402.24,
                   'XLM': 6009.74,
                   'BTC': 0.14,
                   'ETH': 1.82,
                   'USDT': 270.82}
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 'BTC/USDT': 3968.13,
                 'ETH/USDT': 147.81,
                 'USDT/USDT': 1.0,
                 }

        res1 = self.execute(targets, current, rates, mode='mid')
        res2 = self.execute(targets, current, rates, mode='cheap')

        self.assertTrue(res2['total_fee'] < res1['total_fee'])

        
    def test_real2a_max_orders(self):

        targets = {'XRP': 40,
                   'XLM': 20,
                   'BTC': 20,
                   'ETH': 10,
                   'USDT': 10, }
        current = {'XRP': 3352,
                   'XLM': 0,
                   'BTC': 0,
                   'ETH': 0,
                   'USDT': 243, }
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 'BTC/USDT': 3968.13,
                 'ETH/USDT': 147.81,
                 }

        res = self.execute(targets, current, rates, max_orders=3)
        # Test the orders we get are correct
        expected = [Order('ETH/USDT', 'BUY', 0.7521902983559976, 147.81),
                    Order('XLM/XRP', 'BUY', 2902.218229854689, 0.283366),
                    Order('XRP/BTC', 'SELL', 821.9151515151515, 8.102e-05)]
        self.assertEqual(res['orders'], expected)

    def test_real2_nondirect(self):

        targets = {'XRP': 40,
                   'XLM': 20,
                   'BTC': 20,
                   'ETH': 10,
                   'USDT': 10, }
        current = {'XRP': 3352,
                   'XLM': 0,
                   'BTC': 0,
                   'ETH': 0,
                   'USDT': 243, }
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 'BTC/USDT': 3968.13,
                 'ETH/USDT': 147.81,
                 'USDT/USDT': 1.0,
                 }

        res = self.execute(targets, current, rates)
        # Test the orders we get are correct
        expected = [Order('XLM/USDT', 'BUY', 1223.9239101717305, 0.09084),
                    Order('XRP/ETH', 'SELL', 410.95757575757574, 0.00217366),
                    Order('XRP/BTC', 'SELL', 821.9151515151515, 8.102e-05), ]

        self.assertEqual(res['orders'], expected)

        # Test that the final amounts are in proportion to the targets
        base_amounts = {}
        for cur in res['proposed_portfolio'].currencies:
            pair = "{}/{}".format(cur, base)
            base_amounts[cur] = \
                res['proposed_portfolio'].balances[cur] * rates[pair]
        total_base = sum(base_amounts.values())

        expected_targets = {'XRP': 51.56,
                            'XLM': 8.43,
                            'BTC': 20.00,
                            'ETH': 10.00,
                            'USDT': 10.00}

        for cur in targets:
            self.assertAlmostEqual(expected_targets[cur],
                                   (base_amounts[cur] / total_base) * 100,
                                   1)

    def test_badpair2(self):

        targets = {'XRP': 40,
                   'XLM': 20,
                   'BTC': 20,
                   'ETH': 10,
                   'USDT': 10, }
        current = {'XRP': 3352,
                   'XLM': 0,
                   'BTC': 0,
                   'ETH': 0,
                   'USDT': 243, }
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 }

        with self.assertRaises(ValueError):
            self.execute(targets, current, rates)

    def test_badpair3(self):

        targets = {'XRP': 40,
                   'XLM': 20,
                   'BTC': 20,
                   'ETH': 10,
                   'USDT': 10, }
        current = {'XRP': 3352,
                   'XLM': 0,
                   'BTC': 0,
                   'ETH': 0,
                   'USDT': 243, }
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 }

        with self.assertRaises(ValueError):
            self.execute(targets, current, rates)

    def test_zero_balance(self):

        targets = {'XRP': 40,
                   'XLM': 20,
                   'BTC': 20,
                   'ETH': 10,
                   'USDT': 10, }
        current = {'XRP': 0,
                   'XLM': 0,
                   'BTC': 0,
                   'ETH': 0,
                   'USDT': 0, }
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 'BTC/USDT': 3968.13,
                 'ETH/USDT': 147.81,
                 }

        res = self.execute(targets, current, rates)
        # Test the orders we get are correct
        expected = []
        self.assertEqual(res['orders'], expected)

    def test_fees1(self):
        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000, }
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }
        res = self.execute(targets, current, rates)
        self.assertAlmostEqual(res['total_fee'], 0.9)

    def test_fees2(self):
        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000, }
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }
        res = self.execute(targets, current, rates, 0.005)
        self.assertEqual(res['total_fee'], 4.5)


class test_Executor(unittest.TestCase):

    def create_executor(self, targets, current, rates, fee=0.001):
        exchange = DummyExchange(targets.keys(), current, rates, fee)
        portfolio = Portfolio.make_portfolio(targets, exchange)
        balancer = SimpleBalancer()
        executor = Executor(portfolio, exchange, balancer)
        return executor

    def test_threshold_inbalance(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10}
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        executor = self.create_executor(targets, current, rates)
        res = executor.run()

        # Test the orders we get are correct
        expected = []
        self.assertEqual(res['orders'], expected)

    def test_threshold_under(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 46,
                   'XLM': 45,
                   'USDT': 9}
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        executor = self.create_executor(targets, current, rates)
        res = executor.run()

        # Test the orders we get are correct
        expected = []
        self.assertEqual(res['orders'], expected)

    def test_threshold_under_force(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 460,
                   'XLM': 450,
                   'USDT': 90}
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        executor = self.create_executor(targets, current, rates)
        res = executor.run(force=True)

        # Test the orders we get are correct
        expected = [Order('XRP/USDT', 'SELL', 10, 1.0)]
        self.assertEqual(res['orders'], expected)

    def test_threshold_over(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 400,
                   'XLM': 400,
                   'USDT': 200}
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        executor = self.create_executor(targets, current, rates)
        res = executor.run(force=False)

        # TEST the orders we get are correct
        expected = [Order('XLM/USDT', 'BUY', 50, 1.0),
                    Order('XRP/USDT', 'BUY', 50, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_run_notrade(self):
        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 400,
                   'XLM': 400,
                   'USDT': 200}
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        exchange = DummyExchange(targets.keys(), current, rates, 0.001)
        portfolio = Portfolio.make_portfolio(targets, exchange)
        balancer = SimpleBalancer()
        executor = Executor(portfolio, exchange, balancer)

        res = executor.run(force=True, trade=False)

        # Test the orders we get are correct
        expected = [Order('XLM/USDT', 'BUY', 50.0, 1.0),
                    Order('XRP/USDT', 'BUY', 50.0, 1.0), ]
        self.assertEqual(res['orders'], expected)

        self.assertEqual(exchange.balances['XRP'], 400)
        self.assertEqual(exchange.balances['XLM'], 400)
        self.assertEqual(exchange.balances['USDT'], 200)

    def test_run_trade(self):
        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 400,
                   'XLM': 400,
                   'USDT': 200}
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        exchange = DummyExchange(targets.keys(), current, rates, 0.001)
        portfolio = Portfolio.make_portfolio(targets, exchange)
        balancer = SimpleBalancer()
        executor = Executor(portfolio, exchange, balancer)

        res = executor.run(force=True, trade=True)

        # Test the orders we get are correct
        expected = [Order('XLM/USDT', 'BUY', 50, 1.0),
                    Order('XRP/USDT', 'BUY', 50, 1.0), ]
        self.assertEqual(res['orders'], expected)

        self.assertEqual(exchange.balances['XRP'], 449.95)
        self.assertEqual(exchange.balances['XLM'], 449.95)
        self.assertEqual(exchange.balances['USDT'], 100)


class test_DummyExchange(unittest.TestCase):
    def setUp(self):
        balances = {'XRP': 100.0,
                    'BTC': 200.0,
                    'USDT': 300.0}
        rates = {'XRP/USDT': 0.33,
                 'BTC/USDT': 3500.0}
        self.exchange = DummyExchange(balances.keys(), balances, rates)

    def test_balances(self):
        self.assertEqual(self.exchange.balances['XRP'], 100)
        self.assertEqual(self.exchange.balances['BTC'], 200)
        self.assertEqual(self.exchange.balances['USDT'], 300)

    def test_pairs(self):
        expected = ['XRP/XRP', 'XRP/BTC', 'XRP/USDT',
                    'BTC/XRP', 'BTC/BTC', 'BTC/USDT',
                    'USDT/XRP', 'USDT/BTC', 'USDT/USDT']
        self.assertEqual(self.exchange.pairs, expected)

    def test_execute_buy(self):
        order = Order('XRP/USDT', 'BUY', 10, 0.32)
        self.exchange.execute_order(order)
        self.assertEqual(self.exchange.balances['XRP'], 109.99)
        self.assertEqual(self.exchange.balances['BTC'], 200.0)
        self.assertEqual(self.exchange.balances['USDT'], 296.8)

    def test_execute_sell(self):
        order = Order('BTC/USDT', 'SELL', 0.01, 3500)
        self.exchange.execute_order(order)
        self.assertEqual(self.exchange.balances['XRP'], 100.00)
        self.assertEqual(self.exchange.balances['BTC'], 199.99)
        self.assertEqual(self.exchange.balances['USDT'], 334.965)

    def test_execute_buy_toomuch1(self):
        order = Order('XRP/USDT', 'BUY', 1000, 0.32)
        with self.assertRaises(ValueError):
            self.exchange.execute_order(order)

    def test_execute_sell_toomuch2(self):
        order = Order('BTC/USDT', 'SELL', 1000, 3500)
        with self.assertRaises(ValueError):
            self.exchange.execute_order(order)

    def test_preprocess_order_true(self):
        order = Order('XRP/USDT', 'BUY', 50, 0.32)
        self.assertEqual(self.exchange.preprocess_order(order), order)

    def test_preprocess_order_false(self):
        order = Order('XRP/USDT', 'BUY', 0.1, 0.32)
        self.assertIsNone(self.exchange.preprocess_order(order))

    def test_preprocess_order_bad(self):
        order = Order('ZEC/USDT', 'BUY', 10, 0.32)
        self.assertIsNone(self.exchange.preprocess_order(order))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
