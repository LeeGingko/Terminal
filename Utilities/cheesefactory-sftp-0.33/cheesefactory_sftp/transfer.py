# cheesefactory-sftp/transfer.py

import glob
import hashlib
import logging
import os
import re
from pathlib import Path
from typing import List

from .exceptions import BadListValueError
from .utilities import CfSftpUtilities

logger = logging.getLogger(__name__)


class CfSftpTransfer(CfSftpUtilities):
    """File transfer and logging attributes and methods shared by CfSftpGet() and CfSftpPut().

    Notes:
            CfSftp --> CfSftpGet ----> CfSftpTransfer --> CfSftpUtilities --> CfSftpConnection
                   |-> CfSftpPut ->|
    """
    def __init__(self):
        super().__init__()

        # Counters used for status messages and logging.
        self._new_file_count = 0
        self._new_dir_count = 0
        self._existing_file_count = 0
        self._existing_dir_count = 0
        self._regex_skip_count = 0

    #
    # PROTECTED METHODS
    #

    def _transfer(self, action: str = None, local_path: str = None, log_checksum: bool = False,
                  preserve_mtime: bool = True, remote_path: str = None, remove_source: bool = False,
                  rename_local: str = None, rename_remote: str = None, replace_local: dict = None,
                  replace_remote: dict = None) -> str:
        """Download a single, remote file from the SFTP server to the local host.

        Args:
            action: GET or PUT
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
            Path of destination file.

        Notes:
            Paramiko's get() already does a size match check between local and remote file.
        """
        if action not in ('GET', 'PUT'):
            raise ValueError("action != 'GET' or 'PUT'")
        if not isinstance(local_path, str):
            raise ValueError('local_path != str type')
        if not isinstance(preserve_mtime, bool):
            raise ValueError('preserve_mtime != str type')
        if not isinstance(remote_path, str):
            raise ValueError('remote_path != str type')
        if not isinstance(remove_source, bool):
            raise ValueError('remove_source != bool type')
        if rename_local is not None and not isinstance(rename_local, str):
            raise ValueError('rename_local != str type')
        if rename_remote is not None and not isinstance(rename_remote, str):
            raise ValueError('rename_remote != str type')
        if replace_local is not None and not isinstance(replace_local, dict):
            raise ValueError('replace_local != dict type')
        if replace_remote is not None and not isinstance(replace_remote, dict):
            raise ValueError('replace_remote != dict type')

        # For logging, determine if any renaming (or replacing) is occuring.
        rename_local_value = False
        rename_remote_value = False
        if rename_local is not None or replace_local is not None:
            rename_local_value = True
        if rename_remote is not None or replace_remote is not None:
            rename_remote_value = True

        transfer_log = {
            'action': action,
            'action_ok': False,
            'client': 'CfSftp',
            'local_path': local_path,
            'note': None,
            'preserve_mtime': preserve_mtime,
            'preserve_mtime_ok': None,
            'remote_path': remote_path,
            'remove_source': remove_source,
            'remove_source_ok': None,
            'rename_local': rename_local_value,
            'renamed_local_path': None,
            'rename_remote': rename_remote_value,
            'renamed_remote_path': None,
            'sha256_checksum': None,
            'size': None,
            'size_match': True,
            'size_match_ok': False,
            'status': None
        }

        try:
            transfer_log['note'] = 'Stat source file.'
            if action == 'GET':
                source_file_stats = self.sftp.stat(remote_path)
            else:  # action == 'PUT'
                source_file_stats = os.stat(local_path)
            transfer_log['size'] = source_file_stats.st_size

            transfer_log['note'] = 'Ensuring destination dir exists.'
            if action == 'GET':
                destination_dir = Path(local_path).parent
                destination_dir.mkdir(exist_ok=True, parents=True)
            else:  # action == 'PUT'
                destination_dir = str(Path(remote_path).parent)
                try:
                    self.sftp.stat(destination_dir)
                except IOError:  # If remote directory does not exist...
                    try:
                        self.sftp.mkdir(destination_dir)
                    except IOError as e:
                        raise IOError(f'Unable to create remote directory: {destination_dir} ({e})')

            new_local_path = local_path
            if replace_local is not None:
                transfer_log['note'] = 'Replacing local_path.'
                # Replace matching string segments in local_path.
                for old, new in replace_local.items():
                    new_local_path = new_local_path.replace(old, new)
                transfer_log['renamed_local_path'] = new_local_path

            if rename_local is not None:
                transfer_log['note'] = 'Renaming local_path.'
                # Replace placeholders with local_path file parts.
                temp_path = Path(new_local_path)
                new_local_path = rename_local\
                    .replace('%p', str(temp_path.parent))\
                    .replace('%f', str(temp_path.stem))\
                    .replace('%s', str(temp_path.suffix))
                transfer_log['renamed_local_path'] = new_local_path

            new_remote_path = remote_path
            if replace_remote is not None:
                transfer_log['note'] = 'Replacing remote_path.'
                # Replace matching string segments in remote_path.
                for old, new in replace_remote.items():
                    new_remote_path = new_remote_path.replace(old, new)
                transfer_log['renamed_remote_path'] = new_remote_path

            if rename_remote is not None:
                transfer_log['note'] = 'Renaming remote_path.'
                # Replace placeholders with local_path file parts.
                temp_path = Path(remote_path)
                new_remote_path = rename_remote \
                    .replace('%p', str(temp_path.parent)) \
                    .replace('%f', str(temp_path.stem)) \
                    .replace('%s', str(temp_path.suffix))
                transfer_log['renamed_remote_path'] = new_remote_path

            if action == 'GET':
                transfer_log['note'] = 'Downloading file.'

                if rename_local is not None or replace_local is not None:
                    local_path = new_local_path

                self.sftp.get(remotepath=remote_path, localpath=local_path)

                if rename_remote is not None or replace_remote is not None:
                    transfer_log['note'] = 'Renaming remote path.'
                    self.rename(old_path=remote_path, new_path=new_remote_path)
                    remote_path = new_remote_path

            else:  # action == 'PUT'
                transfer_log['note'] = 'Uploading file.'

                if rename_remote is not None or replace_remote is not None:
                    remote_path = new_remote_path

                self.sftp.put(remotepath=remote_path, localpath=local_path, confirm=True)  # confirm does filesize stat

                if rename_local is not None or replace_local is not None:
                    transfer_log['note'] = 'Renaming local path.'
                    Path(local_path).rename(new_local_path)
                    local_path = new_local_path

            if log_checksum is True:
                transfer_log['sha256_checksum'] = self.sha256_checksum(local_path)

            transfer_log['action_ok'] = True
            transfer_log['size_match_ok'] = True  # TODO: Make sure parmioko does size match for both PUT and GET.

            if preserve_mtime is True:
                transfer_log['note'] = 'Preserving mtime.'
                transfer_log['preserve_mtime_ok'] = False
                # Restamp the local file with the appropriate modification time.
                if action == 'GET':
                    os.utime(local_path, (source_file_stats.st_atime, source_file_stats.st_mtime))
                else:  # action == 'PUT'
                    local_path_times = (source_file_stats.st_atime, source_file_stats.st_mtime)
                    self.sftp.utime(remote_path, local_path_times)
                transfer_log['preserve_mtime_ok'] = True
                # TODO: Add preserve_mtime for PUT

            if remove_source is True:
                transfer_log['note'] = 'Removing source.'
                transfer_log['remove_source_ok'] = False
                if action == 'GET':
                    self.remove_file(remote_path)
                else:  # action == 'PUT'
                    Path(local_path).unlink()
                transfer_log['remove_source_ok'] = True

        except (FileNotFoundError, IOError) as e:
            transfer_log['note'] = f"{transfer_log['note']}; {str(e)}"
            transfer_log['status'] = 'ERROR'
            raise
        except BadListValueError as e:
            logger.error(str(e))
            raise
        else:
            if preserve_mtime is True:
                transfer_log['note'] = 'preserve_mtime not yet implemented for PUT'
            else:
                transfer_log['note'] = ''
            transfer_log['status'] = 'OK'
        finally:
            self.log['sftp_transfers'].append(transfer_log)

        return local_path

    def _transfer_by_glob(self, action: str = None, flat_dir: bool = False, glob_filter: str = '*', base_dir: str = '.',
                          log_checksum: bool = False, preserve_mtime: bool = True, recursive_search: bool = False,
                          source_dir: str = '.', remove_source: bool = False,
                          rename_local: str = None, rename_remote: str = None, replace_local: dict = None,
                          replace_remote: dict = None) -> List[str]:
        """Create a list of remote files to download based on glob, then download.

        Creates a recursive list of files and directories in remote_dir and filters by glob_filter.

        Args:
            action:
            base_dir: Local base directory for downloaded files. See flat_dir.
            flat_dir: Do not recreate directory structure in local_base_dir.
            glob_filter:
            log_checksum: Calculate file SHA256 checksum and log resulting value.
            preserve_mtime: Keep modification time of source file.
            recursive_search:
            remove_source: Remove the remote source file.
            source_dir:
            rename_local: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            rename_remote: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            replace_local: Use Python .replace() on local_path string. A dictionary--the keysa are the "old"
                           part of the string to match. The values are the "new" string to replace it with.
            replace_remote: Use Python .replace() on remote_path string. A dictionary--the keys are the "old"
                           part of the string to match. The values are the "new" string to replace it with.

        Returns:
            List of destination files.
        """
        if action == 'GET':
            file_list = self.find_files_by_glob(glob_filter=glob_filter, recursive_search=recursive_search,
                                                remote_dir=source_dir)
        else:  # action == 'PUT'
            file_list = glob.glob(glob_filter)

        if len(file_list) > 0:
            logger.debug(f'file_list after filter ({glob_filter}): {str(file_list)}')
            # Get the files
            transfer_list = self._transfer_by_list(
                action=action, base_dir=base_dir,
                file_list=file_list, flat_dir=flat_dir, log_checksum=log_checksum, preserve_mtime=preserve_mtime,
                remove_source=remove_source, rename_local=rename_local, rename_remote=rename_remote,
                replace_local=replace_local, replace_remote=replace_remote
            )
        else:
            transfer_list = []

        return transfer_list

    def _transfer_by_list(self, action: str = None, base_dir: str = '.', file_list: List[str] = None,
                          flat_dir: bool = False, log_checksum: bool = False, preserve_mtime: bool = True,
                          remove_source: bool = False, rename_local: str = None,
                          rename_remote: str = None, replace_local: dict = None,
                          replace_remote: dict = None) -> List[str]:
        """Download a list of files from the SFTP server to the local host.

        Args:
            action:
            base_dir: Destination base directory for transferred files. See flat_dir.
            file_list: Remote/source path and filename.
            flat_dir: Do not recreate directory structure in the destination's base_dir.
            log_checksum: Calculate file SHA256 checksum and log resulting value.
            preserve_mtime: Keep modification time of source file.
            file_list: Source path and filename.
            remove_source: Remove the source file.
            rename_local: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            rename_remote: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            replace_local: Use Python .replace() on local_path string. A dictionary--the keysa are the "old"
                           part of the string to match. The values are the "new" string to replace it with.
            replace_remote: Use Python .replace() on remote_path string. A dictionary--the keys are the "old"
                           part of the string to match. The values are the "new" string to replace it with.

        Returns:
            List of destination files.
        """
        if not isinstance(file_list, list):
            raise ValueError('remote_files != List[str] type')
        if not isinstance(base_dir, str):
            raise ValueError('local_base_dir != str type')
        if not isinstance(flat_dir, bool):
            raise ValueError('flat_dir != bool type')

        transfer_list = []  # List of resulting destination file paths (after any name changes).
        for file in file_list:
            if action == 'GET':
                remote_path = file
                if flat_dir is True:
                    local_path = str(Path(f'{base_dir}/{Path(file).name}'))
                else:
                    local_path = str(Path(f'{base_dir}/{file}'))
            else:  # action == 'PUT':
                local_path = file
                if flat_dir is True:
                    remote_path = str(Path(f'{base_dir}/{Path(file).name}'))
                else:
                    remote_path = str(Path(f'{base_dir}/{file}'))

            try:
                file = self._transfer(action=action, local_path=local_path, log_checksum=log_checksum,
                                      preserve_mtime=preserve_mtime, remote_path=remote_path,
                                      remove_source=remove_source, rename_local=rename_local,
                                      rename_remote=rename_remote,
                                      replace_local=replace_local, replace_remote=replace_remote)
                transfer_list.append(file)
            except FileExistsError as e:
                logger.warning(str(e))

        return transfer_list

    def _transfer_by_regex(self, action: str = None,
                           base_dir: str = '.', flat_dir: bool = False, log_checksum: bool = False,
                           preserve_mtime: bool = True, regex_filter: str = r'^', source_dir: str = '.',
                           remove_source: bool = False,
                           rename_local: str = None, rename_remote: str = None, replace_local: dict = None,
                           replace_remote: dict = None) -> List[str]:
        """Create a list of remote files to download based on a regex, then download.

        Creates a recursive list of files and directories in remote_dir and filters using re.search().

        Args:
            flat_dir:
            base_dir:
            log_checksum: Calculate file SHA256 checksum and log resulting value.
            preserve_mtime: Keep modification time of source file.
            regex_filter:
            source_dir: Remote/source path and filename.
            remove_source:
            rename_local: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            rename_remote: New filename layout. '%f'=filename without suffix, '%p'=parent directories, '%s'=suffix
            replace_local: Use Python .replace() on local_path string. A dictionary--the keysa are the "old"
                           part of the string to match. The values are the "new" string to replace it with.
            replace_remote: Use Python .replace() on remote_path string. A dictionary--the keys are the "old"
                           part of the string to match. The values are the "new" string to replace it with.
        """
        if action == 'GET':
            file_list = self.find_files_by_regex(regex_filter=regex_filter, remote_dir=source_dir)

        else:  # action == 'PUT'
            try:
                regex_object = re.compile(regex_filter)
            except re.error as e:
                logger.debug(f'Bad regex ({regex_filter}): {str(e)}')
                raise ValueError(f'Bad regex pattern ({regex_filter}): {str(e)}')

            file_list = glob.glob(f'{source_dir}/*')

            # Identify items that do not match the regex
            hit_list = []  # Files to remove from list
            for file in file_list:
                result = regex_object.search(file)
                if result is None:
                    hit_list.append(file)

            # Remove the unmatched files from the file list
            for hit in hit_list:
                file_list.remove(hit)

        if len(file_list) > 0:
            logger.debug(f'remote_files after filter ({regex_filter}): {str(file_list)}')
            # Get the files
            transfer_list = self._transfer_by_list(
                action=action, base_dir=base_dir,
                flat_dir=flat_dir, file_list=file_list, log_checksum=log_checksum, preserve_mtime=preserve_mtime,
                remove_source=remove_source, rename_local=rename_local, rename_remote=rename_remote,
                replace_local=replace_local, replace_remote=replace_remote
            )
        else:
            transfer_list = []

        return transfer_list

    #
    # PUBLIC METHODS
    #

    @staticmethod
    def sha256_checksum(file_path: str = None) -> str:
        """Calculate SHA256 checksum for a file."""
        blocksize = 65536  # blocksize limits memory usage.
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as fp:
            for block in iter(lambda: fp.read(blocksize), b''):
                sha256.update(block)
        return sha256.hexdigest()

    @staticmethod
    def transferred_local_files(log: dict) -> List[str]:
        """Get a list of transferred local files (after any renaming)."""
        transferred_files = []
        for transfer in log['sftp_transfers']:
            if transfer['renamed_local_path'] is not None:
                transferred_files.append(transfer['renamed_local_path'])
            else:
                transferred_files.append(transfer['local_path'])
        return transferred_files

    @staticmethod
    def transferred_remote_files(log: dict) -> List[str]:
        """Get a list of transferred remote files (after any renaming)."""
        transferred_files = []
        for transfer in log['sftp_transfers']:
            if transfer['renamed_remote_path'] is not None:
                transferred_files.append(transfer['renamed_remote_path'])
            else:
                transferred_files.append(transfer['remote_path'])
        return transferred_files
