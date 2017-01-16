# coding=utf-8
#
# Copyright 2014-2016 F5 Networks Inc.
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
#

import datetime
import logging as std_logging
import urllib2

from eventlet import greenthread
from time import time

from neutron.common.exceptions import InvalidConfigurationOption
from neutron.common.exceptions import NeutronException
from neutron.plugins.common import constants as plugin_const

from neutron_lbaas.services.loadbalancer import constants as lb_const

from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging
from oslo_utils import importutils

from f5.bigip import ManagementRoot

from f5_openstack_agent.lbaasv2.drivers.icontrol import constants_v2 as f5const
from f5_openstack_agent.lbaasv2.drivers.icontrol import exceptions as f5ex
from f5_openstack_agent.lbaasv2.drivers.icontrol.utils import serialized
from f5_openstack_agent.lbaasv2.drivers.lbaas_driver_v2 import \
    LBaaSv2BaseDriver

from f5_openstack_agent.services.bigip.cm.cluster_manager import \
    ClusterManager
from f5_openstack_agent.services.bigip.system.system_helper import \
    SystemHelper

LOG = logging.getLogger(__name__)

NS_PREFIX = 'qlbaas-'
__VERSION__ = '10.0.0'

# Configuration objects specific to iControl® driver
# See /etc/neutron/services/f5/f5-openstack-agent.ini
OPTS = [  # XXX maybe we should make this a dictionary
    cfg.StrOpt(
        'f5_ha_type', default='pair',
        help='Are we standalone, pair(active/standby), or scalen'
    ),
    cfg.ListOpt(
        'f5_external_physical_mappings', default=['default:1.1:True'],
        help='Mapping between Neutron physical_network to interfaces'
    ),
    cfg.DictOpt(
        'f5_common_network_ids', default={},
        help='network uuid to existing Common networks mapping'
    ),
    cfg.StrOpt(
        'f5_vtep_folder', default='Common',
        help='Folder for the VTEP SelfIP'
    ),
    cfg.StrOpt(
        'f5_vtep_selfip_name', default=None,
        help='Name of the VTEP SelfIP'
    ),
    cfg.ListOpt(
        'f5_advertised_tunnel_types', default=['gre', 'vxlan'],
        help='tunnel types which are advertised to other VTEPs'
    ),
    cfg.BoolOpt(
        'f5_populate_static_arp', default=False,
        help='create static arp entries based on service entries'
    ),
    cfg.BoolOpt(
        'f5_snat_mode',
        default=True,
        help=('use SNATs, not direct routed mode')
    ),
    cfg.IntOpt(
        'f5_snat_addresses_per_subnet',
        default=1,
        help=('Interface and VLAN for the VTEP overlay network')
    ),
    cfg.BoolOpt(
        'f5_use_namespaces',
        default=True,
        help=('Allow overlapping IP addresses for tenants')
    ),
    cfg.BoolOpt(
        'f5_route_domain_strictness', default=False,
        help='Strict route domain isolation'
    ),
    cfg.IntOpt(
        'f5_max_namespaces_per_tenant', default=1,
        help='How many routing tables the BIG-IP will allocate per tenant'
             ' in order to accommodate overlapping IP subnets'
    ),
    cfg.BoolOpt(
        'f5_common_external_networks', default=True,
        help='Treat external networks as common'
    ),
    cfg.StrOpt(
        'icontrol_hostname',
        default="10.190.5.7",
        help='The hostname (name or IP address) to use for iControl access'
    ),
    cfg.StrOpt(
        'icontrol_username', default='admin',
        help='The username to use for iControl access'
    ),
    cfg.StrOpt(
        'icontrol_password', default='admin', secret=True,
        help='The password to use for iControl access'
    ),
    cfg.IntOpt(
        'icontrol_connection_timeout', default=30,
        help='How many seconds to timeout a connection to BIG-IP'
    ),
    cfg.IntOpt(
        'icontrol_connection_retry_interval', default=10,
        help='How many seconds to wait between retry connection attempts'
    )
]


def is_connected(method):
    # Decorator to check we are connected before provisioning.
    def wrapper(*args, **kwargs):
        instance = args[0]
        if instance.connected:
            try:
                return method(*args, **kwargs)
            except IOError as ioe:
                LOG.error('IO Error detected: %s' % method.__name__)
                instance.connect_bigips()
                raise ioe
        else:
            LOG.error('Cannot execute %s. Not connected. Connecting.'
                      % method.__name__)
            instance.connect_bigips()
    return wrapper


