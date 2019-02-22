#!/usr/bin/env python
#
#  XXX  Identifying information about tests here.
#
#===============
#  This is based on a skeleton test file, more information at:
#
#     https://github.com/linsomniac/python-unittest-skeleton

import unittest

import os
import sys
sys.path.append('..')      # XXX Probably needed to import your code

from crypto_balancer import SimpleBalancer
from crypto_balancer import Order

class test_Balancer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_balancer_noop(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10,}
        current = {'XRP': 450,
                   'XLM': 450,
                   'USDT': 100,}
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }
        balancer = SimpleBalancer(targets, base)
        adjustments = balancer(current, rates)
        self.assertEqual(adjustments, [])

    def test_simple_balancer_start_all_usdt(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000,}
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }
        balancer = SimpleBalancer(targets, base)
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 500), Order('XLM/USDT', 'BUY', 400),]
        self.assertEqual(sorted(adjustments), sorted(expected))

    def test_simple_balancer_start_all_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000,}
        base = "USDT"
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5,
                 }
        balancer = SimpleBalancer(targets, base)
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 1000), Order('XLM/USDT', 'BUY', 800),]
        self.assertEqual(sorted(adjustments), sorted(expected))

    def test_simple_balancer_start_all_xrp(self):
        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 1000,
                   'XLM': 0,
                   'USDT': 0,}
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 'XLM/XRP': 1.0,
                 }
        balancer = SimpleBalancer(targets, base)
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'SELL', 100), Order('XLM/XRP', 'BUY', 400),]
        self.assertEqual(sorted(adjustments), sorted(expected))

    def test_simple_balancer_current_percentages_start_all_usdt(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 0,
                   'XLM': 0,
                   'USDT': 1000,}
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }
        balancer = SimpleBalancer(targets, base)
        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 0,
                    'XLM': 0,
                    'USDT': 100,
                    }
        self.assertEqual(current_percentages, expected)

    def test_simple_balancer_current_percentages_start_xrp_xlm_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 0,}
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4,
                 }
        balancer = SimpleBalancer(targets, base)
        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 20,
                    'XLM': 80,
                    'USDT': 0,
                    }
        self.assertEqual(current_percentages, expected)

    def test_simple_balancer_current_percentages_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50,}
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4,
                 }
        balancer = SimpleBalancer(targets, base)
        current_percentages = balancer.calc_cur_percentage(current, rates)
        expected = {'XRP': 10,
                    'XLM': 40,
                    'USDT': 50,
                    }
        self.assertEqual(current_percentages, expected)

    def test_simple_balancer_differences_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50,}
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4,
                 }
        balancer = SimpleBalancer(targets, base)
        differences = balancer.calc_differences(current, rates)
        expected = {'XRP': 40,
                    'XLM': 0,
                    'USDT': -40,
                    }
        self.assertEqual(differences, expected)

    def test_simple_balancer_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50,}
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4,
                 }
        balancer = SimpleBalancer(targets, base)
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 400),]
        self.assertEqual(sorted(adjustments), sorted(expected))
        
    def test_simple_balancer_base_differences_start_xrp_xlm_usdt_rates(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50,}
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4,
                 }
        balancer = SimpleBalancer(targets, base)
        differences = balancer.calc_base_differences(current, rates)
        expected = {'XRP': 40,
                    'XLM': 0,
                    'USDT': -40,
                    }
        self.assertEqual(differences, expected)

    def test_simple_balancer_base_differences_start_xrp_xlm_usdt_rates2(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50,}
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4,
                 }
        balancer = SimpleBalancer(targets, base)
        differences = balancer.calc_base_differences(current, rates)
        expected = {'XRP': 40,
                    'XLM': 0,
                    'USDT': -40,
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

    def test_simple_balancer_base_differences_start_xrp_xlm_usdt_rates3(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10,}
        current = {'XRP': 40,
                   'XLM': 40,
                   'USDT': 20,}
        base = "USDT"
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5,
                }
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

    def test_simple_balancer_mixed1(self):

        targets = {'XRP': 50,
                   'XLM': 40,
                   'USDT': 10,}
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 50,}
        base = "USDT"
        rates = {'XRP/USDT': 0.1,
                 'XLM/USDT': 0.4,
                 }
        balancer = SimpleBalancer(targets, base)
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 400),]
        self.assertEqual(sorted(adjustments), sorted(expected))

    def test_simple_balancer_mixed2a(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10,}
        current = {'XRP': 40,
                   'XLM': 40,
                   'USDT': 20,}
        base = "USDT"
        rates = {'XRP/USDT': 1.0,
                 'XLM/USDT': 1.0,
                 }
        balancer = SimpleBalancer(targets, base)
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 5), Order('XLM/USDT', 'BUY', 5),]
        self.assertEqual(sorted(adjustments), sorted(expected))

    def test_simple_balancer_mixed2b(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10,}
        current = {'XRP': 80,
                   'XLM': 80,
                   'USDT': 20,}
        base = "USDT"
        rates = {'XRP/USDT': 0.5,
                 'XLM/USDT': 0.5,
                 }
        balancer = SimpleBalancer(targets, base)
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'BUY', 10), Order('XLM/USDT', 'BUY', 10),]
        self.assertEqual(sorted(adjustments), sorted(expected))

    def test_simple_balancer_mixed3a(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10,}
        current = {'XRP': 50,
                   'XLM': 50,
                   'USDT': 0,}
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
        
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'SELL', 5), Order('XLM/USDT', 'SELL', 5),]
        self.assertEqual(sorted(adjustments), sorted(expected))

    def test_simple_balancer_mixed3b(self):

        targets = {'XRP': 45,
                   'XLM': 45,
                   'USDT': 10,}
        current = {'XRP': 100,
                   'XLM': 100,
                   'USDT': 0,}
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
        
        adjustments = balancer(current, rates)
        expected = [Order('XRP/USDT', 'SELL', 10), Order('XLM/USDT', 'SELL', 10),]
        self.assertEqual(sorted(adjustments), sorted(expected))
        
unittest.main()
