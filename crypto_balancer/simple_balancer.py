from crypto_balancer.order import Order


class SimpleBalancer():
    def __init__(self, targets, base, rounds=6, threshold=1):
        self.targets = targets
        self.base = base
        self.rounds = rounds
        self.threshold = threshold

    def __call__(self, amounts, rates, force=False):
        new_amounts = amounts.copy()
        orders = []
        pairs_processed = set()

        # exit if don't need to balance and not forcing
        if not self.needs_balancing(new_amounts, rates) and not force:
            return {'orders': orders, 'amounts': new_amounts}

        rates["{}/{}".format(self.base, self.base)] = 1.0
        for i in range(self.rounds):
            differences = self.calc_base_differences(new_amounts, rates)
            sorted_by_diff = sorted(tuple(differences.items()),
                                    key=lambda x: x[1])

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

            if trade_pair not in pairs_processed:
                orders.append(Order(trade_pair, trade_direction,
                                    trade_amount, trade_rate))
                pairs_processed.add(trade_pair)

            new_amounts[to_sell_cur] -= to_sell_amount_cur
            new_amounts[to_buy_cur] += to_buy_amount_cur

        return {'orders': orders, 'amounts': new_amounts}

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
