from twisted.application import service
from service.GPIOService import GPIOService
from service.SchedulerService import SchedulerService

application = service.Application("carson")

gpioService = GPIOService("gpio-service")
gpioService.setServiceParent(application)

schedulerService = SchedulerService("scheduler-service")
schedulerService.setServiceParent(application)

