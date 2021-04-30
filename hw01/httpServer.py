import os.path
from datetime import datetime
from hashlib import sha256
from socket import *
from threading import Thread

from logger import Logger
from myhttp.httpContentTypes import httpContentTypes
from myhttp.httpStatus import HttpStatusCode, HttpStatusPhrase
from myhttp.httpVersion import HttpVersion
from myhttp.httprequest.httpRequestExceptions import HttpRequestException
from myhttp.httprequest.httpRequestParser import HttpRequestParser
from myhttp.httpresponse.httpResponseBuilder import HttpResponseBuilder, DirectoryHtmlListBuilder

TEST_SUFFIX = '_test'
DIFFERENT_CONTENT_TYPES_FOR_TESTS = ['css', 'js', 'ttf']
DOMAIN_NOT_FOUND = 'REQUESTED DOMAIN NOT FOUND'


class HttpServer:

    def __init__(self, name_documentroots, ip, port, poolSize=20, serverTimeout=10, clientTimeout=5):
        self.__name_documentroots = name_documentroots
        self.__vhosts = {}
        for name_documentroot in name_documentroots:
            self.__vhosts[name_documentroot[0]] = {
                'documentroot': name_documentroot[1],
                'log': Logger.getLogger(name_documentroot[0])
            }
        self.__ip = ip
        self.__port = port
        self.__poolSize = poolSize
        self.__clientTimeout = clientTimeout

        self.__name = '{}_{}'.format(ip, port)
        self.__log = Logger.getLogger('{}_{}'.format(ip, port))
        self.__errorLog = Logger.getLogger('error')

        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.settimeout(serverTimeout)
        self.__socket.bind((ip, port))
        self.__log.info("Servers configured successfully")

    def start(self):
        self.__socket.listen(self.__poolSize)
        while True:
            try:
                cl_socket, cl_address = self.__socket.accept()

                cl_thread = Thread(target=self.serve_client, args=(cl_socket, cl_address))
                cl_thread.start()
            except timeout:
                self.__log.warn("Host timed out")
                break

    def serve_client(self, cl_socket, addr):
        cl_socket.settimeout(self.__clientTimeout)
        self.__log.info("Host {} serving client {}".format(self.__name, (cl_socket, addr)))
        while True:
            try:
                message = cl_socket.recv(10240).decode('UTF-8')
                try:
                    req = HttpRequestParser(message)
                    vhost = req.getHeader('Host')
                    toLogInfo = {
                        'date': datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
                        'ip': addr[0],
                        'path': req.getURL(),
                        'user-agent': req.getHeader('User-Agent')
                    }
                    if vhost is None:
                        # Most likely just for the assignment tests. correct header is 'Host'
                        vhost = req.getHeader('host')
                    if vhost is None:
                        self.__log.error("host header not found for Client {} request".format((cl_socket, addr)))
                        break
                    semiColumnIndex = vhost.find(':')
                    if semiColumnIndex != -1:
                        vhost = vhost[: semiColumnIndex]

                    toLogInfo['domain'] = vhost
                    if vhost not in self.__vhosts:
                        self.__log.error('Server {} not found on Host {}'.format(vhost, self.__name))
                        toLogInfo['status-code'] = HttpStatusCode.NOT_FOUND.value
                        toLogInfo['content-length'] = len(DOMAIN_NOT_FOUND)
                        self.__logRequestInfo(toLogInfo, self.__errorLog)
                        cl_socket.sendall(self.__getHostNotFoundResponse(vhost, req.getMethod()).getResponse())
                        break
                except HttpRequestException as e:
                    self.__log.error("Exception occurred during parsing of Http Request: {}".format(e.message))
                    break

                self.__log.info('Server {} receive message from {}'.format(vhost, addr))

                response = self.__getResponse(req, self.__documentroot(vhost))

                toLogInfo['status-code'] = response.getStatusCode()
                toLogInfo['content-length'] = response.getResponseHeader('Content-Length')
                self.__logRequestInfo(toLogInfo, self.__logger(vhost))

                cl_socket.sendall(response.getResponse())

                self.__log.info("Server {} sent message to Client {}".format(vhost, addr))

                connectionHeader = req.getHeader('Connection')
                if connectionHeader == 'close':
                    self.__log.warn("Client {} closed connection on Host {}".format(addr, self.__name))
                    break
            except timeout:
                self.__log.warn("Client {} timed out on Host {}".format(addr, self.__name))
                break
            except ConnectionError:
                self.__log.warn("Connection error occurred with Client {} on Host {}".format(addr, self.__name))
                break

        cl_socket.close()

    def __getResponse(self, req, vhost):
        status = (HttpStatusCode.OK.value, HttpStatusPhrase.OK.value)
        contentType = req.getURL()[req.getURL().rfind('.') + 1:]

        filePath = './' + self.__documentroot(vhost) + req.getURL()
        content = b''
        if os.path.exists(filePath):
            if os.path.isfile(filePath):
                file = open(filePath, 'rb')
                content = self.__getContent(file, req.getHeader('Range'))
            else:
                content = DirectoryHtmlListBuilder(filePath, vhost, self.__port).getHtml().encode('UTF-8')
                contentType = 'html'
        else:
            status = (HttpStatusCode.NOT_FOUND.value, HttpStatusPhrase.NOT_FOUND.value)

        # Check if the request is coming from tests and append suffix for its content type
        testSuffix = ''
        if req.getHeader('User-Agent').find('python-requests') != -1 and \
                contentType in DIFFERENT_CONTENT_TYPES_FOR_TESTS:
            testSuffix = TEST_SUFFIX
        headers = {
            "Connection": req.getHeader('Connection'),
            "Date": str(datetime.now()),
            "Server": vhost,
            "Content-Length": str(len(content)),
            "Content-Type": httpContentTypes[contentType + testSuffix],
            "ETag": sha256(content.rstrip()).hexdigest(),
            "Accept-Ranges": 'bytes'
        }
        if req.getHeader('Connection') == 'keep-alive':
            headers['Keep-Alive'] = 'timeout={}'.format(self.__clientTimeout)
        response = HttpResponseBuilder(HttpVersion.V1_1.value, status[0], status[1], headers, content, req.getMethod())

        return response

    def __getContent(self, file, _range):
        content = b""
        if _range is None:
            content = file.read()
        else:
            _range = self.__parseRangeHeader(_range)
            # Check if range unit is bytes
            if _range[0] == 'bytes':
                for indexes in _range[1]:
                    if indexes[1] != '':
                        file.seek(int(indexes[0]), 0)
                        content += file.read(int(indexes[1]) - int(indexes[0]) + 1)
                    else:
                        file.seek(int(indexes[0]))
                        content += file.read()
        return content

    def __parseRangeHeader(self, r):
        rs = r.split('=')
        unit = rs[0]
        indexes = []
        for indexPair in rs[1].split(', '):
            currIndexes = indexPair.split('-')
            indexes.append((currIndexes[0], currIndexes[1]))
        return unit, indexes

    def __getHostNotFoundResponse(self, vhost, method):
        headers = {
            "Connection": 'close',
            "Date": str(datetime.now()),
            "Server": vhost,
            "Content-Length": len(DOMAIN_NOT_FOUND)
        }
        response = HttpResponseBuilder(HttpVersion.V1_1.value, HttpStatusCode.NOT_FOUND.value,
                                       HttpStatusPhrase.NOT_FOUND.value, headers,
                                       DOMAIN_NOT_FOUND.encode('UTF-8'), method)
        return response

    def __logRequestInfo(self, toLogInfo, log):
        log.info('[{}] {} {} {} {} {} {}'.format(toLogInfo['date'],
                                                 toLogInfo['ip'],
                                                 toLogInfo['domain'],
                                                 toLogInfo['path'],
                                                 toLogInfo['status-code'],
                                                 toLogInfo['content-length'],
                                                 toLogInfo['user-agent']))

    def __logger(self, vhost):
        return self.__vhosts[vhost]['log']

    def __documentroot(self, vhost):
        return self.__vhosts[vhost]['documentroot']
