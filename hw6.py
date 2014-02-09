import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import math
import copy

def find_events(symbol, data):
	'''
	Based on defination of events find the event (date) and count the number of event
	Key arguments
	symbol: the symbols of stocks
	data: the stock price or other data of stocks

	'''
	df_close = data['close']

	d_rollmean = pd.stats.moments.rolling_mean(df_close, 20, min_periods=20)
	d_rollstd = pd.stats.moments.rolling_std(df_close, 20, min_periods=20)
	#up_band = d_rollmean + d_rollstd
	#low_band = d_rollmean - d_rollstd
	Bollinger_val = (df_close - d_rollmean) / d_rollstd # Bollinger value of stock price
	ts_market = Bollinger_val['SPY']
	
	#initialize the events
	df_events = copy.deepcopy(Bollinger_val)
	df_events = df_events * np.NAN

	ldt_timestamps = Bollinger_val.index

	#find the events
	for s_sym in symbol:
		if s_sym == 'SPY':
			break
		for i in range(1, len(ldt_timestamps)):
			f_bvaltoday = Bollinger_val[s_sym].ix[ldt_timestamps[i]]
			f_bval_yest = Bollinger_val[s_sym].ix[ldt_timestamps[i-1]]
			m_bval_today = ts_market.ix[ldt_timestamps[i]]
			if f_bvaltoday <= -2.0 and f_bval_yest >= -2.0 and m_bval_today >= 1.4:
				df_events[s_sym].ix[ldt_timestamps[i]] = 1
	
	return df_events #return the set of events, number of events

def main():
	dt_start = dt.datetime(2008, 1, 1)
	dt_end = dt.datetime(2009, 12, 31)
	dt_timeofday = dt.timedelta(hours = 16)
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

	dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	ls_symbols = dataobj.get_symbols_from_list("sp5002012")
	ls_symbols.append('SPY')

	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
		d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
		d_data[s_key].fillna(1.0)

	df_event = find_events(ls_symbols, d_data)

	print "Creating Study"
	ep.eventprofiler(df_event, d_data, i_lookback=20, i_lookforward=20, s_filename='MyEventStudy2.pdf', b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')

if __name__ == '__main__':
	main()