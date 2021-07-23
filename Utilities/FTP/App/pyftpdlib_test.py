# -*- coding: utf-8 -*-
import logging
import os
import socket

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer
from pyftpdlib import filesystems

def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Define a new user having full r/w permissions and a read-only
    # anonymous user
    authorizer.add_user('U1', '12345', '.', perm='elradfmwMT', msg_login='Login Successful.', msg_quit='Goodbye.')
    authorizer.add_user('U2', '12345', '.', perm='elradfmwMT', msg_login='Login Successful.', msg_quit='Goodbye.')
    authorizer.add_user('U3', '12345', '.', perm='elradfmwMT', msg_login='Login Successful.', msg_quit='Goodbye.')
    authorizer.add_anonymous(os.getcwd())

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.log_prefix = '[%(username)s]@%(remote_ip)s'
    # Define a customized banner (string returned when client connects)
    handler.banner = 'pyftpdlib based ftpd ready.'
    # Define a customized encode
    handler.encoding = 'gbk'

    # Specify a masquerade address and the range of ports to use for
    # passive connections.  Decomment in case you're behind a NAT.
    #handler.masquerade_address = '151.25.42.11'
    #handler.passive_ports = range(60000, 65535)

    # log
    cwd = os.getcwd()
    logfile = os.path.join(cwd, 'pyftplog.log')
    logging.basicConfig(filename=logfile, level=logging.DEBUG)

    # Instantiate FTP server class and listen on 0.0.0.0:2121
    name = socket.gethostname()
    ip = socket.gethostbyname(name)
    address = (ip, 21)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()


    handler.push("")

if __name__ == '__main__':
    main()
