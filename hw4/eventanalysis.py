import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import datetime as dt
import matplotlib as plt
import pandas as pd
import numpy as np

import math
import copy
import csv

def find_events(symbol, data, eventprice):
	'''
	Based on defination of events find the event (date) and count the number of event, and output to a chart
	Key arguments
	symbol: the symbols of stocks
	data: the stock price or other data of stocks
	eventprice: when yesterday's price is aboce eventprice and today's price is below it, we consider that the event happens

	'''
	df_actualclose = data['actual_close']
	ts_market = df_actualclose['SPY']
	
	#initialize the events
	df_events = copy.deepcopy(df_actualclose)
	df_events = df_events * np.NAN

	ldt_timestamps = df_actualclose.index
	#initial the number of events
	eventnum = 0
	
	writer = csv.writer(open("myorders_10.csv", 'wb'), delimiter=',')
	#find the events
	for s_sym in symbol:
		for i in range(1, len(ldt_timestamps)):
			f_sympricetoday = df_actualclose[s_sym].ix[ldt_timestamps[i]]
			f_symprice_yest = df_actualclose[s_sym].ix[ldt_timestamps[i-1]]

			if f_sympricetoday < eventprice and f_symprice_yest >= eventprice:
				df_events[s_sym].ix[ldt_timestamps[i]] = 1
				row_to_enter = [str(ldt_timestamps[i].year), str(ldt_timestamps[i].month), str(ldt_timestamps[i].day), str(s_sym), "BUY", "100"]
				writer.writerow(row_to_enter)
				if (i+5) < len(ldt_timestamps):
					row_to_enter = [str(ldt_timestamps[i+5].year), str(ldt_timestamps[i+5].month), str(ldt_timestamps[i+5].day), str(s_sym), "SELL", "100"]
					writer.writerow(row_to_enter)

	
	return df_events #return the set of events, number of events



def main():
	dt_start = dt.datetime(2008, 1, 1)
	dt_end = dt.datetime(2009, 12, 31)
	dt_timeofday = dt.timedelta(hours = 16)
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

	dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	#ls_symbols1 = dataobj.get_symbols_from_list("sp5002008") # 2008 yr's S&P500
	ls_symbols2 = dataobj.get_symbols_from_list("sp5002012")
	#ls_symbols1.append('SPY')
	ls_symbols2.append('SPY')

	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	#ldf_data1 = dataobj.get_data(ldt_timestamps, ls_symbols1, ls_keys)
	#d_data1 = dict(zip(ls_keys, ldf_data1))

	# remove the NAN in matrix
	#for s_key in ls_keys:
	#	d_data1[s_key] = d_data1[s_key].fillna(method = 'ffill')
	#	d_data1[s_key] = d_data1[s_key].fillna(method = 'bfill')
	#	d_data1[s_key].fillna(1.0)

	#df_events1, num_e1 = find_events(ls_symbols1, d_data1)

	ldf_data2 = dataobj.get_data(ldt_timestamps, ls_symbols2, ls_keys)
	d_data2 = dict(zip(ls_keys, ldf_data2))

	for s_key in ls_keys:
		d_data2[s_key] = d_data2[s_key].fillna(method = 'ffill')
		d_data2[s_key] = d_data2[s_key].fillna(method = 'bfill')
		d_data2[s_key].fillna(1.0)

	df_events2 = find_events(ls_symbols2, d_data2, 10.0)

	#print num_e1
	#print num_e2
	# use the eventprofile to analyze the events and get a pdf
	#print "Creating Study"
	#ep.eventprofiler(df_events1, d_data1, i_lookback=20, i_lookforward=20, s_filename='MyEventStudy5.pdf', b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')

	print "Creating Study2"
	ep.eventprofiler(df_events2, d_data2, i_lookback=20, i_lookforward=20, s_filename='MyEventStudy3.pdf', b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')

if __name__ == '__main__':
	main()

