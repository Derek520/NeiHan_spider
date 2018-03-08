# -*- coding:utf-8 -*-
import requests
import json,re
from jsonpath import jsonpath



class Neihan_Spider:
    '''内涵段子'''
    def __init__(self):
        self.url = 'http://www.neihanshequ.com/'
        self.next_url = 'http://www.neihanshequ.com/joke/?is_json=1&app_name=neihanshequ_web&max_time={}'
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
        self.session = requests.session()
        self.count=0

    def get_url(self,url):
        '''获取请求'''
        print(url)
        resp = self.session.get(url,headers=self.headers)
        return resp.content.decode()

    def get_first_url(self,resp):
        '''构造页码'''
        print('首页信息。。。。')
        max_time = re.compile(r"max_time:.'(.*?).,\n", re.S)
        data = re.compile(r"<h1 class=\"title\">.*?<p>(.*?)</p>",re.S)
        p = data.findall(resp)
        max_time =max_time.findall(resp)[0]
        return max_time,p

    def pasms_str(self,data):
        '''处理每页数据'''
        resp_json = json.loads(data)
        resp_text = jsonpath(resp_json,'$..text')
        has_more = jsonpath(resp_json, '$..has_more')[0]
        max_time = jsonpath(resp_json, '$..max_time')[0]
        return resp_text,has_more,max_time

    def save_data(self,data):
        '''保存数据'''
        with open('内涵段子.txt','a',encoding='utf8') as f:
            for text in data:
                f.write(text)
                f.write('\n')
                # print(text)
                self.count+=1
                print(self.count)
    def run(self):
        '''逻辑处理'''
        # 1.请求首页
        resp = self.get_url(self.url)
        # 2.获取第一页内容
        max_time,data= self.get_first_url(resp)
        self.save_data(data)
        print(max_time)

        has_more =True
        # 当has_more等于True时，说明没有爬去完毕
        while has_more:
            # 获取第下一页数据
            resp_next = self.get_url(self.next_url.format(max_time))
            resp_text,has_more,max_time = self.pasms_str(resp_next)
            self.save_data(resp_text)


if __name__ == '__main__':
    neihan = Neihan_Spider()
    neihan.run()







