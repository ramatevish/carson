from twisted.application import service
from twisted.python import log
import tempfile
import errno
import sys


class GPIOService(service.Service):

    def __init__(self, name='gpio-service'):
        log.msg("Creating GPIO service")
        # potential for damage if we have two instances of the service running
        if not hasattr(GPIOService, 'instance'):
            log.msg("Setting GPIOService instance")
            GPIOService.instance = self
        else:
            log.err(RuntimeError("There should only be one instance of GPIO service running"))
            sys.exit(1)
        self.setName(name)

    def startService(self):
        log.msg("Starting GPIO service")
        service.Service.startService(self)

        # kludgy / portable check for superuser privilege
        try:
            tempfile.TemporaryFile(dir='/etc')
        except OSError as e:
            if e[0] == errno.EACCES:
                # TODO: ask Ying if this is kosher
                log.err(OSError(errno.EACCES, "Not running as root."))
                sys.exit(1)

        # RPIO stuff
        # TODO: stub out RPIO for testing w/out RPi

    def stopService(self):
        log.msg("Stopping GPIO service")
        service.Service.stopService(self)
        # TODO: cleanup
