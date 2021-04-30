import logging
import os.path
formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class Logger:
    basePath = None

    @staticmethod
    def getLogger(serverName):
        """Get logger for server with given serverName and log file path"""
        if Logger.basePath is None:
            raise Exception("Logger.basePath not defined")

        logFilename = Logger.basePath + '/' + serverName + '.log'
        os.makedirs(os.path.dirname(logFilename), exist_ok=True)

        handler = logging.FileHandler(logFilename)
        handler.setFormatter(formatter)
        logger = logging.getLogger(serverName)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger
