#!/usr/bin/env python

# Copyright 2009-2014 Eucalyptus Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from config_manager.baseconfig import BaseConfig, EucalyptusProperty


class Eucalyptus(BaseConfig):
    def __init__(self):
        super(Eucalyptus, self).__init__(name=None,
                                         description=None,
                                         write_file_path=None,
                                         read_file_path=None,
                                         version=None)
        self.log_level = self.create_property(json_name='log-level')
        self.set_bind_addr = self.create_property('set_bind_addr', value=True)
        self.eucalyptus_repo = self.create_property('eucalyptus-repo')
        self.euca2ools_repo = self.create_property('euca2ools-repo')
        self.enterprise_repo = self.create_property('enterprise-repo')
        self.enterprise = self.create_property('enterprise')
        self.nc = self.create_property('nc')
        self.topology = self.create_property('topology')
        self.network = self.create_property('network')
        self.system_properties = self.create_property('system_properties')
        self.install_load_balancer = self.create_property(
            'install-load-balancer', value=True)
        self.install_imaging_worker = self.create_property('install-imaging-worker', value=True)

        self.use_dns_delegation = self._set_eucalyptus_property(
            name='bootstrap.webservices.use_dns_delegation', value=True)
        self.eucalyptus_props = self.create_property('eucaprops', value=self.eucalyptus_prop_getter)

    @property
    def eucalyptus_prop_getter(self):
        return self.get_eucalyptus_props_from_everywhere()

    def get_eucalyptus_props_from_everywhere(self):
        property_dict = {}
        return property_dict

        # if self._eucalyptus_properties:
        #     for eucalyptus_property in self._eucalyptus_properties:
        #         property_dict[eucalyptus_property.name] = eucalyptus_property.value
        # return property_dict
        # myd = {}
        # myd['test'] = 'blah'
        # myd['test2'] = 'blhaslskdfj'
        # return myd

    def add_topology(self, topology):
        self.topology.value = topology

    def set_log_level(self, log_level):
        self.log_level.value = log_level
