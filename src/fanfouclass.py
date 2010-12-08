# - * - coding: UTF-8 - * -

import sys
import json
import urllib
import base64
import urllib2
import urllib2_file

# 饭否API地址
FANFOU_API = 'http://api2.fanfou.com/'
SOURCE = 'seviper'

# 定义错误
class TooLongStatusError(Exception): pass

class Fanfou:
    '''饭否接口类'''

    def __init__(self, username, password,
            source='api', user_agent='libfanfou'):
        key = 'Basic ' + \
                base64.b64encode('{0}:{1}'.format(username, password))
        opener = urllib2.build_opener()
        opener.addheaders = [
                ('Authorization', key),
                ('User-Agent', user_agent)
                ]
        self.__opener = opener
        self.source = source

    def open_req(self, req):
        code = 200
        content = ''
        try:
            content = self.__opener.open(req)
        except urllib2.HTTPError as e:
            code = e.code
        except:
            raise
        return (code, content)
    
    def verify(self):
        '''验证饭否用户名密码'''
        req = urllib2.Request(FANFOU_API + 'account/verify_credentials.json')
        code, content = self.open_req(req)
        return code != 401

    def update(self, text):
        '''发送消息到饭否'''
        # 如果是空消息则不发送
        text = text.strip()
        if not text:
            return True
        
        # 验证字数限制
        if len(text.decode('utf8')) > 140:
            raise StatusTooLongError()

        # 发送
        post_data = { 'status': text, 'source': SOURCE }
        post_data = urllib.urlencode(post_data)
        req = urllib2.Request(FANFOU_API + 'statuses/update.json', post_data)
        code, content = self.open_req(req)
        
        # 验证返回信息
        return code == 200

    def upload(self, image, text=None):
        '''上传图片到饭否'''
        # 准备数据
        post_data = { 'photo': open(image, 'rb'), 'source': SOURCE }
        if text:
            post_data['status'] = text

        # 验证字数限制
        if len(text.decode('utf8')) > 140:
            raise StatusTooLongError()
        
        # 发送
        req = urllib2.Request(FANFOU_API + 'photos/upload.json', post_data)
        print >>sys.stderr, '正在上传……'
        code, content = self.open_req(req)

        # 验证返回信息
        return code == 200

# vim: ts=4 sw=4 et
