
from datetime import datetime
import MetaTrader5 as mt5

import pandas as pd

import time


def eng_s(rates_frame,rsi_per,rsi_val):
    flesh = 'chay'
    ldf = len(rates_frame)
    i = 0
    flag_rsi3 = 0
    flesh_U = 0
    flesh_D = 0
    flag_rsi3_r = 0

    while i < ldf:

        if rates_frame[rsi_per][i] > rsi_val and rates_frame['ema20'][i] > rates_frame['ema50'][i]:
            flag_rsi3 = 1
        if flag_rsi3 == 1 and rates_frame['open'][i - 1] < rates_frame['close'][i - 1] and rates_frame['low'][i - 1] > \
                rates_frame['close'][i]:
            flag_n = i
            flesh_U = 1
            flag_rsi3 = 0
        if flag_rsi3 == 1 and rates_frame[rsi_per][i] < rsi_val:
            flag_rsi3 = 0

        if flesh_U == 1 and ( ldf - flag_n  > 8 or
                rates_frame['close'][i] > rates_frame['open'][flag_n] or rates_frame['close'][i] > rates_frame['close'][
            flag_n - 1]):

            flesh_U = 0
        if flesh_U == 1 and rates_frame['ema18'][i] > rates_frame['close'][i]:
            flesh_U = 0

        if rates_frame['RSI3'][i] < 100 - rsi_val and rates_frame['ema20'][i] < rates_frame['ema50'][i]:
            flag_rsi3_r = 1
        if flag_rsi3_r == 1 and rates_frame['open'][i - 1] > rates_frame['close'][i - 1] and rates_frame['high'][
            i - 1] < rates_frame['close'][i]:
            flag_nr = i
            flesh_D = 1
            flag_rsi3_r = 0
        if flag_rsi3_r == 1 and rates_frame[rsi_per][i] > 100 - rsi_val:
            flag_rsi3_r = 0

        if flesh_D == 1 and (ldf - flag_nr  > 8 or rates_frame['close'][i] < rates_frame['open'][flag_nr] or rates_frame['close'][i] <
                             rates_frame['close'][flag_nr - 1]):
            flesh_D = 0
        if flesh_D == 1 and rates_frame['ema18'][i] < rates_frame['close'][i]:
            flesh_D = 0
        i += 1
    if flesh_U == 1:
        flesh = 'D'
    elif flesh_D == 1:
        flesh = 'U'
    else:
        flesh = 'chay'
    return flesh




def eng(rates_frame):
    rsi_per = 'RSI3'
    flesh1 = eng_s(rates_frame,rsi_per,87)
    rsi_per = 'RSI14'
    flesh2 = eng_s(rates_frame,rsi_per,75)
    flesh = 'chay'
    if flesh1 != 'chay' and flesh1 == flesh2 :
        flesh = flesh1
    return flesh

def computeRSI(data, time_window):
    diff = data.diff(1).dropna()  # diff in one field(one day)
    # this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff
    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[diff > 0]
    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[diff < 0]
    # check pandas documentation for ewm
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    # values are related to exponential decay
    # we set com=time_window-1 so we get decay alpha=1/time_window
    up_chg_avg = up_chg.ewm(com=time_window - 1, min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window - 1, min_periods=time_window).mean()
    rs = abs(up_chg_avg / down_chg_avg)
    rsi = 100 - 100 / (1 + rs)
    return rsi

