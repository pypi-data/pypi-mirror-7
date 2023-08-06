#
# Copyright (c) 2011, 2013
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
from coils.core import NoSuchPathException, \
    CoilsException, \
    AccessForbiddenException, \
    BLOBManager, \
    NotImplementedException, \
    NotSupportedException
from coils.net import PathObject, Protocol
from viewobject import ViewObject
from entityobject import EntityObject


class AttachFS(Protocol, PathObject):
    __pattern__ = ['^attachfs$', '^public$', ]
    __namespace__ = None
    __xmlrpc__ = False

    def __init__(self, parent, **params):
        self.request = None
        self.entity = None
        self.parameters = None
        PathObject.__init__(self, parent, **params)

    def get_name(self):
        return 'attachfs'

    def is_public(self):
        if self._protocol_name == 'public':
            return True
        else:
            return False

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name in ('download', 'view')):
            return ViewObject(self, name,
                              request=self.request,
                              parameters=self.parameters,
                              context=self.context, )
        elif (name.isdigit()):
            kind = self.context.type_manager.get_type(int(name))
            if (kind.lower() in ('contact', 'enterprise', 'appointment',
                                 'task', 'process', 'route', 'file',
                                 'document', 'folder', 'project')):

                entity = self.context.type_manager.get_entity(long(name))
                if (entity is not None):
                    return EntityObject(self, name,
                                        request=self.request,
                                        entity=entity,
                                        parameters=self.parameters,
                                        context=self.context)
                else:
                    raise CoilsException(
                        'objectId#{0} [{1}] not available for attachment'.
                        format(name, kind))
            elif (kind == 'Unknown'):
                raise CoilsException(
                    'Unable to determine object type for id#{0}'.format(name))
            else:
                raise CoilsException(
                    'Cannot attach to objects of type "{0}".'.format(kind))
        else:
            raise NoSuchPathException('No such object as %s at path' % name)

    def do_HEAD(self):
        self.request.simple_response(
            200,
            data=None,
            mimetype=self.entity.get_mimetype(type_map=self._mime_type_map),
            headers={'etag': self.get_property_getetag(),
                     'Content-Length': str(self.entity.file_size), })

    def do_GET(self):
        self.request.simple_response(
            200,
            data='Login is {0}'.format(self.context))

    def do_POST(self):
        raise NotImplementedException('POST not supported by AttachFS')

    def do_PUT(self, name):
        payload = self.request.get_request_payload()
        mimetype = self.request.headers.get(
            'Content-Type', 'application/octet-stream')
        scratch_file = BLOBManager.ScratchFile()
        scratch_file.write(payload)
        scratch_file.seek(0)
        attachment = None
        attachment = self.context.run_command('attachment::new',
                                              handle=scratch_file,
                                              name=name,
                                              mimetype=mimetype, )
        self.context.commit()
        if (attachment is not None):
            self.request.simple_response(
                201,
                mimetype=mimetype,
                headers={'Content-Length': '0',
                         'Etag': attachment.uuid,
                         'Content-Type': attachment.mimetype, })
        else:
            # TODO; Can this happen without an exception having occurred?
            raise CoilsException('Ooops!')

    def do_DELETE(self, name):
        # TODO: Support If-Match header for concurrency?  Do we really believe
        #       any REST client or web-developer will bother to use it?
        DELETEABLES = ('contact', 'enterprise', 'appointment', 'task',
                       'process', 'route', 'file', 'document', 'folder',
                       'project', )

        # Document
        if name.isdigit():
            object_id = long(name)
            kind = self.context.type_manager.get_type(object_id).lower()
            if kind in DELETEABLES:
                entity = self.context.type_manager.get_entity(object_id)
                if not entity:
                    raise self.no_such_path()
                command = '{0}::delete'.format(kind)
                if not self.context.run_command(command, object=entity):
                    raise AccessForbiddenException(
                        'Insufficient access to delete object')
                self.context.commit()
                self.request.simple_response(
                    204,
                    headers={'X-OpenGroupware-Regarding': str(object_id), })
                return
            elif kind in ('none', 'unknown', ):
                raise NoSuchPathException(
                    'Entity OGo#{0} not available'.format(object_id, ))
            else:
                raise NotSupportedException(
                    'Objects of type "{0}" cannot be deleted via AttachFS'.
                    format(kind))

        # Attachment
        attachment = self.context.run_command('attachment::get', uuid=name)
        if attachment:
            if not self.context.run_command('attachment::delete',
                                            uuid=attachment.uuid):
                raise AccessForbiddenException(
                    'Insufficient access to delete attachment')
        else:
            raise NoSuchPathException('No attachment "{0}" found'.format(name))
        self.context.commit()
        self.request.simple_response(
            204,
            headers={'X-OpenGroupware-Regarding': name, })
