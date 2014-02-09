import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib as plt
import pandas as pd
import numpy as np

from decimal import *

def simulate(startdate, enddate, eq_symbols):

	'''Optimal the allocation of the portfolio to get the portfolio with the highest sharp ratio
	Keyword arguments:
	startdate -- the start date of stocks' historical price
	enddate -- the end date of stocks' historical price
	eq_symbols -- the symbols of stocks

	Returns: 
	best_sdreturn -- the sd of the optimal portfolio's daily return -- float
	best_avereturn -- the average of the optimal portfolio daily return -- float
	best_sharpratio -- the sharp ratio of the optimal portfolio -- float
	daily_cum_ret -- the cumulative return -- floaave
	best_alloc -- the optimal allocation -- float array

	'''

	dt_timeofday = dt.timedelta(hours = 16)
	ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)

	c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldt_data = c_dataobj.get_data(ldt_timestamps, eq_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldt_data))

	na_price = d_data['close'].values # get the adjust-close price
	na_normalized_price = na_price / na_price[0, :] # normalize the price

	best_alloc = [0, 0, 0, 0]
	best_sharpratio = -10000.0
	best_avereturn = 0.0
	best_sdreturn = 0.0
	best_dayreturn = np. zeros((252,1))
	ini_allocation = [0.0,0.0,0.0,0.0]

	for i in range(0,11):
		ini_allocation[1] = 0.0

		for j in range(0,11):
			ini_allocation[2] = 0.0

			for k in range(0,11):
				ini_allocation[3] = 0.0

				for ii in range(0,11):
					#sum2 = np.sum(ini_allocation)
					
					sum2 = Decimal(ini_allocation[0])+Decimal(ini_allocation[1])+Decimal(ini_allocation[2])+Decimal(ini_allocation[3]) # float calculation
					sum2 = round(sum2,1) # reduce the precision to 1 deci
					if sum2 == 1.0:

						allocation_trans = np.transpose(ini_allocation)
						day_por_value = np.dot(na_normalized_price, allocation_trans) # dot multiply to get the portfolio's daily value

						dpv_rets = day_por_value.copy()
						dpv_return = tsu.returnize0(dpv_rets) # get the daily return of portfolio
	
						ave_return = np.average(dpv_return) # average of daily return
						sd_return = np.std(dpv_return) # average of daily sd
	
						sharpr_current = ave_return / sd_return # sharp ratio

						if sharpr_current > best_sharpratio: # comparision and optimize
							best_sharpratio = sharpr_current
							best_avereturn = ave_return
							best_sdreturn = sd_return
							best_dayreturn = np.copy(dpv_return)
							best_alloc = np.copy(ini_allocation)

					ini_allocation[3] = ini_allocation[3] + 0.1
				ini_allocation[2] = ini_allocation[2] + 0.1
			ini_allocation[1] = ini_allocation[1] + 0.1
		ini_allocation[0] = ini_allocation[0] + 0.1
							

	# calculate the cumulative return
	counter = 1
	daily_cum_ret = 1.0
	while counter < np.size(best_dayreturn):
		daily_cum_ret = daily_cum_ret * (1 + best_dayreturn[counter])
		counter = counter + 1
	
	best_sharpratio = best_sharpratio * np.sqrt(252) # annual sharp ratio
	
	return best_sdreturn, best_avereturn, best_sharpratio, daily_cum_ret, best_alloc
	

def main():
	#ls_symbols = ["BRCM", "ADBE", "AMD", "ADI"]
	ls_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
	#ls_symbols = ["AXP", "HPQ", "IBM", "HNZ"]

	dt_start = dt.datetime(2011, 1, 1)
	dt_end = dt.datetime(2011, 12, 31)
	vol, daily_set, sharp, cum_ret, opt_alc = simulate(dt_start, dt_end, ls_symbols)
	print opt_alc
	print sharp
	print vol
	print daily_set
	print cum_ret


if __name__ == '__main__':
	main()