def tenkanH4(currency,tft,tftup):
    rates =None
    ratesup=None
    mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe")
    while (rates is None) and (ratesup is None):
        pd.set_option('display.max_columns', 500)  # number of columns to be displayed
        pd.set_option('display.width', 1500)  # max table width to display
        # import pytz module for working with time zone
        # establish connection to MetaTrader 5 terminal
        if not mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe"):
            print("initialize() failed, error code =", mt5.last_error())
            quit()
        # set time zone to UTC
        # get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
        rates = mt5.copy_rates_from(currency, tft, datetime(2025, 2, 6), 100)
        ratesup = mt5.copy_rates_from(currency, tftup, datetime(2025, 2, 6), 100)
        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame['time'] = rates_frame.time.shift(-1)
    rates_frame.drop(rates_frame.tail(1).index, inplace=True)
    rates_frameup = pd.DataFrame(ratesup)
    rates_frameup = rates_frameup.rename(columns={"close": "closeup", "open": "openup", "low": "lowup", "high": "highup"})
    rates_frameup['time'] = pd.to_datetime(rates_frameup['time'], unit='s')
    rates_frameup['time'] = rates_frameup.time.shift(-1)
    rates_frameup.drop(rates_frameup.tail(1).index, inplace=True)
    rates_frame['RSI3'] = computeRSI(rates_frame['close'], 3)
    rates_frame['RSI14'] = computeRSI(rates_frame['close'], 14)
    rates_frameup['RSI14up'] = computeRSI(rates_frameup['closeup'], 14)
    rates_frame['14-high'] = rates_frame['high'].rolling(4).max()
    rates_frame['14-low'] = rates_frame['low'].rolling(4).min()
    rates_frame['%K'] = (rates_frame['close'] - rates_frame['14-low'])*100/(rates_frame['14-high'] - rates_frame['14-low'])
    rates_frame['%D'] = rates_frame['%K'].rolling(1).mean()
    col = rates_frame.loc[: , '%K':'%D']
    rates_frame['stock'] = rates_frame.loc[: , '%K':'%D'].mean(axis=1)
    rates_frameup['14-highup'] = rates_frameup['highup'].rolling(4).max()
    rates_frameup['14-lowup'] = rates_frameup['lowup'].rolling(4).min()
    rates_frameup['%Kup'] = (rates_frameup['closeup'] - rates_frameup['14-lowup'])*100/(rates_frameup['14-highup'] - rates_frameup['14-lowup'])
    rates_frameup['%Dup'] = rates_frameup['%Kup'].rolling(1).mean()
    col = rates_frameup.loc[: , '%Kup':'%Dup']
    rates_frameup['stockup'] = rates_frameup.loc[: , '%Kup':'%Dup'].mean(axis=1)
    ema_short = rates_frame['close'].ewm(span=20, adjust=False).mean()
    rates_frame['ema20']=rates_frame['close'].ewm(span=20, adjust=False).mean()
    rates_frame['ema50']=rates_frame['close'].ewm(span=50, adjust=False).mean()
    rates_frameup['ema20up']=rates_frameup['closeup'].ewm(span=20, adjust=False).mean()
    rates_frameup['ema50up']=rates_frameup['closeup'].ewm(span=50, adjust=False).mean()
    nine_period_high = rates_frame['high'].rolling(window= 9).max()
    nine_period_low = rates_frame['low'].rolling(window= 9).min()
    rates_frame['tenkan_sen'] = (nine_period_high + nine_period_low) /2
    rates_frame = pd.merge_ordered(rates_frame, rates_frameup, fill_method="ffill")
    rates_frame = rates_frame.drop(['tick_volume', 'spread','real_volume','14-high','14-low','%K','%D','14-highup','14-lowup','%Kup','%Dup'], axis=1)
    rates_frame = rates_frame.drop_duplicates(subset=['time'], keep='last')
    rates_frame = rates_frame.reset_index(drop=True)
    tireH4 = 'chay'
    ldf = len(rates_frame)
    i = 0
    flag_rsi3_n = None
    flag_O = None
    flag_Oj = None
    flag_fo = 0
    flag_foj = 0
    vin = False
    while i < ldf:
        if rates_frame['RSI3'][i] > 87 and rates_frame['closeup'][i] > rates_frame['ema50up'][i] and rates_frame['closeup'][i] > rates_frame['ema20up'][i]\
                and rates_frame['close'][i] > rates_frame['ema50'][i] and rates_frame['close'][i] > rates_frame['ema20'][i]:
            flag_rsi3_n = i
        i += 1
    if flag_rsi3_n is not None:
        i = flag_rsi3_n
        flag_rsi3 = 1
        while i < ldf:
            if rates_frame['stock'][i] < 25  or rates_frame['RSI14up'][i] < 25 or rates_frame['RSI14up'][i] > 75  : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_rsi3 = 0
            if rates_frame['stock'][i] > 25  and (rates_frame['RSI14up'][i] < 25 or rates_frame['RSI14up'][i] > 75)  : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_rsi3 = 2
            if rates_frame['stock'][i] < 25  and rates_frame['RSI14'][i] > 55.5 and (rates_frame['RSI14up'][i] > 25 and rates_frame['RSI14up'][i] < 75)  : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_O = i
            if rates_frame['stock'][i] < 25  and rates_frame['RSI14'][i] > 55.5 and (rates_frame['RSI14up'][i] < 25 or rates_frame['RSI14up'][i] > 75)  : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_Oj = i
            i += 1
        i = flag_rsi3_n + 1
        if flag_rsi3 == 2:
            j = ldf -1
            while j > flag_rsi3_n:
                if rates_frame['stock'][j] < 25 and rates_frame['close'][j] < rates_frame['ema50'][j] and \
                        rates_frame['close'][j] < rates_frame['ema20'][j]:
                    flag_rsi3 = 0
                j -= 1
        if flag_O is not None and i <= flag_O:
            while i <= flag_O :
                #print(rates_frame['stock'][i] - rates_frame['stock'][i-1] > 20)
                if (rates_frame['stock'][i] - rates_frame['stock'][i-1] > 20):
                    vin = True
                i+=1
        elif flag_Oj is not None and i <= flag_Oj:
            while i <= flag_Oj:
                if rates_frame['stock'][i] - rates_frame['stock'][i-1] > 20:
                    vin = True
                i +=1
        elif flag_O is None and flag_Oj is None :
            while i < ldf:
                if rates_frame['stock'][i] - rates_frame['stock'][i-1] > 20:
                    vin = True
                i +=1
        if flag_O is not None : #and flag_rsi3 == 1
            i = flag_O
            flag_fo = 1
            while i < ldf :
                if rates_frame['stock'][i] > 75 or rates_frame['ema50'][i] > rates_frame['close'][i] :
                    flag_fo = 0
                i += 1
        if flag_Oj is not None : #and flag_rsi3 == 1
            i = flag_Oj
            flag_foj = 1
            while i < ldf :
                if rates_frame['stock'][i] > 75 or rates_frame['ema50'][i] > rates_frame['close'][i] :
                    flag_foj = 0
                i += 1
        if vin == False:
            if flag_rsi3 == 1:
                tireH4 = 'v'
            if flag_rsi3 == 2:
                tireH4 = 'j'
            if flag_fo == 1 :
                tireH4 = 'O'
            if flag_foj == 1:
                tireH4 = 'Oj'
    i = 0
    flag_rsi3r_n = None
    flag_Or = None
    flag_Ojr = None
    flag_for = 0
    flag_fojr = 0
    vinr = False
    while i < ldf:
        if rates_frame['RSI3'][i] < 13 and  rates_frame['closeup'][i] < rates_frame['ema50up'][i] and rates_frame['closeup'][i] < rates_frame['ema20up'][i]\
                and  rates_frame['close'][i] < rates_frame['ema50'][i] and rates_frame['close'][i] < rates_frame['ema20'][i]:
            flag_rsi3r_n = i
        i += 1
    if flag_rsi3r_n is not None :
        i = flag_rsi3r_n
        flag_rsi3r =1
        while i < ldf:
            if rates_frame['stock'][i] > 75 or (rates_frame['RSI14up'][i] > 75 or rates_frame['RSI14up'][i] < 25)  : #or rates_frame['tenken_sen'][i] < rates_frame['close'][i]
                flag_rsi3r = 0
            if rates_frame['stock'][i] < 75 and (rates_frame['RSI14up'][i] > 75 or rates_frame['RSI14up'][i] < 25)  : #or rates_frame['tenken_sen'][i] < rates_frame['close'][i]
                flag_rsi3r = 2
            if rates_frame['stock'][i] > 75  and rates_frame['RSI14'][i] < 44.5 and (rates_frame['RSI14up'][i] > 25 and rates_frame['RSI14up'][i] < 75)  : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_Or = i
            if rates_frame['stock'][i] > 75  and rates_frame['RSI14'][i] < 44.5 and (rates_frame['RSI14up'][i] < 25 or rates_frame['RSI14up'][i] > 75)  : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_Ojr = i
            i += 1
        i = flag_rsi3r_n + 1
        if flag_rsi3r == 2:
            j = ldf -1
            while j > flag_rsi3r_n:
                if rates_frame['stock'][j] > 75 and rates_frame['close'][j] > rates_frame['ema50'][j] and \
                        rates_frame['close'][j] > rates_frame['ema20'][j]:
                    flag_rsi3r = 0
                j -= 1
        if flag_Or is not None and i <= flag_Or :
            while i <= flag_Or:
                if (rates_frame['stock'][i-1] - rates_frame['stock'][i]) > 20 :
                    vinr = True
                i += 1
        elif flag_Ojr is not None and i <= flag_Ojr:
            while i <= flag_Ojr:
                if (rates_frame['stock'][i-1] - rates_frame['stock'][i]) > 20 :
                    vinr = True
                i += 1
        elif flag_Or is None and flag_Ojr is None:
            while i < ldf:
                if rates_frame['stock'][i-1] - rates_frame['stock'][i ] > 20:
                    vinr = True
                i += 1
        if flag_Or is not None : #and flag_rsi3r == 1
            i = flag_Or
            flag_for = 1
            while i < ldf:
                if rates_frame['stock'][i] < 25 or rates_frame['ema50'][i] < rates_frame['close'][i] :
                    flag_for = 0
                i += 1
        if flag_Ojr is not None : #and flag_rsi3r == 1
            i = flag_Ojr
            flag_fojr = 1
            while i < ldf:
                if rates_frame['stock'][i] < 25 or rates_frame['ema50'][i] < rates_frame['close'][i] :
                    flag_fojr = 0
                i += 1
        if vinr == False:
            if flag_rsi3r == 1:
                tireH4 = 'r'
            if flag_rsi3r == 2:
                tireH4 = 'j'
            if flag_for == 1 :
                tireH4 = 'Or'
            if flag_fojr == 1:
                tireH4 = 'Ojr'
    return tireH4

def sinn(currency):
    sinH4 = ''
    sinD1 = ''
    for tfts in [[mt5.TIMEFRAME_H4,mt5.TIMEFRAME_D1],[mt5.TIMEFRAME_D1,mt5.TIMEFRAME_W1]]:
        tft = tfts[0]
        tftup = tfts[1]
        tireH4 = tenkanH4(currency, tft, tftup)
        if tft == mt5.TIMEFRAME_H4 and tireH4 in ['O','Or','Oj','Ojr']:
            sinH4 = 'H4'
        if tft == mt5.TIMEFRAME_D1 and tireH4 in ['O','Or','Oj','Ojr']:
            sinD1 = 'D1'
        sin = [sinH4,sinD1]
    return sin


