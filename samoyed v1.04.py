from bittrex import Bittrex
from itertools import cycle
import time

def main():
    try:
        arbitrage_loop()
    except KeyboardInterrupt:
        print("\nCancelled")

'''
Returns instance of bittrex using api key/secret
'''
def get_bittrex_instance():
    return Bittrex('', '')

'''
Returns 0 or 1 (isn't BTC or is BTC), and the balance
'''
def check_balances():
    bit = get_bittrex_instance()
    btc_eth_list = [bit.get_balance('ETH')['result']['Balance']*bit.get_orderbook('USDT-ETH', 'buy'), bit.get_balance('BTC')['result']['Balance']*bit.get_orderbook('USDT-BTC', 'buy')]
    i, balance = btc_eth_list.index(max(btc_eth_list)), max(btc_eth_list)
    return i, balance

def arbitrage_loop():
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
        print(profitability)
        if profitability > 1:
            print("Trade advised.")
        else:
            print("Trade not advised.")

'''
Calculates dollar value post trade(s)
'''
def calculate(start_asset, middle_asset, final_asset):
    balance = .9975062344
    middle_asset_balance = order_finder(start_asset, balance, middle_asset, 'buy')
    final_asset_balance = .9975*order_finder(final_asset, middle_asset_balance, middle_asset, 'sell')
    return usdt_conversion(start_asset, balance, final_asset, final_asset_balance)

'''
Determines dollar value ratio of start/final asset
F12 BIOS UPGRADE revision 1
'''
def usdt_conversion(start_asset, balance, final_asset, final_asset_balance):
    bit = get_bittrex_instance()
    return (final_asset_balance*bit.get_orderbook('USDT-' + final_asset, 'buy')['result'][0]['Rate'])/(balance*bit.get_orderbook('USDT-' + start_asset, 'buy')['result'][0]['Rate'])

'''
Retrieves the orderbook of supplied type and finds order of sufficient quantity
'''
def order_finder(start_asset, balance, final_asset, order_type):
    bit = get_bittrex_instance()
    orders = bit.get_orderbook(start_asset + '-' + final_asset, order_type)['result']
    for order in orders:
        if order_type == 'buy':
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
If bool is 1, begin using BTC. If bool is 0, being using ETH.
'''
def currency_check(bool):
    if bool == True:
        return 'BTC'
    else:
        return 'ETH'

if __name__ == '__main__':
    main()
