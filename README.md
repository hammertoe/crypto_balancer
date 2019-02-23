[![Build Status](https://travis-ci.org/hammertoe/crypto_balancer.svg?branch=master)](https://travis-ci.org/hammertoe/crypto_balancer) [![Coverage Status](https://coveralls.io/repos/github/hammertoe/crypto_balancer/badge.svg?branch=master)](https://coveralls.io/github/hammertoe/crypto_balancer?branch=master)

# Cryptocurrency Portfolio Balancer
A script that can connect to a cryptocurrency exchange and buy/sell cryptocurrency to keep your portfolio balancer to a certain ratio.

## Install

```
$ virtualenv . -python=python3
$ . bin/activate
$ pip install -r requirements.txt
$ pip install -e .
```

## Config
Create a config file in `config.ini` with definition of your exchange and portfolio percentages.

```
[bitrue]
api_key = <api key>
api_secret = <api secret>
targets = XRP 45
          XLM 45
	  USDT 10
```

By default it values the portfolio in USDT, this can be changed with `--valuebase` argument.

## Running

Dry run (don't actually trade) against Bitrue
```
$ crypto_balancer --dry bitrue
```

