

t = Conditions('GBPUSD', mt5.TIMEFRAME_M2)

t.Traitement()

t.cons

t.cons[t.starting_index::]


t.cons_D

t.cons_D[t.starting_index_D::]



t = Datafeed('EURUSD', mt5.TIMEFRAME_H4)

df = t.all_data()

df['stock_tf' + str(t.TF)]

t.Traitement()

t = Eng('EURUSD', mt5.TIMEFRAME_M2)


t.eng_con_2()
t.cons_eng_D
t.starting_index_eng_D


list(t.cons_D['cycle'][t.starting_index_D::])


t.cons_eng_D[t.starting_index_eng_D -1 ::]




myseries = t.cons[t.starting_index::]

myseries.index[myseries['O'] == True].tolist()[0]


t.cons[['time' , 'cycle']][t.starting_index::]

t.cons[['time' , 'con_rsi3' ]].iloc[-15::]

t.df[['time' ,'rsi_tf15_3']].iloc[t.starting_index::]

t.df[['time' ,'stock_tf15']].iloc[t.starting_index::]

i = 425

t.cons_D['cycle'].iloc[i - 1] == 'j' and t.df['stock_tf' + str(t.TF)].iloc[i] < 75

t1 = Zone('GBPUSD', mt5.TIMEFRAME_M1)

t1.