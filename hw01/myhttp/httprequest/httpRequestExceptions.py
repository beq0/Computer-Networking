class HttpRequestException(Exception):
    """Base exception for all myhttp request exceptions"""

    def __init__(self, message="Http Request Exception"):
        self.message = message
        super().__init__(self.message)


class BadRequestException(HttpRequestException):
    """Thrown when request is malformed"""

    def __init__(self, message="Malformed Http Request"):
        self.message = message
        super().__init__(self.message)


class UnsupportedHttpMethodException(HttpRequestException):
    """Thrown when myhttp method is not supported"""

    def __init__(self, method, message="Http method not supported"):
        self.method = method
        self.message = message
        super().__init__(self.message)


class UnsupportedHttpVersionException(HttpRequestException):
    """Thrown when myhttp version is not supported"""

    def __init__(self, version, message="Http version not supported"):
        self.version = version
        self.message = message
        super().__init__(self.message)
