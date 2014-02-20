from twisted.application import service
from service.GPIOService import GPIOService

application = service.Application("carson")
gpioService = GPIOService("gpio-service")
gpioService.setServiceParent(application)