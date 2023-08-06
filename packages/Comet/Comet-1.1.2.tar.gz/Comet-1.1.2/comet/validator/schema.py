# Comet VOEvent Broker.
# Schema validator.
# John Swinbank, <swinbank@transientskp.org>.

from twisted.internet.threads import deferToThread
import lxml.etree as etree

from zope.interface import implementer
from ..icomet import IValidator

@implementer(IValidator)
class CheckSchema(object):
    """
    This takes an ElementTree element, converts it to a string, then reads
    that into lxml for validation. That... can't be optimal.
    """
    def __init__(self, schema):
        self.schema = etree.XMLSchema(etree.parse(schema))

    def __call__(self, event):
        return deferToThread(self.schema.assertValid, event.element)

