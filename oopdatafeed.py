import time
import pandas as pd
from datetime import datetime
import MetaTrader5 as mt5
import pytz
import pandas as pd
import webbrowser
import time
import chime
import numpy as np
import os


class Datafeed(object):

    def __init__(self, currency, TF):
        self.currency = currency
        self.TF = TF

    def getdata(self, currency, TF):
        rates = None
        mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe")
        while rates is None:
            pd.set_option('display.max_columns', 500)
            pd.set_option('display.width', 1500)
            if not mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe"):
                print("initialize() failed, error code =", mt5.last_error())
                quit()
            rates = mt5.copy_rates_from(currency, TF, datetime(2025, 2, 6), 100)
            print(currency)
            mt5.shutdown()
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame['time'] = rates_frame.time.shift(-1)
        rates_frame.drop(rates_frame.tail(1).index, inplace=True)
        return rates_frame

    def computeRSI(self, rates_frame, time_window):
        data = rates_frame['close']
        diff = data.diff(1).dropna()
        up_chg = 0 * diff
        down_chg = 0 * diff
        up_chg[diff > 0] = diff[diff > 0]
        down_chg[diff < 0] = diff[diff < 0]
        up_chg_avg = up_chg.ewm(com=time_window - 1, min_periods=time_window).mean()
        down_chg_avg = down_chg.ewm(com=time_window - 1, min_periods=time_window).mean()
        rs = abs(up_chg_avg / down_chg_avg)
        rates_frame['rsi_tf' + str(self.TF) + '_' + str(time_window)] = 100 - 100 / (1 + rs)
        return rates_frame

    def compute_stock(self, rates_frame):
        rates_frame['14-high'] = rates_frame['high'].rolling(4).max()
        rates_frame['14-low'] = rates_frame['low'].rolling(4).min()
        rates_frame['%K'] = (rates_frame['close'] - rates_frame['14-low']) * 100 / (
                rates_frame['14-high'] - rates_frame['14-low'])
        rates_frame['%D'] = rates_frame['%K'].rolling(1).mean()
        col = rates_frame.loc[:, '%K':'%D']
        rates_frame['stock_tf' + str(self.TF)] = rates_frame.loc[:, '%K':'%D'].mean(axis=1)
        return rates_frame

    def computeEMA(self, rates_frame, period):
        rates_frame['ema_tf' + str(self.TF) + '_' + str(period)] = rates_frame['close'].ewm(span=period,
                                                                                            adjust=False).mean()
        return rates_frame

    def computeTenken(self, rates_frame):
        nine_period_high = rates_frame['high'].rolling(window=9).max()
        nine_period_low = rates_frame['low'].rolling(window=9).min()
        rates_frame['tenken_tf' + str(self.TF)] = (nine_period_high + nine_period_low) / 2
        return rates_frame

    def cal_data(self, currency, TF):
        rates_frame = self.getdata(currency, TF)
        self.computeRSI(rates_frame, 3)
        self.computeRSI(rates_frame, 14)
        self.compute_stock(rates_frame)
        self.computeTenken(rates_frame)
        period = 18
        self.computeEMA(rates_frame, period)
        period = 20
        self.computeEMA(rates_frame, period)
        period = 50
        self.computeEMA(rates_frame, period)
        return rates_frame

    def all_data(self):
        tfs = [mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4,
               mt5.TIMEFRAME_D1, mt5.TIMEFRAME_W1]
        df = self.cal_data(self.currency, self.TF)
        df = df.rename(
            columns={"close": "close_tf" + str(self.TF), "open": "open_tf" + str(self.TF),
                     "low": "low_tf" + str(self.TF), "high": "high_tf" + str(self.TF)})
        df = df.drop(
            ['tick_volume', 'spread', 'real_volume', '14-high', '14-low', '%K', '%D'], axis=1)
        tf_base = self.TF
        for tf in tfs:
            if tfs.index(tf) > tfs.index(self.TF):
                self.TF = tf
                df1 = self.cal_data(self.currency, self.TF)
                df1 = df1.drop(
                    ['tick_volume', 'spread', 'real_volume', '14-high', '14-low', '%K', '%D'], axis=1)
                df1 = df1.rename(
                    columns={"close": "close_tf" + str(self.TF), "open": "open_tf" + str(self.TF),
                             "low": "low_tf" + str(self.TF), "high": "high_tf" + str(self.TF)})
                df = pd.merge_ordered(df, df1, fill_method="ffill")
        self.TF = tf_base
        df = df.drop_duplicates(subset=['time'], keep='last')
        df = df.reset_index(drop=True)
        return df

    def getdf(self):
        df = self.all_data()
        return df

    def get_point(self):
        return self.point


