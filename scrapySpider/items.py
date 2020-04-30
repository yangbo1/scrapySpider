# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    profile_image_url = scrapy.Field() # 头像
    description = scrapy.Field() # 描述
    follow_count = scrapy.Field() # 关注数
    followers_count = scrapy.Field() # 粉丝数
    gender = scrapy.Field() # 性别
    verified = scrapy.Field() # 认证
    verified_reason = scrapy.Field() # 认证原因
    verified_type = scrapy.Field() # 认证
    verified_type_ext = scrapy.Field() # 认证
    statuses_count = scrapy.Field() #
    mbrank = scrapy.Field() #
    mbtype = scrapy.Field() #
    close_blue_v = scrapy.Field() #

    pass
