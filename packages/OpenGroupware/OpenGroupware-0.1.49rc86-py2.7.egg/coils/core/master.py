# Copyright (c) 2010, 2014
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

import logging
import multiprocessing
import datetime
import time
from service import Service
from packet import Packet


class MasterService(Service):
    __service__ = 'coils.master.##'
    __auto_dispatch__ = True
    __is_worker__ = False

    def __init__(self):
        Service.__init__(self)
        self._workers = {}
        self._counter = 0

    def prepare(self):
        try:
            import procname
            procname.setprocname(self.__service__)
        except:
            self.log.info('Failed to set process name for service')

    def start(self, is_background):
        self.__TimeOut__ = 2
        log = logging.getLogger('bootstrap')
        for name in self.service_list:
            try:
                service = self.get_service(name)
                p = multiprocessing.Process(
                    target=service.run, kwargs={'silent': is_background, }
                )
                self.append_process(name, p)
                self.get_process(name).start()
            except Exception, e:
                log.error('Failed to start service {0}'.format(name, ))
                log.exception(e)
                if not is_background:
                    print('Failed to start service {0}'.format(name))
                    print(e)
            else:
                log.info(
                    'Started service {0} as PID#{1}'.
                    format(name, self.get_process(name).pid, )
                )
                if not is_background:
                    print(
                        'Started service {0} as PID#{1}'.
                        format(name, self.get_process(name).pid, )
                    )
        log.info('All services started.')

    @property
    def service_list(self):
        return self._workers.keys()

    def append_service(self, name, target):
        self._workers[name] = [target, ]

    def append_process(self, name, process):
        self._workers[name].append(process)

    def drop_process(self, name, process):
        self._workers[name].remove(process)

    def get_service(self, name):
        return self._workers[name][0]

    def get_process(self, name):
        if len(self._workers[name]) == 2:
            return self._workers[name][1]
        return None

    def work(self):
        '''
        TODO: Component check should be a time-based, not iteration based,
        action
        '''
        self._counter += 1
        if (self._counter == 1) or ((self._counter % 5) == 0):
            for name in self.service_list:
                worker = self.get_process(name)
                if worker:
                    worker.join(0.1)
                    if worker.is_alive():
                        continue

                # Restart the component
                try:
                    print('Service component {0} not running'.format(name))
                    if worker:
                        self.log.debug('Component {0} has failed'.format(name))
                        self.send_administrative_notice(
                            subject='Component {0} has failed.'.format(name),
                            message='Component {0} has failed.'.format(name),
                            urgency=8,
                            category='core')
                        self.drop_process(name, worker)
                        self.log.debug(
                            'Dropped failed worker for {0}.'.format(name, )
                        )

                    service = self.get_service(name)
                    instance = service()
                    print(
                        'Background status is: {0}'.
                        format(self.is_background, )
                    )
                    p = multiprocessing.Process(
                        target=instance.run,
                        kwargs={'silent': self.is_background, },
                    )
                    self.append_process(name, p)
                    self.get_process(name).start()
                    if self._counter > 1:
                        self.log.debug('Component {0} restarted'.format(name))
                        self.send_administrative_notice(
                            subject='Component {0} restart.'.format(name),
                            message='Component {0} restart.'.format(name),
                            urgency=8,
                            category='core')
                    else:
                        self.log.debug('Component {0} started'.format(name))
                except Exception, e:
                    self.log.exception(e)
