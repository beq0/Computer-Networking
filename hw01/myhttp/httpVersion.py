from enum import Enum


class HttpVersion(Enum):
    V0_9 = 'HTTP/0.9'
    V1_0 = 'HTTP/1.0'
    V1_1 = 'HTTP/1.1'
    V2_0 = 'HTTP/2.0'
