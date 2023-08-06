# Copyright 2013 Openstack Foundation
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
import webob.dec
import webob.exc

import wafflehaus.base
import wafflehaus.resource_filter as rf


class BlockResource(wafflehaus.base.WafflehausBase):

    def __init__(self, app, conf):
        super(BlockResource, self).__init__(app, conf)
        self.log.name = conf.get('log_name', __name__)
        self.log.info('Starting wafflehaus resource blocker middleware')
        self.resources = rf.parse_resources(conf.get('resource'))

    def _override(self, req):
        super(BlockResource, self)._override(req)
        new_resource = self._reconf(req, 'str', 'resource')
        if new_resource is not None:
            self.resources = rf.parse_resources(new_resource)

    @webob.dec.wsgify
    def __call__(self, req):
        super(BlockResource, self).__call__(req)
        if not self.enabled:
            return self.app

        if rf.matched_request(req, self.resources):
            self.log.info("Blocked " + str(req.path))
            return webob.exc.HTTPForbidden()
        return self.app


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def block_resource(app):
        return BlockResource(app, conf)
    return block_resource
