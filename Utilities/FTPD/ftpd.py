# -*- coding: utf-8 -*-.
import logging
import os
import socket

from pyftpdlib import filesystems
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer
# 默认导入
from PyQt5.QtCore import QThread, pyqtSignal
from Utilities.FTPD.MyFTPHandler import PrivateFTPHandler


class PrivateFTP(QThread):
    ftpdSignal = pyqtSignal(str)

    def __init__(self):
        super(PrivateFTP, self).__init__()
        self.server = None
        # Instantiate FTP handler class
        self.ftphandler = PrivateFTPHandler

    def run(self):
       # Instantiate a dummy authorizer for managing 'virtual' users
        authorizer = DummyAuthorizer()

        # Define a new user having full r/w permissions and a read-only
        # anonymous user
        authorizer.add_user('U1', '12345', os.getcwd(), perm='elradfmwMT', msg_login='U1 Login Successful.', msg_quit='Goodbye U1.')
        authorizer.add_user('U2', '12345', os.getcwd(), perm='elradfmwMT', msg_login='U2 Login Successful.', msg_quit='Goodbye U2.')
        authorizer.add_user('U3', '12345', os.getcwd(), perm='elradfmwMT', msg_login='U3 Login Successful.', msg_quit='Goodbye U3.')
        authorizer.add_anonymous(os.getcwd())
        self.ftphandler.authorizer = authorizer
        # self.ftphandler.log_prefix = '[%(username)s] - @%(remote_ip)s'
        # Define a customized banner (string returned when client connects)
        # handler.banner = "PYFTPDLIB BASED FTPD READY."

        # Specify a masquerade address and the range of ports to use for
        # passive connections.  Decomment in case you're behind a NAT.
        # handler.masquerade_address = '151.25.42.11'
        # handler.passive_ports = range(60000, 65535)

        # log file
        logfile = os.path.join(os.getcwd(), 'pyftplog.log')
        logging.basicConfig(filename=logfile, level=logging.INFO, encoding='utf-8')

        # Instantiate FTP server class and listen on 0.0.0.0:2121
        name = socket.gethostname()
        ip = socket.gethostbyname(name)
        address = (ip, 21)
        try:
            self.server = FTPServer(address, self.ftphandler)
        except OSError:
            self.ftpdSignal.emit('该IP已经使用！')
            return
        # set a limit for connections
        self.server.max_cons = 5
        self.server.max_cons_per_ip = 1
        # # start ftp server
        self.server.serve_forever()
