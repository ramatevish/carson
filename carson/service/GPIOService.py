from __future__ import print_function
from twisted.application import service
from twisted.python import log
from twisted.internet.defer import Deferred
import tempfile
import errno
import sys
from collections import namedtuple
import time
try:
    import RPi.GPIO as GPIO
except ImportError as e:
    # TODO: have this run after logs is laoded
    log.err("RPi is not setup correctly - using stubs")
    from GPIOStubs import GPIOStubs
    GPIO = GPIOStubs()


ChannelState = namedtuple("ChannelState", ['mode', 'channel', 'value'])


class GPIOService(service.Service):

    # BCM mode uses the Broadcom SOC channel numbers, so this future releases of RPi will require the map to be updated
    # This map is for RPi Revision 2
    MODE = GPIO.BCM
    PIN_MAP = {0: 4, 1: 17, 2: 18, 3: 27, 4: 22, 5: 23, 6: 24, 7: 25}
    OUTPUT = 1
    INPUT = -1

    def __init__(self, name='gpio-service'):
        log.msg("Creating GPIO service")
        # potential for damage if we have two instances of the service running
        if not hasattr(GPIOService, 'instance'):
            log.msg(ImportError("Setting GPIOService instance"))
            GPIOService.instance = self
        else:
            log.err(RuntimeError("There should only be one instance of GPIO service running"))
            sys.exit(1)
        self.setName(name)
        self._channelState = [(None, None)] * 8
        self._channelQueues = [list()] * 8

    def startService(self):
        log.msg("Starting GPIO service")
        service.Service.startService(self)

        # kludgy / portable check for superuser privilege
        try:
            tempfile.TemporaryFile(dir='/etc')
        except OSError as error:
            if error[0] == errno.EACCES:
                log.err(OSError(errno.EACCES, "Not running as root"))
                sys.exit(1)

        try:
            GPIO.setmode(GPIOService.MODE)
        except Exception as exception:
            log.err(exception)
            sys.exit(1)

        self.output(1)
        self.output(1)

    def stopService(self):
        log.msg("Stopping GPIO service")
        service.Service.stopService(self)
        return self.cleanup()

    def output(self, channel, value=GPIO.LOW, deferred=None):
        outputDeferred = self._output(channel, value, deferred=deferred)
        outputDeferred.addCallback(lambda _: time.sleep(1))
        self._cleanupDeferred(outputDeferred)
        d = Deferred()
        d.addCallback(self._checkChannel(channel, outputDeferred))
        d.callback(None)

    def _checkChannel(self, channel, deferred):
        def _checkChannel(_):
            log.msg("Checking for access to channel {}".format(channel))
            queue = self._channelQueues[channel]
            if len(queue):
                log.msg("Adding request on channel {} to queue".format(channel))
                self._channelQueues[channel].append(deferred)
            else:
                queue.append(deferred)
                deferred.callback(None)
                queue.pop(0)
                self._nextDeferred(channel)
        return _checkChannel

    def _nextDeferred(self, channel):
        queue = self._channelQueues[channel]
        if len(queue):
            queue[0].callback(None)
            queue.pop(0)
            self._nextDeferred(channel)
        else:
            return


    def _output(self, channel, value=GPIO.LOW, deferred=None):
        d = deferred if deferred else Deferred()
        def _output(_):
            log.msg("Outputting {} on channel {}".format(value, channel))
            pin = GPIOService.PIN_MAP[channel]
            # GPIO.setup(pinNumber, GPIO.OUT, value) doesn't work for 0
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, value)
            self._channelState[channel] = (GPIOService.OUTPUT, value)
            return True
        d.addCallback(_output)
        return d

    def cleanup(self, deferred=None):
        self._cleanupDeferred(deferred).callback(None)

    def _cleanupDeferred(self, deferred=None):
        d = deferred if deferred else Deferred()
        def _cleanup(_):
            log.msg("Cleaning up GPIO pins")
            # only cleanup if we've set any channels up
            for channelType, channelValue in self._channelState:
                if channelType:
                    GPIO.cleanup()
                    self._channelState = [(None, None)] * 8
                    break
        d.addCallback(_cleanup)
        return d
