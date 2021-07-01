# cheesefactory-sftp/get.py

import logging
from typing import List
from .transfer import CfSftpTransfer

logger = logging.getLogger(__name__)


class CfSftpGet(CfSftpTransfer):
    """GET-related attributes and methods.

    Notes:
        CfSftp --> CfSftpGet ----> CfSftpTransfer --> CfSftpUtilities --> CfSftpConnection
               |-> CfSftpPut ->|
    """
    def __init__(self):
        super().__init__()

    #
    # PUBLIC METHODS
    #

    def get(self, local_path: str = None, log_checksum: bool = False, preserve_mtime: bool = True,
            remote_path: str = None, remove_source: bool = False, rename_local: str = None,
            rename_remote: str = None, replace_local: dict = None,
            replace_remote: dict = None) -> str:
        """Download a single, remote file from the SFTP server to the local host.

        Args:
            local_path: Local/destination path and filename.
            log_checksum: Calculate file SHA256 checksum and log resulting value.
            preserve_mtime: Keep modification time of source file.
            remote_path: Remote/source path and filename.
            remove_source: Remove the remote source file.
            rename_local: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            rename_remote: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            replace_local: Use Python .replace() on local_path string. A dictionary--the keysa are the "old"
                           part of the string to match. The values are the "new" string to replace it with.
            replace_remote: Use Python .replace() on remote_path string. A dictionary--the keys are the "old"
                           part of the string to match. The values are the "new" string to replace it with.

        Returns:
            Final destination file path (after any name changes).
        """
        file = self._transfer(
            action='GET', local_path=local_path,
            log_checksum=log_checksum, preserve_mtime=preserve_mtime, remote_path=remote_path,
            remove_source=remove_source, rename_local=rename_local, rename_remote=rename_remote,
            replace_local=replace_local, replace_remote=replace_remote
        )
        return file

    def get_by_glob(self, flat_dir: bool = False,
                    glob_filter: str = '*', local_base_dir: str = '.', log_checksum: bool = False,
                    preserve_mtime: bool = True, recursive_search: bool = False, remote_dir: str = '.',
                    remove_source: bool = False, rename_local: str = None,
                    rename_remote: str = None, replace_local: dict = None,
                    replace_remote: dict = None) -> List[str]:
        """Create a list of remote files to download based on glob, then download.

        Creates a recursive list of files and directories in remote_dir and filters by glob_filter.

        Args:
            flat_dir: Do not recreate directory structure in local_base_dir.
            glob_filter:
            log_checksum: Calculate file SHA256 checksum and log resulting value.
            local_base_dir: Local base directory for downloaded files. See flat_dir.
            preserve_mtime: Keep modification time of source file.
            recursive_search:
            remote_dir:
            remove_source: Remove the remote source file.
            rename_local: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            rename_remote: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            replace_local: Use Python .replace() on local_path string. A dictionary--the keysa are the "old"
                           part of the string to match. The values are the "new" string to replace it with.
            replace_remote: Use Python .replace() on remote_path string. A dictionary--the keys are the "old"
                           part of the string to match. The values are the "new" string to replace it with.

        Returns:
            List of final destination file paths (after any name changes).
        """
        files = self._transfer_by_glob(
            action='GET', base_dir=local_base_dir,
            flat_dir=flat_dir, glob_filter=glob_filter, log_checksum=log_checksum, preserve_mtime=preserve_mtime,
            recursive_search=recursive_search, remove_source=remove_source, rename_local=rename_local,
            rename_remote=rename_remote, source_dir=remote_dir,
            replace_local=replace_local, replace_remote=replace_remote
        )
        return files

    def get_by_list(self, flat_dir: bool = False,
                    local_base_dir: str = '.', log_checksum: bool = False, preserve_mtime: bool = True,
                    remote_files: List[str] = None, remove_source: bool = False, rename_local: str = None,
                    rename_remote: str = None, replace_local: dict = None,
                    replace_remote: dict = None) -> List[str]:
        """Download a list of files from the SFTP server to the local host.

        Args:
            flat_dir: Do not recreate directory structure in local_base_dir.
            log_checksum: Calculate file SHA256 checksum and log resulting value.
            local_base_dir: Local base directory for downloaded files. See flat_dir.
            preserve_mtime: Keep modification time of source file.
            remote_files: Remote/source path and filename.
            remove_source: Remove the remote source file.
            rename_local: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            rename_remote: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            replace_local: Use Python .replace() on local_path string. A dictionary--the keysa are the "old"
                           part of the string to match. The values are the "new" string to replace it with.
            replace_remote: Use Python .replace() on remote_path string. A dictionary--the keys are the "old"
                           part of the string to match. The values are the "new" string to replace it with.

        Returns:
            List of final destination file paths (after any name changes).
        """
        files = self._transfer_by_list(
            action='GET', base_dir=local_base_dir,
            file_list=remote_files, flat_dir=flat_dir, log_checksum=log_checksum, preserve_mtime=preserve_mtime,
            remove_source=remove_source, rename_local=rename_local, rename_remote=rename_remote,
            replace_local=replace_local, replace_remote=replace_remote
        )
        return files

    def get_files_by_regex(self, flat_dir: bool = False,
                           local_base_dir: str = '.', log_checksum: bool = False, preserve_mtime: bool = True,
                           regex_filter: str = r'^', remote_dir: str = '.', remove_source: bool = False,
                           rename_local: str = None,
                           rename_remote: str = None, replace_local: dict = None,
                           replace_remote: dict = None) -> List[str]:
        """Create a list of remote files to download based on a regex, then download.

        Creates a recursive list of files and directories in remote_dir and filters using re.search().

        Args:
            flat_dir:
            log_checksum: Calculate file SHA256 checksum and log resulting value.
            local_base_dir:
            preserve_mtime: Keep modification time of source file.
            regex_filter:
            remote_dir: Remote/source path and filename.
            remove_source:
            rename_local: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            rename_remote: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            replace_local: Use Python .replace() on local_path string. A dictionary--the keysa are the "old"
                           part of the string to match. The values are the "new" string to replace it with.
            replace_remote: Use Python .replace() on remote_path string. A dictionary--the keys are the "old"
                           part of the string to match. The values are the "new" string to replace it with.

        Returns:
            List of final destination file paths (after any name changes).
        """
        files = self._transfer_by_regex(
            action='GET', base_dir=local_base_dir,
            flat_dir=flat_dir, log_checksum=log_checksum, preserve_mtime=preserve_mtime, regex_filter=regex_filter,
            source_dir=remote_dir, remove_source=remove_source, rename_local=rename_local, rename_remote=rename_remote,
            replace_local=replace_local, replace_remote=replace_remote
        )
        return files
