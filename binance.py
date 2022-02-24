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

average_price_count = 0
average_count = 1

symbol = 'GALAUSDT'

rsi_test = True

while(True):

    #get price symbol
    prices_list = client.futures_ticker()
    for item in prices_list:
        if item['symbol'] == symbol:
            price = float(item['lastPrice'])

    #get history
    klines_arr = client.futures_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "120 min ago UTC", )
    klines = []

    for item in klines_arr:
        klines.append([float(item[1]),float(item[2]),float(item[3]),float(item[4])])

    df = pd.DataFrame(klines, columns=['open', 'high', 'low', 'close'])

    #get values indicators
    macd_values = df.ta.macd(fast=12, slow=26, signal=9)
    rsi_values = df.ta.rsi(length=14)


    rsi = float(rsi_values.values[-1])
    macd_diagram  = float('{:.4}'.format(macd_values['MACDh_12_26_9'].values[-1]))
    macd_result = float('{:.4}'.format(macd_values['MACD_12_26_9'].values[-1]))
    macd_signal  = float('{:.4}'.format(macd_values['MACDs_12_26_9'].values[-1]))

    '''
    if(rsi_test):
        rsi = 21
        rsi_test = False
    '''

    #check rsi
    if(rsi < 30):
        trend_rsi = 'BUY'
        if(trend == 'SELL'):
            profit = True
        if(trend == 'BUY'):
            trend_average = True
            print('Average true')

        #if(trend == 'BUY' and ((average_price_chek - (average_price_chek/100)*1) > price)):

    if(rsi > 70):
        trend_rsi = 'SELL'
        # stoploss
        if(trend == 'BUY'):
            profit = True
        if(trend == 'SELL'):
            trend_average = True
            print('Average true')


        #if(trend == 'SELL' and ((average_price_chek + (average_price_chek/100)*1) < price)):



    #check macd
    if(trend_rsi == 'BUY'):
        if((macd_result > macd_signal) and (macd_result < 0) and (macd_signal < 0)):
            trend = 'BUY'
    if(trend_rsi == 'SELL'):
        if((macd_result < macd_signal) and (macd_result > 0) and (macd_signal > 0)):
            trend = 'SELL'


    #check profit
    if(trend == 'BUY'):
        if((macd_result > macd_diagram) and (macd_result > 0)):
            profit = True
    if(trend == 'SELL'):
        if((macd_result < macd_diagram) and (macd_result < 0)):
            profit = True


    #check average
    if(trend_average):
        if(trend == 'BUY' and ((trend_price - (trend_price / 100) * 1) > price) and (macd_result > macd_signal) and (macd_result < 0) and (macd_signal < 0)):
            trend_price = price
            trend_average = False
            average_price_count += trend_price
            average_count += 1
            print('Average buy/sell: ' + str(trend_price))
            print('Average price: ' + str(average_price_count/average_count))
        if(trend == 'SELL' and ((trend_price + (trend_price / 100) * 1) < price) and (macd_result < macd_signal) and (macd_result > 0) and (macd_signal > 0)):
            trend_price = price
            trend_average = False
            average_price_count += trend_price
            average_count += 1
            print('Average buy/sell: ' + str(trend_price))
            print('Average price: ' + str(average_price_count/average_count))



    #get trend
    if(trend_check != trend):

        trend_price = price
        average_price_count += trend_price
        average_count += 1

        if(trend == 'BUY'):
            print('BUY: ' + str(trend_price))
        if(trend == 'SELL'):
            print('SELL: ' + str(trend_price))



    #get profit
    if (profit):
        print('Price: ' + str(price))
        if(average_price_count >= 2):
            average_price = average_price_count/average_count
            trend_price = average_price
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
        average_price_count = 0
        average_count = 0


    trend_check = trend

    time.sleep(1)
