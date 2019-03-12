[![Build Status](https://travis-ci.org/hammertoe/crypto_balancer.svg?branch=master)](https://travis-ci.org/hammertoe/crypto_balancer) [![Coverage Status](https://coveralls.io/repos/github/hammertoe/crypto_balancer/badge.svg?branch=master)](https://coveralls.io/github/hammertoe/crypto_balancer?branch=master)

# Cryptocurrency Portfolio Balancer

**USE AT YOUR OWN RISK. THIS TRADES REAL MONEY. NO WARRANTY IS GIVEN**

A script that can connect to a cryptocurrency exchange and buy/sell cryptocurrency to keep your portfolio balancer to a certain ratio.

## To support this project

To support this project, feel free to send any tips in XRP to:
https://www.xrptipbot.com/u:HammerToe/n:twitter

Or direct to `rPEPPER7kfTD9w2To4CQk6UCfuHM9c6GDY` dest tag `8172226`

## Install

Via Pip:
```
pip install crypto_balancer
```

Via source from Github:

```
git clone git@github.com:hammertoe/crypto_balancer.git
cd crypto_balancer
virtualenv --python=python3 .
. bin/activate
pip install -r requirements.txt
pip install -e .
```

## Config
Create a config file in `config.ini` with definition of your exchange and portfolio percentages, and theshold (percent) that rebalancing is needed.
An example config file is included at `config.ini.example` but below is all you need:

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
Connected to exchange: binance

Current Portfolio:
  XRP    3272.28  (39.92 / 40.00%)
  BTC    0.14     (20.05 / 20.00%)
  ETH    3.85     (20.02 / 20.00%)
  BNB    22.81    ( 9.99 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.40 USDT
  Balance error: 0.043 / 0.08

No balancing needed
```

To force it to rebalance regardless of if needed:
```
$ crypto_balancer --force binance
Connected to exchange: binance

Current Portfolio:
  XRP    3272.28  (39.92 / 40.00%)
  BTC    0.14     (20.04 / 20.00%)
  ETH    3.85     (20.02 / 20.00%)
  BNB    22.81    ( 9.99 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.28 USDT
  Balance error: 0.042 / 0.08

Balancing needed [FORCED]:

Proposed Portfolio:
  XRP    3278.51  (40.00 / 40.00%)
  BTC    0.14     (20.04 / 20.00%)
  ETH    3.83     (19.95 / 20.00%)
  BNB    22.81    ( 9.99 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.28 USDT
  Balance error: 0.032
  Total fees to re-balance: 0.00199 USDT

Orders:
  BUY 6.2279674364331195 XRP/ETH @ 0.00234478
```

To get it to actually execute trades if needed:

```
$ crypto_balancer --force --trade binance
Connected to exchange: binance

Current Portfolio:
  XRP    3272.28  (39.96 / 40.00%)
  BTC    0.14     (20.04 / 20.00%)
  ETH    3.84     (19.94 / 20.00%)
  BNB    22.94    (10.04 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.01 USDT
  Balance error: 0.043 / 0.08

Balancing needed [FORCED]:

Proposed Portfolio:
  XRP    3272.28  (39.96 / 40.00%)
  BTC    0.14     (20.04 / 20.00%)
  ETH    3.85     (20.00 / 20.00%)
  BNB    22.80    ( 9.98 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.01 USDT
  Balance error: 0.031 / 0.08
  Total fees to re-balance: 0.001592 USDT

Orders:
  Submitted: sell 0.13 BNB/ETH @ 0.08422
```

## Running automatically

You can set this to run in a cron job on a unix system by putting something along the lines of (adjust for your path and email address) below
in your crontab file:

```
MAILTO=matt@example.com
*/5 * * * * OUTPUT=`cd /home/matt/crypto_balancer; bin/crypto_balancer --trade binance`; echo "$OUTPUT" | grep -q "No balancing needed" || echo "$OUTPUT"
```

This will run the script every 5 minutes, and will email you only if some balancing (or an error) occurs.
