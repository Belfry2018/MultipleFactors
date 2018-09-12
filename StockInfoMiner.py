import requests
import re
import pandas as pd
import DBHandler as db


def mineStockData():

	url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb=jQuery112405946568157298318_1535797188570&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)&cmd=C._A&st=(ChangePercent)&sr=-1&p=1&ps=3559&_=1535797189625"
	resp = requests.get(url)
	li = re.findall(r'\[(.+)\]', resp.content.decode("utf-8"))[0][1:-1].split('","')
	add_stocks(li)


def add_stocks(stocks):
	session = db.setup_db()
	for stock in stocks:
		stock = stock.split(",")
		s = db.Stock(code=stock[1], name=stock[2], price=stock[3], RF=stock[4],
				  volumn=stock[6], turnover=stock[15], PE=stock[16])
		session.add(s)
	session.commit()

