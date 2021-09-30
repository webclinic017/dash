from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import time
currency ='EURUSD'
TF = mt5.TIMEFRAME_H4
def get_data(currency,TF):
    rates =None
    mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe")
    while (rates is None) :
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1500)
        if not mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe"):
            print("initialize() failed, error code =", mt5.last_error())
            quit()
        rates = mt5.copy_rates_from(currency, TF, datetime(2025, 2, 6), 100)
        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    data = rates_frame
    return data

def buy (price,lot,TP,SL,starting_date):
    state = 'open'

    if instant_price >= TP:


profit = abs(price - instat_price)


def start(data):
    for i in range(len(data)):
        instant_data = data[i]
