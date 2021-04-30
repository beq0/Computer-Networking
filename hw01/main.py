import json
from threading import Thread

from httpServer import HttpServer
from logger import Logger


def startHttpServer(name_documentroots, _ip, _port):
    HttpServer(name_documentroots, _ip, _port, poolSize=1024).start()


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)
    Logger.basePath = config['log']

    servers = {}
    for serverConf in config['server']:
        ip_port = (serverConf['ip'], serverConf['port'])
        name_documentroot = (serverConf['vhost'], serverConf['documentroot'])
        if ip_port in servers:
            servers[ip_port].append(name_documentroot)
        else:
            servers[ip_port] = [name_documentroot]

    for _ip, _port in servers:
        server_thread = Thread(target=startHttpServer, args=(servers[_ip, _port], _ip, _port))
        server_thread.start()