class Conditions(Datafeed):
    tfs = [mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4, mt5.TIMEFRAME_D1,
           mt5.TIMEFRAME_W1]

    def __init__(self, currency, TF):
        Datafeed.__init__(self, currency, TF)

    def con_rsi(self):
        self.cons = pd.DataFrame(self.df['time'])
        self.cons['con_rsi3'] = self.df['rsi_tf' + str(self.TF) + '_3'] > 87
        self.cons['con_rsi14'] = self.df['rsi_tf' + str(self.TF) + '_14'] > 55.5
        ########################
        self.cons_D = pd.DataFrame(self.df['time'])
        self.cons_D['con_rsi3'] = self.df['rsi_tf' + str(self.TF) + '_3'] < 13
        self.cons_D['con_rsi14'] = self.df['rsi_tf' + str(self.TF) + '_14'] < 44.5
        return self.cons

    def con_tendence(self):
        self.ema_cons = pd.DataFrame()
        for tf in self.tfs:
            if self.tfs.index(tf) >= self.tfs.index(self.TF):
                self.ema_cons['con_ema20_' + str(tf)] = self.df['close_tf' + str(tf)] > self.df[
                    'ema_tf' + str(tf) + '_' + str(20)]
                self.ema_cons['con_ema50_' + str(tf)] = self.df['close_tf' + str(tf)] > self.df[
                    'ema_tf' + str(tf) + '_' + str(50)]
        if self.TF == mt5.TIMEFRAME_M1:
            self.cons['all_trend_tfs'] = ((self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_M1)] ) & (
                    self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_M5)] ) & (
                                                  self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_M15)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_M1)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_M5)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_M15)] ))
        elif self.TF == mt5.TIMEFRAME_M5:
            self.cons['all_trend_tfs'] = (((self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_M5)] ) & (
                    self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_M5)] )) & (
                                                  (self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_M15)] ) & (
                                                  self.ema_cons[
                                                      'con_ema50_' + str(mt5.TIMEFRAME_M15)] )) & (
                                                  (self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_H1)] ) & (
                                                  self.ema_cons[
                                                      'con_ema50_' + str(mt5.TIMEFRAME_H1)] )) & (((
                                                                                                                  self.ema_cons[
                                                                                                                      'con_ema20_' + str(
                                                                                                                          mt5.TIMEFRAME_H4)] ) & (
                                                                                                                  self.ema_cons[
                                                                                                                      'con_ema50_' + str(
                                                                                                                          mt5.TIMEFRAME_H4)] )) | (
                                                                                                                 (
                                                                                                                         self.ema_cons[
                                                                                                                             'con_ema20_' + str(
                                                                                                                                 mt5.TIMEFRAME_D1)] ) & (
                                                                                                                         self.ema_cons[
                                                                                                                             'con_ema50_' + str(
                                                                                                                                 mt5.TIMEFRAME_D1)] ))))
        elif self.TF == mt5.TIMEFRAME_M15:
            self.cons['all_trend_tfs'] = ((self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_M15)]) & (
                    self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_H1)]) & (
                                                  self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_H4)]) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_M15)]) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_H1)]) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_H4)] ))
        elif self.TF == mt5.TIMEFRAME_H1:
            self.cons['all_trend_tfs'] = ((self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_H1)] ) & (
                    self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_H4)] ) & (
                                                  self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_D1)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_H1)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_H4)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_D1)] ))
        elif self.TF == mt5.TIMEFRAME_H4:
            self.cons['all_trend_tfs'] = ((self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_H4)] ) & (
                    self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_D1)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_H4)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_D1)] ))
        elif self.TF == mt5.TIMEFRAME_D1:
            self.cons['all_trend_tfs'] = ((self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_D1)] ) & (
                    self.ema_cons['con_ema20_' + str(mt5.TIMEFRAME_W1)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_D1)] ) & (
                                                  self.ema_cons['con_ema50_' + str(mt5.TIMEFRAME_W1)] ))

        #########################
        self.ema_cons_D = pd.DataFrame()
        for tf in self.tfs:
            if self.tfs.index(tf) >= self.tfs.index(self.TF):
                self.ema_cons_D['con_ema20_' + str(tf)] = self.df['close_tf' + str(tf)] < self.df[
                    'ema_tf' + str(tf) + '_' + str(20)]
                self.ema_cons_D['con_ema50_' + str(tf)] = self.df['close_tf' + str(tf)] < self.df[
                    'ema_tf' + str(tf) + '_' + str(50)]

        if self.TF == mt5.TIMEFRAME_M1:
            self.cons_D['all_trend_tfs'] = ((self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_M1)] ) & (
                    self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_M5)] ) & (self.ema_cons_D[
                                                                                          'con_ema20_' + str(
                                                                                              mt5.TIMEFRAME_M15)] ) & (
                                                    self.ema_cons_D[
                                                        'con_ema50_' + str(mt5.TIMEFRAME_M1)] ) & (
                                                    self.ema_cons_D[
                                                        'con_ema50_' + str(mt5.TIMEFRAME_M5)] ) & (
                                                    self.ema_cons_D['con_ema50_' + str(mt5.TIMEFRAME_M15)] ))
        elif self.TF == mt5.TIMEFRAME_M5:
            self.cons_D['all_trend_tfs'] = (((self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_M5)] ) & (
                    self.ema_cons_D['con_ema50_' + str(mt5.TIMEFRAME_M5)] )) & ((self.ema_cons_D[
                                                                                            'con_ema20_' + str(
                                                                                                mt5.TIMEFRAME_M15)] ) & (
                                                                                               self.ema_cons_D[
                                                                                                   'con_ema50_' + str(
                                                                                                       mt5.TIMEFRAME_M15)] )) & (
                                                    (self.ema_cons_D[
                                                         'con_ema20_' + str(mt5.TIMEFRAME_H1)] ) & (
                                                            self.ema_cons_D['con_ema50_' + str(
                                                                mt5.TIMEFRAME_H1)] )) & (((
                                                                                                         self.ema_cons_D[
                                                                                                             'con_ema20_' + str(
                                                                                                                 mt5.TIMEFRAME_H4)] ) & (
                                                                                                         self.ema_cons_D[
                                                                                                             'con_ema50_' + str(
                                                                                                                 mt5.TIMEFRAME_H4)] )) | (
                                                                                                        (
                                                                                                                self.ema_cons_D[
                                                                                                                    'con_ema20_' + str(
                                                                                                                        mt5.TIMEFRAME_D1)] ) & (
                                                                                                                self.ema_cons_D[
                                                                                                                    'con_ema50_' + str(
                                                                                                                        mt5.TIMEFRAME_D1)] ))))
        elif self.TF == mt5.TIMEFRAME_M15:
            self.cons_D['all_trend_tfs'] = ((self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_M15)] ) & (
                    self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_H1)] ) & (self.ema_cons_D[
                                                                                          'con_ema20_' + str(
                                                                                              mt5.TIMEFRAME_H4)] ) & (
                                                    self.ema_cons_D[
                                                        'con_ema50_' + str(mt5.TIMEFRAME_M15)] ) & (
                                                    self.ema_cons_D[
                                                        'con_ema50_' + str(mt5.TIMEFRAME_H1)] ) & (
                                                    self.ema_cons_D['con_ema50_' + str(mt5.TIMEFRAME_H4)] ))
        elif self.TF == mt5.TIMEFRAME_H1:
            self.cons_D['all_trend_tfs'] = ((self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_H1)] ) & (
                    self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_H4)] ) & (self.ema_cons_D[
                                                                                          'con_ema20_' + str(
                                                                                              mt5.TIMEFRAME_D1)] ) & (
                                                    self.ema_cons_D[
                                                        'con_ema50_' + str(mt5.TIMEFRAME_H1)] ) & (
                                                    self.ema_cons_D[
                                                        'con_ema50_' + str(mt5.TIMEFRAME_H4)] ) & (
                                                    self.ema_cons_D['con_ema50_' + str(mt5.TIMEFRAME_D1)] ))
        elif self.TF == mt5.TIMEFRAME_H4:
            self.cons_D['all_trend_tfs'] = ((self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_H4)] ) & (
                    self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_D1)] ) & (self.ema_cons_D[
                                                                                          'con_ema50_' + str(
                                                                                              mt5.TIMEFRAME_H4)] ) & (
                                                    self.ema_cons_D['con_ema50_' + str(mt5.TIMEFRAME_D1)] ))
        elif self.TF == mt5.TIMEFRAME_D1:
            self.cons_D['all_trend_tfs'] = ((self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_D1)] ) & (
                    self.ema_cons_D['con_ema20_' + str(mt5.TIMEFRAME_W1)] ) & (self.ema_cons_D[
                                                                                          'con_ema50_' + str(
                                                                                              mt5.TIMEFRAME_D1)] ) & (
                                                    self.ema_cons_D['con_ema50_' + str(mt5.TIMEFRAME_W1)] ))

        return self.cons

    def con_stock(self):
        self.cons['con_stock'] = self.df['stock_tf' + str(self.TF)] < 25
        self.cons['con_stock_up'] = self.df['stock_tf' + str(self.tfs[self.tfs.index(self.TF) + 1])] < 25
        ###############################
        self.cons_D['con_stock'] = self.df['stock_tf' + str(self.TF)] > 75
        self.cons_D['con_stock_up'] = self.df['stock_tf' + str(self.tfs[self.tfs.index(self.TF) + 1])] > 75
        return self.cons

    def con_acc(self):
        self.cons['acc'] = ((self.cons['con_rsi3'] ) & (self.cons['all_trend_tfs'] ))
        #######################
        self.cons_D['acc'] = ((self.cons_D['con_rsi3'] ) & (self.cons_D['all_trend_tfs'] ))

    def trt(self):
        if self.cons['acc'].any():
            self.starting_index = self.cons['acc'][::-1].idxmax()
        else:
            self.starting_index = None
        #########################
        if self.cons_D['acc'].any():
            self.starting_index_D = self.cons_D['acc'][::-1].idxmax()
        else:
            self.starting_index_D = None

    def con_rsi14_up(self):
        self.cons['con_rsi14_up'] = (self.df['rsi_tf' + str(self.tfs[self.tfs.index(self.TF) + 1]) + '_14'] > 25) & (
                self.df['rsi_tf' + str(self.tfs[self.tfs.index(self.TF) + 1]) + '_14'] < 75)
        #########################
        self.cons_D['con_rsi14_up'] = (self.df['rsi_tf' + str(self.tfs[self.tfs.index(self.TF) + 1]) + '_14'] < 75) & (
                self.df['rsi_tf' + str(self.tfs[self.tfs.index(self.TF) + 1]) + '_14'] > 25)

    def v_ou_j(self):
        self.cons['v'] = ((self.df['stock_tf' + str(self.TF)] > 75) & (self.cons['con_rsi14_up'] ))
        self.cons['j'] = ((self.df['stock_tf' + str(self.TF)] > 75) & (self.cons['con_rsi14_up'] == False))
        #########################
        self.cons_D['r'] = ((self.df['stock_tf' + str(self.TF)] < 25) & (self.cons_D['con_rsi14_up'] ))
        self.cons_D['j'] = ((self.df['stock_tf' + str(self.TF)] < 25) & (self.cons_D['con_rsi14_up'] == False))

    def O_ou_Oj(self):
        self.cons['O'] = ((self.cons['con_stock'] ) & (self.cons['con_rsi14'] ) & (
                self.cons['con_rsi14_up'] ))
        self.cons['Oj'] = ((self.cons['con_stock'] ) & (self.cons['con_rsi14'] ) & (
                self.cons['con_rsi14_up'] == False))
        #########################
        self.cons_D['Or'] = ((self.cons_D['con_stock'] ) & (self.cons_D['con_rsi14'] ) & (
                self.cons_D['con_rsi14_up'] ))
        self.cons_D['Ojr'] = ((self.cons_D['con_stock'] ) & (self.cons_D['con_rsi14'] ) & (
                self.cons_D['con_rsi14_up'] == False))

    def ini(self):
        self.cons['init'] = False
        myseries = self.cons[self.starting_index::]
        if self.starting_index is not None and myseries['O'].any():
            self.signal_index = myseries.index[myseries['O'] ].tolist()[0]
            self.cons['init'] = self.df['stock_tf' + str(self.TF)] - self.df['stock_tf' + str(self.TF)][
                self.signal_index - 1] > 20

        self.cons_D['init'] = False
        myseries = self.cons_D[self.starting_index_D::]
        if self.starting_index_D is not None and myseries['Or'].any():
            self.signal_index_D = myseries.index[myseries['Or'] ].tolist()[0]
            self.signal_index_D = myseries.index[myseries['Or'] ].tolist()[0]
            self.cons_D['init'] = self.df['stock_tf' + str(self.TF)][self.signal_index_D - 1] - self.df[
                'stock_tf' + str(self.TF)] > 20

    def all_cycle(self):
        self.cons['cycle'] = 'chay'
        if self.starting_index is not None:
            self.cons['cycle'].iloc[self.starting_index] = 'v'
            for i in range(self.starting_index, len(self.cons)):
                if self.cons['cycle'].iloc[i - 1] == 'v' and self.df['stock_tf' + str(self.TF)].iloc[i] > 25:
                    self.cons['cycle'].iloc[i] = 'v'
                elif self.cons['j'].iloc[i]:
                    self.cons['cycle'].iloc[i] = 'j'
                elif self.cons['cycle'].iloc[i - 1] == 'j' and self.df['stock_tf' + str(self.TF)].iloc[i] > 25:
                    self.cons['cycle'].iloc[i] = 'j'
                elif self.cons['O'].iloc[i]  and self.cons['cycle'].iloc[i - 1] == 'v':
                    self.cons['cycle'].iloc[i] = 'O'
                elif self.cons['cycle'].iloc[i - 1] == 'O' and self.df['stock_tf' + str(self.TF)].iloc[i] < 75 and \
                        self.df['close_tf' + str(self.TF)].iloc[i] > \
                        self.df['ema_tf' + str(self.TF) + '_' + str(50)].iloc[i] and self.cons['init'].iloc[i] == False:
                    self.cons['cycle'].iloc[i] = 'O'
                elif self.cons['Oj'].iloc[i]:
                    self.cons['cycle'].iloc[i] = 'Oj'
        #############################################
        self.cons_D['cycle'] = 'chay'
        if self.starting_index_D is not None:
            self.cons_D['cycle'].iloc[self.starting_index_D] = 'r'
            for i in range(self.starting_index_D, len(self.cons_D)):
                if self.cons_D['cycle'].iloc[i - 1] == 'r' and self.df['stock_tf' + str(self.TF)].iloc[i] < 75:
                    self.cons_D['cycle'].iloc[i] = 'r'
                elif self.cons_D['j'].iloc[i] :
                    self.cons_D['cycle'].iloc[i] = 'j'
                elif self.cons_D['cycle'].iloc[i - 1] == 'j' and self.df['stock_tf' + str(self.TF)].iloc[i] < 75:
                    self.cons_D['cycle'].iloc[i] = 'j'
                elif self.cons_D['Or'].iloc[i]  and self.cons_D['cycle'].iloc[i - 1] == 'r':
                    self.cons_D['cycle'].iloc[i] = 'Or'
                elif self.cons_D['cycle'].iloc[i - 1] == 'Or' and (self.df['stock_tf' + str(self.TF)].iloc[i] > 25) and \
                        self.df['close_tf' + str(self.TF)].iloc[i] < \
                        self.df['ema_tf' + str(self.TF) + '_' + str(50)].iloc[i] and self.cons_D['init'].iloc[
                    i] == False:
                    self.cons_D['cycle'].iloc[i] = 'Or'
                elif self.cons_D['Ojr'].iloc[i] :
                    self.cons_D['cycle'].iloc[i] = 'Ojr'

    def signal_U(self):
        self.final_U = 'chay'
        if self.starting_index is not None:
            if 'chay' not in list(self.cons['cycle'][self.starting_index::]):
                self.final_U = self.cons['cycle'].iloc[-1]
        return self.final_U

    def signal_D(self):
        self.final_D = 'chay'
        if self.starting_index_D is not None:
            if 'chay' not in list(self.cons_D['cycle'][self.starting_index_D::]):
                self.final_D = self.cons_D['cycle'].iloc[-1]
        return self.final_D

    def signal(self):
        if self.final_U != 'chay':
            self.final = self.final_U
        elif self.final_D != 'chay':
            self.final = self.final_D
        else:
            self.final = 'chay'
        return self.final

    def Traitement(self):
        self.df = self.getdf()
        self.con_rsi()
        self.con_tendence()
        self.con_stock()
        self.con_acc()
        self.trt()
        self.con_rsi14_up()
        self.v_ou_j()
        self.O_ou_Oj()
        self.ini()
        self.all_cycle()
        self.signal_U()
        self.signal_D()
        self.signal()
        return self.signal()

    def get_inf(self):
        return 'Accceleration à ' + str(self.cons.time.iloc[self.starting_index])


