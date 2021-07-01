# cheesefactory-sftp

-----------------

#### A beautiful SFTP wrapper for Paramiko.
[![PyPI Latest Release](https://img.shields.io/pypi/v/cheesefactory-sftp.svg)](https://pypi.org/project/cheesefactory-sftp/)
[![PyPI status](https://img.shields.io/pypi/status/cheesefactory-sftp.svg)](https://pypi.python.org/pypi/cheesefactory-sftp/)
[![PyPI download month](https://img.shields.io/pypi/dm/cheesefactory-sftp.svg)](https://pypi.python.org/pypi/cheesefactory-sftp/)
[![PyPI download week](https://img.shields.io/pypi/dw/cheesefactory-sftp.svg)](https://pypi.python.org/pypi/cheesefactory-sftp/)
[![PyPI download day](https://img.shields.io/pypi/dd/cheesefactory-sftp.svg)](https://pypi.python.org/pypi/cheesefactory-sftp/)

### Note

This is a major rewrite, now based on Paramiko. The focus has been on basic GET and PUT. As such, some features are not yet finished and this README is woefully inadequate, but things will soon be better than ever.

If I did something bad for you in with this update, I'm sorry. Please `import cheesefactory-sftp==0.15`

### Main Features

**Note:** _This package is still in beta status. As such, future versions may not be backwards compatible and features may change. Parts of it may even be broken._

* Built using paramiko.

### Coming Soon

TBA

### Connect to the remote SFTP server

-----------------
```python
from cheesefactory-sftp import SFTP

sftp = SFTP.connect(
    host='mysftp.example.com',
    port='22',
    username='testuser',
    password='testpass',
)
```

Argument | Type | Default | Description
:--- | :--- | :--- | :---
**host** | str | `127.0.0.1` | Remote server. 
**port** | str | `'22'` | SFTP TCP port. 
**user** | str | | SFTP username
**password** | str | |  SFTP password
**key_path** | str | | Path to private key file.
**key_password** | | str | Password for encrypted private key.
**cnopts** | CfCnOpts | | Extra connection options.
**default_path** | str | | Path set after connection.

### Connection Methods

Method | Description
:--- | :---
[close()](#close) | Close the SFTP connection.
[connect()](#connect) | Connect to a remote SFTP server.
[status()](#status) | Retrieve connection status.


#### close()

Close the SFTP connection.

```python
sftp = SFTP.connect(...)
sftp.close()
```

#### connect()

Connect to a remote SFTP server.

```python
sftp = SFTP.connect(...)
```

Args:</br>
&emsp;_host_ (`str`): Remote SFTP server hostname or IP.</br>
&emsp;_port_ (`int` or `str`): Remote SFTP server port.</br>
&emsp;_user_ (`str`): Account username on remote SFTP server.</br>
&emsp;_password_ (`str`): Account password on remote SFTP server.</br>
&emsp;_key_path_ (`str`): Path to private key file.</br>
&emsp;_key_password_ (`str`): Password for encrypted private key.

#### status()

Retrieve connection status.

```python
sftp = SFTP.connect(...)
status, message = sftp.status()
```

Returns:
1. True (connected) or False (not connected), and
2. 'Transport open and authenticated', 'Transport open. Not authenticated', or 'Transport closed, Not authenticated'

### File and Directory Methods

Method | Description
:--- | :---
[chdir()](#chdir) | Change current remote directory.
[chmod()](#chmod) | Change the permissions of a remote file.
[chown()](#chown) | Change the owner and group of a remote file.
[cwd()](#cwd) | Return the current remote directory.
[delete()](#remove_file) | Alias for remove_file(). **DEPRECATED**
[exists()](#exists) | Does a remote file or directory exist?
[file_size_match()](#file_size_match) | Determine if the sizes of a remote and a local file match.
[is_dir()](#is_dir) | Is the current remote path a directory?
[is_file()](#is_file) | Is the current remote path a file?
[list_dir()](#list_dir) | Return a list of remote directory contents (without `.` and `..`).
[list_files()](#list_dir) | Return a list of remote directory contents (without `.` and `..`). **DEPRECATED**
[mkdir()](#mkdir) | Create a remote directory.
[remove()](#remove) | Delete a remote file or directory.
[remove_dir()](#remove_dir) | Delete a remote directory.
[remove_file()](#remove_file) | Delete a remote file.
[rename()](#rename) | Rename a remote flie or folder.
[stat()](#stat) | Retrieve information about a remote file. Mimics Python's os.stat structure.

---

#### chdir()

Change current remote directory.

```python
sftp = SFTP.connect(...)
sftp.chdir('/tmp/downloads')
```

Args:</br>
&emsp;_path_ (`str`): New remote directory.

---

#### chmod()

Change the permissions of a remote file.

```python
sftp = SFTP.connect(...)
sftp.chmod(path='/tmp/myfile', mode=644)
```

Args:</br>
&emsp;_path_ (`str`): Remote file path.</br>
&emsp;_mode_ (`int`): Unix-style permission (e.g. 0644)

---

#### chown()

Change the owner and group of a remote file.

```python
sftp = SFTP.connect(...)
sftp.chown(path='/tmp/myfile', uid=1003, gid=1003)
```

Args:</br>
&emsp;_path_ (`str`): Remote file path.</br>
&emsp;_uid_ (`int`): New user ID.</br>
&emsp;_gid_ (`int`): New group ID.

---

#### cwd()

Return the current remote directory.

```python
sftp = SFTP.connect(...)
sftp.cwd()
```

Returns:</br>
&emsp;(`str`) Current remote working directory.

---

#### exists()

Does a remote file or directory exist?

```python
sftp = SFTP.connect(...)
sftp.exists('/tmp/myfile')
```

Args:</br>
&emsp;_path_ (`str`): File or directory to test.</br>

Returns:</br>
&emsp;(`int`) **True** if file or directory exists. **False** if it does not.

---

#### is_dir()

Is the current remote path a directory?

```python
sftp = SFTP.connect(...)
sftp.is_dir()
```

Args:</br>
&emsp;_path_ (`str`): The path to test.

Returns:</br>
&emsp;(`bool`) **True** if it is, **False** if it ain't.

---

#### is_file()

Is the current remote path a file?

```python
sftp = SFTP.connect(...)
sftp.is_file()
```

Args:</br>
&emsp;_path_ (`str`): The path to test.

Returns:</br>
&emsp;(`bool`) **True** if it is, **False** if it is not.

---

#### list_dir()

Return a list of remote directory contents (without `.` and `..`).

```python
sftp = SFTP.connect(...)
sftp.list_dir()
```

Args:</br>
&emsp;_path_ (`str`): Remote path.</br>
&emsp;_recursive_ (`bool`): Include contents of sub-directories in output?

Returns:</br>
&emsp;(`list`) A list of directory contents.

---

#### mkdir()

Create a remote directory.

```python
sftp = SFTP.connect(...)
sftp.mkdir()
```

Args:</br>
&emsp;_path_ (`str`): Name of the folder to create.</br>
&emsp;_mode_ (`int`): Posix-style permissions for the folder. Given in octal (without preceding 0)

---

#### remove()

Delete a remote file or directory.

```python
sftp = SFTP.connect(...)
sftp.remove()
```

Args:</br>
&emsp;_path_ (`str`): Relative or absolute path of file or directory to delete.

Raises:</br>
&emsp;`IOError`: if path is neither directory nor file.

---

#### remove_dir()

Delete a remote directory.

```python
sftp = SFTP.connect(...)
sftp.remove_dir()
```

Args:</br>
&emsp;_path_ (`str`): Relative or absolute path of directory to delete.

---

#### remove_file()

Delete a remote file.

```python
sftp = SFTP.connect(...)
sftp.remove_file()
```

Args:</br>
&emsp;_path_ (`str`): Relative or absolute path of file to delete.

---

#### rename()

Rename a remote flie or folder.

```python
sftp = SFTP.connect(...)
sftp.rename()
```

Args:</br>
&emsp;_old_path_ (`str`): Existing name of file or directory.
&emsp;_new_path_ (`str`): New name for the file or directory. Must not already exist.

---

#### stat()

Retrieve information about a remote file. Mimics Python's os.stat structure. 

Supported fields: st_mode, st_size, st_uid, st_gid, st_atime, and st_mtime. 

```python
sftp = SFTP.connect(...)
sftp.stat()
```

Args:</br>
&emsp;_path_ (`str`): The filename to stat.

Returns:</br>
&emsp;(`paramiko.SFTPAttributes()`) Attributes about the given file.


## Log

Metrics concerning the status and performance of CfSftp are available via the `log` attribute.

```python
sftp = CfSftp.connect(
    host='mysftp.example.com',
    port='22',
    username='testuser',
    password='testpass',
)
```
```python
>>> sftp.log
{'sftp_host': 'mysftp.example.com', 'sftp_password': 'testpass', 'sftp_port': '22', 'sftp_username': 'testuser'}
```

### Log keys

The following log keys are available:

  * sftp_connection_ok: bool (Was the SFTP connection established successfully?)
  * sftp_connection_note: str (Connection problem details)
  * sftp_host: str
  * sftp_last_utility_note
  * sftp_password: str
  * sftp_port: str
  * sftp_transfers: List (Details for each transfer during the SFTP session.)
    * action: 'GET' or 'PUT'
    * action_ok: bool
    * append_local: str
    * append_remote: str
    * client: str
    * local_path: str
    * note: str
    * preserve_mtime: bool
    * preserve_mtime_ok: bool
    * remote_path: str
    * remove_source: bool
    * remove_source_ok: bool
    * renamed_local_path: str
    * renamed_remote_path: str
    * size: int
    * size_match: bool
    * size_match_ok: bool
    * status: 'OK', 'ERROR'
  * sftp_user: str

