from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import requests
import re
import pymysql


def create_database():
	db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='nibabaqyc', charset='utf8')
	cursor = db.cursor()
	cursor.execute("create database stock_info")


connect = create_engine("mysql+mysqlconnector://root:31415926@localhost:3306/bequank?charset=utf8", encoding="utf-8",
                        echo=True)
Base = declarative_base()
create_database()


class Stock(Base):
	# head = ['code', 'name', 'price', 'RF', 'turnover', 'PE', 'volumn']
	__tablename__ = "stocks"  # table name
	__table_args__ = {"mysql_charset": "utf8"}
	id = Column(Integer, primary_key=True, autoincrement=True)
	code = Column(String(6))
	name = Column(String(32))
	price = Column(String(32))
	RF = Column(String(32))
	turnover = Column(String(32))
	PE = Column(String(32))
	volumn = Column(String(32))


def create_table():
	Base.metadata.create_all(connect)  # create the structure of table


def get_session():
	session_class = sessionmaker(bind=connect)
	return session_class()


def add_stocks(stocks):
	session = get_session()
	for stock in stocks:
		stock = stock.split(",")
		s = Stock(code=stock[1], name=stock[2], price=stock[3], RF=stock[4],
		          volumn=stock[6], turnover=stock[15], PE=stock[16])
		session.add(s)
	session.commit()


def init_database():
	create_table()
	url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb=jQuery112405946568157298318_1535797188570&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)&cmd=C._A&st=(ChangePercent)&sr=-1&p=1&ps=3559&_=1535797189625"
	resp = requests.get(url)
	li = re.findall(r'\[(.+)\]', resp.content.decode("utf-8"))[0][1:-1].split('","')
	add_stocks(li)


def update_stocks(stocks):
	session = get_session()
	for stock in stocks:
		stock = stock.split(",")
		data = session.query(Stock).filter(Stock.code == stock[1]).first()
		data.name = stock[2]
		data.price = stock[3]
		data.RF = stock[4]
		data.volumn = stock[6]
		data.turnover = stock[15]
		data.PE = stock[16]
		session.merge(data)
	session.commit()


def update_database():
	url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb=jQuery112405946568157298318_1535797188570&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)&cmd=C._A&st=(ChangePercent)&sr=-1&p=1&ps=3559&_=1535797189625"
	resp = requests.get(url)
	li = re.findall(r'\[(.+)\]', resp.content.decode("utf-8"))[0][1:-1].split('","')
	update_stocks(li)


# update_database()


if __name__ == "__main__":
	init_database()
	update_database()
