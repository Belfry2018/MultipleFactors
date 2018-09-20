from flask import Flask
from flask_apscheduler import APScheduler
import tushare as ts
import json
import DBHandler as db
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

	data=ts.get_k_data(code).head(90)
	for index, row in data.iterrows():
		temp={}
		temp['time']=row['date']
		temp['start']=row['open']
		temp['end']=row['close']
		temp['max']=row['high']
		temp['min']=row['low']
		temp['volume']=row['volume']
		stocks.append(temp)

	result['trendData']=stocks

	return json.dumps(result,ensure_ascii=False)

# 根据recordId获得需要回测的策略
# recordId是long
def getStrategy(recordId):
	rid=int(recordId)   # python3中整数就是long
	session=db.setup_db()
	strategy=session.query(Strategy).filter(Strategy.id==rid).one()
	return strategy


def getAStockBasicData(code):
	session=db.setup_db()
	stock=session.query(db.Stock).filter(db.Stock.code==code).one()
	return stock

def getStocksData():
	df=ts.get_today_all()
	df.to_sql('stock',db.get_engine(),if_exists='replace',index=False)
	pass


if __name__ == "__main__" :
	# db.setup_db()
	# getStocksData()
	# getStrategy(12232323)
	app.run(debug=True)