class iControlDriver(LBaaSv2BaseDriver):

    def __init__(self, conf, registerOpts=True):
        # The registerOpts parameter allows a test to
        # turn off config option handling so that it can
        # set the options manually instead. """
        super(iControlDriver, self).__init__()

        self.conf = conf
        if registerOpts:
            self.conf.register_opts(OPTS)

        # Connection to every bigip device succeeded
        self.connected = False
        self.last_connect_attempt = None

        # Initialization completed successfully
        self.initialized = False

        self.plugin_rpc = None  # overrides base, same value

        self.driver_name = 'f5-lbaasv2-icontrol'

        # Helpers
        self.system_helper = None
        self.cluster_manager = None

        # BIG-IP® containers
        self.__bigips = {}
        self.__traffic_groups = []

        # List of icontrol hostnames from configuration
        self.hostnames = []

        # Get BIG-IP® hosts and check credentials.
        self._init_bigip_hostnames()

        # Initialize manager/helper classes.
        self._init_bigip_managers()

        # Connect to and initialize each device.
        self._init_bigips()

        # Initialize agent configuration reported to Neutron
        local_ips = []
        self._init_agent_configuration(local_ips)

        self.initialized = True

    def post_init(self):
        # run any post initialized tasks, now that the agent
        # is fully connected
        pass

    def _init_agent_configuration(self, local_ips):
        # Initialize the agent configuration
        self.agent_configurations = {}
        if self.conf.f5_global_routed_mode:
            LOG.info('WARNING - f5_global_routed_mode enabled.'
                     ' There will be no L2 or L3 orchestration'
                     ' or tenant isolation provisioned. All vips'
                     ' and pool members must be routable through'
                     ' pre-provisioned SelfIPs.')
            self.conf.f5_use_namespaces = False
            self.conf.f5_snat_mode = True
            self.conf.f5_snat_addresses_per_subnet = 0
            self.agent_configurations['tunnel_types'] = []
            self.agent_configurations['bridge_mappings'] = {}
        else:
            self.agent_configurations['tunnel_types'] = \
                self.conf.f5_advertised_tunnel_types
            for net_id in self.conf.f5_common_network_ids:
                LOG.debug('network %s will be mapped to /Common/%s'
                          % (net_id, self.conf.f5_common_network_ids[net_id]))

            self.agent_configurations['common_networks'] = \
                self.conf.f5_common_network_ids
            self.agent_configurations['f5_common_external_networks'] = \
                self.conf.f5_common_external_networks

        self.agent_configurations['device_drivers'] = [self.driver_name]

        icontrol_endpoints = {}
        for host, bigip in self.__bigips.iteritems():
            ic_host = {}
            ic_host['version'] = self.system_helper.get_version(bigip)
            ic_host['device_name'] = bigip.device_name
            ic_host['platform'] = self.system_helper.get_platform(bigip)
            ic_host['serial_number'] = \
                self.system_helper.get_serial_number(bigip)
            icontrol_endpoints[host] = ic_host

        self.agent_configurations['tunneling_ips'] = local_ips
        self.agent_configurations['icontrol_endpoints'] = icontrol_endpoints

        if self.network_builder:
            self.agent_configurations['bridge_mappings'] = \
                self.network_builder.interface_mapping

    def _init_bigip_hostnames(self):
        """Parse hostnames and verify bigip creds exist."""
        if not self.conf.icontrol_hostname:
            raise InvalidConfigurationOption(
                opt_name='icontrol_hostname',
                opt_value='valid hostname or IP address'
            )
        if not self.conf.icontrol_username:
            raise InvalidConfigurationOption(
                opt_name='icontrol_username',
                opt_value='valid username'
            )
        if not self.conf.icontrol_password:
            raise InvalidConfigurationOption(
                opt_name='icontrol_password',
                opt_value='valid password'
            )

        self.hostnames = self.conf.icontrol_hostname.split(',')
        self.hostnames = [item.strip() for item in self.hostnames]
        self.hostnames = sorted(self.hostnames)

    def _init_bigip_managers(self):
        self.cluster_manager = ClusterManager()
        self.system_helper = SystemHelper()
        self.network_builder = None

    def _init_bigips(self):

        # Connect to all BIG-IP®s
        if self.connected:
            return
        try:
            if not self.conf.debug:
                requests_log = std_logging.getLogger(
                    "requests.packages.urllib3")
                requests_log.setLevel(std_logging.ERROR)
                requests_log.propagate = False
            else:
                requests_log = std_logging.getLogger(
                    "requests.packages.urllib3")
                requests_log.setLevel(std_logging.DEBUG)
                requests_log.propagate = True

            self.last_connect_attempt = datetime.datetime.now()

            first_bigip = self._open_bigip_connection(
                self.hostnames[0])
            self._init_bigip(first_bigip, self.hostnames[0], None)
            self.__bigips[self.hostnames[0]] = first_bigip

            device_group_name = self._validate_ha(first_bigip)
            self._init_traffic_groups(first_bigip)

            # connect to the rest of the devices
            for hostname in self.hostnames[1:]:
                bigip = self._open_bigip_connection(hostname)
                self.__bigips[hostname] = bigip
                self._init_bigip(bigip, self.hostnames[0], device_group_name)

            self.connected = True

        except NeutronException as exc:
            LOG.error('Could not communicate with all ' +
                      'iControl devices: %s' % exc.msg)
            greenthread.sleep(5)  # this should probably go away
            raise
        except Exception as exc:
            LOG.error('Could not communicate with all ' +
                      'iControl devices: %s' % exc.message)
            greenthread.sleep(5)  # this should probably go away
            raise

    def _open_bigip_connection(self, hostname):
        """Open bigip connection and initialize device."""
        LOG.debug('Opening iControl connection to %s @ %s' %
                  (self.conf.icontrol_username, hostname))

        return ManagementRoot(hostname,
                              self.conf.icontrol_username,
                              self.conf.icontrol_password)

    def _init_bigip(self, bigip, hostname, check_group_name=None):
        """Prepare a bigip for usage."""
        major_version, minor_version = self._validate_bigip_version(
            bigip, hostname)

        device_group_name = None
        extramb = self.system_helper.get_provision_extramb(bigip)
        if int(extramb) < f5const.MIN_EXTRA_MB:
            raise f5ex.ProvisioningExtraMBValidateFailed(
                'Device %s BIG-IP not provisioned for '
                'management LARGE.' % hostname)

        if self.conf.f5_ha_type == 'pair' and \
                self.cluster_manager.get_sync_status(bigip) == 'Standalone':
            raise f5ex.BigIPClusterInvalidHA(
                'HA mode is pair and bigip %s in standalone mode'
                % hostname)

        if self.conf.f5_ha_type == 'scalen' and \
                self.cluster_manager.get_sync_status(bigip) == 'Standalone':
            raise f5ex.BigIPClusterInvalidHA(
                'HA mode is scalen and bigip %s in standalone mode'
                % hostname)

        if self.conf.f5_ha_type != 'standalone':
            device_group_name = self.cluster_manager.get_device_group(bigip)
            if not device_group_name:
                raise f5ex.BigIPClusterInvalidHA(
                    'HA mode is %s and no sync failover '
                    'device group found for device %s.'
                    % (self.conf.f5_ha_type, hostname))
            if check_group_name and device_group_name != check_group_name:
                raise f5ex.BigIPClusterInvalidHA(
                    'Invalid HA. Device %s is in device group'
                    ' %s but should be in %s.'
                    % (hostname, device_group_name, check_group_name))
            bigip.device_group_name = device_group_name

        if self.network_builder:
            for network in self.conf.common_network_ids.values():
                if not self.network_builder.vlan_exists(bigip,
                                                        network,
                                                        folder='Common'):
                    raise f5ex.MissingNetwork(
                        'Common network %s on %s does not exist'
                        % (network, bigip.hostname))

        # Add extra attributes.
        bigip.device_name = self.cluster_manager.get_device_name(bigip)
        bigip.mac_addresses = self.system_helper.get_mac_addresses(bigip)
        bigip.device_interfaces = \
            self.system_helper.get_interface_macaddresses_dict(bigip)
        bigip.assured_networks = {}
        bigip.assured_tenant_snat_subnets = {}
        bigip.assured_gateway_subnets = []

        if self.conf.f5_ha_type != 'standalone':
            self.cluster_manager.disable_auto_sync(device_group_name, bigip)

        # Turn off tunnel syncing... our VTEPs are local SelfIPs
        if self.system_helper.get_tunnel_sync(bigip) == 'enable':
            self.system_helper.set_tunnel_sync(bigip, enabled=False)

        LOG.debug('Connected to iControl %s @ %s ver %s.%s'
                  % (self.conf.icontrol_username, hostname,
                     major_version, minor_version))

        return bigip

    def _validate_ha(self, first_bigip):
        # if there was only one address supplied and
        # this is not a standalone device, get the
        # devices trusted by this device. """
        device_group_name = None
        if self.conf.f5_ha_type == 'standalone':
            if len(self.hostnames) != 1:
                raise f5ex.BigIPClusterInvalidHA(
                    'HA mode is standalone and %d hosts found.'
                    % len(self.hostnames))
        elif self.conf.f5_ha_type == 'pair':
            device_group_name = self.cluster_manager.\
                get_device_group(first_bigip)
            if len(self.hostnames) != 2:
                mgmt_addrs = []
                devices = self.cluster_manager.devices(first_bigip,
                                                       device_group_name)
                for device in devices:
                    mgmt_addrs.append(
                        self.cluster_manager.get_mgmt_addr_by_device(device))
                self.hostnames = mgmt_addrs
            if len(self.hostnames) != 2:
                raise f5ex.BigIPClusterInvalidHA(
                    'HA mode is pair and %d hosts found.'
                    % len(self.hostnames))
        elif self.conf.f5_ha_type == 'scalen':
            device_group_name = self.cluster_manager.\
                get_device_group(first_bigip)
            if len(self.hostnames) < 2:
                mgmt_addrs = []
                devices = self.cluster_manager.devices(first_bigip,
                                                       device_group_name)
                for device in devices:
                    mgmt_addrs.append(
                        self.cluster_manager.get_mgmt_addr_by_device(
                            first_bigip, device))
                self.hostnames = mgmt_addrs
        return device_group_name

    def _init_traffic_groups(self, bigip):
        self.__traffic_groups = self.cluster_manager.get_traffic_groups(bigip)
        if 'traffic-group-local-only' in self.__traffic_groups:
            self.__traffic_groups.remove('traffic-group-local-only')
        self.__traffic_groups.sort()

    def _validate_bigip_version(self, bigip, hostname):
        # Ensure the BIG-IP® has sufficient version
        major_version = self.system_helper.get_major_version(bigip)
        if major_version < f5const.MIN_TMOS_MAJOR_VERSION:
            raise f5ex.MajorVersionValidateFailed(
                'Device %s must be at least TMOS %s.%s'
                % (hostname, f5const.MIN_TMOS_MAJOR_VERSION,
                   f5const.MIN_TMOS_MINOR_VERSION))
        minor_version = self.system_helper.get_minor_version(bigip)
        if minor_version < f5const.MIN_TMOS_MINOR_VERSION:
            raise f5ex.MinorVersionValidateFailed(
                'Device %s must be at least TMOS %s.%s'
                % (hostname, f5const.MIN_TMOS_MAJOR_VERSION,
                   f5const.MIN_TMOS_MINOR_VERSION))
        return major_version, minor_version

    def set_context(self, context):
        # Context to keep for database access
        pass

    def set_plugin_rpc(self, plugin_rpc):
        # Provide Plugin RPC access
        self.plugin_rpc = plugin_rpc

    def flush_cache(self):
        # Remove cached objects so they can be created if necessary
        for bigip in self.get_all_bigips():
            bigip.assured_networks = {}
            bigip.assured_tenant_snat_subnets = {}
            bigip.assured_gateway_subnets = []

    @serialized('create_loadbalancer')
    @is_connected
    def create_loadbalancer(self, loadbalancer, service):
        """Create loadbalancer."""
        self._common_service_handler(service)

    @serialized('update_loadbalancer')
    @is_connected
    def update_loadbalancer(self, old_loadbalancer, loadbalancer, service):
        """Update loadbalancer."""
        # anti-pattern three args unused.
        self._common_service_handler(service)

    @serialized('delete_loadbalancer')
    @is_connected
    def delete_loadbalancer(self, loadbalancer, service):
        """Delete loadbalancer."""
        LOG.debug("Deleting loadbalancer")
        self._common_service_handler(service, True)

    @serialized('create_listener')
    @is_connected
    def create_listener(self, listener, service):
        """Create virtual server."""
        LOG.debug("Creating listener")
        self._common_service_handler(service)

    @serialized('update_listener')
    @is_connected
    def update_listener(self, old_listener, listener, service):
        """Update virtual server."""
        LOG.debug("Updating listener")
        service['old_listener'] = old_listener
        self._common_service_handler(service)

    @serialized('delete_listener')
    @is_connected
    def delete_listener(self, listener, service):
        """Delete virtual server."""
        LOG.debug("Deleting listener")
        self._common_service_handler(service)

    @serialized('create_pool')
    @is_connected
    def create_pool(self, pool, service):
        """Create lb pool."""
        LOG.debug("Creating pool")
        self._common_service_handler(service)

    @serialized('update_pool')
    @is_connected
    def update_pool(self, old_pool, pool, service):
        """Update lb pool."""
        LOG.debug("Updating pool")
        self._common_service_handler(service)

    @serialized('delete_pool')
    @is_connected
    def delete_pool(self, pool, service):
        """Delete lb pool."""
        LOG.debug("Deleting pool")
        self._common_service_handler(service)

    @serialized('create_member')
    @is_connected
    def create_member(self, member, service):
        """Create pool member."""
        LOG.debug("Creating member")
        self._common_service_handler(service)

    @serialized('update_member')
    @is_connected
    def update_member(self, old_member, member, service):
        """Update pool member."""
        LOG.debug("Updating member")
        self._common_service_handler(service)

    @serialized('delete_member')
    @is_connected
    def delete_member(self, member, service):
        """Delete pool member."""
        LOG.debug("Deleting member")
        self._common_service_handler(service)

    @serialized('create_health_monitor')
    @is_connected
    def create_health_monitor(self, health_monitor, service):
        """Create pool health monitor."""
        LOG.debug("Creating health monitor")
        self._common_service_handler(service)

    @serialized('update_health_monitor')
    @is_connected
    def update_health_monitor(self, old_health_monitor,
                              health_monitor, service):
        """Update pool health monitor."""
        LOG.debug("Updating health monitor")
        self._common_service_handler(service)

    @serialized('delete_health_monitor')
    @is_connected
    def delete_health_monitor(self, health_monitor, service):
        """Delete pool health monitor."""
        LOG.debug("Deleting health monitor")
        self._common_service_handler(service)

    @is_connected
    def get_stats(self, service):
        pass

    def set_tunnel_rpc(self, tunnel_rpc):
        # Provide FDB Connector with ML2 RPC access
        pass

    def set_l2pop_rpc(self, l2pop_rpc):
        # Provide FDB Connector with ML2 RPC access
        pass

    def fdb_add(self, fdb):
        # Add (L2toL3) forwarding database entries
        pass

    def fdb_remove(self, fdb):
        # Remove (L2toL3) forwarding database entries
        pass

    def fdb_update(self, fdb):
        # Update (L2toL3) forwarding database entries
        pass

    # remove ips from fdb update so we do not try to
    # add static arps for them because we do not have
    # enough information to determine the route domain
    def remove_ips_from_fdb_update(self, fdb):
        pass

    def tunnel_update(self, **kwargs):
        # Tunnel Update from Neutron Core RPC
        pass

    def tunnel_sync(self):
        # Only sync when supported types are present

        # Tunnel sync sent.
        return True

    @serialized('sync')
    @is_connected
    def sync(self, service):
        """Sync service defintion to device."""
        pass

    @serialized('backup_configuration')
    @is_connected
    def backup_configuration(self):
        # Save Configuration on Devices
        pass

    def _common_service_handler(self, service, delete_partition=False):
        # Assure that the service is configured on bigip(s)
        pass

    def get_bigip(self):
        # Get one consistent big-ip
        # As implemented I think this always returns the "first" bigip
        # without any HTTP traffic? CONFIRMED: __bigips are mgmt_rts
        hostnames = sorted(self.__bigips)
        for i in range(len(hostnames)):  # C-style make Pythonic.
            try:
                bigip = self.__bigips[hostnames[i]]  # Calling devices?!
                return bigip
            except urllib2.URLError:
                pass
        raise urllib2.URLError('cannot communicate to any bigips')

    def get_bigip_hosts(self):
        # Get all big-ip hostnames under management
        return self.__bigips

    def get_all_bigips(self):
        # Get all big-ips under management
        return self.__bigips.values()

    def get_config_bigips(self):
        # Return a list of big-ips that need to be configured.
        return self.get_all_bigips()
