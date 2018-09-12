
from sqlalchemy import Column, BIGINT, BLOB, TEXT, VARCHAR, INT, FLOAT, BOOLEAN, ForeignKey, create_engine
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
Base=declarative_base()

class Stock(Base):

	__tablename__ = "stock"  # table name
	__table_args__ = {"mysql_charset": "utf8"}
	# id = Column(BIGINT, primary_key=True, autoincrement=True)
	code = Column(TEXT,primary_key=True)#股票代码
	name = Column(TEXT)#名字
	changepercent=Column(FLOAT)#跌涨幅
	trade=Column(FLOAT)#现价
	open=Column(FLOAT)#开盘价
	high=Column(FLOAT)#最高价
	low=Column(FLOAT)#最低价
	settlement=Column(FLOAT)#昨日收盘价
	volume=Column(BIGINT)#成交量
	turnoverratio=Column(FLOAT)#换手率
	amount=Column(FLOAT)#成交额
	per=Column(FLOAT)#市盈率
	pb=Column(FLOAT)#市净率
	mktcap=Column(FLOAT)#总市值
	nmc=Column(FLOAT)#流通市值




def create_table(connect):
	Base.metadata.create_all(connect)  # create the structure of table

# initialize connection
def setup_db():
	engine=create_engine('mysql+mysqlconnector://root:31415926@localhost:3306/bequank?charset=utf8')#,echo=True
	# create_table(engine)
	DBSession=sessionmaker(bind=engine)
	return DBSession()

def get_engine():
	engine=create_engine('mysql+pymysql://root:31415926@localhost:3306/bequank?charset=utf8')#,echo=True
	return engine


'''
add:        session.add(obj)
delete:     session.query(class)[.filter()].delete()
modify:     session.query(class).filter(conditions).update({class.attribute:new_val}[, other options ])
search:     session.query()[.filter()].(all()/one())
commit:     session.commit()
close:      session.close()
'''
# if __name__=='__main__':
# 	session=setup_db()
# 	session.close()