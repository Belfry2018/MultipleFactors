from flask import Flask
from flask_apscheduler import APScheduler
from datetime import datetime
import tushare as ts
import json
import pandas as pd
import DBHandler as db
import numpy as np
from DBHandler import Strategy

'''
scheduer每隔一小时更新一次股票数据
'''
class Config(object):
	JOBS=[
		{
			'id':'job1',
			'func':'App:job1',
			'args':(1,2),
			'trigger':'interval',
			'seconds':3600
			#每小时自动获取一次股票数据
		}
	]
	SCHEDULER_API_ENABLED=True

def job1(a,b):
	print('fetching stock data')
	getStocksData()


app=Flask("MultipleFactors")
app.config.from_object(Config())
scheduler=APScheduler()
scheduler.init_app(app)
scheduler.start()

# 没有使用numpy的后果
def list_add(a,b):
	c = []
	for i in range(len(a)):
		c.append(a[i]+b[i])
	return c


#返回包括此月份的前12个月
def getOneYearMonthList(a):
	yearNow = int(a.split('-')[0])
	monthNow = int(a.split('-')[1])
	retList = []
	if monthNow == 12:
		for i in range(12):
			retList.append(str(yearNow) + '-' + str(i+1))
	else:
		monthBegin = monthNow+1
		monthBeforeNum = 12 - monthNow
		for i in range(monthBeforeNum):
			retList.append(str(yearNow-1) + '-' + str(monthBegin+i))
		for i in range(12 -monthBeforeNum):
			retList.append(str(yearNow) + '-' + str(i+1))
	return retList





@app.route('/stock/<string:code>')
def getAStock(code):
	result={}
	stocks=[]
	result['stockId']=code

	stock=getAStockBasicData(code)
	result['stockName']=stock.name
	result['currentPrice']=stock.trade
	result['trend']=stock.changepercent
	result['turnoverRate']=stock.turnoverratio
	result['marketProfitability']=stock.per
	result['totalVolume']=stock.volume

	data=ts.get_hist_data(code).head(90)
	for index, row in data.iterrows():
		temp={}
		temp['time']=row['date']
		temp['start']=row['open']
		temp['end']=row['close']
		temp['max']=row['high']
		temp['min']=row['low']
		temp['volume']=row['volume']
		stocks.append(temp)

	stocks.sort(key=lambda x:x['time'])
	result['trendData']=stocks

	return json.dumps(result,ensure_ascii=False)


@app.route('/strategy/recommend/profit')
def getProfitInfo():
	result={}
	stocks=[]

	tempProfitDic = getProfitDic()
	result['risk']=tempProfitDic.get('var')
	result['todayBenefit']=tempProfitDic.get('value')
	templist =getTopX()
	profitList = [0,0,0,0,0,0,0,0,0,0,0,0]
	for i in range(10):
		stockId =templist[i][0]
		temp = {}
		temp['buyRate'] = tempProfitDic.get(stockId)
		tempProfit =getMonthReturnPerYear(stockId)
		for i in range(12):
			tempProfit[i]=tempProfit[i]*temp['buyRate']
		profitList =list_add(profitList,tempProfit)
		temp['stockId']=stockId
		stock=getAStockBasicData(stockId)
		temp['stockName']=stock.name
		temp['currentPrice']=stock.trade
		temp['trend']=stock.changepercent
		temp['turnoverRate']=stock.turnoverratio
		temp['marketProfitability']=stock.per
		temp['todayVolume']=stock.volume

		stocks.append(temp)
	result['stocks']=stocks

	loopbackData = []
	loopbackPeryear =getSZData('2018-06')
	monthList =getOneYearMonthList('2018-06')
	for i in range(12):
		temp = {}
		temp['data']= monthList[i]
		temp['上证指数']= loopbackPeryear.get(temp['data'])
		temp['自选股'] = profitList[i]
		loopbackData.append(temp)

	result['loopback'] = loopbackData


	return json.dumps(result,ensure_ascii=False)

@app.route('/strategy/recommend/risk')
def getRiskInfo():
	result={}
	stocks=[]

	tempRiskDic = getRiskDic()
	result['risk']=tempRiskDic.get('var')
	result['todayBenefit']=tempRiskDic.get('value')
	templist =getTopX()
	profitList = [0,0,0,0,0,0,0,0,0,0,0,0]
	for i in range(10):
		stockId =templist[i][0]
		temp = {}
		temp['buyRate'] = tempRiskDic.get(stockId)
		tempProfit =getMonthReturnPerYear(stockId)
		for i in range(12):
			tempProfit[i]=tempProfit[i]*temp['buyRate']
		profitList =list_add(profitList,tempProfit)
		temp['stockId']=stockId
		stock=getAStockBasicData(stockId)
		temp['stockName']=stock.name
		temp['currentPrice']=stock.trade
		temp['trend']=stock.changepercent
		temp['turnoverRate']=stock.turnoverratio
		temp['marketProfitability']=stock.per
		temp['todayVolume']=stock.volume

		stocks.append(temp)
	result['stocks']=stocks

	loopbackData = []
	loopbackPeryear =getSZData('2018-06')
	monthList =getOneYearMonthList('2018-06')
	for i in range(12):
		temp = {}
		temp['data']= monthList[i]
		temp['上证指数']= loopbackPeryear.get(temp['data'])
		temp['自选股'] = profitList[i]
		loopbackData.append(temp)

	result['loopback'] = loopbackData


	return json.dumps(result,ensure_ascii=False)

def getStrategy(recordId):
	rid=int(recordId)   # python3中整数就是long
	session=db.setup_db()
	strategy=session.query(Strategy).filter(Strategy.id==rid).one()
	return strategy

