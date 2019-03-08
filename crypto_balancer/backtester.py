from crypto_balancer.backtest_exchange import BacktestExchange
from crypto_balancer.simple_balancer import SimpleBalancer
from crypto_balancer.portfolio import Portfolio

if __name__ == '__main__':
    Xbalances = {'XRP':3269.878282,
                'BTC': 0.13551801,
                'ETH': 3.78736025,
                'BNB': 25.08296788,
                'USDT': 251.05799855}

    balances = {'XRP': 50000.0,
                'BTC': 0.0,
                'ETH': 0.0,
                'USD': 0.0}

    balances = {'XRP': 0.0,
                'BTC': 0.0,
                'ETH': 0.0,
                'USD': 10000.0}

    Xtargets = {'XRP': 40,
               'BTC': 20,
               'ETH': 20,
               'BNB': 10,
               'USDT': 10, }

    Xtargets = {'XRP': 20,
               'BTC': 20,
               'ETH': 20,
               'BNB': 20,
               'USDT': 20, }

    Xtargets = {'XRP': 40,
               'BTC': 20,
               'ETH': 20,
               'USD': 20, }

    targets = {'XRP': 80,
               'USD': 20, }
    
    for t in range(10,100,10):
        threshold = t / 10.0
        exchange = BacktestExchange('/Development/crypto_balancer/data/*.json', balances.copy())
        portfolio = Portfolio.make_portfolio(targets, exchange, threshold, quote_currency="USD")
        balancer = SimpleBalancer()
        num_trades = 0

        while portfolio.needs_balancing:
            res = balancer.balance(portfolio,
                                   exchange,
                                   accuracy=True,
                                   max_orders=4)
            for order in res['orders']:
                try:
                    r = exchange.execute_order(order)
                    num_trades += 1
                except ValueError:
                    pass

            portfolio.sync_balances()
            
        initial_portfolio = portfolio.copy()
        
        while True:

            if portfolio.needs_balancing:
                res = balancer.balance(portfolio,
                                       exchange,
                                       accuracy=True,
                                       max_orders=2)
                for order in res['orders']:
                    try:
                        r = exchange.execute_order(order)
                        num_trades += 1
                    except ValueError:
                        pass

                portfolio.sync_balances()
                
            try:
                exchange.tick()
            except StopIteration:
                break
            portfolio.sync_rates()

        print("Threshold:", threshold)
        print("Initial value:", initial_portfolio.valuation_quote)
        print("Final value: ", portfolio.valuation_quote)

        portfolio.balances = initial_portfolio.balances

        print("B&H value: ", portfolio.valuation_quote)
        print("Number of trades: ", num_trades)
        print()
    