class Manage(Conditions):

    def __init__(self):
        self.currencys = ['EURUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'GOLD', 'WTI', '#USSPX500', '#USNDAQ100', '#US30',
                          '#Euro50', 'EURGBP']
        self.TFs = [mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5,
                    mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1,
                    mt5.TIMEFRAME_H4, mt5.TIMEFRAME_D1]

    def addition(self, curr):
        all_results = []
        for TFi in self.TFs:
            test1 = Conditions(curr, TFi)
            signal = test1.Traitement()
            all_results.append(signal)
        return all_results

    def toshow(self):
        result = np.array(list(map(self.addition, self.currencys)))
        data = {'I': self.currencys, 'M1': result[:, 0], 'M5': result[:, 1], 'M15': result[:, 2], 'H1': result[:, 3],
                'H4': result[:, 4], 'D1': result[:, 5]}
        df_final = pd.DataFrame(data)
        return df_final

    @staticmethod
    def update_map_M1(curr):
        TFi = mt5.TIMEFRAME_M1
        test1 = Conditions(curr, TFi)
        signal = test1.Traitement()
        return signal

    @staticmethod
    def update_map_M5(curr):
        TFi = mt5.TIMEFRAME_M5
        test1 = Conditions(curr, TFi)
        signal = test1.Traitement()
        return signal

    @staticmethod
    def update_map_M15(curr):
        TFi = mt5.TIMEFRAME_M15
        test1 = Conditions(curr, TFi)
        signal = test1.Traitement()
        return signal

    @staticmethod
    def update_map_H1(curr):
        TFi = mt5.TIMEFRAME_H1
        test1 = Conditions(curr, TFi)
        signal = test1.Traitement()
        return signal

    @staticmethod
    def update_map_H4(curr):
        TFi = mt5.TIMEFRAME_H4
        test1 = Conditions(curr, TFi)
        signal = test1.Traitement()
        return signal

    @staticmethod
    def update_map_D1(curr):
        TFi = mt5.TIMEFRAME_D1
        test1 = Conditions(curr, TFi)
        signal = test1.Traitement()
        return signal

    def update(self, df_final):
        dt = datetime.now()
        updated = []
        if dt.second == 1:
            df_final['M1'] = list(map(self.update_map_M1, self.currencys))
            updated.append('M1 Updated')
            if dt.minute in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
                df_final['M5'] = list(map(self.update_map_M5, self.currencys))
                updated.append('M5 Updated')
                if dt.minute in [0, 15, 30, 45, ]:
                    df_final['M15'] = list(map(self.update_map_M15, self.currencys))
                    updated.append('M15 Updated')
                    if dt.minute == 0:
                        df_final['H1'] = list(map(self.update_map_H1, self.currencys))
                        updated.append('H1 Updated')
                        if dt.hour in [0, 4, 8, 12, 16, 20]:
                            df_final['H4'] = list(map(self.update_map_H4, self.currencys))
                            updated.append('H4 Updated')
            print(updated)
            print(df_final)
        return df_final


