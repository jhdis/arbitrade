# Digital Currency Arbitrage
## Summary
This project trades digital currencies, centering around Bitcoin (BTC) and Ethereum (ETH), and the altcoin markets the two share with each other.  An example:

```
BTC -> X1 -> ETH -> X2 -> BTC -> ... 
```

Where X1 and X2 are a cycle of predefined altcoins.  Once all altcoin options have been expired, the program checks the profitability of trading between BTC and ETH, and then repeats.  It's possible to dynamically retrieve markets that are shared between BTC and ETH, but this can be a lengthy process and some markets exist but have been discontinued by Bittrex.

## Prerequisites
The first step in using this program is to put an API key and secret into the respective quotations here:

```
def get_bittrex_instance():
    return Bittrex('', '')
```

[This](https://coinigy.freshdesk.com/support/solutions/articles/1000087495-how-do-i-find-my-api-key-on-bittrex-com-) is a great guide on setting up an API key.

### Balances
When determining whether to start with BTC or ETH, the program determines which asset you currently contain the greatest dollar value using Tether markets in the following fashion:

```
btc_eth_list = [bit.get_balance('ETH')['result']['Balance']*usdt_conversion('ETH'), bit.get_balance('BTC')['result']['Balance']*usdt_conversion('BTC')]
i, balance = btc_eth_list.index(max(btc_eth_list)), max(btc_eth_list)
```

Once found, the **total contents of the wallet will be used**.  Choice of starting balance will be added in the future.

## TO DO
- ~~Fill or kill trading~~
- ~~Cancel open orders when program is terminated~~
- Final trade (BTC-ETH/ETH-BTC) on cycle completion
- ~~Rate return~~
- Dynamic balance and starting asset choice
- Dyanmic parameters for calculate function

## Acknowledgments
This is built using a python wrapper for Bittrex's API found [here](https://github.com/ericsomdahl/python-bittrex).
