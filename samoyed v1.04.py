from bittrex import Bittrex
from itertools import cycle
import time

def main():
    arbitrage_loop()

#Returns instance of bittrex using api key/secret

def get_bittrex_instance():
    return Bittrex('', '')

#Returns 0 or 1 (ETH or BTC), and the balance
def check_balances(bit):
    btc_eth_list = [bit.get_balance('ETH')['result']['Balance']*usdt_conversion('ETH'), bit.get_balance('BTC')['result']['Balance']*usdt_conversion('BTC')]
    i, balance = btc_eth_list.index(max(btc_eth_list)), max(btc_eth_list)
    '''
    if balance ==  0:
        print("No funds available.")
        exit(0)
    '''
    return i, balance

#Retrieves a list of shared markets between BTC and ETH. Intentionally unused - lengthy process, and Bittrex can have markets listed that have been discontinued.
def get_markets(bit):
    market_list = []
    for currency in bit.get_currencies()['result']:
        if bit.get_marketsummary('BTC-' + currency['Currency'])['result'] and bit.get_marketsummary('ETH-' + currency['Currency'])['result']:
            market_list.append(currency['Currency'])
        print(market_list)
    return market_list

#SC has been removed
def arbitrage_loop():
    try:
        middle_assets = cycle(['LTC', 'DASH', 'XMR', 'DGB', 'XRP', 'XEM', 'XLM', 'FCT', 'DGD', 'WAVES', 'ETC', 'STRAT', 'SNGLS', 'REP', 'NEO',
                               'ZEC', 'GNT', 'LGD', 'TRST', 'WINGS', 'RLC', 'GNO', 'GUP', 'LUN', 'HMQ', 'ANT', 'SC', 'BAT', '1ST', 'QRL', 'CRB',
                               'PTOY', 'MYST', 'CFI', 'BNT', 'NMR', 'SNT', 'MCO', 'ADT', 'FUN', 'PAY', 'MTL', 'STORJ', 'ADX', 'OMG', 'CVC', 'QTUM',
                               'BCC', 'DNT', 'ADA', 'MANA', 'SALT', 'TIX', 'RCN', 'VIB', 'POWR', 'BTG', 'ENG'])
        middle_assets_iterator = iter(middle_assets)
        bit = get_bittrex_instance()
        while True:
            bool_val, balance = check_balances(bit)
            start_asset = currency_check(bool_val)
            middle_asset = next(middle_assets_iterator)
            profitability, rate1, rate2 = calculate(start_asset,  middle_asset, currency_check(not bool_val))
            print(start_asset, "->", middle_asset, "->", currency_check(not bool_val), "=", 100*profitability, "% of pre-trade balance.")
            if profitability > 1:
                # transaction(start_asset, rate1, middle_asset, rate2, currency_check(not bool_val))
                print("Completed.")
            else:
                print("Skipped.")
    except Exception:
        #In the event the program is terminated in the middle of a transaction, balances are printed and open orders are cancelled
        open_order_list = bit.get_open_orders()['result']
        if open_order_list:
            for order in open_order_list:
                print("Cancelling", order['Exchange'], "order...")
                if bit.cancel(order['OrderUuid'])['success'] == 'True':
                    print("Cancelled.")
                else:
                    print("Order cannot be cancelled.")
        print("Holdings:", bit.get_balance('BTC')['result']['Balance'], "BTC,", bit.get_balance('ETH')['result']['Balance'], "ETH,", bit.get_balance(middle_asset)['result']['Balance'], middle_asset)
        print("\nTerminated.")
        exit(0)

#Calculates dollar value post trade(s).  Original balance is 1 BTC/ETH, but traded amount is 99.7506234414% to account for fees as accurately as possible.
def calculate(start_asset, middle_asset, final_asset):
    balance = .997506234414
    middle_asset_balance, rate1 = order_finder(start_asset, balance, middle_asset, 'sell')
    final_asset_balance, rate2 = order_finder(final_asset, middle_asset_balance, middle_asset, 'buy')
    final_asset_balance = final_asset_balance*.9975
    return (final_asset_balance*usdt_conversion(final_asset))/(balance*usdt_conversion(start_asset)), rate1, rate2

#Determines dollar value ratio of start/final asset
def usdt_conversion(asset):
    bit = get_bittrex_instance()
    return bit.get_orderbook('USDT-' + asset, 'buy')['result'][0]['Rate']

#Retrieves the orderbook of supplied type and finds order of sufficient quantity for fill or kill
def order_finder(start_asset, balance, final_asset, order_type):
    bit = get_bittrex_instance()
    orders = bit.get_orderbook(start_asset + '-' + final_asset, order_type)['result']
    for order in orders:
        rate = order['Rate']
        if order_type == 'sell':
            final_asset_balance = balance / rate
        else:
            final_asset_balance = balance * rate
        if final_asset_balance < order['Quantity']:
            break
    return final_asset_balance, rate


#Dynamically takes in arguments - if only 3 arguments, then the final transaction is to take place.
def transaction(*args):
    bit = get_bittrex_instance()
    arg_iter = iter(args)
    start_asset, rate1, middle_asset = arg_iter.__next__(), arg_iter.__next__(), arg_iter.__next__()
    try:
        rate2, final_asset = arg_iter.__next__(), arg_iter.__next__()
        if bit.trade_buy(start_asset + '-' + middle_asset, 'LIMIT', bit.get_balance(start_asset)['result']['Balance'], rate1, 'FILL_OR_KILL', 'NONE')['result']['success'] == 1:
            sleeper(bit)
            if bit.trade_sell(final_asset + '-' + middle_asset, 'LIMIT', bit.get_balance(middle_asset)['result']['Balance'], rate2, 'FILL_OR_KILL', 'NONE')['result']['success'] ==1:
                sleeper(bit)
            else:
                print("Trade to final asset could not be completed. Terminating.")
                exit(0)
        else:
            print("Trade to middle asset could not be completed. Terminating.")
            exit(0)
    except Exception:
        if start_asset == 'BTC':
            if bit.trade_buy('BTC-ETH', 'LIMIT', bit.get_balance(start_asset)['result']['Balance'], rate1, 'FILL_OR_KILL', 'NONE')['success'] == 1:
                sleeper(bit)
            else:
                print("Trade between BTC/ETH could not be completed. Terminating.")
                exit(0)
        else:
            if bit.trade_sell('BTC-ETH', 'LIMIT', bit.get_balance(start_asset)['result']['Balance'], rate1, 'FILL_OR_KILL','NONE')['success'] == 1:
                sleeper(bit)
            else:
                print("Trade between BTC/ETH could not be completed. Terminating.")
                exit(0)

#Wait while open orders are being filled
def sleeper(bit):
    while bit.get_open_orders()['result']:
        time.sleep(1)

#If bool is 1, begin using BTC. If bool is 0, begin using ETH.
def currency_check(bool):
    if bool == True:
        return 'BTC'
    else:
        return 'ETH'

if __name__ == '__main__':
    main()
