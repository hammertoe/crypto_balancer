import unittest

from crypto_balancer.simple_balancer import SimpleBalancer
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


class test_SimpleBalancer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_noop(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 450,
                   'XLM': 450,
                   'USDT': 100, }
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0, }
        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)
        self.assertEqual(res['orders'], [])

    def test_start_all_usdt(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000, }
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }
        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 500, 1.0),
                    Order('XLM/USDT', 'BUY', 400, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_start_all_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000, }
        base = "USDT"
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5, }
        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)
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
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0, }
        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)
        expected = [Order('XLM/XRP', 'BUY', 400, 1.0),
                    Order('XRP/USDT', 'SELL', 100, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_current_percentages_start_all_usdt(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000, }
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0, }
        balancer = SimpleBalancer(targets, base)
        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 0,
                    'XLM': 0,
                    'USDT': 100, }
        self.assertEqual(current_percentages, expected)

    def test_current_percentages_start_xrp_xlm_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 0, }
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }
        balancer = SimpleBalancer(targets, base)
        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 20,
                    'XLM': 80,
                    'USDT': 0, }
        self.assertEqual(current_percentages, expected)

    def test_current_percentages_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }
        balancer = SimpleBalancer(targets, base)
        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 10,
                    'XLM': 40,
                    'USDT': 50, }
        self.assertEqual(current_percentages, expected)

    def test_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }
        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 400, 0.1), ]
        self.assertEqual(res['orders'], expected)

    def test_base_differences_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }
        balancer = SimpleBalancer(targets, base)
        differences = balancer.calc_base_differences(current, rates)
        expected = {'XRP': 40,
                    'XLM': 0,
                    'USDT': -40, }
        self.assertEqual(differences, expected)

    def test_base_differences_start_xrp_xlm_usdt_rates2(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }
        balancer = SimpleBalancer(targets, base)
        differences = balancer.calc_base_differences(current, rates)
        expected = {'XRP': 40,
                    'XLM': 0,
                    'USDT': -40, }
        self.assertEqual(differences, expected)

        final_base = {}
        final_targets = {}
        total_base = 0
        for cur in current:
            if cur == base:
                final_base[cur] = current[cur]
            else:
                symbol = "{}/{}".format(cur, base)
                final_base[cur] = current[cur] * rates[symbol]
            final_base[cur] += differences[cur]
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
        base = "USDT"
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5, }
        balancer = SimpleBalancer(targets, base)
        differences = balancer.calc_base_differences(current, rates)
        expected = {'XRP': 7,
                    'XLM': 7,
                    'USDT': -14,
                    }
        self.assertEqual(differences, expected)

        final_base = {}
        final_targets = {}
        total_base = 0
        for cur in current:
            if cur == base:
                final_base[cur] = current[cur]
            else:
                symbol = "{}/{}".format(cur, base)
                final_base[cur] = current[cur] * rates[symbol]
            final_base[cur] += differences[cur]
            total_base += final_base[cur]

        for cur in final_base:
            final_targets[cur] = (final_base[cur] / total_base) * 100

        self.assertEqual(targets, final_targets)

    def test_mixed1(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50, }
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4, }
        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 400, 0.1), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed2a(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 40,
                   'XLM': 40,
                   'USDT': 20, }
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0, }
        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)
        expected = [Order('XLM/USDT', 'BUY', 5, 1.0),
                    Order('XRP/USDT', 'BUY', 5, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed2b(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 80,
                   'XLM': 80,
                   'USDT': 20, }
        base = "USDT"
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5,
                 }
        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)
        expected = [Order('XLM/USDT', 'BUY', 10, 0.5),
                    Order('XRP/USDT', 'BUY', 10, 0.5), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed3a(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 50,
                   'XLM': 50,
                   'USDT': 0, }
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }

        balancer = SimpleBalancer(targets, base)

        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 50,
                    'XLM': 50,
                    'USDT': 0,
                    }
        self.assertEqual(current_percentages, expected)

        res = balancer(current, rates)
        expected = [Order('XRP/USDT', 'SELL', 5, 1.0),
                    Order('XLM/USDT', 'SELL', 5, 1.0), ]
        self.assertEqual(res['orders'], expected)

    def test_mixed3b(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 0, }
        base = "USDT"
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5,
                 }

        balancer = SimpleBalancer(targets, base)

        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 50,
                    'XLM': 50,
                    'USDT': 0,
                    }
        self.assertEqual(current_percentages, expected)

        res = balancer(current, rates)
        expected = [Order('XRP/USDT', 'SELL', 10, 0.5),
                    Order('XLM/USDT', 'SELL', 10, 0.5), ]
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
                 }

        balancer = SimpleBalancer(targets, base)

        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 89.83458852984236,
                    'XLM': 0.0,
                    'USDT': 10.165411470157638}
        self.assertEqual(current_percentages, expected)

        res = balancer(current, rates)
        # Test the orders we get are correct
        expected = [Order('XLM/XRP', 'BUY', 11813.295267503301, 0.283366),
                    Order('XLM/USDT', 'BUY', 43.58363936591818, 0.09084), ]
        self.assertEqual(res['orders'], expected)

        # Test that the final amounts are in proportion to the targets
        base_amounts = {}
        for cur in res['amounts']:
            pair = "{}/{}".format(cur, base)
            base_amounts[cur] = res['amounts'][cur] * rates[pair]
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
        current = {'XRP': 3352,
                   'XLM': 0,
                   'BTC': 0,
                   'ETH': 0,
                   'USDT': 243, }
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 'BTC/USDT': 3968.13,
                 'ETH/USDT': 147.81,
                 }

        balancer = SimpleBalancer(targets, base)

        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'USDT': 18.434403020292592,
                    'BTC': 0,
                    'ETH': 0,
                    'XLM': 0.0,
                    'XRP': 81.56559697970741}
        self.assertEqual(current_percentages, expected)

        res = balancer(current, rates)
        # Test the orders we get are correct
        expected = [Order('XRP/BTC', 'SELL', 821.9151515151515, 0.00008102),
                    Order('XLM/XRP', 'BUY', 2902.218229854689, 0.283366),
                    Order('ETH/USDT', 'BUY', 0.7521902983559976, 147.81),
                    Order('XRP/ETH', 'SELL', 64.3393939393937, 0.00217366), ]
        self.assertEqual(res['orders'], expected)

        # Test that the final amounts are in proportion to the targets
        base_amounts = {}
        for cur in res['amounts']:
            pair = "{}/{}".format(cur, base)
            base_amounts[cur] = res['amounts'][cur] * rates[pair]
        total_base = sum(base_amounts.values())
        for cur in targets:
            self.assertAlmostEqual(targets[cur],
                                   (base_amounts[cur] / total_base) * 100)

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
                 }

        balancer = SimpleBalancer(targets, base)

        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'USDT': 18.434403020292592,
                    'BTC': 0,
                    'ETH': 0,
                    'XLM': 0.0,
                    'XRP': 81.56559697970741}
        self.assertEqual(current_percentages, expected)

        import pdb; pdb.set_trace()
        res = balancer(current, rates)
        # Test the orders we get are correct
        expected = [Order('XRP/BTC', 'SELL', 821.9151515151515, 0.00008102),
                    Order('ETH/USDT', 'BUY', 0.7521902983559976, 147.81),
                    Order('XRP/ETH', 'SELL', 64.3393939393937, 0.00217366), ]
        self.assertEqual(res['orders'], expected)

        # Test that the final amounts are in proportion to the targets
        base_amounts = {}
        for cur in res['amounts']:
            pair = "{}/{}".format(cur, base)
            base_amounts[cur] = res['amounts'][cur] * rates[pair]
        total_base = sum(base_amounts.values())
        for cur in targets:
            self.assertAlmostEqual(targets[cur],
                                   (base_amounts[cur] / total_base) * 100)

    def test_badpair1(self):

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
                 }

        balancer = SimpleBalancer(targets, base)
        with self.assertRaises(ValueError):
            balancer(current, rates)

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
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 }

        balancer = SimpleBalancer(targets, base)
        with self.assertRaises(ValueError):
            balancer(current, rates)

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
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 }

        balancer = SimpleBalancer(targets, base)
        with self.assertRaises(ValueError):
            balancer.calc_base_differences(current, rates)

    def test_threshold_inbalance(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10}
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)

        # test if portfolio needs balancing
        self.assertFalse(balancer.needs_balancing(current, rates))

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
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)

        # test if portfolio needs balancing
        self.assertFalse(balancer.needs_balancing(current, rates))

        # Test the orders we get are correct
        expected = []
        self.assertEqual(res['orders'], expected)

    def test_threshold_under_force(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 46,
                   'XLM': 45,
                   'USDT': 9}
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates, force=True)

        # test if portfolio needs balancing
        self.assertFalse(balancer.needs_balancing(current, rates))

        # Test the orders we get are correct
        expected = [Order('XRP/USDT', 'SELL', 1, 1.0)]
        self.assertEqual(res['orders'], expected)

    def test_threshold_over(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10, }
        current = {'XRP': 40,
                   'XLM': 40,
                   'USDT': 20}
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }

        balancer = SimpleBalancer(targets, base)
        res = balancer(current, rates)

        # test if portfolio needs balancing
        self.assertTrue(balancer.needs_balancing(current, rates))

        # Test the orders we get are correct
        expected = [Order('XLM/USDT', 'BUY', 5, 1.0),
                    Order('XRP/USDT', 'BUY', 5, 1.0), ]
        self.assertEqual(res['orders'], expected)

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
        base = "USDT"
        rates = {'XRP/USDT': 0.32076,
                 'XLM/USDT': 0.09084,
                 'XLM/XRP': 0.283366,
                 'XRP/BTC': 0.00008102,
                 'XRP/ETH': 0.00217366,
                 'BTC/USDT': 3968.13,
                 'ETH/USDT': 147.81,
                 }

        balancer = SimpleBalancer(targets, base)

        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'USDT': 0,
                    'BTC': 0,
                    'ETH': 0,
                    'XLM': 0,
                    'XRP': 0}
        self.assertEqual(current_percentages, expected)

        res = balancer(current, rates)
        # Test the orders we get are correct
        expected = []
        self.assertEqual(res['orders'], expected)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
