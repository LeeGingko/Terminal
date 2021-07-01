# cheesefactory-sftp/exceptions.py


class Error(Exception):
    """Base class."""
    pass


class FileSizeMismatchError(Error):

    def __init__(self, local_path: str, local_size: str, remote_path: str, remote_size: str):
        """Exception raised when source and destination files do not match.

        Args:
            local_path: Path of local file.
            local_size: Size of local file.
            remote_path: Path of remote file.
            remote_size: Size of remote file.
        """
        self.local_path = local_path
        self.local_size = local_size
        self.remote_path = remote_path
        self.remote_size = remote_size

    def __str__(self):
        return f'Size mismatch -- Local: {self.local_path} ({self.local_size}) != ' \
               f'Remote: {self.remote_path} ({self.remote_size})'


class EmptyListError(Error):

    def __init__(self, function_name: str, variable_name: str):
        """Exception raised when a list of paths is empty.

        Args:
            function_name: Path of local file.
            variable_name: Size of local file.
        """
        self.function_name = function_name
        self.variable_name = variable_name

    def __str__(self):
        return f'Path list is empty. Function: {self.function_name}, Variable: {self.variable_name}'


class BadListValueError(Error):

    def __init__(self, message: str):
        """Exception raised when a bad value is given in a list.

        Args:
            message: User-defined message.
        """
        self.message = message

    def __str__(self):
        return str(self.message)


class InternalValueError(Error):

    def __init__(self, message: str):
        """Exception raised when a bad value is given in a list.

        Args:
            message: User-defined message.
        """
        self.message = message

    def __str__(self):
        return str(self.message)