class Zone(Datafeed):

    def __init__(self, currency, TF):
        Datafeed.__init__(self, currency, TF)

    def calzone(self):
        df = self.getdf()

        if df['close_tf' + str(self.TF)].iloc[- 1] > df['ema_tf' + str(self.TF) + str(20)].iloc[- 1] and \
                df['close_tf' + str(self.TF)].iloc[- 1] > df['ema_tf' + str(self.TF) + str(50)].iloc[- 1] and \
                df['close_tf' + str(self.tfs[self.tfs.index(self.TF)])].iloc[- 1] > \
                df['ema_tf' + str(self.tfs[self.tfs.index(self.TF)]) + str(20)].iloc[- 1] and \
                df['close_tf' + str(self.tfs[self.tfs.index(self.TF)])].iloc[- 1] > \
                df['ema_tf' + str(self.tfs[self.tfs.index(self.TF)]) + str(50)].iloc[- 1]:
            self.DT = 'v'
        elif df['close_tf' + str(self.TF)].iloc[- 1] < df['ema_tf' + str(self.TF) + str(20)].iloc[- 1] and \
                df['close_tf' + str(self.TF)].iloc[- 1] < \
                df['ema_tf' + str(self.TF) + str(50)].iloc[- 1] and \
                df['close_tf' + str(self.tfs[self.tfs.index(self.TF)])].iloc[- 1] < \
                df['ema_tf' + str(self.tfs[self.tfs.index(self.TF)]) + str(20)].iloc[- 1] and \
                df['close_tf' + str(self.tfs[self.tfs.index(self.TF)])].iloc[- 1] < \
                df['ema_tf' + str(self.tfs[self.tfs.index(self.TF)]) + str(50)].iloc[- 1]:
            self.DT = 'r'
        else:
            self.DT = 'chay'

        self.last_close = df['close_tf' + str(self.TF)].iloc[-1]
        self.sma5 = (df['close_tf' + str(self.TF)].iloc[- 2] + df['close_tf' + str(self.TF)].iloc[- 3] +
                     df['close_tf' + str(self.TF)].iloc[- 4] +
                     df['close_tf' + str(self.TF)].iloc[- 5] + df['close_tf' + str(self.TF)].iloc[- 6]) / 5
        self.sma3 = (df['close_tf' + str(self.TF)].iloc[- 2] + df['close_tf' + str(self.TF)].iloc[- 3] +
                     df['close_tf' + str(self.TF)].iloc[- 4]) / 3

        mt5.initialize(r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe")
        point = mt5.symbol_info(self.currency).point
        mt5.shutdown()
        dfc = df['close_tf' + str(self.TF)]
        ldf = len(df) - 1
        lows = [0] * (ldf + 1)
        highs = [0] * (ldf + 1)
        backstep = 5
        dev = 3
        last_low = 0
        last_high = 0
        for shift in range(2, ldf + 1):
            val = min(df['low_tf' + str(self.TF)][shift], df['low_tf' + str(self.TF)][shift - 1],
                      df['low_tf' + str(self.TF)][shift - 2])
            if val == last_low:
                val = 0
            else:
                last_low = val
                if df['low_tf' + str(self.TF)][shift] - val > dev * point:
                    val = 0
                else:
                    for back in range(1, backstep):
                        res = lows[shift - back]
                        if res != 0 and res > val:
                            lows[shift - back] = 0
            if df['low_tf' + str(self.TF)][shift] == val:
                lows[shift] = val
            else:
                lows[shift] = 0
            val = max(df['high_tf' + str(self.TF)][shift], df['high_tf' + str(self.TF)][shift - 1],
                      df['high_tf' + str(self.TF)][shift - 2])
            if val == last_high:
                val = 0
            else:
                last_high = val
                if val - df['high_tf' + str(self.TF)][shift] > dev * point:
                    val = 0
                else:
                    for back in range(1, backstep):
                        res = highs[shift - back]
                        if res != 0 and res < val:
                            highs[shift - back] = 0
            if df['high_tf' + str(self.TF)][shift] == val:
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
        while kn > 1:
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
        zonesh = []
        for i in levelsh:
            k = i[0]
            tkasser = False
            while k < len(df) - 1:
                if i[1] < df['close_tf' + str(self.TF)][k]:
                    tkasser = True
                k += 1
            if i[0] == 0 or (len(df) - i[0]) == 1:
                a = [df['close_tf' + str(self.TF)][i[0] - 2], df['open_tf' + str(self.TF)][i[0] - 2],
                     df['close_tf' + str(self.TF)][i[0] - 1], df['open_tf' + str(self.TF)][i[0] - 1],
                     df['close_tf' + str(self.TF)][i[0]], df['open_tf' + str(self.TF)][i[0]]]
            elif i[0] == 1 or (len(df) - i[0]) == 2:
                a = [df['close_tf' + str(self.TF)][i[0] - 2], df['open_tf' + str(self.TF)][i[0] - 2],
                     df['close_tf' + str(self.TF)][i[0] - 1], df['open_tf' + str(self.TF)][i[0] - 1],
                     df['close_tf' + str(self.TF)][i[0]], df['open_tf' + str(self.TF)][i[0]],
                     df['close_tf' + str(self.TF)][i[0] + 1], df['open_tf' + str(self.TF)][i[0] + 1]]
            elif i[0] >= 2:
                a = [df['close_tf' + str(self.TF)][i[0] - 2], df['open_tf' + str(self.TF)][i[0] - 2],
                     df['close_tf' + str(self.TF)][i[0] - 1], df['open_tf' + str(self.TF)][i[0] - 1],
                     df['close_tf' + str(self.TF)][i[0]], df['open_tf' + str(self.TF)][i[0]],
                     df['close_tf' + str(self.TF)][i[0] + 1], df['open_tf' + str(self.TF)][i[0] + 1],
                     df['close_tf' + str(self.TF)][i[0] + 2], df['open_tf' + str(self.TF)][i[0] + 2]]
            # , max(df['close'][i[0] + 1], df['open'][i[0] + 1]),max(df['close'][i[0] + 2], df['open'][i[0] + 2]), max(df['close'][i[0] + 3], df['open'][i[0] + 3])
            a.sort()
            if not tkasser:
                zonesh.append([a[-2], i[1], df['time'][i[0] - 2], df['time'][len(df) - 1]])
        zonesl = []
        for i in levelsl:
            k = i[0]
            tkasser1 = False
            while k < len(df) - 2:
                if i[1] > df['close_tf' + str(self.TF)][k]:
                    tkasser1 = True
                k += 1
            if i[0] == 0 or (len(df) - i[0]) == 1:
                a = [df['close_tf' + str(self.TF)][i[0] - 2], df['open_tf' + str(self.TF)][i[0] - 2],
                     df['close_tf' + str(self.TF)][i[0] - 1], df['open_tf' + str(self.TF)][i[0] - 1],
                     df['close_tf' + str(self.TF)][i[0]], df['open_tf' + str(self.TF)][i[0]]]
            elif i[0] == 1 or (len(df) - i[0]) == 2:
                a = [df['close_tf' + str(self.TF)][i[0] - 2], df['open_tf' + str(self.TF)][i[0] - 2],
                     df['close_tf' + str(self.TF)][i[0] - 1], df['open_tf' + str(self.TF)][i[0] - 1],
                     df['close_tf' + str(self.TF)][i[0]], df['open_tf' + str(self.TF)][i[0]],
                     df['close_tf' + str(self.TF)][i[0] + 1], df['open_tf' + str(self.TF)][i[0] + 1]]
            elif i[0] >= 2:
                a = [df['close_tf' + str(self.TF)][i[0] - 2], df['open_tf' + str(self.TF)][i[0] - 2],
                     df['close_tf' + str(self.TF)][i[0] - 1], df['open_tf' + str(self.TF)][i[0] - 1],
                     df['close_tf' + str(self.TF)][i[0]], df['open_tf' + str(self.TF)][i[0]],
                     df['close_tf' + str(self.TF)][i[0] + 1], df['open_tf' + str(self.TF)][i[0] + 1],
                     df['close_tf' + str(self.TF)][i[0] + 2], df['open_tf' + str(self.TF)][i[0] + 2]]
            # , min(df['close'][i[0] + 1], df['open'][i[0] + 1]),min(df['close'][i[0] + 2], df['open'][i[0] + 2]), min(df['close'][i[0] + 3], df['open'][i[0] + 3])
            a.sort()
            if not tkasser1:
                zonesl.append([i[1], a[1], df['time'][i[0] - 2], df['time'][len(df) - 1]])
        z = zonesl + zonesh
        self.df = df
        return z

    def free(self, zones, real_DT, real_Ex, real_Ex1, real_last_close_M15, pivots):
        louta = []
        fou9 = []
        inside_zone = False
        for i in zones:
            louta.append(i[1])
            fou9.append(i[0])
            if i[0] < self.last_close < i[1]:
                inside_zone = True
        last_touche = 'n'
        if not inside_zone:
            f = [i for i in fou9 if i >= self.last_close]
            l = [i for i in louta if i <= self.last_close]
            fp = [i for i in pivots if i >= self.last_close]
            lp = [i for i in pivots if i <= self.last_close]
            f += fp
            l += lp
            f.sort()
            l.sort()
            if len(f) > 0:
                f1 = f[0]
                i = len(self.df) - 1
                while i > 1 and self.df['high_tf' + str(self.TF)][i] < f1:
                    i -= 1
                if1 = i
            else:
                if1 = 9999999
            i = len(self.df) - 1
            if len(l) > 0:
                l1 = l[-1]
                while i > 1 and self.df['low_tf' + str(self.TF)][i] > l1:
                    i -= 1
                il1 = i
            else:
                il1 = 9999999
            if if1 < il1 and real_DT == 'v' and self.df['rsi_tf' + str(self.TF) + str(14)].iloc[
                -1] < 75 and real_last_close_M15 > real_Ex1[3] and real_Ex1[1] < \
                    real_Ex1[2] and real_Ex1[2] < real_Ex1[3] and real_Ex1[3] < real_Ex1[
                4]:  # and real_last_close_M15 > real_Ex1[1] and real_Ex1[1] > real_Ex1[2] and real_Ex1[2] >
                # real_Ex1[3] and real_Ex1[3] > real_Ex1[4]
                last_touche = 'l'
            elif if1 < il1 and real_DT == 'v' and self.df['rsi_tf' + str(self.TF) + str(14)].iloc[
                -1] > 75 and real_last_close_M15 > real_Ex1[3] and real_Ex1[
                1] < \
                    real_Ex1[2] and real_Ex1[2] < real_Ex1[3] and real_Ex1[3] < real_Ex1[4]:
                last_touche = 'E'
            elif if1 > il1 and real_DT == 'r' and self.df['rsi_tf' + str(self.TF) + str(14)].iloc[
                -1] > 25 and real_last_close_M15 < real_Ex1[3] and real_Ex1[
                1] > \
                    real_Ex1[2] and real_Ex1[2] > real_Ex1[3] and real_Ex1[3] > real_Ex1[4]:  #
                last_touche = 'f'
            elif if1 > il1 and real_DT == 'r' and self.df['rsi_tf' + str(self.TF) + str(14)].iloc[
                -1] < 25 and real_last_close_M15 < real_Ex1[3] and real_Ex1[
                1] > \
                    real_Ex1[2] and real_Ex1[2] > real_Ex1[3] and real_Ex1[3] > real_Ex1[4]:
                last_touche = 'Er'
        return last_touche

'''
from man import db
from datetime import datetime
from man import Item
'''
currencys = ['EURUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'GOLD', 'WTI', '#USSPX500', '#USNDAQ100', '#US30',
             '#Euro50',
             'EURGBP']

t = Manage()
d = t.toshow()
'''
db.drop_all()
db.create_all()
for i in range(len(d)):
    item = Item(name=currencys[i], M1=d['M1'][i], M5=d['M5'][i], M15=d['M15'][i],
                H1=d['H1'][i], H4=d['H4'][i], D1=d['D1'][i])
    db.session.add(item)
    db.session.commit()
'''
print(d)
while True:
    t.update(d)