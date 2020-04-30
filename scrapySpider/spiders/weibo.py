# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request

from scrapySpider.items import UserItem
from scrapySpider.utils.cache_utils import Cache
cache = Cache()

def parse_user(args):
    pass


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['m.weibo.cn']
    user_info_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={user_id}'
    fans = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{user_id}&since_id={index}'
    headers = {
        'Referer': 'https://m.weibo.cn/api/container/getIndex?type=uid&value={user_id}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    follows = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{user_id}&since_id={index}'
    # 鹿晗
    # start_users = ['1537790411', '5516714899']
    start_urls = ['https://m.weibo.cn/api/container/getIndex?type=uid&value=1537790411']
    # 蔡徐坤
    # start_urls = ['https://m.weibo.cn/api/container/getIndex?type=uid&value=1776448504']
    # def start_requests(self, response):
    #     for uid in self.start_users:
    #         yield Request(self.user_info_url.format(user_id=uid), callback=self.parse_user)

    user_cache = {}
    def parse(self, response):
        # self.logger.debug(response)
        result = json.loads(response.text)
        user_info = result.get('data').get('userInfo')
        user_item = UserItem()
        field_map = {
            'id': 'id',
                'name': 'screen_name',
                'profile_image_url': 'profile_image_url',
                'description': 'description',
                'follow_count': 'follow_count',
                'followers_count': 'followers_count',
                'gender': 'gender',
                'verified': 'verified',
                'verified_reason': 'verified_reason',
                'verified_type': 'verified_type',
                'verified_type_ext': 'verified_type_ext',
                'statuses_count': 'statuses_count',
                'mbrank': 'mbrank',
                'mbtype': 'mbtype',
                'close_blue_v': 'close_blue_v',
        }
        for k, v in field_map.items():
            user_item[k] = user_info.get(v)
        print(user_item['id'], user_item['name'])
        # if cache.hexists("WEIBO_USER", user_info.get('id')):
        #     print(user_item, '已存在')
        #     cache.incr("WEIBO_USER_REPEAT_COUNT")
        #     return
        i = cache.hset("WEIBO_USER", dict(user_item)['id'], json.dumps(dict(user_item), ensure_ascii=False))
        if i == 1:
            cache.incr("WEIBO_USER_COUNT")
        yield user_item
        # 用户id
        uid = user_info.get('id')

        fans_count = user_info.get('followers_count')
        # 只能查到250页 5000个粉丝
        for i in range(min(int(fans_count/20), 250)):
            yield Request(self.fans.format(user_id=uid, index=i), callback=self.parse_fans)

        follows_count = user_info.get('follow_count')
        #查关注
        for i in range(int(follows_count / 20)):
            yield Request(self.follows.format(user_id=uid, index=i), callback=self.parse_fans)

    def parse_fans(self, response):
        result = json.loads(response.text)
        if result.get('data').get('cards') is None:
            return
        cards = result.get('data').get('cards')
        users = cards[len(cards) - 1].get('card_group')
        for u in users:
            if u.get('user') is None:
                continue
            user_item = UserItem()
            field_map = {
                'id': 'id',
                'name': 'screen_name',
                'profile_image_url': 'profile_image_url',
                'description': 'description',
                'follow_count': 'follow_count',
                'followers_count': 'followers_count',
                'gender': 'gender',
                'verified': 'verified',
                'verified_reason': 'verified_reason',
                'verified_type': 'verified_type',
                'verified_type_ext': 'verified_type_ext',
                'statuses_count': 'statuses_count',
                'mbrank': 'mbrank',
                'mbtype': 'mbtype',
                'close_blue_v': 'close_blue_v',
            }
            for k, v in field_map.items():
                user_item[k] = u.get('user').get(v)
            print(user_item['id'], user_item['name'])
            if cache.hexists("WEIBO_USER", dict(user_item)['id']):
                print(user_item['name'], '已存在')
                cache.incr("WEIBO_USER_REPEAT_COUNT")
                continue
            i = cache.hset("WEIBO_USER", dict(user_item)['id'], json.dumps(dict(user_item), ensure_ascii=False))
            if i == 1:
                cache.incr("WEIBO_USER_COUNT")
            yield user_item
            uid = u.get('user').get('id')
            self.user_cache[uid] = 0
            yield Request(self.user_info_url.format(user_id=uid), callback=self.parse)