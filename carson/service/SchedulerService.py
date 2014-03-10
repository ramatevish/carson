from twisted.application import service
from twisted.enterprise import adbapi
from twisted.python import log
import os


class SchedulerService(service.Service):

    def __init__(self, servicename='scheduler-service', filename='scheduled'):
        log.msg("Starting SchedulerService")
        self.setName(servicename)

        log.msg("Connecting to scheduling database")
        dbpool = adbapi.ConnectionPool("sqlite3", filename)

    def startService(self):
        log.msg("Starting scheduler service")
        service.Service.startService(self)

    def stopService(self):
        log.msg("Stopping scheduler service")
        service.Service.stopService(self)
