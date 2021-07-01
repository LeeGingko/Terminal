# cheesefactory-sftp/__init__.py

import logging
from .get import CfSftpGet
from .put import CfSftpPut


logger = logging.getLogger(__name__)


class CfSftp(CfSftpGet, CfSftpPut):
    """A beautiful SFTP wrapper for Paramiko."""
    def __init__(self):
        super().__init__()
