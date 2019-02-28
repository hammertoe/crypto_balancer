from crypto_balancer.order import Order
from random import shuffle, choice


class SimpleBalancer():
    def __init__(self, rounds=6, attempts=10000):
        self.rounds = rounds
        self.attempts = attempts

    def balance(self, portfolio, exchange):
        pairs_processed = set()
        attempts = []
        rates = exchange.rates
        quote_currency = portfolio.quote_currency

        # Add in the identify rate just so we don't have to special
        # case it later 
        rates["{}/{}".format(quote_currency, quote_currency)] = 1.0

        # We brute force try a number of attempts to balance
        for _ in range(self.attempts):
            total_fee = 0.0
            portfolio.sync_balances()
            pairs_processed = set()
            orders = []
            last_differences = []

            for i in range(self.rounds):
                differences = sorted(portfolio.differences_quote.items())

                # not making progress, so break
                if differences == last_differences:
                    break

                # keep track of last one so we can see if making progress
                last_differences = differences
                
                # Find all the currencies that need to increase their
                # percentages of the portfolio and those that need to decrease
                positives = [x for x in differences if x[1] > 0]
                negatives = [x for x in differences if x[1] < 0]

                # Nothing here so break early
                if not (positives and negatives):
                    break
                
                order = None

                # pick random positive and negative to match
                p_cur, p_amount = choice(positives)
                n_cur, n_amount = choice(negatives)

                # randomly choose to fulfil the most from the
                # source or dest
                trade_amount_quote = choice([p_amount, -n_amount])

                # Work out the pair to get to the quote currency
                to_sell_pair_quote = "{}/{}".format(n_cur, quote_currency)
                to_buy_pair_quote = "{}/{}".format(p_cur, quote_currency)

                # Work out how much of the currency to buy/sell
                to_sell_amount_cur = \
                    trade_amount_quote / rates[to_sell_pair_quote]
                to_buy_amount_cur = \
                    trade_amount_quote / rates[to_buy_pair_quote]

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
                    # Adjust the amounts of each currency we hold
                    portfolio.balances[p_cur] += to_buy_amount_cur
                    portfolio.balances[n_cur] -= to_sell_amount_cur

                    if  portfolio.balances[n_cur] < 0:
                        # gone negative so not valid result
                        break

                    trade_rate = rates[trade_pair]
                    order = Order(trade_pair, trade_direction,
                                  trade_amount, trade_rate)

                # if we have not already processed this pair then add
                # the order to list of orders to execute and note the
                # pair so we don't try and use it again
                if order and trade_pair not in pairs_processed:
                    orders.append(order)
                    pairs_processed.add(trade_pair)
                    # keep track of the total fee of these orders
                    total_fee += trade_amount_quote * exchange.fee
                    
            # Check the at the end we have no differences outstanding
            if orders and not [cur for (cur,diff) in differences if abs(diff) > 1e-3]:
                attempts.append((total_fee, orders, portfolio.balances))

        if attempts:
            # sort our attempts so the lowest price one is first
            attempts.sort(key=lambda x: x[:2])
            total_fee, orders, balances = attempts[0]
        else:
            total_fee, orders, balances = 0, [], portfolio.balances
            
        return {'orders': orders,
                'amounts': balances,
                'total_fee': total_fee}


