from crypto_balancer.order import Order
from random import shuffle, choice


class SimpleBalancer():
    def __init__(self, targets, base, rounds=6, threshold=1):
        self.targets = targets
        self.base = base
        self.rounds = rounds
        self.attempts = 10000
        self.threshold = threshold

    def __call__(self, amounts, rates, force=False):
        new_amounts = amounts.copy()
        pairs_processed = set()
        attempts = []
        fee = 0.1

        # exit if don't need to balance and not forcing
        if not self.needs_balancing(new_amounts, rates) and not force:
            return {'orders': [], 'amounts': new_amounts}

        rates["{}/{}".format(self.base, self.base)] = 1.0

        # We brute force try a number of attempts to balance
        for _ in range(self.attempts):
            total_fee = 0.0
            new_amounts = amounts.copy()
            pairs_processed = set()
            orders = []

            for i in range(self.rounds):
                differences = self.calc_base_differences(new_amounts, rates)

                # Find all the currencies that need to increase their
                # percentages of the portfolio and those that need to decrease
                positives = [x for x in differences.items() if x[1] > 0]
                negatives = [x for x in differences.items() if x[1] < 0]

                # Shuffle them so we try them in different orders
                shuffle(positives)
                shuffle(negatives)

                order = None

                # Loop through trying different combinations
                for p_cur, p_amount in positives:
                    for n_cur, n_amount in negatives:
                        # if we already have an order, nothing to do
                        if order:
                            break

                        # randomly choose to fulfil the most from the
                        # source or dest
                        trade_amount_base = choice([p_amount, -n_amount])

                        # Work out the pair to get to the base currency
                        to_sell_pair_base = "{}/{}".format(n_cur, self.base)
                        to_buy_pair_base = "{}/{}".format(p_cur, self.base)

                        # Work out how much of the currency to buy/sell
                        to_sell_amount_cur = \
                            trade_amount_base / rates[to_sell_pair_base]
                        to_buy_amount_cur = \
                            trade_amount_base / rates[to_buy_pair_base]

                        trade_direction = None

                        # try and see if we have the pair we need
                        # and if so, buy it
                        pair = "{}/{}".format(p_cur, n_cur)
                        if pair in rates:
                            trade_direction = "BUY"
                            trade_pair = pair
                            trade_amount = to_buy_amount_cur

                        # if previous failed then reverse paid and try
                        # sell instead
                        pair = "{}/{}".format(n_cur, p_cur)
                        if pair in rates:
                            trade_direction = "SELL"
                            trade_pair = pair
                            trade_amount = to_sell_amount_cur

                        # We got a direction, so we know we can either
                        # buy or sell this pair
                        if trade_direction:
                            trade_rate = rates[trade_pair]
                            order = Order(trade_pair, trade_direction,
                                          trade_amount, trade_rate)

                            # Adjust the amounts of each currency we hold
                            new_amounts[p_cur] += to_buy_amount_cur
                            new_amounts[n_cur] -= to_sell_amount_cur

                            # we are done so break
                            break

                # if we have not already processed this pair then add
                # the order to list of orders to execute and note the
                # pair so we don't try and use it again
                if order and trade_pair not in pairs_processed:
                    orders.append(order)
                    pairs_processed.add(trade_pair)
                    # keep track of the total fee of these orders
                    total_fee += trade_amount_base * (fee/100.0)

            # Check the at the end we have no differences outstanding
            # and that none of the new amounts have gone negative
            if not [x for x in differences.values() if abs(x) > 1e-12] \
               and not [x for x in new_amounts.values() if x < 0]:
                attempts.append((total_fee, orders, new_amounts))

        # sort our attempts so the lowest price one is first
        attempts.sort(key=lambda x: x[:2])
        total_fee, orders, new_amounts = attempts[0]
        return {'orders': orders, 'amounts': new_amounts,
                'total_fee': total_fee}

    def needs_balancing(self, amounts, rates):
        current_percentages = self.calc_cur_percentage(amounts, rates)
        for cur in self.targets:
            if abs(self.targets[cur] - current_percentages[cur]) \
               > self.threshold:
                return True
        return False

    def calc_base_values(self, amounts, rates):
        base_values = {}
        for cur, amount in amounts.items():
            if cur == self.base:
                base_values[cur] = amount
            else:
                pair = "{}/{}".format(cur, self.base)
                if pair not in rates:
                    raise ValueError("Invalid pair: {}".format(pair))
                base_values[cur] = amount * rates[pair]

        return base_values

    def calc_cur_percentage(self, amounts, rates):
        # first convert the amounts into their base value
        base_values = self.calc_base_values(amounts, rates)
        current_percentages = {}
        total_base_value = sum(base_values.values())
        for cur, base_value in base_values.items():
            if total_base_value:
                current_percentages[cur] = (base_value/total_base_value) * 100
            else:
                current_percentages[cur] = 0

        return current_percentages

    def calc_base_differences(self, amounts, rates):
        # first convert the amounts into their base value
        base_values = self.calc_base_values(amounts, rates)
        differences = {}
        total_base_value = sum(base_values.values())
        for cur in base_values:
            differences[cur] = (total_base_value*(self.targets[cur]/100.0)) \
                               - base_values[cur]
        return differences