@app.route('/strategy/record/<int:recordId>')
def getStrategyInfo(recordId):
	result={}
	stocks=[]
	oldStrategy = getStrategy(recordId)
	result['recordName'] = oldStrategy.name
	result['recordTime'] = oldStrategy.time
	# result['todayBenefit']
	tempRate = 0
	for i in range(10):
		stockId =oldStrategy.items[i].stock_id
		temp = {}
		temp['buyRate'] = oldStrategy.items[i].buy_rate
		temp['stockId']=stockId
		stock=getAStockBasicData(stockId)
		temp['stockName']=stock.name
		temp['currentPrice']=stock.trade
		temp['trend']=stock.changepercent
		temp['turnoverRate']=stock.turnoverratio
		temp['marketProfitability']=stock.per
		temp['todayVolume']=stock.volume
		tempRate = tempRate + temp['buyRate']*getMonthReturnLatest(temp['stockId'])
		stocks.append(temp)
	result['todayBenefit']=tempRate
	result['stocks']=stocks

	return json.dumps(result,ensure_ascii=False)
# 根据recordId获得需要回测的策略
# recordId是long


@app.route('/strategy/loopback/<int:recordId>')
def getLoopbackInfo(recordId):
	oldStrategy = getStrategy(recordId)
	profitList = [0,0,0,0,0,0,0,0,0,0,0,0]
	for i in range(10):
		stockId =oldStrategy.items[i].stock_id
		temp = {}
		temp['buyRate'] = oldStrategy.item[i].buy_rate
		tempProfit =getMonthReturnPerYear(stockId)
		for i in range(12):
			tempProfit[i]=tempProfit[i]*temp['buyRate']
		profitList =list_add(profitList,tempProfit)

	loopbackData = []
	loopbackPeryear =getSZData('2018-06')
	monthList =getOneYearMonthList('2018-06')
	for i in range(12):
		temp = {}
		temp['data']= monthList[i]
		temp['上证指数']= loopbackPeryear.get(temp['data'])
		temp['自选股'] = profitList[i]
		loopbackData.append(temp)

	result = loopbackData

	return json.dumps(result,ensure_ascii=False)	


def getAStockBasicData(code):
	session=db.setup_db()
	stock=session.query(db.Stock).filter(db.Stock.code==code).one()
	return stock

def getStocksData():
	df=ts.get_today_all()
	df.to_sql('stock',db.get_engine(),if_exists='replace',index=False)
	pass

def getSZData(date):
	date=date+'-32'
	df=ts.get_hist_data(code='sh',ktype='M')
	df=df[['date','open','close']]
	df=df[df['date']<=date].sort_index(ascending=False).head(12)
	res={}
	for line in df.values:
		open=line[1]
		close=line[2]
		date=line[0][0:7]
		res[date]=(close-open)/open
	return res

def getTopX():
	object = pd.read_csv('gupiao_profit.csv');
	object = object.head(10)
	idlist = object.values.tolist()
	finaldic = []
	for i in range(10):
		stockNum ='%06d' % idlist[i][0]
		finaldic.append([stockNum,idlist[i][1]])

	return finaldic

def getRiskDic():
	object = pd.read_csv('VaR/stockchoice.csv')
	object = object.tail(1).values.tolist()[0]
	finaldic = {}
	finaldic['value']= object[0]
	finaldic['var']= object[1]
	for i in range(10):
		stockNum = '%06d' %object[2*i+2]
		finaldic[stockNum]= object[2*i+3]

	return finaldic

def getProfitDic():
	object = pd.read_csv('VaR/stockchoice.csv')
	object = object.head(1).values.tolist()[0]
	finaldic = {}
	finaldic['value']= object[0]
	finaldic['var']= object[1]
	for i in range(10):
		stockNum = '%06d' %object[2*i+2]
		finaldic[stockNum]= object[2*i+3]

	return finaldic


def getMonthReturnPerYear(code):
	date_necessity = '2018-07'
	Object = pd.read_csv('gupiao/objects/'+code+'_20060101-20180823.csv')
	Object = Object.get(['tradeDate', 'dailyReturnReinv'])
	Object['month'] = Object['tradeDate'].apply(lambda x: datetime.strftime(datetime.strptime(x, "%Y-%m-%d"), "%Y-%m"))

	new_Object = pd.DataFrame(columns=['month', 'dailyReturnReinv'])
	for (i, (month, dat)) in enumerate(Object.groupby('month')):
		if month >= date_necessity:
			break
		new_Object.loc[i, ['month']] = month
		new_Object.loc[i, ['dailyReturnReinv']] = dat[['dailyReturnReinv']].apply(np.mean)

	return new_Object.tail(12).get('dailyReturnReinv').values.tolist()


def getMonthReturnLatest(code):
	Object = pd.read_csv('gupiao/objects/'+code+'_20060101-20180823.csv')
	Object = Object.get(['tradeDate', 'dailyReturnReinv'])
	Object['month'] = Object['tradeDate'].apply(lambda x: datetime.strftime(datetime.strptime(x, "%Y-%m-%d"), "%Y-%m"))

	new_Object = pd.DataFrame(columns=['month', 'dailyReturnReinv'])
	for (i, (month, dat)) in enumerate(Object.groupby('month')):
		new_Object.loc[i, ['month']] = month
		new_Object.loc[i, ['dailyReturnReinv']] = dat[['dailyReturnReinv']].apply(np.mean)

	return new_Object.tail(1).get('dailyReturnReinv').values.tolist()[0]



if __name__ == "__main__" :
	# db.setup_db()
	# getStocksData()
	# print(getAStock('000001'))
	# getStrategy(12232323)
	# app.run(debug=True)
	print(getMonthReturnLatest('000520'))


