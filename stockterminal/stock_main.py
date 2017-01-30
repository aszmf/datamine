# -*-coding:utf-8 -*-
# 
# Created on 2017-01-27, by zmf
#using tushare
# 

__author__ = 'felix'

import requests
import time
import sys
import os
import vtPath
import threading
import tushare as ts
from tushare.trader import trader as stocktrader
from optparse import OptionParser
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-ORC/tesseract'

class Worker(threading.Thread):
    """多线程获取"""
    def __init__(self, work_queue, result_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.start()

    def run(self):
        while True:
            func, arg, code_index = self.work_queue.get()
            res = func(arg, code_index)
            self.result_queue.put(res)
            if self.result_queue.full():
                res = sorted([self.result_queue.get() for i in range(self.result_queue.qsize())], key=lambda s: s[0], reverse=True)
                res.insert(0, ('0', u'名称     股价'))
                print('***** start *****')
                for obj in res:
                    print(obj[1])
                print( '***** end *****\n')
            self.work_queue.task_done()


class Stock(object):

    """股票实时价格获取"""

    def __init__(self, code, thread_num):
        self.code = code
        self.work_queue = Queue()
        self.threads = []
        self.__init_thread_poll(thread_num)

    def __init_thread_poll(self, thread_num):
        self.params = self.code.split(',')
        self.params.extend(['s_sh000001', 's_sz399001'])  # 默认获取沪指、深指
        self.result_queue = Queue(maxsize=len(self.params[::-1]))
        for i in range(thread_num):
            self.threads.append(Worker(self.work_queue, self.result_queue))

    def __add_work(self, stock_code, code_index):
        self.work_queue.put((self.value_get, stock_code, code_index))

    def del_params(self):
        for obj in self.params:
            self.__add_work(obj, self.params.index(obj))

    def wait_all_complete(self):
        for thread in self.threads:
            if thread.isAlive():
                thread.join()

    @classmethod
    def value_get(cls, code, code_index):
        slice_num, value_num = 21, 3
        name, now = u'——无——', u'  ——无——'
        if code in ['s_sh000001', 's_sz399001']:
            slice_num = 23
            value_num = 1
        r = requests.get("http://hq.sinajs.cn/list=%s" % (code,))
        res = r.text.split(',')
        if len(res) > 1:
            name, now = r.text.split(',')[0][slice_num:], r.text.split(',')[value_num]
        return code_index, name + ' ' + now
		
	
# 文件路径名
path = os.path.abspath(os.path.dirname(__file__))    
ICON_FILENAME = 'vnpy.ico'
ICON_FILENAME = os.path.join(path, ICON_FILENAME)  

SETTING_FILENAME = 'VT_setting.json'
SETTING_FILENAME = os.path.join(path, SETTING_FILENAME)  		
	

#def before_trader()
def parse(code_list):
    '''process stock'''
    is_buy    = 0
    buy_val   = []
    buy_date  = []
    sell_val  = []
    sell_date = []
    df = ts.get_hist_data(STOCK)
    ma20 = df[u'ma20']
    close = df[u'close']
    rate = 1.0
    idx = len(ma20)

    while idx > 0:
        idx -= 1
        close_val = close[idx]
        ma20_val = ma20[idx]
        if close_val > ma20_val:
                if is_buy == 0:
                        is_buy = 1
                        buy_val.append(close_val)
                        buy_date.append(close.keys()[idx])
        elif close_val < ma20_val:
                if is_buy == 1:
                        is_buy = 0
                        sell_val.append(close_val)
                        sell_date.append(close.keys()[idx])

    print("stock number: %s"%(STOCK))
    print("buy count   : %d" %len(buy_val))
    print("sell count  : %d" %len(sell_val))

    for i in range(len(sell_val)):
        rate = rate * (sell_val[i] * (1 - 0.002) / buy_val[i])
        print("buy date : %s, buy price : %.2f"%(buy_date[i], buy_val[i]))
        print("sell date: %s, sell price: %.2f"%(sell_date[i], sell_val[i]))

    print("rate: %.2f" % rate)
 

#def after_trader()
	
def main():
    """主程序入口"""
    # 重载sys模块，设置默认字符串编码方式为utf8
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    
	 # 设置Qt的皮肤
    try:
        f = file(SETTING_FILENAME)
        setting = json.load(f)    
        if setting['darkStyle']:
            import qdarkstyle
            app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))
    except:
        pass
	
	
    ts.set_broker('zxjt',user='30449422',passwd='123456')
	#中信建投
	#ts.set_broker('htzq',user='3283982983',passwd ='382829') #华泰证券
	
    ts.get_broker()#print infor
    csc=ts.TraderAPI('zxjt')             #中信建投
    csc.login()                          #login
    baseinfo=csc.baseinfo()              #获取账户基本信息
    fundkeyong=baseinfo['fundav1']       #可用余额
    fundtotal=csc.position()             #获取持仓列表
    captotal==baseinfo['marketvalue']    #证券总市值

    STOCK = '600000'       ##浦发银行
    parse(STOCK)
''' 
csc.buy('000903',price=7.71,count=100) 
csc.sell('600020',price=19.66,count=100)  #按数量卖出
csc.sell ('600020',price=19.66,amount=10000) #按总金额卖出
csc.entrust_list() #获取委托单列表     撤单操作必须通过获取委托单列表的数据，部分数据会作为参数传递给撤单函数
csc.cancel(ordersno='262138,265447',orderdate='20160930,20160930')  #撤单操作    
   #ordersno和orderdate在多个证券撤单时，都是以逗号分隔，这两个参数的数据来自委托单接口
csc.deal_list(begin=20160920,end=20160929)   #获取成交列表
ts.get_realtime_quotes('000581')   #获取实时行情监控   使用一个股票
ts.get_realtime_quotes(['6000848','000980','000981'])     #获取实时行情监控   使用数组
ts.get_realtime_quotes(df['code'].tail(10))     #获取实时行情监控   使用pandas
#上证指数
ts.get_realtime_quotes('sh')

#上证指数 深圳成指 沪深300指数 上证50 中小板 创业板
ts.get_realtime_quotes(['sh','sz','hs300','sz50','zxb','cyb'])

#混搭
ts.get_realtime_quotes(['sh','600848'])


实时数据的内容为Level1行情：

0：name，股票名称
1：open，今日开盘价
2：pre_close，昨日收盘价
3：price，当前价格
4：high，今日最高价
5：low，今日最低价
6：bid，竞买价，即“买一”报价
7：ask，竞卖价，即“卖一”报价
8：volume，成交量 
9：amount，成交金额（元 CNY）
10：b1_v，委买一（笔数 ）
11：b1_p，委买一（价格 ）
12：b2_v，“买二”
13：b2_p，“买二”
14：b3_v，“买三”
15：b3_p，“买三”
16：b4_v，“买四”
17：b4_p，“买四”
18：b5_v，“买五”
19：b5_p，“买五”
20：a1_v，委卖一（笔数）
21：a1_p，委卖一（价格）
...
30：date，日期；
31：time，时间；

需在函数后面加问号查看关于实盘交易各类接口的输入输出参数详细注释，例如：查看持仓列表的返回值含义注释，可使用 csc.position? ，效果如下：

获取所有股市的代码：
stock_info=ts.get_stock_basics()
def get_all_stock_id():
    #获取所有股票代码
    for i in stock_info.index:
        print i
获取股市市场的基本信息：
 
stock_info=ts.get_stock_basics()
 
'''
	
	
	
	
	
	
	
	
	
	
	
if __name__ == '__main__':
    main()
	