#!/usr/bin/env python
# - * - coding: UTF-8 - * -

import sys
import getpass
import keyring
import mimetypes
import ConfigParser

from os import path
from termcolor import colored

from fanfouclass import Fanfou, TooLongStatusError

CONFIG_FILE = path.join(path.expanduser('~'), '.seviper')
KEYRING_SERVICE = 'seviper'
VERSION = '0.1'
SOURCE = 'seviper'
USER_AGENT = 'seviper {0}'.format(VERSION)

def create_config():
    '''创建配置文件'''
    # 获取信息
    try:
        username = raw_input('用户名：')
        password = getpass.getpass('密码：')
    except KeyboardInterrupt:
        print
        exit(1)

    # 保存密码
    keyring.set_password(KEYRING_SERVICE, username, password)
    
    # 保存配置文件
    config = ConfigParser.RawConfigParser()
    config.add_section('Auth')
    config.set('Auth', 'username', username)
    with open(CONFIG_FILE, 'wb') as f:
        config.write(f)

def get_auth_info():
    '''获取饭否登入的验证字符串'''
    # 读取用户名
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE)
    try:
        username = config.get('Auth', 'username')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return False

    # 获得密码
    password = keyring.get_password(KEYRING_SERVICE, username)
    if password == None:
        return False
    
    # 获得用户名密码
    return username, password

def get_filetype(filename):
    '''获取文件的类型'''
    file_type = mimetypes.guess_type(filename)
    if not file_type or not file_type[0]:
        return None
    return file_type[0].split('/')[0]

def print_usage():
    '''打印用法信息'''
    print '用法：{0} 消息'.format(sys.argv[0])
    print '  或：{0} 图片 [消息]'.format(sys.argv[0])
    print '  或：{0} 消息文件'.format(sys.argv[0])
    print '在饭否上发送消息或上传图片'
    print '对于最后一种，消息文件必须为文本文件，'
    print '文本文件中的每一行将作为一个消息被发送'
    print '如果消息文件为“-”，则从标准输入中读取'

def print_error_notice(*msgs):
    '''输出错误信息'''
    print >>sys.stderr, colored(msgs[0], 'red', attrs=['bold']),
    for msg in msgs:
        print >>sys.stderr, msg,

def print_success_notice(*msgs):
    '''输出成功信息'''
    print >>sys.stderr, colored(msgs[0], 'green', attrs=['bold']),
    for msg in msgs[1:]:
        print >>sys.stderr, msg,

def main():
    # 验证配置文件
    if not path.exists(CONFIG_FILE) or not get_auth_info():
        print >>sys.stderr, '请输入饭否的注册信息'
        create_config()

    # 验证用户名密码
    while True:
        username, password = get_auth_info()
        fanfou = Fanfou(username, password)
        if fanfou.verify():
            break
        print_error_notice('用户名或密码错误，请重新输入')
        create_config()

    def send_and_notice(func, *args):
        try:
            ret = func(*args)
        except TooLongStatusError:
            print_error_notice('错误', '消息超过140字')
            return False
        else:
            if ret:
                print_success_notice('发送成功', *args)
                return True
            else:
                print_error_notice('发送失败', *args)
                return False

    def send_lines_in_file(fp):
        ret = True
        for line in fp:
            ret = send_and_notice(fanfou.update, line)
            if not ret:
                ret = False
        return ret

    exit_code = 0
    # 获取参数
    if len(sys.argv) == 1:
        # 输出用法
        print_usage()
    else:
        # 根据参数发送
        arg1 = sys.argv[1]
        if arg1 == '-':
            ret = send_lines_in_file(sys.stdin)
            if not ret:
                exit_code = 1
        elif path.exists(arg1):
            file_type = get_filetype(arg1)
            if file_type == 'image':
                # 上传图片
                ret = send_and_notice(fanfou.upload,
                        arg1, ' '.join(sys.argv[2:]))
                if not ret:
                    exit_code = 1
            elif file_type == 'text':
                # 消息文件
                with open(arg1, 'r') as f:
                    ret = send_lines_in_file(f)
                    if not ret:
                        exit_code = 1
            else:
                # 错误
                print_error_notice('错误', '未知的文件类型', arg1)
                exit_code = 1
        else:
            # 发送单条消息
            ret = send_and_notice(fanfou.update, ' '.join(sys.argv[1:]))
            if not ret:
                exit_code = 1
    
    # 返回
    return exit_code

if __name__ == '__main__':
    exit(main())

# vim: ts=4 sw=4 et
