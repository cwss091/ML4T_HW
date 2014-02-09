import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib as plt
import pandas as pd
import numpy as np
import csv

def _csv_read_sym_dates(filename):

	''' import csv files which record strategy order '''

	reader = csv.reader(open(filename, 'rU'), delimiter = ',')
	dates = []
	symbols = []
	# input the dates and symbols of strategy seperately
	for row in reader:
		if not (row[3] in symbols):
			symbols.append(row[3])
		date = dt.datetime(int(row[0]), int(row[1]), int(row[2]))
		if not (date in dates):
			dates.append(date)
	dates = sorted(dates) # sort date from past
	#print symbols
	return symbols, dates



def _get_data(symbols, dates):
	
	''' read actual close price of symbols from Yahoo! Finance'''
	
	dt_timeofday = dt.timedelta(hours = 16)
	ldt_timestamps = du.getNYSEdays(dates[0], dt.timedelta(days=1) + dates[-1], dt_timeofday) # dates[-1] is the last element of array

	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	
	dataobj = da.DataAccess('Yahoo', cachestalltime=0)

	ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))
	
	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
		d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
		d_data[s_key].fillna(1.0)
	
	df_close = d_data['close']
	

	return df_close, ldt_timestamps



def _trade_mat_generate(filename, ldt_timestamps, symbols, close):

	''' generate the trade matrix of selected symbols in selected time period '''

	reader = csv.reader(open(filename, 'rU'), delimiter = ',')

	time_last = len(ldt_timestamps)
	sym_num = len(symbols)
	
	df = np.zeros((time_last, sym_num)) # set up the matrix of trading 
	df = pd.DataFrame(df, index=ldt_timestamps, columns=symbols)
	#print df
	
	for row in reader:
		date = dt.datetime(int(row[0]), int(row[1]), int(row[2]))
		#print date
		# revise the date. Because date from the csv is 00:00:00, but the close price is 16:00:00, so it needs revised.
		revise_date = close.index[close.index >= date][0]
		#print close.index[close.index >= date][0]
		if row[4] == "BUY":
			df.ix[revise_date][row[3]] += float(row[5])
		if row[4] == "SELL":
			df.ix[revise_date][row[3]] -= float(row[5])

	#print df.ix[

	return df



def _cash_value(trading_mat, ini_cv, close):
	
	''' generate the cash value of each strategy day '''
	
	date = trading_mat.index
	#print date
	symbol = trading_mat.columns
	#print symbol
	cv = np.zeros((len(date), 1))
	cv = pd.DataFrame(cv, index=date, columns=['CASH']) # 'CASH' should be in the bracket
	#print cv
	#r1 = trading_mat.ix[date[0]].values
	#print date[0]
	#r2 = close.ix[close.index[0]].values
	
	#print cv.ix[date[0]]
	#print len(date)
	'''dot means product of matrix, and we should use value to calculate '''

	print ini_cv
	for i in range(0, len(date)):
		if i == 0:
			#print trading_mat.ix[date[i]].values
			#print close.ix[date[i]].values
			#print np.dot(trading_mat.ix[date[i]].values, close.ix[date[i]].values)
			cv.ix[date[i]] += float(ini_cv - np.dot(trading_mat.ix[date[i]].values, close.ix[date[i]].values))
			#cv.ix[date[i]] = ini_cv
			#print cv.ix[date[i]]
		else:
			cv.ix[date[i]] += float(cv.ix[date[i-1]] - np.dot(trading_mat.ix[date[i]].values, close.ix[date[i]].values))
			#if i == 1:
			#	print cv.ix[date[i]]
	#print cv.ix[date[0]], cv.ix[date[1]], cv.ix[date[2]]
	return cv



def _portfolio_value(cashvalue, trading_mat, close):

	''' generate the hoding matrix and generate the timeprocess of portfolio value'''
	
	date = trading_mat.index
	symbol = trading_mat.columns
	len_date = len(date)
	len_sym = len(symbol)
	holding_mat = trading_mat
	for i in range(1, len_date):
		holding_mat.ix[date[i]][symbol] += holding_mat.ix[date[i-1]][symbol]
	holding_mat = holding_mat.join(cashvalue, how='outer')


	#cach unit generation
	cu = np.zeros((len_date, 1))
	cu = pd.DataFrame(cu, index=date, columns=['CASH'])
#	generate the price matrix
	price_mat = close.join(cu, how='outer')
	
	for i in range(0, len_date):
		price_mat.ix[date[i]]['CASH'] += 1.0 
	
#	generate the matrix of portfolio value
	portfolio_vmat = np.zeros((len_date,1))
	portfolio_vmat =pd.DataFrame(portfolio_vmat, index=date, columns=['PORTFOLIO_VALUE'])
	for i in range(0, len_date):
		portfolio_vmat.ix[date[i]] += np.dot(price_mat.ix[date[i]].values, holding_mat.ix[date[i]].values)
	
	return portfolio_vmat


def _parameters_invest(portfolio_vmat):

	''' calculate the the average return, standard deviation and sharpe ratio '''
	
	date = portfolio_vmat.index
	len_returnrate = len(date) - 1
	totalreturn = portfolio_vmat.ix[date[len_returnrate]] / portfolio_vmat.ix[date[0]]

	print "total return of fund is ", totalreturn
	dpv_rets = portfolio_vmat.values.copy()
	dpv_return = tsu.returnize0(dpv_rets)

	ave_return = np.average(dpv_return)
	sd_return = np.std(dpv_return)

	sharperatio = ave_return / sd_return * np.sqrt(252.0)

	print "average daily return is ", ave_return
	print "standard deviation is ", sd_return
	print "sharpe ratio is ", sharperatio



def _csv_write_timevalue(portfolio_vmat, filename):

	''' write the timeseries of portfolio's value to a csv file '''
	
	writer = csv.writer(open(filename, 'wb'), delimiter=',')
	for row in portfolio_vmat.index:
		#print row
		#print portfolio_vmat.ix[row]
		row_to_enter = [str(row.year), str(row.month), str(row.day), str(portfolio_vmat.ix[row].values)]
		writer.writerow(row_to_enter)


def main():
	symbols, dates = _csv_read_sym_dates("myorders.csv")
	#print dates
	close_price, timestamps = _get_data(symbols, dates)
	#print close_price.ix[0], close_price.ix[1], close_price.ix[2]
	trade_matrix = _trade_mat_generate("myorders.csv", timestamps, symbols, close_price)
	#print trade_matrix
	''' input the initial amount of cash '''
	Initial_cash = float(raw_input("Please input the initial cash: "))
	CValue = _cash_value(trade_matrix, Initial_cash, close_price)
	#print CValue
	portfolio_value = _portfolio_value(CValue, trade_matrix, close_price)
	#print portfolio_value
	_csv_write_timevalue(portfolio_value, "Value_timeseries.csv")
	_parameters_invest(portfolio_value)



if __name__ == '__main__':
	main()



