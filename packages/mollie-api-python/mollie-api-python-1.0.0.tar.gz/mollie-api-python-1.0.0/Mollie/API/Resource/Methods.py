from Base import *
from Mollie.API.Object import Method


class Methods(Base):
    def getResourceObject(self, result):
        return Method(result)