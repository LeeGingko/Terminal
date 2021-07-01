# connection.py

import logging
import paramiko
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


class CfSftpConnection:
    """SFTP connection attributes and methods. Based on Paramiko.

    This is the base class which includes the connection and "utility" methods. Does not include GET or PUT methods--
    anything that moves the file.

    Attributes:
        host: Remote SFTP server hostname or IP.
        port: Remote SFTP server port.
        user: Account username on remote SFTP server.
        password: Account password on remote SFTP server.
        key_path: Path to private key file.
        key_password: Password for encrypted private key.

    Notes:
        CfSftp --> CfSftpGet ----> CfSftpTransfer --> CfSftpUtilities --> CfSftpConnection
               |-> CfSftpPut ->|
    """
    def __init__(self):

        self.host: Union[str, None] = None
        self.port: Union[int, None] = None
        self.user: Union[str, None] = None
        self.password: Union[str, None] = None
        self.key_path: Union[str, None] = None
        self.key_password: Union[str, None] = None

        self._private_key = None
        self._transport = None   # Transport connection
        self.sftp: Union[paramiko.SFTPClient, None] = None   # SFTP over transport connection

        self.log = {}  # A dictionary of metrics

    #
    # PROPERTIES
    #

    @property
    def status(self):
        """Retrieve connection status.

        status() for cheesefactory programs should return True/False along with any reasons.

        Returns:
            True, if live. False, if not live.
            Additional info, such as error codes. (not implemented)
        """
        session_open = self._transport.is_active()
        session_authenticated = self._transport.is_authenticated()

        if session_open and session_authenticated:
            return True, 'Transport open and authenticated.'
        if session_open and not session_authenticated:
            return False, 'Transport open. Not authenticated.'
        if not session_open:
            return False, 'Transport closed. Not authenticated.'

    #
    # CLASS METHODS
    #

    @classmethod
    def connect(cls, host: str = '127.0.0.1', port: Union[str, int] = '22', user: str = None, password: str = None,
                key_path: str = None, key_password: str = None):
        """Connect to a remote SFTP server.

        Args:
            host: Remote SFTP server hostname or IP.
            port: Remote SFTP server port.
            user: Account username on remote SFTP server.
            password: Account password on remote SFTP server.
            key_path: Path to private key file.
            key_password: Password for encrypted private key.
        """
        connection = cls()

        connection.host = host
        connection.port = port
        connection.user = user
        connection.password = password
        connection.key_path = key_path
        connection.key_password = key_password

        connection.log['sftp_connection_ok'] = False
        connection.log['sftp_host'] = host
        connection.log['sftp_note'] = None
        connection.log['sftp_password'] = password
        connection.log['sftp_port'] = port
        connection.log['sftp_transfers'] = []
        connection.log['sftp_user'] = user

        try:
            connection._get_key()
            connection._start_transport()
            connection._start_sftp()
        except Exception as e:
            connection.log['sftp_connection_note'] = str(e)
            raise
        else:
            connection.log['sftp_connection_ok'] = True
            logger.info(f'SFTP connection established to: {host}')
            return connection

    #
    # PROTECTED METHODS
    #

    def _get_key(self):
        """If key is valid, import it."""
        if self.key_path is not None:
            if not Path(self.key_path).exists():
                raise ValueError(f'key_path is not a valid file path: {self.key_path}')

            try:  # try rsa
                self._private_key = paramiko.RSAKey.from_private_key_file(
                    filename=self.key_path,
                    password=self.key_password
                )
            except paramiko.SSHException:  # if it fails, try dsa
                self._private_key = paramiko.DSSKey.from_private_key_file(
                    filename=self.key_path,
                    password=self.key_password
                )

    def _start_transport(self):
        """Start transport session."""
        try:
            self._transport = paramiko.transport.Transport((self.host, int(self.port)))
            self._transport.connect(None, self.user, self.password, self._private_key)
        except Exception as e:
            logger.critical(f'Problem starting transport: {e}')
            exit(1)

    def _start_sftp(self):
        """Start SFTP over transport."""
        try:
            self.sftp = paramiko.SFTPClient.from_transport(self._transport)
            # if self.accept_unknown_host_key is True:
            #    self.sftp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        except Exception as e:
            logger.critical(f'Problem starting SFTPClient session: {e}')
            self._transport.close()
            exit(1)

    #
    # PUBLIC METHODS
    #

    def close(self):
        """Close the SFTP session and transport channel."""
        try:
            self.sftp.close()
        except AttributeError:
            pass
