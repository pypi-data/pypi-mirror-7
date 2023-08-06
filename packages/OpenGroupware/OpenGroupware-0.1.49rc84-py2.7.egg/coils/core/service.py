# Copyright (c) 2009, 2013, 2014
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import sys  # We use .stdin, .stdout, .stderr, and .exit from sys
import os  # We use getpid and access envion from "os".
import time
import socket
import base64
import logging
import yaml
import traceback
import gc
from multiprocessing import Pipe
from packet import Packet
from broker import Broker
from coils.foundation.api import objgraph as COILS_objgraph
from coils.foundation import ServerDefaultsManager
from coils.foundation.api.amq import AMQPConnectionException


class Service(object):
    __auto_dispatch__ = False
    __is_worker__ = False
    __AMQDebugOn__ = None
    __ServiceDebugOn__ = None
    __TimeOut__ = 10
    # Queues will automatically expire after two days with no activity
    __AMQ_Expiration__ = 172800000
    RUNNING = True

    def __init__(self):

        self.hello_uuid = None
        os.environ['TZ'] = 'UTC'
        time.tzset()

        self.defaults_manager = ServerDefaultsManager()

        Service.__AMQDebugOn__ = \
            self.defaults_manager.bool_for_default('BusDebugEnabled')

        Service.__ServiceDebugOn__ = \
            self.defaults_manager.bool_for_default('ServiceDebugEnabled')

    @property
    def amq_debug(self):
        return Service.__AMQDebugOn__

    @property
    def service_debug(self):
        return Service.__ServiceDebugOn__

    @property
    def broker(self):
        return self._broker

    @property
    def bus_host_name(self):
        return base64.encodestring(socket.gethostname().lower())[:-1]

    def setup(self, silent=True):
        '''
        Initialize the component; this includes assigning the service
        component name, closing standard in/out/err, marshalling the
        broker and attaching to the message bus.  This methid is called
        prior to prepare().
        '''

        self.is_background = silent

        self._pid = os.getpid()
        self.__service__ = \
            self.__service__.replace('$$', str(os.getpid()))
        self.__service__ = \
            self.__service__.replace('##', str(self.bus_host_name))

        if self.is_background:
            sys.stdout.write(
                '{0}: Closing closing strdout/stdin/stderr [background]\n'.
                format(self.__service__, )
            )
            sys.stdout.flush()
            sys.stdin = open('/dev/null', 'r')
            sys.stdout = open('/dev/null', 'w')
            sys.stderr = open('/dev/null', 'w')
        else:
            sys.stdout.write(
                '{0}: Not closing stdout/stdin/stderr [foreground]\n'.
                format(self.__service__, )
            )
            sys.stdout.flush()

        self._broker = Broker()
        self.log = logging.getLogger(self.__service__)
        self._broker.subscribe(
            self.__service__,
            self.receive_message,
            expiration=self.__AMQ_Expiration__,
        )
        self.log.info(
            'Bus Debug Enabled: {0} ServiceDebugEnabled: {1}'.
            format(
                Service.__AMQDebugOn__,
                Service.__ServiceDebugOn__,
            )
        )

    def send(
        self,
        packet,
        callback=None,
        exchange='OpenGroupware_Coils',
        fanout=False,
    ):
        if self.amq_debug:
            self.log.debug(
                'Sending "{0}" to "{1}"'.
                format(
                    packet.uuid,
                    packet.target,
                )
            )
        self._broker.send(
            packet,
            callback=callback,
            exchange=exchange,
            fanout=fanout,
        )
        return packet.uuid

    def send_administrative_notice(
        self,
        subject=None,
        message=None,
        urgency=9,
        category='unspecified',
        attachments=[],
    ):
        # TODO: Support attachments
        try:
            self.send(
                Packet(
                    None,
                    'coils.administrator/notify',
                    {'urgency': urgency,
                     'category': category,
                     'subject': subject,
                     'message': message, },
                )
            )
        except KeyboardInterrupt:
            raise
        except Exception, e:
            self.log.error(
                'Exception attempting to send administrative notice'
            )
            self.log.exception(e)

    def shutdown(self):
        if self.service_debug:
                self.log.debug(
                    '{0} PID#{1} shutting down.'.
                    format(self.__service__, os.getpid(), )
                )
        if self.amq_debug:
            self.log.debug('Shutting down AMQ broker.')
        self._broker.close()
        if self.amq_debug:
            self.log.debug('AMQ broker is shutdown.')
        sys.exit(0)

    def receive_message(self, message):
        packet = self._broker.packet_from_message(message)
        if (packet is not None):
            if (self.amq_debug):
                self.log.debug(
                    'received {0} from {1}'.
                    format(
                        packet.uuid,
                        packet.source,
                    )
                )
            try:
                method = Packet.Method(packet.target).lower()
                parameter = Packet.Parameter(packet.target)
            except KeyboardInterrupt:
                raise
            except Exception, e:
                self.log.error(
                    'Error decoding packet target: {0}'.format(packet.target, )
                )
                self.log.exception(e)
            else:
                response = self.process(method, parameter, packet)
                if (response is not None):
                    self.send(response)

    def wait(self, timeout=None):
        self._broker.wait(timeout)

    def prepare(self):
        try:
            import procname
            procname.setprocname(self.__service__)
        except KeyboardInterrupt:
            raise
        except:
            self.log.info('Failed to set process name for service')
        '''
        packet = Packet(
            '{0}/__hello_ack'.format( self.__service__ ),
            'coils.master.{0}/__hello'.format( self.bus_host_name ),
            self.__service__ )
        self.hello_uuid = packet.uuid
        self.send( packet )
        '''
        if (self.amq_debug or self.service_debug):
            self.log.debug('Hello packet sent to master,')

    def do___ping(self, parameter, packet):
        return Packet.Reply(packet, packet.data)

    def do___hello(self, parameter, packet):
        return Packet.Reply(packet, packet.data)

    def do___hello_ack(self, parameter, packet):
        if (
            self.hello_uuid == packet.reply_to and
            str(packet.data) == self.__service__
        ):
            if (self.amq_debug or self.service_debug):
                self.log.debug(
                    'Recevied valid Hello ACK from {0}'.format(packet.source, )
                )

    def do___null(self, parameter, packet):
        pass

    def do___shutdown(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {'status': 200,
                 'text': 'Shutdown message received', },
            )
        )
        self.RUNNING = False

    def do___collect(self, parameter, packet):
        try:
            gc.collect()
        except:
            return Packet.Reply(
                packet,
                {'status': 500,
                 'text': 'Attempt to invoke GC failed', },
            )
        else:
            return Packet.Reply(packet, {'status': 201, 'text': 'OK'})

    def do___audit_address(self, parameter, packet):
        pass

    def do___audit_appointment(self, parameter, packet):
        pass

    def do___audit_collection(self, parameter, packet):
        pass

    def do___audit_contact(self, parameter, packet):
        pass

    def do___audit_document(self, parameter, packet):
        pass

    def do___audit_enterprise(self, parameter, packet):
        pass

    def do___audit_folder(self, parameter, packet):
        pass

    def do___audit_note(self, parameter, packet):
        pass

    def do___audit_process(self, parameter, packet):
        pass

    def do___audit_project(self, parameter, packet):
        pass

    def do___audit_route(self, parameter, packet):
        pass

    def do___audit_routegroup(self, parameter, packet):
        pass

    def do___audit_resource(self, parameter, packet):
        pass

    def do___audit_task(self, parameter, packet):
        pass

    def do___audit_team(self, parameter, packet):
        pass

    def do___reconfigure(self, parameter, packet):
        self.log.debug(
            'Reconfigure event received, service does not implement '
            'handling of configuration reload'
        )

    def do___types(self, parameter, packet):
        payload = COILS_objgraph.get_most_common_types(limit=25)
        self.log.info('responding to __types request')
        return Packet.Reply(
            packet,
            {'status': 200, 'text': 'OK', 'payload': payload, },
        )

    def process(self, method, parameter, packet):
        if (self.amq_debug or self.service_debug):
            self.log.debug('Processing message.')
        method = 'do_{0}'.format(method)
        if (hasattr(self, method)):
            if (self.amq_debug or self.service_debug):
                self.log.debug('Invoking method: {0}'.format(method))
            try:
                return getattr(self, method)(parameter, packet)
            except KeyboardInterrupt:
                raise
            except Exception, e:
                self.log.exception(e)
                message = (
                    'Exception in method {0} of component {1}.\n{2}'.
                    format(
                        method, self.__service__,
                        traceback.format_exc(),
                    )
                )
                self.send_administrative_notice(
                    subject=(
                        'Message processing xception in component {0}'.
                        format(self.__service__, )
                    ),
                    message=message,
                    urgency=8,
                    category='bus')
                raise e
            else:
                if (self.amq_debug or self.service_debug):
                    self.log.debug(
                        '{0} completed without exception'.format(method, )
                    )
        else:
            #if (self.service_debug):
            self.log.error('Service has no such method as {0}'.format(method))
        return None

    def work(self):
        pass

    def run(self, silent=True):
        self.RUNNING = True
        self.setup(silent=silent)
        self.prepare()
        if (self.service_debug):
            self.log.debug('Entering event loop.')
        while self.RUNNING:
            try:
                self.wait(timeout=self.__TimeOut__)
            except KeyboardInterrupt:
                self.shutdown()
            except AMQPConnectionException:
                self.shutdown()
            else:
                self.work()
