import pandas as pd
import numpy as np
import yfinance as yf
import statsmodels.api as sm
import datetime as dt
import copy
import time 
import sys
# for plotting MACD
def MACD(DF,a=12,b=26,c=9):
    '''function to calculate MACD Moving Average Convergence and Divergence
    typical values a = 12; b = 26; c = 9;'''
    df = DF.copy()
    if df.shape[0] > 0:
        df['MA_Fast'] = df['Adj Close'].ewm(span=a,min_periods=a).mean()
        df['MA_Slow'] = df['Adj Close'].ewm(span=b,min_periods=b).mean()
        df['MACD'] = df['MA_Fast'] - df['MA_Slow']
        df['Signal'] = df['MACD'].ewm(span=c,min_periods=c).mean()
        #round off the macd difference
        df['MACD_diff'] = np.round(df['MACD'] - df['Signal'],3) 
        # moving average of macd diif
        df['MACD_diff_roll_5'] = df['MACD_diff'].rolling(window=5,min_periods=5).mean()
        '''function to calculate MA Moving Average values a = 10; b = 20;'''
        df['MA_10'] = df['Close'].rolling(window=10,min_periods=10).mean()
        df['MA_20'] = df['Close'].rolling(window=20,min_periods=20).mean()
        df['MA diff 10-20'] = np.round(df['MA_10'] - df['MA_20'],3) 
        df['MA_diff_roll_5'] = df['MA diff 10-20'].rolling(window=5,min_periods=5).mean()    
        df.reset_index(inplace=True)
        #heikin ashi close
        df['HA close']=(df['Open']+df['Close']+df['High']+df['Low'])/4
        #initialize heikin ashi open
        df['HA open']=float(0)
        df['HA open'][0]=df['Open'][0]
        #heikin ashi open
        for n in range(1,len(df)):
            df.at[n,'HA open']=(df['HA open'][n-1]+df['HA close'][n-1])/2        
        #heikin ashi high/low
        temp=pd.concat([df['HA open'],df['HA close'],df['Low'],df['High']],axis=1)
        df['HA high']=temp.apply(max,axis=1)
        df['HA low']=temp.apply(min,axis=1)    
        #colour of candles
        df['colour'] = np.where(df['HA open'] < df['HA close'],'green','red')
        #rolling 2 candles are continous green or not
        df['colour_sample'] = np.where(df['colour'] == 'green',1,-1)
        df['colour_rolling_2'] = df['colour_sample'].rolling(window=2,min_periods=2).mean()
        del df['Adj Close']
        del df['Volume']
        df.dropna(inplace=True)
        df.set_index(df["Datetime"],inplace=True,drop=True)
        #for buy signal
        df['buy/sell'] = np.where(((df['colour_rolling_2'] == 1) & (df['MA_diff_roll_5'] > 1.5) & \
                                (df['MACD_diff_roll_5'] > 0.3) & (df['Signal'] > 0) & (df['MACD_diff'] > 0)),'buy','no')
        # for sell signal
        df['sell/no'] = np.where(((df['colour_rolling_2'] == -1) & (df['MA_diff_roll_5'] < 1.5) | \
                        (df['MACD_diff_roll_5'] < 0.3) & (df['Signal'] < 0) & (df['MACD_diff'] < 0) & (df['MA_diff_roll_5'] < 1.5) | \
                        (df['MACD_diff'] < 0) & (df['MACD_diff_roll_5'] < 0.3) & (df['Signal'] < 0) & (df['colour_rolling_2'] == -1)),'sell','no')
        return df
    else:
        return df
        
# # for checking today price break or not previous day close
# data1d['higher_than_prevoius'] = 'a'
# for i in range(1,len(data1d)):
#     if data1d.Close[i] > data1d.Close[i-1]:
#         data1d['higher_than_prevoius'][i] = 'yes'
#     else:
#         data1d['higher_than_prevoius'][i] = 'no'
        
# # mering 1day and 1hr chart with previous candle high or not
# final_with_1hr_and_1d = copy.deepcopy(madf)
# final_with_1hr_and_1d['high_or_no'] = 'a'
# for i in range (0,len(madf1d)):
#     for j in range(0,len(madf)):
#         if madf1d.index.month[i] == madf.index.month[j] & madf1d.index.day[i] == madf.index.day[j]:
#             final_with_1hr_and_1d['high_or_no'][j] = madf1d['higher_than_prevoius'][i]
#         else:
#             pass
# data = yf.download('CIPLA.NS',start='2020-09-20', end='2020-11-17',interval='60m')
# madf = MACD(data)

ticker = ['RELIANCE.NS','CIPLA.NS','BAJAJ-AUTO.NS','ITC.NS','TITAN.NS','MARUTI.NS','LT.NS','ONGC.NS','NTPC.NS','GAIL.NS','MM.NS']


ohlcv_data = {}
ohlcv_data_update = ohlcv_data.copy()
for tick in ticker:
    print('********{}*******'.format(tick))
    ohlcv_data[tick] = yf.download(tick,start='2020-11-15', end='2020-11-20',interval='1m')

start_tick = time.time()
for tick in ohlcv_data:
    print('**********',tick)
    madf = MACD(ohlcv_data[tick])
    ohlcv_data_update[tick] = madf 

# for tick in ohlcv_data_update:
#     print(ohlcv_data_update[tick].tail(1))

# ohlcv_data_update['RELIANCE.NS']
# a = ohlcv_data_update['RELIANCE.NS']['Close'].resample('15Min').ohlc()
# b = yf.download('RELIANCE.NS',start='2020-11-15', end='2020-11-20',interval='15m')

# b['diff'] = a['open'] - b['Open']
portfolio = pd.DataFrame()
error = pd.DataFrame()
for tick in ohlcv_data_update:
    df = ohlcv_data_update[tick].copy()
    try:
        if df.loc[df.index[-1], 'buy/sell'] == 'buy':
            print('buy nowww')
            # adding data to portfolio dataframe if trade has buy signal
            newcol = pd.Series({'time':dt.datetime.today(),'buy_price':a.loc[a.index[-1]]['Close'], 'stock':tick})
            newser = df.loc[df.index[-1].append(newcol)
            portfolio = portfolio.append(newser,ignore_index = True)      
        else:
            print('Noooooo')
    except:
        # capturing error in error dataframe
        newcol = pd.Series({'time':dt.datetime.today(),'error':sys.exc_info(), 'stock':tick})
        error = error.append(newcol,ignore_index=True)
        print('error capture')
    

# type(newser)
# a = a.append(newser,ignore_index = True)
# madf.loc[madf['buy/sell'] == 'buy']


# for tick in ohlcv_data_update:
#     print(ohlcv_data_update[tick].tail(1)['buy/sell'])




# a = ohlcv_data_update[tick]
# a.loc[a.index[-1], 'buy/sell'].assign({'time':dt.datetime.today(),'buy_price':a.loc[a.index[-1]]['Close']})

# stock_pick.loc[stock_pick.index[-1], "Regime"] = 0

# a.loc[a.index[-1]].append(add)


# add = pd.Series({'time':dt.datetime.today(),'buy_price':a.loc[a.index[-1]]['Close']})


# sys.exc_info()
