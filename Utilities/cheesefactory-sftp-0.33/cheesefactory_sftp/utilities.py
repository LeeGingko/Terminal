# cheesefactory-sftp/utilities.py

import fnmatch
import logging
import paramiko
import re
import warnings

from .exceptions import FileSizeMismatchError
from .connection import CfSftpConnection
from pathlib import Path
from stat import S_IMODE, S_ISDIR, S_ISREG
from typing import List

logger = logging.getLogger(__name__)


class CfSftpUtilities(CfSftpConnection):
    """Basic utilities for use with an SFTP connection. Does not include any file transfer methods.

    Notes:
        CfSftp --> CfSftpGet ----> CfSftpTransfer --> CfSftpUtilities --> CfSftpConnection
               |-> CfSftpPut ->|
    """

    def __init__(self):
        super().__init__()

    #
    # PUBLIC METHODS
    #

    def chdir(self, path: str):
        """Change current remote directory.

        Args:
            path: New remote directory.
        """
        self.sftp.chdir(path=path)

    def chmod(self, path: str, mode: int):
        """Change the permissions of a remote file.

        Args:
            path: Remote file path.
            mode: Unix-style permission (e.g. 0644)
        """
        mode = self.octal_to_decimal(mode)
        self.sftp.chmod(path=path, mode=mode)

    def chown(self, path: str, uid: int, gid: int):
        """Change the owner and group of a remote file.

        Args:
            path: Remote file path.
            uid: New user ID.
            gid: New group ID.
        """
        self.sftp.chown(path=path, uid=uid, gid=gid)

    def cwd(self) -> str:
        """Return the current remote directory.

        Returns:
            Current remote working directory.
        """
        # If self.chdir() never set a directory, then paramiko returns None.
        cwd = self.sftp.getcwd()

        if cwd is None:
            return '/'
        else:
            return cwd

    def delete(self, path):
        """Alias for remove_file().

        *** DEPRECATED ***

        Args:
            path: Relative or absolute path of file to delete.
        """
        self.deprecation('CfSftp.delete() is DEPRECATED and will be removed in a future release.')
        self.remove_file(path=path)

    @staticmethod
    def deprecation(message: str):
        warnings.warn(message, DeprecationWarning)

    def exists(self, path: str) -> bool:
        """Does a remote file or directory exist?

        Args:
            path: File or directory to test.
        Returns:
            True if file or directory exists. False if it does not.
        """
        try:
            self.sftp.stat(path)
        except FileNotFoundError:
            return False
        else:
            return True

    def find_files_by_glob(self, glob_filter: str = '*', recursive_search: bool = False,
                           remote_dir: str = '.') -> List[str]:
        """Create a list of remote files to download based on glob, then download.

        Creates a recursive list of files and directories in remote_dir and filters by glob_filter.

        Args:
            glob_filter:
            recursive_search:
            remote_dir:
        """
        if not isinstance(glob_filter, str):
            raise ValueError('glob_filter != str type')
        if not isinstance(recursive_search, bool):
            raise ValueError('recursive_search != bool type')
        if not isinstance(remote_dir, str):
            raise ValueError('remote_dir != str type')

        # Make file list
        try:
            files = self.list_dir(remote_dir, recursive=recursive_search)
            logger.debug(f'Unfiltered remote files: {str(files)}')
        except FileNotFoundError as e:
            raise FileNotFoundError(f'remote_dir does not exist on remote server ({e})')

        # Identify items that do not match the glob_filter
        hit_list = []  # Files to remove from list
        for file in files:
            if fnmatch.fnmatch(file, glob_filter) is False:
                hit_list.append(file)
        # Remove the unmatched files from the file list
        for hit in hit_list:
            files.remove(hit)

        if len(files) == 0:
            logger.debug(f'No files found after filter ({glob_filter}): {str(files)}')

        return files

    def find_files_by_regex(self, regex_filter: str = r'^', remote_dir: str = '.') -> List[str]:
        """Create a list of remote files to download based on a regex, then download.

        Creates a recursive list of files and directories in remote_dir and filters using re.search().

        Args:
            regex_filter:
            remote_dir: Remote/source path and filename.
        """
        if not isinstance(regex_filter, str):
            raise ValueError('regex_filter != str type')
        if not isinstance(remote_dir, str):
            raise ValueError('remote_dir != str type')

        # Make file list
        try:
            files = self.list_dir(remote_dir, recursive=True)
            logger.debug(f'Unfiltered remote files: {str(files)}')
        except FileNotFoundError as e:
            raise FileNotFoundError(f'remote_dir does not exist on remote server ({e})')

        # Identify items that do not match the glob_filter
        hit_list = []  # Files to remove from list

        try:
            regex_object = re.compile(regex_filter)
        except re.error as e:
            logger.debug(f'Bad regex ({regex_filter}): {str(e)}')
            raise ValueError(f'Bad regex pattern ({regex_filter}): {str(e)}')

        for file in files:
            result = regex_object.search(file)
            if result is None:
                hit_list.append(file)

        # Remove the unmatched files from the file list
        for hit in hit_list:
            files.remove(hit)

        if len(files) == 0:
            logger.debug(f'No files found after filter ({regex_filter}): {str(files)}')

        return files

    def is_dir(self, path) -> bool:
        """Is the current remote path a directory?

        Args:
            path: The path to test.
        Returns:
            True if it is, False if it ain't.
        """
        try:
            result = S_ISDIR(self.sftp.stat(path).st_mode)
        except IOError:  # No such path
            result = False
        return result

    def is_file(self, path: str):
        """Is the current remote path a file?

        Args:
            path: The path to test.
        Returns:
            True if the path is a file. False if it is not.
        """
        try:
            result = S_ISREG(self.sftp.stat(path).st_mode)
        except IOError:  # no such path
            result = False
        return result

    def list_dir(self, path: str = '.', recursive: bool = False) -> List[str]:
        """Return a list of remote directory contents (without . and ..)

        Args:
            path: Remote path.
            recursive: Include contents of sub-directories in output?
        Returns:
            A list of directory contents.
        """
        dir_list = []
        if recursive is False:
            for file in self.sftp.listdir(path):
                dir_list.append(f'{path}/{file}')
        else:
            def dig(dig_path):
                dig_list = self.sftp.listdir(dig_path)
                for item in dig_list:
                    item = f'{dig_path}/{item}'
                    dir_list.append(item)  # Prepend the file/dir name with the dir
                    logger.debug(f"stat'ing {item}")
                    if S_ISDIR(self.sftp.stat(item).st_mode):
                        dig(item)

            dig(path)
        return dir_list

    def list_files(self, remote_directory: str = '/'):
        """Return a list of remote directory contents (without . and ..)

        *** DEPRECATED ***

        Args:
            remote_directory: The remote path to list.
        """
        self.deprecation('CfSftp.list_files() is DEPRECATED and will be removed in a future release.')
        self.list_dir(path=remote_directory)

    def mkdir(self, path: str, mode: int = 755):
        """Create a remote directory.

        Args:
            path: Name of the folder to create.
            mode: Posix-style permissions for the folder. Given in octal (without preceding 0)
        """
        mode = self.octal_to_decimal(mode)
        self.sftp.mkdir(path=path, mode=mode)

    @staticmethod
    def octal_to_decimal(number: int) -> int:
        """Convert an octal number (given as int) to a decimal.

        Args:
            number: Octal number (as an int).
        Returns:
            Converted number.
        """
        return int(str(number), 8)

    def remove(self, path):
        """Delete a remote file or directory.

        Args:
            path: Relative or absolute path of file or directory to delete.
        Raises:
            IOError: if path is neither directory nor file.
        """
        if self.is_dir(path):
            self.remove_dir(path=path)
        elif self.is_file(path):
            self.remove_file(path=path)
        else:
            raise IOError(f'Attempting to remove unknown file type: {path}')

    def remove_dir(self, path):
        """Delete a remote file or directory.

        Args:
            path: Relative or absolute path of directory to delete.
        """
        self.sftp.rmdir(path=path)

    def remove_file(self, path: str, missing_ok: bool = False):
        """Delete a remote file.

        Args:
            path: Relative or absolute path of file to delete.
            missing_ok: Do not raise an error if the file exists?
        """
        try:
            self.sftp.remove(path=path)
        except FileNotFoundError:
            if missing_ok is True:
                return
            else:
                raise

    def rename(self, old_path, new_path):
        """Rename a remote file or folder.

        Args:
            old_path: Existing name of file or directory.
            new_path: New name for the file or directory. Must not already exist.
        """
        try:
            self.sftp.rename(oldpath=old_path, newpath=new_path)
        except IOError:
            raise IOError('IOError: Perhaps the new_path already exists?')

    def size_match(self, local_path: str, remote_path: str, remote_size: int = None) -> bool:
        """Determine if the sizes of a remote and a local file match.

        Args:
            local_path: Local file.
            remote_path: Remote file.
            remote_size: Remote file size. If None, do a stat and figure it out.
        Returns:
            True, if match. False, if no match.
        """
        # TODO: Make it clearer that size match can be against a remote file or given size.
        if remote_size is None:
            remote_size = self.sftp.stat(remote_path).st_size

        local_size = Path(local_path).stat().st_size
        logger.debug(f'local_size: {local_size} <-> remote_size: {remote_size}')
        if local_size != remote_size:
            return False
        else:
            return True

    @staticmethod
    def st_mode_to_octal(val: int) -> int:
        """SFTAttributes st_mode returns an stat type that shows more than what can be set.  Trim off those bits and
        convert to an int representation. If you want an object that was `chmod 711` to return a value of 711, use this
        function.

        Args:
            val: The value of an st_mode attr returned by SFTPAttributes. Must be at least 3 digits.

        Returns:
            An integer representation of octal mode.
        """
        return int(str(oct(S_IMODE(val)))[-3:])

    def stat(self, path: str) -> paramiko.SFTPAttributes():
        """Retrieve information about a remote file. Mimics Python's os.stat structure.

        Supported fields: st_mode, st_size, st_uid, st_gid, st_atime, and st_mtime.

        Args:
            path: The filename to stat.
        Returns:
            Attributes about the given file.
        """
        return self.sftp.stat(path=path)
