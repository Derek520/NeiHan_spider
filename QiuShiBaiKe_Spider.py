# -*- coding:utf-8 -*-
import requests,re,json
from lxml import etree
from time import time
from queue import Queue
from threading import Thread

class QiuBai_Spider:
    '''糗事百科'''
    def __init__(self):
        self.url = 'https://www.qiushibaike.com/8hr/page/{}/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Cookie': 'csrftoken=34decf1a83b0bb9fabde0f15995b7f77; tt_webid=6529672643712075271; uuid="w:665cf328800a407592f581f92f7f89ce"; _ga=GA1.2.600726372.1520307886; _gid=GA1.2.322955237.1520307886'}
        self.url_list_queue =Queue() #每页url列表队列
        self.html_queue =Queue()    # 每次访问返回的html内容队列
        self.content_queue =Queue() # 提取的内容队列

    def get_url_list(self):
        '''获取url列表'''
        # url_list = [self.url.format(i) for i in range(1,14)]
        # return url_list

        for i in range(1,14):
            # 将每页url放进列表队列中
            self.url_list_queue.put(self.url.format(i))

    def parse_url(self):
        '''发送请求'''
        while True:
            # 依次取出列表队列的数据
            url = self.url_list_queue.get()
            print(url)
            resp = requests.get(url,headers=self.headers)
            # return resp.content.decode()
            # 将返回的数据,放进html队列中
            self.html_queue.put(resp.content.decode())
            # 在取出队列的数据时候，需要让队列减一
            self.url_list_queue.task_done()

    def get_content_list(self):
        '''提取数据'''
        while True:
            # 取出返回的html数据
            html_str =self.html_queue.get()
            # 进行Html初始化
            html = etree.HTML(html_str)
            # 使用xpath提取数据,返回结果列表
            html_data =html.xpath('//div[@id="content-left"]/div')

            list1 = []
            # 便利列表取出数据放进字典中
            for data in html_data:
                dict = {}
                dict['content'] = data.xpath('.//div[@class="content"]/span/text()')
                # print(html_list)
                # 将字典放进列表中
                list1.append(dict)
            # 将提取到的数据，放进队列中
            self.content_queue.put(list1)
            # 取出队列一个，就要删除一个
            self.html_queue.task_done()

    def save_data(self):
        '''保存'''

        while True:
            # 取出content队列中的数据，并且保存
            data = self.content_queue.get()

            with open('糗事百科.txt','a') as f:
                for txt in data:
                    data_txt = json.dumps(txt,ensure_ascii=False,indent=2)
                    f.write(data_txt)
                    f.write('\n')
            # 每个队列取出数据时，都要配合task_done减一
            self.content_queue.task_done()

    def run(self):
        '''逻辑'''
        # 开始时间
        start_time = time()
        # 1.URL——list
        # url_list = self.get_url_list()
        # # 2.遍历请求
        # for url in url_list:
        #     print(url)
        #     html_str = self.parse_url(url)
        #     # 3.提取数据
        #     data = self.get_content_list(html_str)
        #     # 4.保存数据
        #     self.save_data(data)

        thd_list = [] # 定义空列表放每个线程
        # 定义一个线程生成url_list
        td1 = Thread(target=self.get_url_list)
        thd_list.append(td1)
        # 定义多个线程发起请求
        for i in range(2):
            td2 =Thread(target=self.parse_url)
            thd_list.append(td2)
        # 定义一个线程提取数据
        td3 =Thread(target=self.get_content_list)
        thd_list.append(td3)
        # 定义一个线程保存数据
        td4 = Thread(target=self.save_data)
        thd_list.append(td4)
        # 遍历开启每个子线程,并且设置为守护线程
        for t in thd_list:
            t.setDaemon(True)
            t.start()
        # 遍历队列等待,等待队列为空的时候，主线程退出
        for q in [self.html_queue,self.content_queue,self.url_list_queue]:
            q.join()

        # 结束时间
        end_time = time()

        print('主线程结束，用时{}'.format(end_time-start_time))

if __name__ == '__main__':
    qb = QiuBai_Spider()
    qb.run()