import time
from random import randint


class GPIOStubs(object):

    LOW = 0
    HIGH = 1
    IN = 1
    OUT = 0

    # pin modes
    BCM = 11
    BOARD = 10

    # pulldown resistor modes
    PUD_OFF = 20
    PUD_DOWN = 21
    PUD_UP = 22

    # async input detection
    RISING = 31
    FALLING = 32
    BOTH = 33

    I2C = 42

    def __init__(self):
        self._mode = None
        self._pinModes = [0] * 32
        self._pinValues = [0] * 32

        # pulldown resistor status
        self._pulldownStatus = [GPIOStubs.PUD_OFF] * 32

    def setmode(self, mode, *args, **kwargs):
        self._mode = mode

    def cleanup(self, pin=None):
        if pin:
            self._pinModes[pin] = 0
        else:
            if sum(map(lambda n: abs(n), self._pinModes)) == 0:
                # TODO: warning message for if we clean up unused pins
                pass
            for pin in xrange(32):
                if self._pinModes[pin]:
                    self._pinModes = [0] * 32
                    break

    def setup(self, pin, mode, **kwargs):
        self._pinModes[pin] = mode

    def output(self, pin, value=LOW, **kwargs):
        if self._pinModes[pin] != GPIOStubs.OUT:
            # TODO: error
            pass
        time.sleep(.2)
        self._pinValues[pin] = value

    def input(self, pin):
        if self._pinModes[pin] != GPIOStubs.IN:
            # TODO: error
            pass
        pinValue = self._pinValues[pin]
        pudStatus = self._pulldownStatus[pin]

        # simulate randomness from mains
        if pudStatus == GPIOStubs.PUD_OFF:
            pinValue = randint(0, 1)

        # TODO: don't account for input voltage
        return pinValue