def tire_vert(currency,TF,TFup):
    rates =None
    ratesup=None
    mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe")
    while (rates is None) and (ratesup is None):
        pd.set_option('display.max_columns', 500)  # number of columns to be displayed
        pd.set_option('display.width', 1500)  # max table width to display
        # import pytz module for working with time zone
        # establish connection to MetaTrader 5 terminal
        if not mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe"):
            print("initialize() failed, error code =", mt5.last_error())
            quit()
        # set time zone to UTC
        # get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
        rates = mt5.copy_rates_from(currency, TF, datetime(2025, 2, 6), 100)
        ratesup = mt5.copy_rates_from(currency, TFup, datetime(2025, 2, 6), 100)
        if TF == mt5.TIMEFRAME_M1:
            ratesupup = mt5.copy_rates_from(currency, mt5.TIMEFRAME_M15, datetime(2025, 2, 6), 100)
        if TF == mt5.TIMEFRAME_M5:
            ratesupup = mt5.copy_rates_from(currency, mt5.TIMEFRAME_H1, datetime(2025, 2, 6), 100)
            ratesupupup = mt5.copy_rates_from(currency, mt5.TIMEFRAME_H4, datetime(2025, 2, 6), 100)
            ratesupupupup = mt5.copy_rates_from(currency, mt5.TIMEFRAME_D1, datetime(2025, 2, 6), 100)
        if TF == mt5.TIMEFRAME_M15:
            ratesupup = mt5.copy_rates_from(currency, mt5.TIMEFRAME_H4, datetime(2025, 2, 6), 100)
        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame['time'] = rates_frame.time.shift(-1)
    rates_frame.drop(rates_frame.tail(1).index, inplace=True)
    rates_frameup = pd.DataFrame(ratesup)
    rates_frameup = rates_frameup.rename(columns={"close": "closeup", "open": "openup", "low": "lowup", "high": "highup"})
    rates_frameup['time'] = pd.to_datetime(rates_frameup['time'], unit='s')
    rates_frameup['time'] = rates_frameup.time.shift(-1)
    rates_frameup.drop(rates_frameup.tail(1).index, inplace=True)
    if TF == mt5.TIMEFRAME_M1:
        rates_frameupup = pd.DataFrame(ratesupup)
        rates_frameupup = rates_frameupup.rename(columns={"close": "closeupup", "open": "openupup", "low": "lowupup", "high": "highupup"})
        rates_frameupup['time'] = pd.to_datetime(rates_frameupup['time'], unit='s')
        rates_frameupup['time'] = rates_frameupup.time.shift(-1)
        rates_frameupup.drop(rates_frameupup.tail(1).index, inplace=True)
        rates_frameupup['ema20upup'] = rates_frameupup['closeupup'].ewm(span=20, adjust=False).mean()
        rates_frameupup['ema50upup'] = rates_frameupup['closeupup'].ewm(span=50, adjust=False).mean()
    if TF == mt5.TIMEFRAME_M5:
        rates_frameupup = pd.DataFrame(ratesupup)
        rates_frameupup = rates_frameupup.rename(columns={"close": "closeupup", "open": "openupup", "low": "lowupup", "high": "highupup"})
        rates_frameupupup = pd.DataFrame(ratesupupup)
        rates_frameupupup = rates_frameupupup.rename(columns={"close": "closeupupup", "open": "openupupup", "low": "lowupupup", "high": "highupupup"})
        rates_frameupupupup = pd.DataFrame(ratesupupupup)
        rates_frameupupupup = rates_frameupupupup.rename(columns={"close": "closeupupupup", "open": "openupupupup", "low": "lowupupupup", "high": "highupupupup"})
        rates_frameupup['time'] = pd.to_datetime(rates_frameupup['time'], unit='s')
        rates_frameupupup['time'] = pd.to_datetime(rates_frameupupup['time'], unit='s')
        rates_frameupupupup['time'] = pd.to_datetime(rates_frameupupupup['time'], unit='s')
        rates_frameupup['time'] = rates_frameupup.time.shift(-1)
        rates_frameupupup['time'] = rates_frameupupup.time.shift(-1)
        rates_frameupupupup['time'] = rates_frameupupupup.time.shift(-1)
        rates_frameupup.drop(rates_frameupup.tail(1).index, inplace=True)
        rates_frameupupup.drop(rates_frameupupup.tail(1).index, inplace=True)
        rates_frameupupupup.drop(rates_frameupupupup.tail(1).index, inplace=True)
        rates_frameupup['ema20upup'] = rates_frameupup['closeupup'].ewm(span=20, adjust=False).mean()
        rates_frameupup['ema50upup'] = rates_frameupup['closeupup'].ewm(span=50, adjust=False).mean()
        rates_frameupupup['ema20upupup'] = rates_frameupupup['closeupupup'].ewm(span=20, adjust=False).mean()
        rates_frameupupup['ema50upupup'] = rates_frameupupup['closeupupup'].ewm(span=50, adjust=False).mean()
        rates_frameupupupup['ema20upupupup'] = rates_frameupupupup['closeupupupup'].ewm(span=20, adjust=False).mean()
        rates_frameupupupup['ema50upupupup'] = rates_frameupupupup['closeupupupup'].ewm(span=50, adjust=False).mean()
    if TF == mt5.TIMEFRAME_M15:
        rates_frameupup = pd.DataFrame(ratesupup)
        rates_frameupup = rates_frameupup.rename(columns={"close": "closeupup", "open": "openupup", "low": "lowupup", "high": "highupup"})
        rates_frameupup['time'] = pd.to_datetime(rates_frameupup['time'], unit='s')
        rates_frameupup['time'] = rates_frameupup.time.shift(-1)
        rates_frameupup.drop(rates_frameupup.tail(1).index, inplace=True)
        rates_frameupup['ema20upup'] = rates_frameupup['closeupup'].ewm(span=20, adjust=False).mean()
        rates_frameupup['ema50upup'] = rates_frameupup['closeupup'].ewm(span=50, adjust=False).mean()
    rates_frame['RSI3'] = computeRSI(rates_frame['close'], 3)
    rates_frame['RSI14'] = computeRSI(rates_frame['close'], 14)
    rates_frameup['RSI14up'] = computeRSI(rates_frameup['closeup'], 14)
    rates_frame['14-high'] = rates_frame['high'].rolling(4).max()
    rates_frame['14-low'] = rates_frame['low'].rolling(4).min()
    rates_frame['%K'] = (rates_frame['close'] - rates_frame['14-low'])*100/(rates_frame['14-high'] - rates_frame['14-low'])
    rates_frame['%D'] = rates_frame['%K'].rolling(1).mean()
    col = rates_frame.loc[: , '%K':'%D']
    rates_frame['stock'] = rates_frame.loc[: , '%K':'%D'].mean(axis=1)
    rates_frameup['14-highup'] = rates_frameup['highup'].rolling(4).max()
    rates_frameup['14-lowup'] = rates_frameup['lowup'].rolling(4).min()
    rates_frameup['%Kup'] = (rates_frameup['closeup'] - rates_frameup['14-lowup'])*100/(rates_frameup['14-highup'] - rates_frameup['14-lowup'])
    rates_frameup['%Dup'] = rates_frameup['%Kup'].rolling(1).mean()
    col = rates_frameup.loc[: , '%Kup':'%Dup']
    rates_frameup['stockup'] = rates_frameup.loc[: , '%Kup':'%Dup'].mean(axis=1)
    ema_short = rates_frame['close'].ewm(span=20, adjust=False).mean()
    rates_frame['ema18'] = rates_frame['close'].ewm(span=20, adjust=False).mean()
    rates_frame['ema20']=rates_frame['close'].ewm(span=20, adjust=False).mean()
    rates_frame['ema50']=rates_frame['close'].ewm(span=50, adjust=False).mean()
    rates_frameup['ema20up']=rates_frameup['closeup'].ewm(span=20, adjust=False).mean()
    rates_frameup['ema50up']=rates_frameup['closeup'].ewm(span=50, adjust=False).mean()
    nine_period_high = rates_frame['high'].rolling(window= 9).max()
    nine_period_low = rates_frame['low'].rolling(window= 9).min()
    rates_frame['tenkan_sen'] = (nine_period_high + nine_period_low) /2
    rates_frame = pd.merge_ordered(rates_frame, rates_frameup, fill_method="ffill")
    if TF == mt5.TIMEFRAME_M1 or TF == mt5.TIMEFRAME_M5 or TF == mt5.TIMEFRAME_M15:
        rates_frame = pd.merge_ordered(rates_frame, rates_frameupup, fill_method="ffill")
    if TF == mt5.TIMEFRAME_M5:
        rates_frame = pd.merge_ordered(rates_frame, rates_frameupupup, fill_method="ffill")
        rates_frame = pd.merge_ordered(rates_frame, rates_frameupupupup, fill_method="ffill")
    rates_frame = rates_frame.drop(['tick_volume', 'spread','real_volume','14-high','14-low','%K','%D','14-highup','14-lowup','%Kup','%Dup'], axis=1)
    rates_frame = rates_frame.drop_duplicates(subset=['time'], keep='last')
    rates_frame = rates_frame.reset_index(drop=True)
    return  rates_frame

