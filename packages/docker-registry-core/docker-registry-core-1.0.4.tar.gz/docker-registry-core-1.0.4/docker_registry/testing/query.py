# -*- coding: utf-8 -*-

from nose import tools

from ..core import driver
from ..core import exceptions


class Query(object):

    def __init__(self, scheme=None):
        self.scheme = scheme

    def testDriverIsAvailable(self):
        drvs = driver.available()
        assert self.scheme in drvs

    def testFetchingDriver(self):
        resultdriver = driver.fetch(self.scheme)
        # XXX hacking is sick
        storage = __import__('docker_registry.drivers.%s' % self.scheme,
                             globals(), locals(), ['Storage'], 0)  # noqa

        assert resultdriver == storage.Storage
        assert issubclass(resultdriver, driver.Base)
        assert resultdriver.scheme == self.scheme

    @tools.raises(exceptions.NotImplementedError)
    def testFetchingNonExistentDriver(self):
        driver.fetch("nonexistentstupidlynameddriver")
