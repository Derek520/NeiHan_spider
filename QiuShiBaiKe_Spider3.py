# -*- coding:utf-8 -*-
import random

import requests,json
from lxml import etree
from threading import Thread
from queue import Queue
from time import time,sleep
from User_agent import User_Agt
class QiuShiBaiKe(object):
    '''糗事百科'''
    def __init__(self):
        self.url = 'https://www.qiushibaike.com/8hr/page/{}/'
        self.session = requests.session()
        # self.headers ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
        self.headers = {'User-Agent':User_Agt()}
        self.count =0  # 定义计数器
        self.url_list_queue = Queue()  # 创建页码url_list队列
        self.detail_url_list_queue = Queue()  # 创建详情页url_list队列
        self.content_queue = Queue()

    def get_url_list(self): # 页码url_list
        '''url_list'''
        print('>>>>>>>>>>>获取页码url_list>>>>>>>>>>>>>>')
        # url_list = [self.url.format(i) for i in range(1,14)]
        # return url_list
        # 将页码放进对列中
        for i in range(1, 14):
            url =self.url.format(i)
            self.url_list_queue.put(url)

    def get_detail_url_list(self): # 详情页url_list
        '''detail_url'''
        while True:
            url = self.url_list_queue.get()
            print('>>>>>>>>>>>获取详情页url_list>>>>>>>>>>>>>')

            # print(url)
            list1 = []
            resp = requests.get(url,headers=self.headers,timeout=1)
            html = etree.HTML(resp.content.decode())
            detail_url = html.xpath('//div[@id="content-left"]/div//a[@class="contentHerf"]/@href')
            # print(len(detail_url))

            for i in detail_url:
                list1.append('https://www.qiushibaike.com'+i)
                dt_url = 'https://www.qiushibaike.com' + i
                self.detail_url_list_queue.put(dt_url)
                # sleep(random.random(1, 3))
            # print(list1)
            # self.detail_url_list_queue.put(list1)
            # return list1
            self.url_list_queue.task_done()

    def parse_url(self):
        '''抓取详情页数据'''
        while True:
            url = self.detail_url_list_queue.get()
            print('>>>>>>>>>>>>>>抓取详情页数据>>>>>>>>>>>>>>>')

            list_content = []

            print(url)
            dict = {}
            resp = requests.get(url,headers=self.headers,timeout=5)
            html = etree.HTML(resp.content.decode())
            dict["nofollow"] = "https:"+html.xpath('//div[@class="author clearfix"]/a/img/@src')[0] if len(html.xpath('//div[@class="author clearfix"]/a/img/@src'))>0 else None
            dict["content"] = html.xpath('//div[@class="content"]/text()')[0] if len(html.xpath('//div[@class="content"]/text()'))>0 else None
            dict["thumb"] = "https:"+html.xpath('//div[@class="thumb"]//img/@src')[0] if len(html.xpath('//div[@class="thumb"]//img/@src'))>0 else None
            dict["name"] = html.xpath('//div[@class="author clearfix"]/a/h2/text()')[0] if len(html.xpath('//div[@class="author clearfix"]/a/h2/text()'))>0 else None
            dict["stats-vote"] = html.xpath('//div[@class="stats"]/span/i/text()')[0] if len(html.xpath('//div[@class="stats"]/span/i/text()'))>0 else None
            dict["stats-comments"] = html.xpath('//div[@class="stats"]/span/i/text()')[-1] if len(html.xpath('//div[@class="stats"]/span/i/text()'))>1 else None
            dict["commnts"] = html.xpath('//div[@class="comments-list clearfix"]//div//span/text()')
            dict["hotCmt"] = html.xpath('//article[@class="hotCmt"]//div[@class="main-text"]/text()') if len(html.xpath('//article[@class="hotCmt"]//div[@class="main-text"]/text()'))>0 else None
            # print(dict)
            list_content.append(json.dumps(dict,ensure_ascii=False,indent=2))

            self.content_queue.put(list_content)
            sleep(random.random())
            self.detail_url_list_queue.task_done()
        # return list_content
            # print(tx)
            # print(content)
            # print(name)
            # print(commnts_count)
            # print(commnts)
    def save_data(self):
        '''保存数据'''
        while True:
            if not self.content_queue.empty():

                list_content = self.content_queue.get()

                print('--------保存数据-----------')
                with open('糗事百科.txt','a') as f:
                    for content in list_content:
                        f.write(content)
                        f.write('\n')
                        self.count+=1
                        print('<<<<<<<<<<<<<<<<写入第{}条<<<<<<<<<<<<<<'.format(self.count))

                self.content_queue.task_done()
            else:
                sleep(random.random())

    def run(self):
        '''逻辑处理'''
        start_time =time()

        # 创建线程列表
        thd_list = []
        # 创建获取页码列表的子线程
        thd1 = Thread(target=self.get_url_list)
        thd_list.append(thd1)
        # 创建获取详情页列表的子线程
        thd2 = Thread(target=self.get_detail_url_list)
        thd_list.append(thd2)
        # 创建抓取数据的子线程
        for i in range(8):
            thd3 = Thread(target=self.parse_url)
            thd_list.append(thd3)
        # 创建保存数据的子线程
        thd4 = Thread(target=self.save_data)
        thd_list.append(thd4)

        for t in thd_list:
            t.setDaemon(True)
            t.start()

        for q in [self.url_list_queue,self.detail_url_list_queue,self.content_queue]:
            q.join()
        # url_list = self.get_url_list()
        # detail_url = self.get_detail_url_list(url_list)
        # list_content = self.parse_url(detail_url)
        # self.save_data(list_content)
        end_time = time()

        print('保存完毕-----用时{}'.format(end_time-start_time))
if __name__ == '__main__':
    qb = QiuShiBaiKe()
    qb.run()