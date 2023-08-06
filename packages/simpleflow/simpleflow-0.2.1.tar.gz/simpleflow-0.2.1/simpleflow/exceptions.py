class ExecutionBlocked(Exception):
    pass


class TaskException(Exception):
    """
    Wrap an exception raised by a task.

    """
    def __init__(self, exception):
        """
        :param exception: raised by a task.
        :type  exception: TaskFailed.

        """
        self.exception = exception

    def __repr__(self):
        return '{}(exception={})'.format(
            self.__class__.__name__,
            self.exception)


class TaskFailed(Exception):
    """
    Wrap the error's *reason* and *details* for an task that failed.

    :param reason: of the failure.
    :type  reason: str.
    :param details: of the failure.
    :type  details: str.

    """
    def __init__(self, reason, details=None):
        super(TaskFailed, self).__init__(self, reason, details)
        self.reason = reason
        self.details = None

    def __repr__(self):
        return '{}(reason="{}", details="{}")'.format(
            self.__class__.__name__,
            self.reason,
            self.details)


class TimeoutError(Exception):
    def __init__(self, timeout_type, timeout_value=None):
        self.timeout_type = timeout_type
        self.timeout_value = timeout_value

    def __repr__(self):
        return 'TimeoutError({})'.format(self.timeout_type)
