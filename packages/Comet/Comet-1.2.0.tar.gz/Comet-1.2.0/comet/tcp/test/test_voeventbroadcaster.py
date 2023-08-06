import lxml.etree as etree

from twisted.internet import reactor
from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DUMMY_IAMALIVE
from ...test.support import DUMMY_ACK
from ...test.support import DUMMY_NAK
from ...test.support import DUMMY_AUTHENTICATE
from ...test.support import DUMMY_AUTHENTICATE_RESPONSE
from ...test.support import DUMMY_AUTHENTICATE_RESPONSE_LEGACY
from ...test.support import DUMMY_VOEVENT
from ...test.support import DUMMY_EVENT_IVORN
from ...test.support import DUMMY_SERVICE_IVORN
from ...test.support import DummyEvent

from ..protocol import VOEventBroadcaster
from ..protocol import VOEventBroadcasterFactory
from ...service.broker import BCAST_TEST_INTERVAL

class DummyBroadcaster(object):
    def __init__(self):
        self.received_alive = False
        self.received_event = False

    def sendIAmAlive(self):
        self.received_alive = True

    def send_event(self, event):
        self.received_event = True


class VOEventBroadcasterFactoryTestCaseBase(unittest.TestCase):
    def setUp(self, test_interval=BCAST_TEST_INTERVAL):
        self.factory = VOEventBroadcasterFactory(
            DUMMY_SERVICE_IVORN, test_interval
        )
        self.factory.alive_loop.clock = task.Clock()
        self.factory.test_loop.clock = task.Clock()
        self.factory.broadcasters.append(DummyBroadcaster())
        self.connector = reactor.listenTCP(0, self.factory)

    def tearDown(self):
        self.connector.stopListening()


class VOEventBroadcasterFactoryTestCase(VOEventBroadcasterFactoryTestCaseBase):
    def test_protocol(self):
        self.assertEqual(self.factory.protocol, VOEventBroadcaster)

    def test_sendIamAlive(self):
        self.assertEqual(self.factory.alive_loop.running, True)
        self.factory.alive_loop.clock.advance(self.factory.IAMALIVE_INTERVAL)
        for broadcaster in self.factory.broadcasters:
            self.assertEqual(broadcaster.received_alive, True)

    def test_sendTestEvent(self):
        self.assertEqual(self.factory.test_loop.running, True)
        self.factory.test_loop.clock.advance(BCAST_TEST_INTERVAL)
        for broadcaster in self.factory.broadcasters:
            self.assertEqual(broadcaster.received_event, True)


class VOEventBroadcasterFactoryNoTestEventsTestCase(VOEventBroadcasterFactoryTestCaseBase):
    # In this special case, we cause the factory not to broadcast test events
    # to the network.
    def setUp(self):
        VOEventBroadcasterFactoryTestCaseBase.setUp(self, 0)

    def test_DoNotSendTestEvent(self):
        self.assertEqual(self.factory.test_loop.running, False)
        self.factory.test_loop.clock.advance(BCAST_TEST_INTERVAL)
        for broadcaster in self.factory.broadcasters:
            self.assertEqual(broadcaster.received_event, False)


class VOEventBroadcasterTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = VOEventBroadcasterFactory(
            DUMMY_SERVICE_IVORN, BCAST_TEST_INTERVAL
        )
        self.factory.alive_loop.clock = task.Clock()
        self.factory.test_loop.clock = task.Clock()
        self.connector = reactor.listenTCP(0, self.factory)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def tearDown(self):
        self.connector.stopListening()

    def test_register_broadcaster(self):
        # Should now be a broadcaster registered with the factory
        self.assertIn(self.proto, self.factory.broadcasters)

    def test_sent_authenticate(self):
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("authenticate", received_element.attrib['role'])
        self.assertEqual(DUMMY_SERVICE_IVORN, received_element.find('Origin').text)

    def test_sendIAmAlive(self):
        self.tr.clear()
        init_alive_count = self.proto.alive_count
        self.factory.alive_loop.clock.advance(self.factory.IAMALIVE_INTERVAL)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("iamalive", received_element.attrib['role'])
        self.assertEqual(DUMMY_SERVICE_IVORN, received_element.find('Origin').text)
        self.assertEqual(self.proto.alive_count - init_alive_count, 1)

    def test_alive_timeout(self):
        self.assertEqual(self.tr.connected, True)
        for x in range(self.proto.MAX_ALIVE_COUNT + 1):
            self.proto.sendIAmAlive()
        self.assertEqual(self.tr.connected, False)

    def test_lack_of_ack(self):
        self.assertEqual(self.tr.connected, True)
        self.proto.outstanding_ack = self.proto.MAX_OUTSTANDING_ACK + 1
        self.proto.sendIAmAlive()
        self.assertEqual(self.tr.connected, False)

    def test_send_event(self):
        # Note lack of filter!
        self.tr.clear()
        init_outstanding_ack = self.proto.outstanding_ack
        self.proto.send_event(DummyEvent())
        self.assertEqual(self.tr.value()[4:], DummyEvent().text)
        self.assertEqual(self.proto.outstanding_ack - init_outstanding_ack, 1)

    def test_send_event_with_filter_reject(self):
        def check_output(result):
            self.assertEqual(self.tr.value(), "")
        init_outstanding_ack = self.proto.outstanding_ack
        def check_ack_increment(result):
            self.assertEqual(self.proto.outstanding_ack - init_outstanding_ack, 0)
        self.tr.clear()
        self.proto.filters.append(
            etree.XPath("/*[local-name()=\"VOEvent\" and @role!=\"test\"]")
        ) # Will reject dummy event with role "test"
        d = self.proto.send_event(DummyEvent())
        d.addCallback(check_output)
        d.addCallback(check_ack_increment)
        return d

    def test_send_event_with_filter_accept(self):
        def check_output(result):
            self.assertEqual(self.tr.value()[4:], DummyEvent().text)
        init_outstanding_ack = self.proto.outstanding_ack
        def check_ack_increment(result):
            self.assertEqual(self.proto.outstanding_ack - init_outstanding_ack, 1)
        self.tr.clear()
        self.proto.filters.append(
            etree.XPath("/*[local-name()=\"VOEvent\" and @role=\"test\"]")
        ) # Will accept dummy event with role "test"
        d = self.proto.send_event(DummyEvent())
        d.addCallback(check_output)
        d.addCallback(check_ack_increment)
        return d

    def test_receive_unparsable(self):
        # An unparsable message should generate no response, but the
        # transport should not disconnect.
        self.tr.clear()
        unparsable = "This is not parsable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparsable)
        self.proto.stringReceived(unparsable)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, True)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        self.tr.clear()
        incomprehensible = "<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, True)

    def test_receive_iamalive(self):
        self.tr.clear()
        init_alive_count = self.proto.alive_count
        self.proto.stringReceived(DUMMY_IAMALIVE)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(init_alive_count - self.proto.alive_count, 1)

    def test_receive_ack(self):
        self.tr.clear()
        init_outstanding_ack = self.proto.outstanding_ack
        self.proto.stringReceived(DUMMY_ACK)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(init_outstanding_ack - self.proto.outstanding_ack, 1)

    def test_receive_nak(self):
        self.tr.clear()
        self.proto.stringReceived(DUMMY_NAK)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, False)

    def _test_sets_filter(self, filter_list):
        self.tr.clear()
        self.assertEqual(len(self.proto.filters), 0)
        self.proto.stringReceived(DUMMY_AUTHENTICATE_RESPONSE(filter_list).text)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, True)
        self.assertEqual(len(self.proto.filters), len(filter_list))

    def test_receive_authenticateresponse_with_filters(self):
        self._test_sets_filter([
            "/*[local-name()=\"VOEvent\" and @role=\"test\"]",
            "//Param[@name=\"SC_Lat\" and @value<600]"
        ])

    def test_receive_authenticateresponse_legacy(self):
        # The legacy forma is in violation of the Transport schema. We no
        # longer generate packets that look like this, but the broker still
        # recognizes them.
        demo_filter =  "//Param[@name=\"SC_Lat\" and @value&lt;600]"
        self.tr.clear()
        self.assertEqual(len(self.proto.filters), 0)
        self.proto.stringReceived(DUMMY_AUTHENTICATE_RESPONSE_LEGACY % demo_filter)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, True)
        self.assertEqual(len(self.proto.filters), 1)

    def test_receive_authenticateresponse_with_bad_filter(self):
        self.tr.clear()
        self.assertEqual(len(self.proto.filters), 0)
        self.proto.stringReceived(
            DUMMY_AUTHENTICATE_RESPONSE(["Not a valid XPath expression"]).text
        )
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, True)
        self.assertEqual(len(self.proto.filters), 0)
