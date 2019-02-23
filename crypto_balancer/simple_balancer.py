from crypto_balancer.order import Order

class SimpleBalancer():
    def __init__(self, targets, base):
        self.targets = targets
        self.base = base
        self.rounds = 6

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
                if pair not in rates:
                    raise ValueError("Invalid pair: {}".format(pair))
                base_values[cur] = amount * rates[pair]

        total_base_value = sum(base_values.values())
        for cur in base_values:
            differences[cur] = (total_base_value*(self.targets[cur]/100.0)) - base_values[cur]
        return differences
    

