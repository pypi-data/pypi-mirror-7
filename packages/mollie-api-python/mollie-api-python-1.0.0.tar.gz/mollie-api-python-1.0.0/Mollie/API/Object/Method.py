from Base import *


class Method(Base):
    IDEAL = 'ideal'
    PAYSAFECARD = 'paysafecard'
    CREDITCARD = 'creditcard'
    MISTERCASH = 'mistercash'
    BANKTRANSFER = 'banktransfer'
    PAYPAL = 'paypal'
    BITCOIN = 'bitcoin'

    def getMinimumAmount(self):
        if not self['amount'] or 'minimum' not in self['amount']:
            return None
        return float(self['amount']['minimum'])

    def getMaximumAmount(self):
        if not self['amount'] or 'maximum' not in self['amount']:
            return None
        return float(self['amount']['maximum'])

    def getNormalImage(self):
        if not self['image'] or 'normal' not in self['image']:
            return None
        return str(self['image']['normal'])

    def getBiggerImage(self):
        if not self['image'] or 'bigger' not in self['image']:
            return None
        return str(self['image']['bigger'])
