import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def _get_bolliger(ls_symbol, ldt_timestamps):

	''' get bollinger band of stock price walk '''

	dateobj = da.DataAccess('Yahoo', cachestalltime = 0)
	ls_keys =['open', 'high', 'low', 'close', 'volume', 'actual_close']

	ldf_data = dateobj.get_data(ldt_timestamps, ls_symbol, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	d_close = d_data['close']

	'''calculate rolling mean and standard deviation '''

	d_rollmean = pd.stats.moments.rolling_mean(d_close, 20, min_periods=20)
	d_rollstd = pd.stats.moments.rolling_std(d_close, 20, min_periods=20)
	up_band = d_rollmean + d_rollstd
	low_band = d_rollmean - d_rollstd

	plt.clf()
	fig = plt.figure()
	fig.add_subplot(111)
	plt.plot(ldt_timestamps, d_close)
	plt.plot(ldt_timestamps, d_rollmean)
	plt.legend([ls_symbol, 'Moving Avg.'])
	plt.ylabel('Adjusted Close')
	plt.xlabel('Date')
	fig.autofmt_xdate(rotation = 45)
	plt.savefig('close_and_rollingmean.pdf', format='pdf')

	Bollinger_val = (d_close - d_rollmean) / d_rollstd # Bollinger value of stock price
	print Bollinger_val['2010-06-23'] # key for quiz is here

	return Bollinger_val, up_band, low_band, d_close


def _Plot_Bollinger(Bollinger_val, d_close, ls_symbol, up_band, low_band, ldt_timestamps):

	''' plot bollinger band '''

	plt.clf()
	fig2 = plt.figure()
	fig2.add_subplot(2, 1, 1)
	plt.plot(ldt_timestamps, d_close)
	#plt.fill_between(ldt_timestamps, low_band, up_band, facecolor='grey', alpha=0.5)
	plt.plot(ldt_timestamps, up_band)
	plt.plot(ldt_timestamps, low_band)
	plt.legend([ls_symbol])
	plt.ylabel('Adjusted Close')
	fig2.autofmt_xdate(rotation = 45)

	Norm_lowb = -1 + np.zeros((len(up_band), 1))
	Norm_upb = 1 + np.zeros((len(low_band), 1))

	fig2.add_subplot(2, 1, 2)
	plt.plot(ldt_timestamps, Bollinger_val)
	#plt.fill_between(ldt_timestamps, Norm_lowb, Norm_upb, facecolor='grey', alpha=0.5)
	plt.plot(ldt_timestamps, Norm_upb)
	plt.plot(ldt_timestamps, Norm_lowb)
	plt.ylabel('Adjusted Close')
	fig2.autofmt_xdate(rotation = 45)
	plt.savefig('Bollingerex.pdf', format = 'pdf')




def main():

	ls_symbol = ["MSFT"]
	dt_start = dt.datetime(2010, 1, 1)
	dt_end = dt.datetime(2010, 12, 31)
	dt_timeofday = dt.timedelta(hours = 16)
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

	boll_val, upband, lowband, act_close = _get_bolliger(ls_symbol, ldt_timestamps)
	_Plot_Bollinger(boll_val, act_close, ls_symbol, upband, lowband, ldt_timestamps)
	

if __name__ == '__main__':
	main()