def trt(rates_frame):
    tire = 'chay'
    ldf = len(rates_frame)
    i = 0
    flag_rsi3_n = None
    flag_O = None
    flag_Oj = None
    flag_fo = 0
    flag_foj = 0
    vin = False
    contre = False
    while i < ldf:
        if TF == mt5.TIMEFRAME_M1 or TF == mt5.TIMEFRAME_M5 or TF == mt5.TIMEFRAME_M15:
            if rates_frame['RSI3'][i] > 87 and rates_frame['closeup'][i] > rates_frame['ema50up'][i] and rates_frame['closeup'][i] > rates_frame['ema20up'][i]\
                    and rates_frame['close'][i] > rates_frame['ema50'][i] and rates_frame['close'][i] > rates_frame['ema20'][i] and rates_frame['closeupup'][i] > rates_frame['ema50upup'][i] and rates_frame['closeupup'][i] > rates_frame['ema20upup'][i]:
                flag_rsi3_n = i
                contre = False
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][i] < rates_frame['ema50upupup'][i] and\
                        rates_frame['closeupupupup'][i] < rates_frame['ema20upupup'][i] and\
                        rates_frame['closeupupupup'][i] < rates_frame['ema50upupupup'][i] and\
                        rates_frame['closeupupupup'][i] < rates_frame['ema20upupupup'][i] :
                    contre = True
        else:
            if rates_frame['RSI3'][i] > 87 and rates_frame['closeup'][i] > rates_frame['ema50up'][i] and rates_frame['closeup'][i] > rates_frame['ema20up'][i]\
                    and rates_frame['close'][i] > rates_frame['ema50'][i] and rates_frame['close'][i] > rates_frame['ema20'][i]:
                flag_rsi3_n = i
        i += 1
    if flag_rsi3_n is not None:
        i = flag_rsi3_n
        flag_rsi3 = 1
        while i < ldf:
            if rates_frame['stock'][i] < 25  or rates_frame['RSI14up'][i] < 25 or rates_frame['RSI14up'][i] > 75 or rates_frame['tenkan_sen'][i] > rates_frame['close'][i] : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_rsi3 = 0
            if rates_frame['stock'][i] > 25  and (rates_frame['RSI14up'][i] < 25 or rates_frame['RSI14up'][i] > 75) and rates_frame['tenkan_sen'][i] < rates_frame['close'][i] : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_rsi3 = 2
            if rates_frame['stock'][i] < 25  and rates_frame['RSI14'][i] > 55.5 and (rates_frame['RSI14up'][i] > 25 and rates_frame['RSI14up'][i] < 75) and rates_frame['tenkan_sen'][i] < rates_frame['close'][i] : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_O = i
            if rates_frame['stock'][i] < 25  and rates_frame['RSI14'][i] > 55.5 and (rates_frame['RSI14up'][i] < 25 or rates_frame['RSI14up'][i] > 75) and rates_frame['tenkan_sen'][i] < rates_frame['close'][i] : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_Oj = i
            i += 1
        i = flag_rsi3_n + 1
        if flag_rsi3 == 2:
            j = ldf -1
            while j > flag_rsi3_n:
                if rates_frame['stock'][j] < 25 and rates_frame['close'][j] < rates_frame['ema50'][j] and \
                        rates_frame['close'][j] < rates_frame['ema20'][j]:
                    flag_rsi3 = 0
                j -= 1
        if flag_O is not None and i <= flag_O:
            ini = rates_frame['stock'][i - 1]
            while i <= flag_O :
                if ini > rates_frame['stock'][i]:
                    ini = rates_frame['stock'][i]
                #print(rates_frame['stock'][i] - rates_frame['stock'][i-1] > 20)
                if (rates_frame['stock'][i] - ini > 20):
                    vin = True
                i+=1
        elif flag_Oj is not None and i <= flag_Oj:
            inij = rates_frame['stock'][i - 1]
            while i <= flag_Oj:
                if inij > rates_frame['stock'][i]:
                    inij = rates_frame['stock'][i]
                if rates_frame['stock'][i] - inij > 20 :
                    vin = True
                i +=1
        elif flag_O is None and flag_Oj is None :
            inin = rates_frame['stock'][i - 1]
            while i < ldf:
                if inin > rates_frame['stock'][i]:
                    inin = rates_frame['stock'][i]
                if rates_frame['stock'][i] - inin > 20:
                    vin = True
                i +=1
        if flag_O is not None : #and flag_rsi3 == 1
            i = flag_O
            flag_fo = 1
            while i < ldf :
                if rates_frame['stock'][i] > 75 or rates_frame['ema50'][i] > rates_frame['close'][i] :
                    flag_fo = 0
                i += 1
        if flag_Oj is not None : #and flag_rsi3 == 1
            i = flag_Oj
            flag_foj = 1
            while i < ldf :
                if rates_frame['stock'][i] > 75 or rates_frame['ema50'][i] > rates_frame['close'][i] :
                    flag_foj = 0
                i += 1
        if vin == False:
            ldf = len(rates_frame) - 1
            if flag_rsi3 == 1:
                tire = 'v'
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][ldf] < rates_frame['ema50upupup'][ldf] and \
                        rates_frame['closeupupup'][ldf] < rates_frame['ema20upupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] < rates_frame['ema50upupupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] < rates_frame['ema20upupupup'][ldf]:
                    tire = 'v_att'
            if flag_rsi3 == 2:
                tire = 'j'
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][ldf] < rates_frame['ema50upupup'][ldf] and \
                        rates_frame['closeupupup'][ldf] < rates_frame['ema20upupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] < rates_frame['ema50upupupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] < rates_frame['ema20upupupup'][ldf]:
                    tire = 'j_att'
            if flag_fo == 1 :
                tire = 'O'
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][ldf] < rates_frame['ema50upupup'][ldf] and \
                        rates_frame['closeupupup'][ldf] < rates_frame['ema20upupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] < rates_frame['ema50upupupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] < rates_frame['ema20upupupup'][ldf]:
                    tire = 'O_att'
            if flag_foj == 1:
                tire = 'Oj'
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][ldf] < rates_frame['ema50upupup'][ldf] and \
                        rates_frame['closeupupup'][ldf] < rates_frame['ema20upupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] < rates_frame['ema50upupupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] < rates_frame['ema20upupupup'][ldf]:
                    tire = 'Oj_att'
    i = 0
    flag_rsi3r_n = None
    flag_Or = None
    flag_Ojr = None
    flag_for = 0
    flag_fojr = 0
    vinr = False
    while i < ldf:
        if TF == mt5.TIMEFRAME_M1 or TF == mt5.TIMEFRAME_M5 or TF == mt5.TIMEFRAME_M15:
            if rates_frame['RSI3'][i] < 13 and  rates_frame['closeup'][i] < rates_frame['ema50up'][i] and rates_frame['closeup'][i] < rates_frame['ema20up'][i]\
                    and  rates_frame['close'][i] < rates_frame['ema50'][i] and rates_frame['close'][i] < rates_frame['ema20'][i] and  rates_frame['closeupup'][i] < rates_frame['ema50upup'][i] and rates_frame['closeupup'][i] < rates_frame['ema20upup'][i]:
                flag_rsi3r_n = i
        else :
            if rates_frame['RSI3'][i] < 13 and  rates_frame['closeup'][i] < rates_frame['ema50up'][i] and rates_frame['closeup'][i] < rates_frame['ema20up'][i]\
                    and  rates_frame['close'][i] < rates_frame['ema50'][i] and rates_frame['close'][i] < rates_frame['ema20'][i]:
                flag_rsi3r_n = i
        i += 1
    if flag_rsi3r_n is not None :
        i = flag_rsi3r_n
        flag_rsi3r =1
        while i < ldf:
            if rates_frame['stock'][i] > 75 or (rates_frame['RSI14up'][i] > 75 or rates_frame['RSI14up'][i] < 25) or rates_frame['tenkan_sen'][i] < rates_frame['close'][i] : #or rates_frame['tenken_sen'][i] < rates_frame['close'][i]
                flag_rsi3r = 0
            if rates_frame['stock'][i] < 75 and (rates_frame['RSI14up'][i] > 75 or rates_frame['RSI14up'][i] < 25) and rates_frame['tenkan_sen'][i] > rates_frame['close'][i] : #or rates_frame['tenken_sen'][i] < rates_frame['close'][i]
                flag_rsi3r = 2
            if rates_frame['stock'][i] > 75  and rates_frame['RSI14'][i] < 44.5 and (rates_frame['RSI14up'][i] > 25 and rates_frame['RSI14up'][i] < 75) and rates_frame['tenkan_sen'][i] > rates_frame['close'][i] : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_Or = i
            if rates_frame['stock'][i] > 75  and rates_frame['RSI14'][i] < 44.5 and (rates_frame['RSI14up'][i] < 25 or rates_frame['RSI14up'][i] > 75) and rates_frame['tenkan_sen'][i] > rates_frame['close'][i] : #or rates_frame['tenkan_sen'][i] > rates_frame['close'][i]
                flag_Ojr = i
            i += 1
        i = flag_rsi3r_n + 1
        if flag_rsi3r == 2:
            j = ldf -1
            while j > flag_rsi3r_n:
                if rates_frame['stock'][j] > 75 and rates_frame['close'][j] > rates_frame['ema50'][j] and \
                        rates_frame['close'][j] > rates_frame['ema20'][j]:
                    flag_rsi3r = 0
                j -= 1
        if flag_Or is not None and i <= flag_Or :
            inir = rates_frame['stock'][i - 1]
            while i <= flag_Or:
                if inir < rates_frame['stock'][i]:
                    inir = rates_frame['stock'][i]
                if (inir - rates_frame['stock'][i]) > 20 :
                    vinr = True
                i += 1
        elif flag_Ojr is not None and i <= flag_Ojr:
            inirj = rates_frame['stock'][i - 1]
            while i <= flag_Ojr:
                if inirj < rates_frame['stock'][i]:
                    inirj = rates_frame['stock'][i]
                if (inirj - rates_frame['stock'][i]) > 20 :
                    vinr = True
                i += 1
        elif flag_Or is None and flag_Ojr is None:
            inirn = rates_frame['stock'][i - 1]
            while i < ldf:
                if inirn < rates_frame['stock'][i]:
                    inirn = rates_frame['stock'][i]
                if inirn - rates_frame['stock'][i] > 20:
                    vinr = True
                i += 1
        if flag_Or is not None : #and flag_rsi3r == 1
            i = flag_Or
            flag_for = 1
            while i < ldf:
                if rates_frame['stock'][i] < 25 or rates_frame['ema50'][i] < rates_frame['close'][i] :
                    flag_for = 0
                i += 1
        if flag_Ojr is not None : #and flag_rsi3r == 1
            i = flag_Ojr
            flag_fojr = 1
            while i < ldf:
                if rates_frame['stock'][i] < 25 or rates_frame['ema50'][i] < rates_frame['close'][i] :
                    flag_fojr = 0
                i += 1
        if vinr == False:
            ldf = len(rates_frame)-1
            if flag_rsi3r == 1:
                tire = 'r'
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][ldf] > rates_frame['ema50upupup'][ldf] and \
                        rates_frame['closeupupup'][ldf] > rates_frame['ema20upupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] > rates_frame['ema50upupupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] > rates_frame['ema20upupupup'][ldf]:
                    tire = 'r_att'
            if flag_rsi3r == 2:
                tire = 'j'
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][ldf] > rates_frame['ema50upupup'][ldf] and \
                        rates_frame['closeupupup'][ldf] > rates_frame['ema20upupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] > rates_frame['ema50upupupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] > rates_frame['ema20upupupup'][ldf]:
                    tire = 'j_att'
            if flag_for == 1 :
                tire = 'Or'
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][ldf] > rates_frame['ema50upupup'][ldf] and \
                        rates_frame['closeupupup'][ldf] > rates_frame['ema20upupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] > rates_frame['ema50upupupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] > rates_frame['ema20upupupup'][ldf]:
                    tire = 'Or_att'
            if flag_fojr == 1:
                tire = 'Ojr'
                if TF == mt5.TIMEFRAME_M5 and rates_frame['closeupupup'][ldf] > rates_frame['ema50upupup'][ldf] and \
                        rates_frame['closeupupup'][ldf] > rates_frame['ema20upupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] > rates_frame['ema50upupupup'][ldf] and \
                        rates_frame['closeupupupup'][ldf] > rates_frame['ema20upupupup'][ldf]:
                    tire = 'Ojr_att'
    if TF == mt5.TIMEFRAME_H4 and tire == 'chay' :
        tenk1 = sinn(currency)
        if 'H4' in tenk1:
            tire = 'T'
    if TF == mt5.TIMEFRAME_D1 and tire == 'chay':
        tenk1 = sinn(currency)
        if 'D1' in tenk1:
            tire = 'T'
    return tire


def findzones(currency,TF,TFup):
    rates = None
    ratesup = None
    mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe")
    while (rates is None) and (ratesup is None):
        pd.set_option('display.max_columns', 500)  # number of columns to be displayed
        pd.set_option('display.width', 1500)  # max table width to display
        # import pytz module for working with time zone
        # establish connection to MetaTrader 5 terminal
        if not mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe"):
            print("initialize() failed, error code =", mt5.last_error())
            quit()
        # set time zone to UTC
        # get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
        rates = mt5.copy_rates_from(currency, TF, datetime(2025, 2, 6), 200)
        ratesup = mt5.copy_rates_from(currency, TFup, datetime(2025, 2, 6), 100)
        point = mt5.symbol_info(currency).point
        mt5.shutdown()
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame['time'] = rates_frame.time.shift(-1)
    rates_frameup = pd.DataFrame(ratesup)
    rates_frameup = rates_frameup.rename(
        columns={"close": "closeup", "open": "openup", "low": "lowup", "high": "highup"})
    rates_frameup['time'] = pd.to_datetime(rates_frameup['time'], unit='s')
    rates_frameup['time'] = rates_frameup.time.shift(-1)
    rates_frame['ema20'] = rates_frame['close'].ewm(span=20, adjust=False).mean()
    rates_frame['ema50'] = rates_frame['close'].ewm(span=50, adjust=False).mean()
    rates_frameup['ema20up'] = rates_frameup['closeup'].ewm(span=20, adjust=False).mean()
    rates_frameup['ema50up'] = rates_frameup['closeup'].ewm(span=50, adjust=False).mean()
    rates_frame['RSI14'] = computeRSI(rates_frame['close'], 14)
    ll= len(rates_frame)
    sma5 = (rates_frame['close'][ll - 2]+rates_frame['close'][ll - 3]+rates_frame['close'][ll - 4]+rates_frame['close'][ll - 5]+rates_frame['close'][ll - 6])/5
    sma3 = (rates_frame['close'][ll - 2]+rates_frame['close'][ll - 3]+rates_frame['close'][ll - 4])/3
    rates_frame = pd.merge_ordered(rates_frame, rates_frameup, fill_method="ffill")
    rates_frame = rates_frame.drop_duplicates(subset=['time'], keep='last')
    rates_frame = rates_frame.reset_index(drop=True)
    rates_frame = rates_frame[140:]
    rates_frame = rates_frame.reset_index(drop=True)
    if rates_frame['close'][len(rates_frame) - 1] > rates_frame['ema20'][len(rates_frame) - 1] and rates_frame['close'][
        len(rates_frame) - 1] > rates_frame['ema50'][len(rates_frame) - 1] and rates_frame['closeup'][
        len(rates_frame) - 1] > rates_frame['ema20up'][len(rates_frame) - 1] and rates_frame['closeup'][
        len(rates_frame) - 1] > rates_frame['ema50up'][len(rates_frame) - 1]:
        DT = 'v'
    elif rates_frame['close'][len(rates_frame) - 1] < rates_frame['ema20'][len(rates_frame) - 1] and \
            rates_frame['close'][len(rates_frame) - 1] < \
            rates_frame['ema50'][len(rates_frame) - 1] and rates_frame['closeup'][len(rates_frame) - 1] < \
            rates_frame['ema20up'][len(rates_frame) - 1] and \
            rates_frame['closeup'][len(rates_frame) - 1] < rates_frame['ema50up'][len(rates_frame) - 1]:
        DT = 'r'
    else:
        DT = 'chay'
    ldf = len(rates_frame)
    last_close = rates_frame['close'][len(rates_frame)-1]
    real_Ex = [rates_frame['RSI14'][len(rates_frame)-1],rates_frame['ema50'][len(rates_frame)-1],rates_frame['ema20'][len(rates_frame)-1],sma5,sma3]
    df = rates_frame
    dfc = df['close']
    ldf = len(df) -1
    lows = [0] * (ldf +1)
    highs = [0] * (ldf +1)
    backstep = 5
    dev = 3
    last_low = 0
    last_high = 0
    for shift in range(2, ldf + 1):
        val = min(df['low'][shift], df['low'][shift - 1], df['low'][shift - 2])
        if val == last_low:
            val = 0
        else:
            last_low = val
            if df['low'][shift] - val > dev * point:
                val = 0
            else:
                for back in range(1, backstep):
                    res = lows[shift - back]
                    if res != 0 and res > val:
                        lows[shift - back] = 0
        if df['low'][shift] == val:
            lows[shift] = val
        else:
            lows[shift] = 0
        val = max(df['high'][shift], df['high'][shift - 1], df['high'][shift - 2])
        if val == last_high:
            val = 0
        else:
            last_high = val
            if val - df['high'][shift] > dev * point:
                val = 0
            else:
                for back in range(1, backstep):
                    res = highs[shift - back]
                    if res != 0 and res < val:
                        highs[shift - back] = 0
        if df['high'][shift] == val:
            highs[shift] = val
        else:
            highs[shift] = 0
    kn = len(highs) - 1
    while kn > 1:
        if highs[kn] != 0 or lows[kn] != 0:
            highs[kn] = 0
            lows[kn] = 0
            break
        kn -= 1
    kn = len(highs) - 1
    lastpeak = None
    while kn >  1:
        if highs[kn] != 0 and lastpeak == 'H':
            if highs[kn] > lastpeakval:
                highs[lastpeakvali] = 0
            else:
                highs[kn] = 0
        if lows[kn] != 0 and lastpeak == 'L':
            if lows[kn] < lastpeakval:
                lows[lastpeakvali] = 0
            else:
                lows[kn] = 0
        if highs[kn] != 0:
            lastpeak = 'H'
            lastpeakval = highs[kn]
            lastpeakvali = kn
        if lows[kn] != 0:
            lastpeak = 'L'
            lastpeakval = lows[kn]
            lastpeakvali = kn
        kn -= 1
    levelsh = []
    levelsl = []
    for i in range(len(highs)):
        if highs[i] != 0:
            levelsh.append((i, highs[i]))
        if lows[i] != 0:
            levelsl.append((i, lows[i]))
    zonesh=[]
    for i in levelsh:
        k = i[0]
        tkasser = False
        while k < len(df) - 1 :
            if i[1] < df['close'][k] :
                tkasser = True
            k += 1
        if i[0] == 0 or (len(df) - i[0]) == 1:
            a=[df['close'][i[0] - 2], df['open'][i[0] - 2], df['close'][i[0] - 1], df['open'][i[0] - 1],df['close'][i[0]], df['open'][i[0]]]
        elif i[0] == 1 or (len(df) - i[0]) == 2:
            a=[df['close'][i[0] - 2], df['open'][i[0] - 2], df['close'][i[0] - 1], df['open'][i[0] - 1],df['close'][i[0]], df['open'][i[0]],df['close'][i[0]+1], df['open'][i[0]+1]]
        elif i[0] >= 2:
            a=[df['close'][i[0] - 2], df['open'][i[0] - 2], df['close'][i[0] - 1], df['open'][i[0] - 1],df['close'][i[0]], df['open'][i[0]],df['close'][i[0]+1], df['open'][i[0]+1],df['close'][i[0]+2], df['open'][i[0]+2]]
        #, max(df['close'][i[0] + 1], df['open'][i[0] + 1]),max(df['close'][i[0] + 2], df['open'][i[0] + 2]), max(df['close'][i[0] + 3], df['open'][i[0] + 3])
        a.sort()
        if not tkasser:
            zonesh.append([a[-2], i[1] ,df['time'][i[0] - 2],df['time'][len(df)-1]])
    zonesl=[]
    for i in levelsl:
        k = i[0]
        tkasser1 = False
        while k < len(df) - 2 :
            if i[1] > df['close'][k]:
                tkasser1 = True
            k += 1
        if i[0] == 0 or (len(df) - i[0]) == 1:
            a = [df['close'][i[0] - 2], df['open'][i[0] - 2], df['close'][i[0] - 1], df['open'][i[0] - 1],df['close'][i[0]], df['open'][i[0]]]
        elif i[0] == 1 or (len(df) - i[0]) == 2:
            a=[df['close'][i[0] - 2], df['open'][i[0] - 2], df['close'][i[0] - 1], df['open'][i[0] - 1],df['close'][i[0]], df['open'][i[0]], df['close'][i[0] + 1], df['open'][i[0] + 1]]
        elif i[0] >= 2:
            a = [df['close'][i[0] - 2], df['open'][i[0] - 2], df['close'][i[0] - 1], df['open'][i[0] - 1],
                 df['close'][i[0]], df['open'][i[0]], df['close'][i[0] + 1], df['open'][i[0] + 1],
                 df['close'][i[0] + 2], df['open'][i[0] + 2]]
        #, min(df['close'][i[0] + 1], df['open'][i[0] + 1]),min(df['close'][i[0] + 2], df['open'][i[0] + 2]), min(df['close'][i[0] + 3], df['open'][i[0] + 3])
        a.sort()
        if not tkasser1:
            zonesl.append([i[1] ,a[1] ,df['time'][i[0] - 2],df['time'][len(df)-1]])
    z = zonesl + zonesh
    return z,last_close,df,DT,real_Ex


def free(zones,last_close,df,real_DT,real_Ex,real_Ex1,real_last_close_M15, pivots,currency):
    louta=[]
    fou9 = []
    inside_zone = False
    for i in zones:
        louta.append(i[1])
        fou9.append(i[0])
        if last_close > i[0] and last_close < i[1]:
            inside_zone = True
    last_touche = 'n'
    if not inside_zone:
        f = [i for i in fou9 if i >= last_close]
        l = [i for i in louta if i <= last_close]
        fp = [i for i in pivots if i >= last_close]
        lp = [i for i in pivots if i <= last_close]
        f += fp
        l += lp
        f.sort()
        l.sort()
        if len(f) > 0:
            f1 = f[0]
            i= len(df) - 1
            while i > 1  and df['high'][i] < f1 :
                i -=1
            if1 = i
        else:
            if1 = 9999999
        i = len(df) - 1
        if len(l) > 0:
            l1 = l[-1]
            while i > 1  and df['low'][i] > l1 :
                i -=1
            il1 = i
        else:
            il1 = 9999999
        if if1 < il1 and real_DT == 'v' and real_Ex[0] < 75 and real_last_close_M15 > real_Ex1[3] and real_Ex1[1] < real_Ex1[2] and real_Ex1[2] < real_Ex1[3] and real_Ex1[3] < real_Ex1[4]: #  and real_last_close_M15 > real_Ex1[1] and real_Ex1[1] > real_Ex1[2] and real_Ex1[2] > real_Ex1[3] and real_Ex1[3] > real_Ex1[4]
            last_touche = 'l'
        elif if1 < il1 and real_DT == 'v' and real_Ex[0] > 75 and real_last_close_M15 > real_Ex1[3] and real_Ex1[1] < real_Ex1[2] and real_Ex1[2] < real_Ex1[3] and real_Ex1[3] < real_Ex1[4]:
            last_touche = 'E'
        elif if1 > il1 and real_DT == 'r' and real_Ex[0] > 25 and real_last_close_M15 < real_Ex1[3] and real_Ex1[1] > real_Ex1[2] and real_Ex1[2] > real_Ex1[3] and real_Ex1[3] > real_Ex1[4]:#
            last_touche = 'f'
        elif if1 > il1 and real_DT == 'r' and real_Ex[0] < 25 and real_last_close_M15 < real_Ex1[3] and real_Ex1[1] > real_Ex1[2] and real_Ex1[2] > real_Ex1[3] and real_Ex1[3] > real_Ex1[4]:
            last_touche = 'Er'
        '''
        elif if1 == il1 and real_DT == 'v' and real_Ex[0] < 75 and real_last_close_M15 > real_Ex1[1] and real_Ex1[1] > real_Ex1[2] and real_Ex1[2] > real_Ex1[3] and real_Ex1[3] > real_Ex1[4]:
            last_touche = 'l'
        elif if1 == il1 and real_DT == 'r' and real_Ex[0] > 25 and real_last_close_M15 < real_Ex1[1] and real_Ex1[1] < real_Ex1[2] and real_Ex1[2] < real_Ex1[3] and real_Ex1[3] < real_Ex1[4]:
            last_touche = 'f'
        '''
    return last_touche

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def freedom(currency):
    zones = []
    pivots = []
    for tfs in [[mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1],[mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4],[mt5.TIMEFRAME_H4, mt5.TIMEFRAME_D1], [mt5.TIMEFRAME_D1, mt5.TIMEFRAME_W1],[mt5.TIMEFRAME_W1, mt5.TIMEFRAME_MN1]]:
        tf = tfs[0]
        tfup = tfs[1]
        if tf == mt5.TIMEFRAME_M15:
            z1, real_last_close_M15, df2, real_DT5, real_Ex1 = findzones(currency, tf, tfup)
        elif tf == mt5.TIMEFRAME_H1:
            z, real_last_close,df1,real_DT,real_Ex = findzones(currency, tf , tfup)
        else :
            z,last_close,df,DT,Ex = findzones(currency,tf,tfup)
        if tf != mt5.TIMEFRAME_M15:
            zones += z
        if tfup == mt5.TIMEFRAME_D1:
            ldf = len(df) - 1
            pD = (df['highup'][ldf] + df['lowup'][ldf] + df['closeup'][ldf]) / 3
            S1D = (pD * 2) - df['highup'][ldf]
            S2D = pD - (df['highup'][ldf] - df['lowup'][ldf])
            R1D = (pD * 2) - df['lowup'][ldf]
            R2D = pD + (df['highup'][ldf] - df['lowup'][ldf])
            pivots += [pD, S1D, S2D, R1D, R2D]
        if tfup == mt5.TIMEFRAME_W1:
            ldf = len(df) - 1
            pW = (df['highup'][ldf] + df['lowup'][ldf] + df['closeup'][ldf]) / 3
            S1W = (pW * 2) - df['highup'][ldf]
            S2W = pW - (df['highup'][ldf] - df['lowup'][ldf])
            R1W = (pW * 2) - df['lowup'][ldf]
            R2W = pW + (df['highup'][ldf] - df['lowup'][ldf])
            pivots += [pW, S1W, S2W, R1W, R2W]
        if tfup == mt5.TIMEFRAME_MN1:
            ldf = len(df) - 1
            pM = (df['highup'][ldf] + df['lowup'][ldf] + df['closeup'][ldf]) / 3
            S1M = (pM * 2) - df['highup'][ldf]
            S2M = pM - (df['highup'][ldf] - df['lowup'][ldf])
            R1M = (pM * 2) - df['lowup'][ldf]
            R2M = pM + (df['highup'][ldf] - df['lowup'][ldf])
            pivots += pM, S1M, S2M, R1M, R2M
    if currency == 'EURUSD' :
        lowrond = truncate(real_last_close, 3)
        highrond = lowrond + 0.001
    if currency == 'GBPUSD' :
        lowrond = truncate(real_last_close, 2)
        highrond = lowrond + 0.01
    if currency == 'GOLD' :
        lowrond = truncate(real_last_close, -1)
        highrond = lowrond + 10
    if currency == 'WTI' :
        lowrond = truncate(real_last_close, 0)
        highrond = lowrond + 1
    if currency == '#USSPX500' :
        lowrond = truncate(real_last_close, -2)
        highrond = lowrond + 100
    if currency == '#USNDAQ100' :
        lowrond = truncate(real_last_close, -2)
        highrond = lowrond + 100
    if currency == '#US30' :
        lowrond = truncate(real_last_close, -2)
        highrond = lowrond + 100
    if currency == '#Germany30' :
        lowrond = truncate(real_last_close, -2)
        highrond = lowrond + 100
    if currency == '#Euro50' :
        lowrond = truncate(real_last_close, -1)
        highrond = lowrond + 10
    if currency == 'USDCAD' :
        lowrond = truncate(real_last_close, 2)
        highrond = lowrond + 0.01
    if currency == 'USDJPY' :
        lowrond = truncate(real_last_close, 0)
        highrond = lowrond + 1
    if currency == 'EURGBP' :
        lowrond = truncate(real_last_close, 2)
        highrond = lowrond + 0.01
    pivots += [lowrond]
    pivots += [highrond]
    last_touche = free(zones,real_last_close,df1,real_DT ,real_Ex,real_Ex1,real_last_close_M15, pivots,currency )
    return last_touche


currencys = ['EURUSD', 'GBPUSD', 'USDCAD','USDJPY', 'GOLD','WTI','#USSPX500','#USNDAQ100', '#US30', '#Germany30', '#Euro50','EURGBP']# '@EP','@ENQ', '@YM', '@RTY', '@DD', '@DSX', 'XAUUSD', '@CLE', '@DB', 'TYAH21','EURUSD', 'GBPUSD', 'USDCAD','USDJPY','EURGBP'


dfg = 0


currencys = ['EURUSD', 'GBPUSD', 'USDCAD','USDJPY', 'GOLD','WTI','#USSPX500','#USNDAQ100', '#US30', '#Germany30', '#Euro50','EURGBP']# '@EP','@ENQ', '@YM', '@RTY', '@DD', '@DSX', 'XAUUSD', '@CLE', '@DB', 'TYAH21','EURUSD', 'GBPUSD', 'USDCAD','USDJPY','EURGBP'
TFs = [[mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5], [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15],
       [mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1], [mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4],
       [mt5.TIMEFRAME_H4, mt5.TIMEFRAME_D1], [mt5.TIMEFRAME_D1, mt5.TIMEFRAME_W1],
       ]
M1 = []
M2 = []
for TFi in TFs:
    for currency in currencys:
        TF = TFi[0]
        TFup = TFi[1]
        M1.append(tire_vert(currency, TF, TFup))
    M2.append([TF, M1])
    M1 = []
data = {'Zone':'' ,'I': currencys, 'M1': '', 'M5': '', 'M15': '', 'H1': '', 'H4': '','D1': ''}

df = pd.DataFrame(data)
dfg = df




from man import db

from man import Item
from man import Ud


while True:
    start_time = time.time()
    dt = datetime.now()
    if dt.second == 1:
        TFs = [[mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5], [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15],[mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1], [mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4],[mt5.TIMEFRAME_H4, mt5.TIMEFRAME_D1], [mt5.TIMEFRAME_D1, mt5.TIMEFRAME_W1]]
        M1 = []
        M2 = []
        M3 = []
        M4 = []
        for TFi in TFs:
            for currency in currencys:
                TF = TFi[0]
                TFup = TFi[1]
                rates_frame = tire_vert(currency, TF, TFup)
                M1.append(trt(rates_frame))
                M3.append(eng(rates_frame))
            M2.append([TF, M1])
            M4.append([TF, M3])
            M1 = []
            M3 = []
        last_touches = []
        for currency in currencys:
            last_touches.append(freedom(currency))
        data = {'Zone': last_touches,'I': currencys, 'M1': M2[0][1], 'M5': M2[1][1], 'M15': M2[2][1], 'H1': M2[3][1], 'H4': M2[4][1],
                'D1': M2[5][1]}
        df = pd.DataFrame(data)
        data1 = {'I': currencys, 'M1': M4[0][1], 'M5': M4[1][1], 'M15': M4[2][1], 'H1': M4[3][1], 'H4': M4[4][1],
                'D1': M4[5][1]}
        df1 = pd.DataFrame(data1)
        global A
        for i in df.columns:
            for j in range(len(df)):
                if dfg[i][j] == 'v' and (df[i][j] == 'O' or df[i][j] == 'T') and i != 'M1':# and i != 'M1'
                    C_out = df['I'][j]
                    TF_out = i
                    A = C_out +' '+ TF_out
                if dfg[i][j] == 'r' and (df[i][j] == 'Or' or df[i][j] == 'Tr') and i != 'M1':# and i != 'M1'
                    C_out = df['I'][j]
                    TF_out = i
                    A = C_out +'  '+ TF_out
        db.drop_all()
        db.create_all()
        for i in range(len(df)):
            item = Item(Zone=df['Zone'][i],name=currencys[i],M1=df['M1'][i],M5=df['M5'][i],M15=df['M15'][i],H1=df['H1'][i], H4=df['H4'][i], D1=df['D1'][i])
            db.session.add(item)
            db.session.commit()
        for i in range(len(df1)):
            item2 = Ud(name=currencys[i],M1=df1['M1'][i],M5=df1['M5'][i],M15=df1['M15'][i],H1=df1['H1'][i], H4=df1['H4'][i], D1=df1['D1'][i])
            db.session.add(item2)
            db.session.commit()
        dfg = df
        print("done")
        print(df)
        print("--- %s seconds ---" % (time.time() - start_time))




'''
from man import db

db.create_all()

currencys = ['EURUSD', 'GBPUSD', 'USDCAD','USDJPY', 'GOLD','WTI','#USSPX500','#USNDAQ100', '#US30', '#Germany30','#Euro50','EURGBP']# '@EP','@ENQ', '@YM', '@RTY', '@DD', '@DSX', 'XAUUSD', '@CLE', '@DB', 'TYAH21','EURUSD', 'GBPUSD', 'USDCAD','USDJPY','EURGBP'



from man import db
db.drop_all()
db.create_all()


for i in range(len(df)-1):
    item = Item(Zone=df['Zone'][i],name=currencys[i],M1=df['M1'][i],M5=df['M5'][i],M15=df['M15'][i],H1=df['H1'][i], H4=df['H4'][i], D1=df['D1'][i])
    db.session.add(item)
    db.session.commit()


for item in Item.query.all():
    item.name
    item.Zone
    item.M1

Item.query.all()[0].name
'''