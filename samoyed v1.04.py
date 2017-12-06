from bittrex import Bittrex
from itertools import cycle
import time

def main():
    arbitrage_loop()

'''
Returns instance of bittrex using api key/secret
'''
def get_bittrex_instance():
    return Bittrex('', '')

'''
Returns 0 or 1 (ETH or BTC), and the balance
'''
def check_balances():
    bit = get_bittrex_instance()
    btc_eth_list = [bit.get_balance('ETH')['result']['Balance']*usdt_conversion('ETH'), bit.get_balance('BTC')['result']['Balance']*usdt_conversion('BTC')]
    i, balance = btc_eth_list.index(max(btc_eth_list)), max(btc_eth_list)
    '''
    Commented out for testing purposes.
    
    if balance ==  0:
        print("No funds available.")
        exit(0)
    '''
    return i, balance

def arbitrage_loop():
    try:
        middle_assets = cycle(['LTC', 'DASH', 'XMR', 'DGB', 'XRP', 'XEM', 'XLM', 'FCT', 'DGD', 'WAVES', 'ETC', 'STRAT',
             'SNGLS', 'REP', 'NEO', 'ZEC', 'TIME', 'GNT', 'LGD', 'TRST', 'WINGS', 'RLC', 'GNO', 'GUP', 'LUN', 'TKN', 'HMQ', 'ANT',
             'BAT', '1ST', 'QRL', 'CRB', 'PTOY', 'MYST', 'CFI', 'BNT', 'NMR', 'SNT', 'MCO', 'ADT', 'FUN', 'PAY', 'MTL', 'STORJ',
             'ADX', 'OMG', 'CVC', 'QTUM', 'BCC'])
        middle_assets_iterator = iter(middle_assets)
        bit = get_bittrex_instance()
        while True:
            bool_val, balance = check_balances()
            start_asset = currency_check(bool_val)
            middle_asset = next(middle_assets_iterator)
            profitability = calculate(start_asset,  middle_asset, currency_check(not bool_val))
            print(start_asset, "->", middle_asset, "->", currency_check(not bool_val), "=", 100*profitability, "% of pre-trade balance.")
            if profitability > 1:
                '''
                This is where transaction takes place.
                '''
                print("Trade completed.")
            else:
                print("Trade skipped.")
    except Exception:
        '''
        In the event the program is terminated in the middle of a transaction, balances are printed.
        '''
        print("Holdings:", bit.get_balance('BTC')['result']['Balance'], "BTC,", bit.get_balance('ETH')['result']['Balance'], "ETH,", bit.get_balance(middle_asset)['result']['Balance'], middle_asset)
        print("\nTerminated.")
        exit(0)

'''
Calculates dollar value post trade(s)
'''
def calculate(start_asset, middle_asset, final_asset):
    balance = .9975062344
    middle_asset_balance = order_finder(start_asset, balance, middle_asset, 'sell')
    final_asset_balance = .9975*order_finder(final_asset, middle_asset_balance, middle_asset, 'buy')
    return (final_asset_balance*usdt_conversion(final_asset))/(balance*usdt_conversion(start_asset))

'''
Determines dollar value ratio of start/final asset
'''
def usdt_conversion(asset):
    bit = get_bittrex_instance()
    return bit.get_orderbook('USDT-' + asset, 'buy')['result'][0]['Rate']

'''
Retrieves the orderbook of supplied type and finds order of sufficient quantity for fill or kill
'''
def order_finder(start_asset, balance, final_asset, order_type):
    bit = get_bittrex_instance()
    orders = bit.get_orderbook(start_asset + '-' + final_asset, order_type)['result']
    for order in orders:
        if order_type == 'sell':
            final_asset_balance = balance / order['Rate']
        else:
            final_asset_balance = balance * order['Rate']
        if final_asset_balance < order['Quantity']:
            break
    return final_asset_balance

'''
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
USE THIS TYPE OF FORMAT FOR THE ACTUAL TRANSACTIONS
'''

'''
If bool is 1, begin using BTC. If bool is 0, begin using ETH.
'''
def currency_check(bool):
    if bool == True:
        return 'BTC'
    else:
        return 'ETH'

if __name__ == '__main__':
    main()
