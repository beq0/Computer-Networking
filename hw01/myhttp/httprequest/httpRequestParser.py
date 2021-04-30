from myhttp.httpMethod import HttpMethod
from myhttp.httpVersion import HttpVersion
from myhttp.httprequest.httpRequestExceptions import BadRequestException, UnsupportedHttpMethodException, \
    UnsupportedHttpVersionException
import urllib.parse


class HttpRequestParser:
    __SUPPORTED_METHODS = {HttpMethod.GET.value, HttpMethod.HEAD.value}
    __SUPPORTED_HTTP_VERSIONS = {HttpVersion.V1_1.value, HttpVersion.V2_0.value}
    __BREAK_LINE = '\r\n'

    def __init__(self, request):
        self.__index = 0
        self.__request = request
        self.__parseRequest()

    def getBody(self):
        return self.__body

    def getMethod(self):
        return self.__method

    def getURL(self):
        return self.__URL

    def getVersion(self):
        return self.__httpVersion

    def getHeader(self, header):
        if header in self.__headers:
            return self.__headers[header]
        return None

    def __parseRequest(self):
        requestLineEndIndex = self.__request.find(self.__BREAK_LINE)
        requestLine = self.__request[0: requestLineEndIndex]
        self.__index = requestLineEndIndex + len(self.__BREAK_LINE)
        self.__parseRequestLine(requestLine)

        headersEndIndex = self.__request.find(self.__BREAK_LINE * 2)
        headers = self.__request[self.__index: headersEndIndex]
        self.__index = headersEndIndex + len(self.__BREAK_LINE * 2)
        self.__parseHeaders(headers)

        self.__body = self.__request[self.__index:]

    def __parseRequestLine(self, requestLine):
        # Parse method
        currIndex = 0
        spaceAfterMethod = requestLine.find(" ", currIndex)
        if spaceAfterMethod == -1:
            raise BadRequestException()
        self.__method = requestLine[0:spaceAfterMethod]
        if self.__method not in self.__SUPPORTED_METHODS:
            raise UnsupportedHttpMethodException(self.__method)
        currIndex = spaceAfterMethod + 1

        # Check if there is more then one space after method
        if requestLine[currIndex] == ' ':
            raise BadRequestException

        # Parse URL
        spaceAfterURL = requestLine.find(" ", currIndex)
        if spaceAfterURL == -1:
            raise BadRequestException
        self.__URL = urllib.parse.unquote_plus(requestLine[currIndex: spaceAfterURL])
        currIndex = spaceAfterURL + 1

        # Check if there is more then one space after URL
        if requestLine[currIndex] == ' ':
            raise BadRequestException

        # Parse Version
        self.__httpVersion = requestLine[currIndex:]
        if self.__httpVersion not in self.__SUPPORTED_HTTP_VERSIONS:
            raise UnsupportedHttpVersionException(self.__httpVersion)

    def __parseHeaders(self, headersTxt):
        self.__headers = {}
        headersArr = headersTxt.split(self.__BREAK_LINE)
        for h in headersArr:
            spaceIndex = h.find(' ')
            if spaceIndex == -1 or h[spaceIndex - 1] != ':':
                raise BadRequestException
            headerKey = h[: spaceIndex - 1]
            headerValue = h[spaceIndex + 1:]
            self.__headers[headerKey] = headerValue
