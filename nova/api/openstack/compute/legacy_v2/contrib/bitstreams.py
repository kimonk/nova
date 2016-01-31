# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import webob.exc

from nova.api.openstack import common
from nova.api.openstack.compute.views import images as views_images
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova import exception
from nova.i18n import _
import nova.image
import nova.utils
import pydevd
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
ALIAS = 'bitstreams'

SUPPORTED_FILTERS = {
    'name': 'name',
    'status': 'status',
    'changes-since': 'changes-since',
    'server': 'property-instance_uuid',
    'type': 'property-image_type',
    'minRam': 'min_ram',
    'minDisk': 'min_disk',
}


class bitstreamsController(wsgi.Controller):
    """Base controller for retrieving/displaying bitstreams."""

    _view_builder_class = views_images.ViewBuilder

    def __init__(self, **kwargs):

        super(bitstreamsController, self).__init__(**kwargs)
        self._image_api = nova.image.API()

    def _get_filters(self, req):
        """Return a dictionary of query param filters from the request.

        :param req: the Request object coming from the wsgi layer
        :retval a dict of key/value filters
        """
        filters = {}
        for param in req.params:
            if param in SUPPORTED_FILTERS or param.startswith('property-'):
                # map filter name or carry through if property-*
                filter_name = SUPPORTED_FILTERS.get(param, param)
                filters[filter_name] = req.params.get(param)

        # ensure server filter is the instance uuid
        filter_name = 'property-instance_uuid'
        try:
            filters[filter_name] = filters[filter_name].rsplit('/', 1)[1]
        except (AttributeError, IndexError, KeyError):
            pass

        filter_name = 'status'
        if filter_name in filters:
            # The Image API expects us to use lowercase strings for status
            filters[filter_name] = filters[filter_name].lower()

        return filters

    @extensions.expected_errors(404)
    def show(self, req, id):
        """Return detailed information about a specific bitstreams given its bitstreams (image)
        .

        :param req: `wsgi.Request` object
        :param id: Image identifier
        """

        context = req.environ['nova.context']

        try:
            image = self._image_api.get(context, id)
        except (exception.ImageNotFound, exception.InvalidImageRef):
            explanation = _("Image not found.")
            raise webob.exc.HTTPNotFound(explanation=explanation)
        if image.get("properties", {}).get("is-vnf") is not None:
            if image.get("properties", {}).get("is-vnf") == 'True':
                # LOG.debug("the property is %s", isvnf)

                #(tNova spec: Check the is-vnf property of the stored in glance imgage. If true the image obj is returned

                req.cache_db_items('images', [image], 'id')
                return self._view_builder.show(req, image)
        else:
            return None


    @extensions.expected_errors((403, 404))
    @wsgi.response(204)
    def delete(self, req, id):
        """Delete an image, if allowed.

        :param req: `wsgi.Request` object
        :param id: Image identifier (integer)
        """
        context = req.environ['nova.context']
        try:
            self._image_api.delete(context, id)
        except exception.ImageNotFound:
            explanation = _("Image not found.")
            raise webob.exc.HTTPNotFound(explanation=explanation)
        except exception.ImageNotAuthorized:
            # The image service raises this exception on delete if glanceclient
            # raises HTTPForbidden.
            explanation = _("You are not allowed to delete the image.")
            raise webob.exc.HTTPForbidden(explanation=explanation)

    @extensions.expected_errors(400)
    def index(self, req):
        """Return an index listing of images available to the request.

        :param req: `wsgi.Request` object

        """
        context = req.environ['nova.context']
        filters = self._get_filters(req)
        page_params = common.get_pagination_params(req)

        bitstreams=[]

        try:
            images = self._image_api.get_all(context, filters=filters,
                                             **page_params)
        except exception.Invalid as e:
            raise webob.exc.HTTPBadRequest(explanation=e.format_message())

        LOG.debug("images size is %s", images.__len__())
       # pydevd.settrace('192.168.1.4',port=5678, stdoutToServer=True, stderrToServer=True, suspend=True)

        for image in images:
             LOG.debug("image is %s", image.get("name"))
           # if not image.get("properties", {}).get("is-vnf") is not None:
                #LOG.debug("the property is %s", image.get("properties", {}).get("is-vnf"))
             if image.get("properties", {}).get("is-vnf") =="True":
                #LOG.debug("removed %s ", image.get("name"))
                bitstreams.append(image)
                #images.remove(image)
                #LOG.debug("size is now %s",images.__len__())


        return self._view_builder.index(req, bitstreams)

    @extensions.expected_errors(400)
    def detail(self, req):
        """Return a detailed index listing of images available to the request.
q
        :param req: `wsgi.Request` object.

        """
        context = req.environ['nova.context']
        filters = self._get_filters(req)
        page_params = common.get_pagination_params(req)
        try:
            images = self._image_api.get_all(context, filters=filters,
                                             **page_params)
        except exception.Invalid as e:
            raise webob.exc.HTTPBadRequest(explanation=e.format_message())

        req.cache_db_items('images', images, 'id')
        return self._view_builder.detail(req, images)


class Bitstreams(extensions.V21APIExtensionBase):
    """Proxying API for Images."""

    name = "bitstreams"
    alias = ALIAS
    version = 1

    def get_resources(self):
        coll_actions = {'detail': 'GET'}
        resource = extensions.ResourceExtension(ALIAS,
                bitstreamsController(),
                collection_actions=coll_actions)

        return [resource]

    def get_controller_extensions(self):
        return []
