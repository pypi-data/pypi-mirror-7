#
# Copyright (c) 2011, 2013, 2014
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import os  # We use .getpid from "os".  Generally using "os" is considered BAD
import traceback
import logging
import multiprocessing
import time
from Queue import Empty as EmptyQueue
from threading import Thread
from packet import Packet
from broker import Broker
from coils.foundation import ServerDefaultsManager
from service import Service
from worker_events import \
    AMQ_RECEIVED, \
    AMQ_TRANSMIT, \
    AMQ_ACKNOWLEDGE, \
    AMQ_FAIL, \
    AMQ_TIMEOUT, \
    WORKER_ERROR, \
    SEND_ADMIN_NOTICE, \
    AP_SCHEDULE_FIRE, \
    WORKER_RECONFIGURE

from apscheduler.scheduler import Scheduler
from apscheduler.triggers import SimpleTrigger, IntervalTrigger, CronTrigger
from apscheduler.jobstores.ram_store import RAMJobStore


class ThreadedService(Service):
    '''
    ThreadedService extends Service but uses a dictionary of threads, one
    thread listens on the AMQ connection - threads can feed the thread-safe
    queue to create a simple main-loop.  ThreadedService can thus receive
    messages, as well as listen for other events (in custom threads), and
    still provide a simple syncronous main-loop.
    '''
    __auto_dispatch__ = False
    __is_worker__ = False
    __TimeOut__ = 10
    threads = {}  # Dictionary of worker threads maintained by the service

    def __init__(self):
        Service.__init__(self)
        self._event_queue = multiprocessing.Queue(maxsize=4096)
        self._work_queue = multiprocessing.Queue(maxsize=4096)
        self.threads['amqRx'] = \
            Thread(
                target=self.listen_to_bus,
                name='amqReceiver',
                args=(self, ),
            )
        self._workers = {}

    def start_workers(self, count, classname, name_generator):
        for counter in range(count):
            name = name_generator()
            worker = classname(
                name=name,
                work_queue=self._work_queue,
                event_queue=self.event_queue,
                silent=self.is_background,
            )
            self._workers[name] = worker
            self._workers[name].start()
            self.log.debug('Worker "{0}" started'.format(name, ))

    def stop_workers(self):

        if not self._workers:
            return

        counter = len(self._workers) * 10
        while self._workers and counter:
            counter += -1
            for name, worker in self._workers.items():
                if worker.is_alive():
                    self.enqueue_work(None, None, target=name, )
                    self.log.debug(
                        'Requesting worker "{0}" self-terminate.'.
                        format(name),
                    )
                    worker.join(0.1)
                else:
                    self.log.debug(
                        'Worker successfully "{0}" self-terminated.'.
                        format(name, )
                    )
                    del self._workers[name]
            time.sleep(0.1)

        # Forcibly terminate any workers still alive
        if self._workers:
            for name, worker in self._workers.items():
                if worker.is_alive():
                    self.log.warn('Terminating worker "{0}"'.format(name))
                    worker.terminate()

        # Drain the work queue
        self.log.warn('Draining event queue')
        while not self._work_queue.empty():
            try:
                self._work_queue.get_nowait()
            except EmptyQueue:
                break
        self._work_queue.close()
        self.log.debug('All workers terminated, work queue is empty.')

    def stop_threads(self):

        # Join the threads until shutdown
        counter = len(self.threads) * 10
        while self.threads and counter:
            counter += -1
            for name, thread in self.threads.items():
                if thread.is_alive():
                    self.log.info(
                        'Waiting for thread "{0}" to terminate (cycle#{1})'.
                        format(name, counter, )
                    )
                    thread.join(0.2)
                else:
                    self.log.info('Thread "{0}" has terminated'.format(name, ))
                    del self.threads[name]
            '''
            We send an empty packet to ourselves to ensure the AMQ Rx
            thread wakes up from select
            '''
            self.send(
                Packet(
                    None,
                    '{0}/__null'.format(self.__service__, ),
                    {},
                )
            )
            time.sleep(0.2)
        if self.threads:
            self.log.error('There are remaining non-terminated threads!')

        # Drain the event queue
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except EmptyQueue:
                break
        self._event_queue.close()
        self.log.debug('Event queue is empty.')

    def enqueue_work(self, command, payload, target=None, ):
        self._work_queue.put((command, payload, target, ), True, 1, )

    #
    # Properties
    #

    @property
    def event_queue(self):
        return self._event_queue

    @property
    def is_shutdown(self):
        return not self.RUNNING

    #
    # Setup / Prepare
    #

    def subscribe_to_fanout_exchange(self):
        '''
        Subscribe to the fan-out exchange in order to receive audit events.
        The Broker mush already be initialized when this method is called.
        '''
        if not self._broker:
            raise CoilsException(
                'Attempt to subscribe to fanout exchange but Broker'
                'is not available.'
            )
        self._broker.subscribe(
            '{0}.events'.format(self.__service__, ),
            self.receive_message,
            expiration=900000,
            queue_type='fanout',
            durable=False,
            exchange_name='OpenGroupware_Coils_Notify',
        )

    def setup(self, silent=True):
        '''
        Perform service setup and start all the registered threads.
        '''
        Service.setup(self, silent=silent, )

        # Statup the APSchedular
        self._ap_scheduler = Scheduler()
        self._ap_scheduler.add_jobstore(
            RAMJobStore(),
            'service_schedule',
        )
        self._ap_scheduler.configure(misfire_grace_time=58, )
        self._ap_scheduler.start()
        self.log.debug('Scheduler started')

    def prepare(self):
        '''
        Perform post setup Service preperation for run-loop
        '''
        Service.prepare(self)
        for name, thread in self.threads.items():
            self.log.info('Starting thread "{0}"'.format(name, ))
            thread.start()
            thread.join(0.1)
            self.log.info('Thread "{0}" started'.format(name, ))

    #
    # Schedular Plumbing
    #

    def schedule_at_interval(
        self,
        name,
        weeks=0,
        days=0,
        hours=0,
        minutes=0,
        seconds=0,
        start_date=None,
        message=None,
        data=None,
    ):
        if message:
            self._ap_scheduler.add_interval_job(
                name=name,
                weeks=weeks,
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                start_date=start_date,
                func=self.receive_schedule_event,
                args=(message, data, ),
            )
            self.log.debug(
                'Scheduler interval job "{0}" created'.
                format(name, )
            )
    #
    # Component Plumbing
    #

    def shutdown(self):
        '''
        Change the running state to False, wait for all the threads to
        terminate, then shutdown the Broker and exit.
        '''
        self.RUNNING = False
        self.log.info(
            'Service "{0}" (PID#{1}) shutting down.'.
            format(self.__service__, os.getpid(), )
        )

        self.log.debug('Stopping scheduler')
        self._ap_scheduler.shutdown()

        self.log.debug('Stopping threads')
        self.stop_threads()

        self.log.debug('Stopping workers')
        self.stop_workers()

        if self.amq_debug:
            self.log.debug('Shutting down AMQ broker.')

        self._broker.close()

        if self.amq_debug:
            self.log.debug('AMQ broker is shutdown.')

        sys.exit(0)

    def listen_to_bus(self, service):
        '''
        Thread method, this listens to the AMQ bus and puts received
        messages on the event queue
        '''
        if self.amq_debug:
            self.log.debug('Spinning up AMQ bus listener')
        while self.RUNNING:
            if self._broker.wait(timeout=self.__TimeOut__):
                if self.amq_debug:
                    self.log.debug('AMQ Bus Timeout')
                self.event_queue.put((AMQ_TIMEOUT, ))
        if self.amq_debug:
            self.log.debug('AMQ bus listener shutdown')
        return

    def receive_message(self, message):
        '''
        Called as a handler by the Broker when an AMQ message is recieved.
        Attempts to decode the message into a Packet and place it on the queue
        for processing.
        '''
        packet = self._broker.packet_from_message(message)
        if packet:
            if self.amq_debug:
                self.log.debug(
                    'received "{0}" from "{1}"'.
                    format(packet.uuid, packet.source, )
                )
            self.event_queue.put((AMQ_RECEIVED, packet, ))

    def process_packet(self, packet):
        '''
        Called by process_event to deal with an AMQ packet.
        '''
        try:
            method = Packet.Method(packet.target).lower()
            parameter = Packet.Parameter(packet.target)
        except Exception, e:
            self.log.error(
                'Error decoding packet target: {0}'.
                format(packet.target, )
            )
            self.log.exception(e)
            return False
        else:
            response = self.process_message(method, parameter, packet)
            if (response is not None):
                self.send(response)
            return True

    def receive_schedule_event(self, message, data, ):
        self.event_queue.put((message, data, ))
        self.log.debug('Schedule message "{0}" delivered'.format(message, ))
        return

    def process_message(self, method, parameter, packet):
        '''
        Deal with a message from the AMQ bus, mapped to a do_* handler
        '''
        if (self.amq_debug or self.service_debug):
            self.log.debug('Processing message.')
        method = 'do_{0}'.format(method)
        if (hasattr(self, method)):
            if self.amq_debug or self.service_debug:
                self.log.debug('Invoking method: {0}'.format(method))
            try:
                return getattr(self, method)(parameter, packet)
            except Exception, e:
                self.log.exception(e)
                message = (
                    'Exception in method {0} of component {1}.\n{2}'.
                    format(
                        method,
                        self.__service__,
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
                    category='bus',
                )
                raise e
            else:
                if (self.amq_debug or self.service_debug):
                    self.log.debug(
                        '{0} completed without exception'.
                        format(method, )
                    )
        else:
            self.log.error('Service has no such method as {0}'.format(method))
        return None

    def process_service_specific_event(self, event_class, event_data):
        '''
        Children can override this to process events of their own very
        special types
        '''
        return

    def process_event(self, event):
        '''
        Deal with an event off the event queue
        '''
        if event[0] == AMQ_RECEIVED:
            self.process_packet(event[1])
        elif event[0] == AMQ_TIMEOUT:
            self.work()
        elif event[0] == WORKER_ERROR:
            self.send_administrative_notice(
                subject='Service worker encountered unexpected exception',
                message=event[1],
                urgency=8,
                category='unknown',
            )
        elif event[0] == SEND_ADMIN_NOTICE:
            self.send_administrative_notice(
                subject=event[1][0],
                message=event[1][1],
                urgency=event[1][2],
                category=event[1][3])
        else:
            self.process_service_specific_event(
                event[0], event[1],
            )

    def run(self, silent=True):
        '''
        Go into the event processing loop.
        '''

        self.RUNNING = True

        self.setup(silent=silent)
        if self.service_debug:
            self.log.debug('Service setup complete.')
        self.log.debug('Service setup complete.')
        self.prepare()
        if self.service_debug:
            self.log.debug('Service prepared for run.')
        self.log.debug('Service prepared for run.')
        self.log.debug('Entering event loop.')
        while self.RUNNING:
            try:
                event = self.event_queue.get()
                self.process_event(event)
            except KeyboardInterrupt:
                self.RUNNING = False
        self.shutdown()

    def work(self):
        pass

    #
    # Core method handlers
    #

    def do___shutdown(self, parameter, packet):
        '''
        Received a message to stop running, reply and switch to shutdown mode.
        '''
        self.send(
            Packet.Reply(
                packet,
                {'status': 200,
                 'text': 'OK', },
            )
        )
        self.log.info('Received a shutdown request.')
        self.RUNNING = False

    def do___reconfigure(self, parameter, packet):
        if not self._workers:
            return
        for name, worker in self._workers.items():
            if worker.is_alive():
                self.log.debug(
                    'Sending reconfigure event to {0}'.
                    format(name, )
                )
                self.enqueue_work(
                    WORKER_RECONFIGURE,
                    None,
                    target=name,
                )
