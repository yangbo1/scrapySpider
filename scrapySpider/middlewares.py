# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import random
import re
import time

from scrapy import signals
from scrapy import settings
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils import defer
from twisted.internet.error import DNSLookupError, ConnectionDone, ConnectError, ConnectionLost, TCPTimedOutError
from twisted.web._newclient import ResponseFailed

from scrapySpider.utils import crawl_proxy


class ScrapyspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

from scrapy.http.headers import Headers
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from fake_useragent import UserAgent
# class RandomUserAgentMiddleware(object):
#     """
#     随机选取 代理（User-Agent）
#     """
#
#     def __init__(self, crawler):
#         # self.user_agent = user_agent
#         # self.headers = Headers()
#         super(RandomUserAgentMiddleware, self).__init__()
#         self.ua = UserAgent()
#         # self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random') #从setting文件中读取RANDOM_UA_TYPE值
#     @classmethod
#     def from_crawler(cls, crawler):
#         """
#         开始构造请求前执行的方法\n
#         :param crawler:整个爬虫的全局对象\n
#         :return:
#         """
#         # 从配置里获取 用户代理（User-Agent） 列表
#         # return cls(user_agent=crawler.settings.get('USER_AGENT_LIST'))
#         return cls(crawler)
#
#     def process_request(self, request, spider):
#         """
#         发送请求前执行的方法\n
#         :param request:请求\n
#         :param spider:爬虫应用\n
#         :return:
#         """
#
#         # # 从 代理 列表中随机选取一个 代理
#         # agent = random.choice(self.user_agent)
#         # # print('当前 User-Agent ：', agent)
#         # self.headers['User-Agent'] = agent
#         # request.headers = self.headers
#
#         request.headers.setdefault('User_Agent', self.ua.random)
#         pass

class IPProxyMiddleware(object):
    """
    IP 代理池中间件
    """
    EXCEPTIONS_TO_RETRY = (TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)
    def __init__(self):
        # 爬取有效 ip
        self.count = 1
        self.ip_list = crawl_proxy.get_ips()
        # 请求已经失败的次数
        self.retry_time = 0
        # self.index = random.randint(0, len(self.ip_list) - 1)

    def process_request(self, request, spider):
        """
        处理将要请求的 Request
        :param request:
        :param spider:
        :return:
        """
        # 失败重试次数
        self.retry_time = 0
        #
        # if len(self.ip_list) < 5:
        #     self.ip_list.extend(crawl_proxy.get_ips(refresh=True))
        # 随机选取 ip
        # proxy = json.loads(self.ip_list[self.index])
        self.proxy = json.loads(random.choice(list(self.ip_list.values())))
        print('选取的 ip：' + self.proxy.get('proxy'))
        # 设置代理
        request.meta['proxy'] = self.proxy.get('proxy')

    def process_response(self, request, response, spider):
        """
        处理返回的 Response
        :param request:
        :param response:
        :param spider:
        :return:
        """
        # 针对4**、和5** 响应码，重新选取 ip
        if re.findall('[45]\d+', str(response.status)):
            print(u'[%s] 响应状态码：%s' % (response.url, response.status))
            # if self.retry_time > 1:
            #     print('删除无效ip： %s', self.proxy.get('ip'))
            #     if (len(self.ip_list) > 0):
            #         self.ip_list.pop(self.proxy.get('ip'))
                # crawl_proxy.del_ip(self.proxy.get('ip'))
                # return response
            # if response.status == 418 or response.status == 503 or response.status == 400:
            if response.status != 200:
                # sec = random.randrange(30, 35)
                # print(u'休眠 %s 秒后重试' % sec)
                # time.sleep(1)
                print(list(self.ip_list.keys()))
                print('删除无效ip：', self.proxy.get('proxy'))
                if (len(self.ip_list) > 0):
                    self.ip_list.pop(self.proxy.get('proxy'))
                crawl_proxy.del_ip(self.proxy.get('proxy'))
                # return response
            # self.retry_time += 1

            if (len(self.ip_list) == 0):
                print("本地ip全部失效, 重新获取缓存", self.count)
                self.ip_list = crawl_proxy.get_ips(pages=0, refresh=False, count=self.count)
                self.count = (self.count+1)%10
            self.proxy = json.loads(random.choice(list(self.ip_list.values())))
            request.meta['proxy'] = self.proxy.get('proxy')
            return request
        return response
    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            print(list(self.ip_list.keys()))
            print('删除无效ip：', self.proxy.get('proxy'))
            crawl_proxy.del_ip(self.proxy.get('proxy'))
            if (len(self.ip_list) > 0):
                self.ip_list.pop(self.proxy.get('proxy'))
            if (len(self.ip_list) == 0):
                print("本地ip全部失效, 重新获取缓存", self.count)
                self.ip_list = crawl_proxy.get_ips(pages=0, refresh=False, count=self.count)
                self.count = (self.count+1)%10
            self.proxy = json.loads(random.choice(list(self.ip_list.values())))
            request.meta['proxy'] = self.proxy.get('proxy')
            return request