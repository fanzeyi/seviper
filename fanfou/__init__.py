# - * - coding: UTF-8 - * -

import sys
import json
import urllib
import base64
import urllib2
import urllib2_file

# 饭否API地址
FANFOU_API = 'http://api2.fanfou.com/'

# 定义错误
class TooLongStatusError(Exception): pass

class Fanfou:
    '''饭否接口类'''

    def __init__(self, username, password,
            source='api', user_agent='python-fanfou'):
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
        # XXX 有问题：code无法正常捕获
        try:
            content = self.__opener.open(req).read()
        except urllib2.HTTPError as e:
            code = e.code
        return (code, content)
    
    def verify(self):
        '''验证饭否用户名密码'''
        req = urllib2.Request(FANFOU_API + 'account/verify_credentials.json')
        code, content = self.open_req(req)
        return code != 401

    def get_public_timeline(self, count=20, html=True):
        '''现实随便看看的消息
        
        count       为返回的数量，有效值为 1-20，默认值为 20
        html        为 True 时对@识别，并返回识别@后的 html 代码
        '''
        
        query_data = {}
        if count != 20: query_data['count'] = count
        if html:        query_data['format'] = 'html'

        query_string = urllib.urlencode(query_data)
        req = urllib2.Request(FANFOU_API + 'statuses/public_timeline.json' +
                              '?' + query_string)
        code, condent = self.open_req(req)
        if code != 200:
            raise Exception('Error: {0}'.format(code))

        return json.loads(content)

    def get_friends_timeline(self, id='', count=20, html=True,
                             since_id='', max_id='', page=1):
        '''获取用户和好友的消息

        id          为用户 ID ，没有此参数时返回用户和好用的所有消息。
        count       为返回的数量，有效值为 1-20，默认值为 20
        html        为 True 时对@识别，并返回识别@后的 html 代码
        since_id    仅返回比此 ID 大的消息
        max_id      仅返回 ID 小于等于此 ID 的消息
        page        页码，从 1 开始
        '''
        # 构造查询数据
        query_data = {}
        if id:          query_data['id'] = id
        if count != 20: query_data['count'] = count
        if html:        query_data['format'] = 'html'
        if since_id:    query_data['since_id'] = since_id
        if max_id:      query_data['max_id'] = max_id
        if page > 1:    query_data['page'] = page

        # 执行查询
        query_string = urllib.urlencode(query_data)
        req = urllib2.Request(FANFOU_API + 'statuses/friends_timeline.json' +
                              '?' + query_string)
        code, content = self.open_req(req)
        if code != 200:
            raise Exception('Error: {0}'.format(code))
        
        # 解析
        data = json.loads(content)
        return data

    def get_user_timeline(self, id='', count=20, html=True,
                          since_id='', max_id='', page=1):
        '''获取用户的消息

        id          为用户 ID ，没有此参数时获取当前登入的用户的 timeline
        count       为返回的数量，有效值为 1-20，默认值为 20
        html        为 True 时对@识别，并返回识别@后的 html 代码
        since_id    仅返回比此 ID 大的消息
        max_id      仅返回 ID 小于等于此 ID 的消息
        page        页码，从 1 开始
        '''

        # 构造查询数据
        query_data = {}
        if id:          query_data['id'] = id
        if count != 20: query_data['count'] = count
        if html:        query_data['format'] = 'html'
        if since_id:    query_data['since_id'] = since_id
        if max_id:      query_data['max_id'] = max_id
        if page > 1:    query_data['page'] = page

        # 执行查询
        query_string = urllib.urlencode(query_data)
        req = urllib2.Request(FANFOU_API + 'statuses/user_timeline.json' +
                              '?' + query_string)
        code, content = self.open_req(req)
        if code != 200:
            raise Exception('Error: {0}'.format(code))
        
        # 解析
        return json.loads(content)

    def get_status(self, id):
        '''获取指定消息
        
        id          消息的ID
        '''
    
        req = urllib2.Request(FANFOU_API +
                              'statuses/show/{0}.json'.format(id))
        code, content = self.open_req(req)
        if code != 200:
            raise Exception('Error: {0}'.format(code))
    
        return json.loads(content)

    def get_replies(self, count=20, html=True,
                    since_id='', max_id='', page=1):
        '''获取给当前用户的消息

        count       为返回的数量，有效值为 1-20，默认值为 20
        html        为 True 时对@识别，并返回识别@后的 html 代码
        since_id    仅返回比此 ID 大的消息
        max_id      仅返回 ID 小于等于此 ID 的消息
        page        页码，从 1 开始
        '''

        # 构造查询数据
        query_data = {}
        if count != 20: query_data['count'] = count
        if html:        query_data['format'] = 'html'
        if since_id:    query_data['since_id'] = since_id
        if max_id:      query_data['max_id'] = max_id
        if page > 1:    query_data['page'] = page

        # 执行查询
        query_string = urllib.urlencode(query_data)
        req = urllib2.Request(FANFOU_API + 'statuses/replies.json' +
                              '?' + query_string)
        code, content = self.open_req(req)
        if code != 200:
            raise Exception('Error: {0}'.format(code))
        
        # 解析
        return json.loads(content)

    def update(self, text):
        '''发送消息到饭否
        
        text        要发送的消息'''

        # 如果是空消息则不发送
        text = text.strip()
        if not text:
            return True
        
        # 验证字数限制
        if len(text.decode('utf8')) > 140:
            raise TooLongStatusError()

        # 发送
        post_data = { 'status': text, 'source': self.source }
        post_data = urllib.urlencode(post_data)
        req = urllib2.Request(FANFOU_API + 'statuses/update.json', post_data)
        code, content = self.open_req(req)
        
        # 验证返回信息
        return code == 200

    def destory(self, id):
        '''删除消息
        
        id          消息 ID'''

        # 删除
        post_data = urllib.urlencode({ 'id': id })
        req = urllib2.Request(FANFOU_API + 'statuses/destroy.json', post_data)
        code, content = self.open_req(req)

        # 返回
        return code == 200

    def upload(self, image, text=None):
        '''上传图片到饭否
        
        image       图片地址'''

        # 准备数据
        post_data = { 'photo': open(image, 'rb'), 'source': self.source }
        if text:
            post_data['status'] = text

        # 验证字数限制
        if len(text.decode('utf8')) > 140:
            raise TooLongStatusError()
        
        # 发送
        req = urllib2.Request(FANFOU_API + 'photos/upload.json', post_data)
        print >>sys.stderr, '正在上传……'
        code, content = self.open_req(req)

        # 验证返回信息
        return code == 200

    def get_friends(self, id='', page=1):
        '''获取好友列表
    
        id          用户 ID，没有此参数返回当前用户好友列表
        page        页码，从 1 开始
        '''

        # 构造查询数据
        query_data = {}
        if id:          query_data['id'] = id
        if page > 1:    query_data['page'] = page

        # 执行查询
        query_string = urllib.urlencode(query_data)
        req = urllib2.Request(FANFOU_API + 'users/friends.json' +
                              '?' + query_string)
        code, content = self.open_req(req)
        if code != 200:
            raise Exception('Error: {0}'.format(code))
        
        # 解析
        return json.loads(content)
        
    def get_followers(self, id='', page=1):
        '''获取关注者列表

        id          用户 ID，没有此参数返回当前用户关注者列表
        page        页码，从 1 开始
        '''

        # 构造查询数据
        query_data = {}
        if id:          query_data['id'] = id
        if page > 1:    query_data['page'] = page

        # 执行查询
        query_string = urllib.urlencode(query_data)
        req = urllib2.Request(FANFOU_API + 'users/followers.json' +
                              '?' + query_string)
        code, content = self.open_req(req)
        if code != 200:
            raise Exception('Error: {0}'.format(code))
        
        # 解析
        return json.loads(content)

    def get_show(self, id=''):
        '''获取用户详细信息
    
        id          用户 ID，没有此参数返回当前用户
        '''

        query_string = urllib.urlencode({ 'id': id }) if id else ''
        req = urllib2.Request(FANFOU_API + 'users/show.json' +
                              '?' + query_string)
        code, content = self.open_req(req)
        if code != 200:
            raise Exception('Error: {0}'.format(code))
        
        return json.loads(content)

# vim: ts=4 sw=4 et
