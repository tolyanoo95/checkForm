from binance.client import Client
from binance.enums import *
import time
from datetime import datetime
import pandas as pd
import pandas_ta as ta


# Get API key
api_key = 'CAZBO8QbA35BRqBPOAbV8RYdbJZpMOgnlR0B86BtUjtngeV3CkEQVaQ39ecEQflv'
api_secret = 'VfnfF3HjQ8K4bz7F5rJMeQJqhc1UF7W863BwGkMhKBM1CWCsFOunKlGzt4pNLkpV'
client = Client(api_key, api_secret)

#start values
trend = False
trend_check = False
trend_rsi = False
trend_price = False
trend_average = False
profit = False


symbol = 'GALAUSDT'
deposite = 100
order = 11
all_coins = 0
all_orders = 0
average_price = 0

rsi_test = True

while(True):

    #get price symbol
    prices_list = client.futures_ticker()
    for item in prices_list:
        if item['symbol'] == symbol:
            price = float(item['lastPrice'])

    #get history
    klines_arr = client.futures_historical_klines(symbol, Client.KLINE_INTERVAL_3MINUTE, "5 hour ago UTC", )
    klines = []

    for item in klines_arr:
        klines.append([float(item[1]),float(item[2]),float(item[3]),float(item[4])])

    df = pd.DataFrame(klines, columns=['open', 'high', 'low', 'close'])

    #get values indicators
    macd_values = df.ta.macd(fast=12, slow=26, signal=9)
    rsi_values = df.ta.rsi(length=14)


    rsi = float(rsi_values.values[-1])
    macd_diagram  = float('{:.5}'.format(macd_values['MACDh_12_26_9'].values[-1]))
    macd_result = float('{:.5}'.format(macd_values['MACD_12_26_9'].values[-1]))
    macd_signal  = float('{:.5}'.format(macd_values['MACDs_12_26_9'].values[-1]))

    '''
    if(rsi_test):
        rsi = 71
        rsi_test = False
    '''

    #check rsi
    if(rsi < 30):
        trend_rsi = 'BUY'
        if(trend == 'SELL'):
            profit = True
        if(trend == 'BUY'):
            trend_average = True

    if(rsi > 70):
        trend_rsi = 'SELL'
        # stoploss
        if(trend == 'BUY'):
            profit = True
        if(trend == 'SELL'):
            trend_average = True


    #check macd
    if(trend_rsi == 'BUY'):
        if((macd_result > macd_signal) and (macd_result < 0) and (macd_signal < 0)):
            trend = 'BUY'
    if(trend_rsi == 'SELL'):
        if((macd_result < macd_signal) and (macd_result > 0) and (macd_signal > 0)):
            trend = 'SELL'


    #check profit
    #macd_profit = float('{:.8}'.format(macd_values['MACD_12_26_9'].values[-2]))
    if(trend == 'BUY'):
        if((macd_result > macd_diagram) and (macd_result > 0)):
            profit = True
            if(trend_rsi == 'BUY'):
                trend_rsi = False
    if(trend == 'SELL'):
        if((macd_result < macd_diagram) and (macd_result < 0)):
            profit = True
            if(trend_rsi == 'SELL'):
                trend_rsi = False


    #check average
    if(trend_average):
        if(trend == 'BUY' and ((trend_price - (trend_price / 100) * 1) > price) and (macd_result > macd_signal) and (macd_result < 0) and (macd_signal < 0) and (rsi > 30)):
            trend_price = price
            trend_average = False
            order = order + ((order/100)*50)
            coins = order/trend_price
            all_coins += coins
            all_orders += order
            average_price = all_orders/all_coins
            print('*' * 10)
            print('Average buy/sell: ' + str(trend_price))
            print('Order: ' + str(order))
            print('Coins: ' + str(coins))
            print('All coins: ' + str(all_coins))
            print('All order: ' + str(all_orders))
            print('Average price: ' + str(average_price))
            print('*' * 10)
        if(trend == 'SELL' and ((trend_price + (trend_price / 100) * 1) < price) and (macd_result < macd_signal) and (macd_result > 0) and (macd_signal > 0) and (rsi < 70)):
            trend_price = price
            trend_average = False
            order = order + ((order / 100) * 50)
            coins = order / trend_price
            all_coins += coins
            all_orders += order
            average_price = all_orders / all_coins
            print('*'*10)
            print('Average buy/sell: ' + str(trend_price))
            print('Order: ' + str(order))
            print('Coins: ' + str(coins))
            print('All coins: ' + str(all_coins))
            print('All order: ' + str(all_orders))
            print('Average price: ' + str(average_price))
            print('*' * 10)



    #get trend
    if(trend_check != trend):

        trend_price = price
        coins = order/trend_price
        all_coins += coins
        all_orders += order

        if(trend == 'BUY'):
            print('BUY: ' + str(trend_price))
        if(trend == 'SELL'):
            print('SELL: ' + str(trend_price))
        print('Coins: ' + str(all_coins))
        print('All order: ' + str(all_orders))


    #get profit
    if (profit):
        print('Price: ' + str(price))
        if(average_price):
            trend_price = average_price
        print('Trend price ' + str(trend_price))
        if(trend == 'SELL'):
            procent = ((trend_price - price) / trend_price) * 100
        if(trend == 'BUY'):
            procent = ((price - trend_price) / price) * 100
        print('Profit: ' + str(round(procent,3)) + '%')
        print('-' * 10)

        trend = False
        trend_check = False
        profit = False
        trend_average = False
        order = 11
        all_coins = 0
        all_orders = 0
        average_price = 0


    trend_check = trend

    time.sleep(1)
