# -*- coding: utf-8 -*-.
import os

import GetSetObj
from pyftpdlib.handlers import FTPHandler


class PrivateFTPHandler(FTPHandler):
    def on_connect(self):
        ftppanel = GetSetObj.get(3) 
        ftppanel.tbMessageAppend('客户端[' + self.remote_ip + ']已连接成功')

    def on_disconnect(self):
        ftppanel = GetSetObj.get(3)
        ftppanel.tbMessageAppend('客户端[' + self.remote_ip + ']已断开连接')

    def on_login(self, username):
        ftppanel = GetSetObj.get(3)
        ftppanel.tbMessageAppend('客户端用户[' + username + ']已登录')

    def on_logout(self, username):
        ftppanel = GetSetObj.get(3)
        ftppanel.tbMessageAppend('客户端用户[' + username + ']已退出')

    def on_file_sent(self, file):
        ftppanel = GetSetObj.get(3)
        ftppanel.tbMessageAppend('发送文件：' + file + '成功')

    def on_file_received(self, file):
        ftppanel = GetSetObj.get(3)
        ftppanel.tbMessageAppend('收到客户端文件：' + file)

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        # os.remove(file)
        pass
