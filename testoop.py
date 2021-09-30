

t = Conditions('WTI', mt5.TIMEFRAME_H1)

t.Traitement()

t.cons


list(t.cons['cycle'][t.starting_index::])


t.cons[t.starting_index::]




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