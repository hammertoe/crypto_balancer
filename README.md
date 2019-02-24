[![Build Status](https://travis-ci.org/hammertoe/crypto_balancer.svg?branch=master)](https://travis-ci.org/hammertoe/crypto_balancer) [![Coverage Status](https://coveralls.io/repos/github/hammertoe/crypto_balancer/badge.svg?branch=master)](https://coveralls.io/github/hammertoe/crypto_balancer?branch=master)

# Cryptocurrency Portfolio Balancer

**USE AT YOUR OWN RISK. THIS TRADES REAL MONEY. NO WARRENTY IS GIVEN**

A script that can connect to a cryptocurrency exchange and buy/sell cryptocurrency to keep your portfolio balancer to a certain ratio.

## Install

```
$ virtualenv . -python=python3
$ . bin/activate
$ pip install -r requirements.txt
$ pip install -e .
```

## Config
Create a config file in `config.ini` with definition of your exchange and portfolio percentages, and theshold (percent) that rebalancing is needed:

```
[binance]
api_key = <api key>
api_secret = <api secret>
threshold = 2.0
targets = XRP 40
          BTC 20
	  ETH 20
	  BNB 10
	  USDT 10
```

By default it values the portfolio in USDT, this can be changed with `--valuebase` argument.

## Running

Dry run (don't actually trade) against Binance
```
$ crypto_balancer binance
Connected to exchange: Binance

Balances:
  XRP 401.6
  BTC 0.01609
  ETH 0.42
  BNB 3.09173906
  USDT 33.182232

Porfolio value:
  XRP 120.92778400000002 (39.79 / 40.00%)
  BTC 60.723096850000005 (19.98 / 20.00%)
  ETH 58.266600000000004 (19.17 / 20.00%)
  BNB 30.807170102510998 (10.14 / 10.00%)
  USDT 33.182232 (10.92 / 10.00%)
Total value: 303.91 USDT

No balancing needed
```

To force it to rebalance regadless of if needed:
```
$ crypto_balancer --force binance
Connected to exchange: Binance

Balances:
  XRP 401.6
  BTC 0.01609
  ETH 0.42
  BNB 3.09173906
  USDT 33.182232

Porfolio value:
  XRP 120.59445600000002 (39.75 / 40.00%)
  BTC 60.66066765 (19.99 / 20.00%)
  ETH 58.188900000000004 (19.18 / 20.00%)
  BNB 30.791402233305003 (10.15 / 10.00%)
  USDT 33.182232 (10.94 / 10.00%)
Total value: 303.42 USDT

Balancing needed:
BUY 0.01800593003472523 ETH/USDT @ 138.54500000000002
BUY 1.4973656525450756 XRP/BNB @ 0.030144999999999998
BUY 1.0755472579300063 XRP/USDT @ 0.300285
BUY 6.064565297859811e-06 BTC/USDT @ 3770.085

No trades placed, as '--trade' not given on command line
```

To get it to actually execute trades if needed:

```
$ crypto_balancer --force --trade binance
Connected to exchange: Binance

Balances:
  XRP 401.6
  BTC 0.01609
  ETH 0.42
  BNB 0.78000764
  USDT 56.155182

Porfolio value:
  XRP 120.81935200000002 (39.80 / 40.00%)
  BTC 60.7695165 (20.02 / 20.00%)
  ETH 58.09649999999999 (19.14 / 20.00%)
  BNB 7.74957090531 (2.55 / 10.00%)
  USDT 56.155182 (18.50 / 10.00%)
Total value: 303.59 USDT

Balancing needed:
BUY 2.2756791459924015 BNB/USDT @ 9.93525
BUY 0.01895191961729272 ETH/USDT @ 138.325
BUY 1.8787227415645225 XRP/USDT @ 0.30084500000000003
BUY 0.17115863297709613 XRP/BTC @ 7.965500000000001e-05

Order placed: BNB/USDT buy 2.27 @ 9.9353 
Order too small to process: BUY 0.01895191961729272 ETH/USDT @ 138.325
Order too small to process: BUY 1.8787227415645225 XRP/USDT @ 0.30084500000000003
Order too small to process: BUY 0.17115863297709613 XRP/BTC @ 7.965500000000001e-05
```
