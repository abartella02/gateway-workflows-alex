# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2020-06-10
# Gateway Version: 20.12.1
# Description: Isolator with Kompira Cloud Sonar Integration.py

import os
import json
import ipaddress

from datetime import datetime, timedelta
from dateutil import parser
from threading import Lock

from bluecat import util
from bluecat.util import safe_str
from bluecat.entity import Entity
from bluecat.api_exception import BAMException, PortalException

from sonar.sonarapi import SonarAPI
from dnsedge.edgeapi import EdgeAPI

#
# Should be in API
#
def denyMACAddress(configuration, macaddr):
    try:
        configuration._api_client.service.denyMACAddress(configuration.get_id(), macaddr)
    except WebFault as e:
        print('Exception at denyMACAddress(%s)' % util.safe_str(e))
        raise BAMException(safe_str(e))
        
class IsolatorWithSonarException(Exception): pass

class IsolatorWithSonar(object):
    _unique_instance = None
    _lock = Lock()
    _config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.json'

    @classmethod
    def __internal_new__(cls):
        return super().__new__(cls)

    @classmethod
    def get_instance(cls, debug=False):
        if cls._unique_instance is None:
            with cls._lock:
                if cls._unique_instance is None:
                    cls._unique_instance = cls.__internal_new__()
                    cls._unique_instance._debug = debug
                    cls._unique_instance._nodes = []
                    cls._unique_instance._load()
        return cls._unique_instance

    def _load(self):
        with open(IsolatorWithSonar._config_file) as f:
            self._config = json.load(f)

    def get_value(self, key):
        value = None
        with IsolatorWithSonar._lock:
            if key in self._config.keys():
                value = self._config[key]
        return value

    def set_value(self, key, value):
        with IsolatorWithSonar._lock:
            self._config[key] = value

    def get_nodes(self):
        nodes = []
        with IsolatorWithSonar._lock:
            nodes = self._nodes
        return nodes

    def set_nodes(self, nodes):
        with IsolatorWithSonar._lock:
            self._nodes = nodes

    def clear_nodes(self):
        with IsolatorWithSonar._lock:
            self._nodes = []

    def save(self):
        with IsolatorWithSonar._lock:
            with open(IsolatorWithSonar._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def _get_assignable_name(self, node):
        assignalbe_name = ''
        try:
            ipaddress.IPv4Address(node['name'])
        except ipaddress.AddressValueError:
            assignalbe_name = node['name']
        return assignalbe_name

    def _construct_sonar_url(self, sonar_api, node):
        return sonar_api.get_node_detail_url(node['network_id'], node['id'])
        
    def _construct_linked_name(self, sonar_api, node):
        return "<a href='%s'  target='_blank'>%s</a>" % \
            (self._construct_sonar_url(sonar_api, node), node['name'])

    def _collect_nodes(self, configuration, sonar_api, network_id):
        nodes = []
        now = datetime.now()
        sonar_nodes = sonar_api.get_nodes(network_id)
        
        for sn in sonar_nodes:
            for ad in sn['addresses']:
                node = {}
                node['id'] = sn['managedNodeId']
                node['network_id'] = network_id
                node['order'] = util.ip42int(ad['addr'])
                node['name'] = sn['displayName']
                node['system'] = sn['system']['family']
                
                if node['system'] == '':
                    try:
                        node['system'] = ad['extraFields']['macaddr']['organizationName']
                    except:
                        pass
                        
                node['ipaddr'] = ad['addr']
                node['macaddr'] = ad['macaddr'].upper().replace(':', '-')
                node['detail_link'] = self._construct_sonar_url(sonar_api, node)
                node['linked_name'] = self._construct_linked_name(sonar_api, node)
                
                node['last_found'] = sn['lastScanSucceededAt']
                lastfound = parser.parse(sn['lastScanSucceededAt'])
                lastfound = lastfound.replace(tzinfo=None)
                if (now - lastfound) < timedelta(days=30):
                    node['state'] = 'UNKNOWN'
                    nodes.append(node)
        nodes.sort(key = lambda node: node['order'])
        
        return nodes

    def _collect_ip4_networks(self, configuration, ip4_networks, ipaddr):
        pack_address = util.ip42int(ipaddr)
        for ip4_network in ip4_networks:
            cidr = ip4_network.get_property('CIDR')
            network = ipaddress.IPv4Network(cidr)
            start_address = util.ip42int(str(network.network_address))
            end_address = util.ip42int(str(network.broadcast_address))
            if start_address <= pack_address <= end_address:
                return
                
        try:
            found = configuration.get_ip_range_by_ip(Entity.IP4Network, ipaddr)
            if found is not None:
                ip4_networks.append(found)
                
        except PortalException as e:
            print(safe_str(e))
            
    def _compare_nodes(self, configuration, nodes):
        ip4_networks = []
        include_matches = self.get_value('include_matches')
        
        for node in nodes:
            self._collect_ip4_networks(configuration, ip4_networks, node['ipaddr'])
            
        for ip4_network in ip4_networks:
            ip4_addresses = ip4_network.get_children_of_type(Entity.IP4Address)
            for ip4_address in ip4_addresses:
                founds = [node for node in nodes if node['ipaddr'] == ip4_address.get_address()]
                if 0 < len(founds):
                    macaddress = ip4_address.get_property('macAddress')
                    found = founds[0]
                    if found['macaddr'] != macaddress:
                        found['state'] = 'MISMATCH'
                    else:
                        try:
                            mac_address = configuration.get_mac_address(macaddress)
                            source = mac_address.get_property('ImportedSource')
                            if source is not None and source != '':
                                found['state'] = 'MATCH'
                        except PortalException as e:
                            pass
                    if include_matches == False and found['state'] == 'MATCH':
                        nodes.remove(found)
                    
        nodes.sort(key = lambda node: node['order'])
        
    def _update_mac_by_node(self, configuration, node):
        mac_address = None
        assignalbe_name = self._get_assignable_name(node)
        try:
            mac_address = configuration.get_mac_address(node['macaddr'])
            if mac_address.get_name() is None and assignalbe_name != '':
                mac_address.set_name(assignalbe_name)
        except PortalException as e:
            mac_address = configuration.add_mac_address(node['macaddr'], assignalbe_name)
            
        mac_address.set_property('DetailLink', node['detail_link'])
        mac_address.set_property('System', node['system'])
        mac_address.set_property('ImportedSource', 'Sonar')
        mac_address.update()

    def _assigne_by_node(self, configuration, node):
        try:
            iprange = configuration.get_ip_range_by_ip('DHCP4Range', node['ipaddr'])
        except PortalException as e:
            properties='name=' + self._get_assignable_name(node)
            ipaddress = \
                configuration.assign_ip4_address(node['ipaddr'], \
                    node['macaddr'], '', 'MAKE_STATIC', properties=properties)
        self._update_mac_by_node(configuration, node)

    def _update_by_node(self, configuration, node):
        try:
            ipaddress = configuration.get_ip4_address(node['ipaddr'])
            assignalbe_name = self._get_assignable_name(node)
            if ipaddress.get_name() is None and assignalbe_name != '':
                ipaddress.set_name(assignalbe_name)
            ipaddress.set_property('macAddress', node['macaddr'])
            ipaddress.update()
        except PortalException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % safe_str(e))
            
        self._update_mac_by_node(configuration, node)

    def _free_by_node(self, configuration, node):
        try:
            iprange = configuration.get_ip_range_by_ip('DHCP4Range', node['ipaddr'])
        except PortalException as e:
            try:
                ipaddress = configuration.get_ip4_address(node['ipaddr'])
                ipaddress.delete()
            except PortalException as e:
                if self._debug:
                    print('DEBUG: Exceptin <%s>' % safe_str(e))

    def collect_nodes(self, configuration):
        succeed = False
        try:
            sonar_api = SonarAPI(self.get_value('kompira_url'), self.get_value('api_token'), debug=True)
            if not sonar_api.validate_api_key():
                return succeed
                
            network = sonar_api.get_network_by_name(self.get_value('network_name'))
            if (network is not None) and (network['networkId'] != ''):
                nodes = self._collect_nodes(configuration, sonar_api, network['networkId'])
                self._compare_nodes(configuration, nodes)
                self.set_nodes(nodes)
                
        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return succeed

    def isolate_nodes(self, configuration):
        succeed = False
        target_ips = []
        
        for node in self.get_nodes():
            denyMACAddress(configuration, node['macaddr'])
            target_ips.append(node['ipaddr'])
            
        try:
            edge_api = EdgeAPI(self.get_value('edge_url'), debug=True)
            if not edge_api.validate_edgeurl():
                return succeed
                
            if not edge_api.login(self.get_value('edge_client_id'), self.get_value('edge_secret')):
                return succeed
                
            policy = edge_api.get_policy_by_name(self.get_value('edge_policy_name'))
            if policy is None:
                return succeed
                
            id = policy.pop('id')
            del policy['timestamp']
            del policy['policyVersionId']
            
            policy['sourceIps']['ranges'].extend(target_ips)
            succeed = edge_api.update_policy(id, policy)
            
        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
                
        self.clear_nodes()
        return succeed
    
