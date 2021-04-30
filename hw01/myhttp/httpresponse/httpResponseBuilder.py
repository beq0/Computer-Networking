import os
import urllib.parse

from myhttp.httpMethod import HttpMethod


class HttpResponseBuilder:
    __BREAK_LINE = '\r\n'

    def __init__(self, httpVersion, statusCode, phrase, headers, body, method):
        """Body has to be encoded"""
        self.__statusCode = statusCode
        self.__headers = headers
        self.__response = ""
        self.__constructStatusLine(httpVersion, statusCode, phrase)
        self.__constructHeaders(headers)
        self.__response += self.__BREAK_LINE

        self.__response = self.__response.encode('UTF-8')
        if method != HttpMethod.HEAD.value:
            self.__response += body

    def getResponse(self):
        return self.__response

    def getResponseHeader(self, headerKey):
        if headerKey in self.__headers:
            return self.__headers[headerKey]
        return None

    def getStatusCode(self):
        return self.__statusCode

    def __constructStatusLine(self, httpVersion, statusCode, phrase):
        self.__response += '{} {} {}{}'.format(httpVersion, statusCode, phrase, self.__BREAK_LINE)

    def __constructHeaders(self, headers):
        if headers is not None:
            for key, val in headers.items():
                self.__response += '{}: {}{}'.format(key, val, self.__BREAK_LINE)


class DirectoryHtmlListBuilder:
    def __init__(self, dirPath, serverName, port):
        self.__serverName = serverName
        self.__port = port
        self.__html = '<!DOCTYPE html>\n' + \
                      '<html>\n' + \
                      '<head>\n' + \
                      '<title>{}</title>\n'.format("Contents of " + dirPath) + \
                      '</head>\n' + \
                      '<body>\n' + \
                      '<ul>\n' + \
                      '{}\n'.format(self.__getHtmlListItems(dirPath)) + \
                      '</ul>\n' + \
                      '</body>\n' + \
                      '</html>\n'

    def getHtml(self):
        return self.__html

    def __getHtmlListItems(self, dirPath):
        result = ''
        dirPathUrl = dirPath
        indexOfServerName = dirPathUrl.find(self.__serverName)
        if dirPathUrl[0] != -1:
            dirPathUrl = dirPathUrl[indexOfServerName + len(self.__serverName):]
        if dirPathUrl[-1] != '/':
            dirPathUrl += '/'
        for path in os.listdir(dirPath):
            pathUrl = self.__getUrl(dirPathUrl + urllib.parse.quote_plus(path))
            result += '<li>{}: <a href={}>{}</a></li>\n'.format(path, pathUrl, pathUrl)
        return result

    def __getUrl(self, file):
        return 'http://{}:{}{}'.format(self.__serverName,
                                       self.__port,
                                       file)
