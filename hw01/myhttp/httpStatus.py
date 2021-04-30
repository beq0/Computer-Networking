from enum import Enum


class HttpStatusCode(Enum):
    OK = 200
    MOVED_PERMANENTLY = 301
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    HTTP_VERSION_NOT_SUPPORTED = 505


class HttpStatusPhrase(Enum):
    OK = "OK"
    MOVED_PERMANENTLY = "Moved Permanently"
    BAD_REQUEST = "Bad Request"
    NOT_FOUND = "Not Found"
    INTERNAL_ERROR = "Internal Server Error"
    HTTP_VERSION_NOT_SUPPORTED = "HTTP Version Not Supported"
