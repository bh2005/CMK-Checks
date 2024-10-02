# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2016-04-08
#
# 2023-06-14: moved wato file to check_parameters sub directory


from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Dictionary,
    ListChoice,
)

from cmk.gui.plugins.wato.inventory import (
    RulespecGroupInventory,
)

_removecolumns_cisco_wlc_aps_lwap = [
    # ('name', 'Name'),
    # (if_mac_address', 'MAC Address'),
    # ('admin', 'Admin state'),
    # ('power_status', 'Power status'),
    # ('led_state', 'LED state'),
    # ('last_reboot_reason', 'Last reboot reason'),
    # ('telnet', 'Telnet enabled'),
    # ('ssh', 'SSH enabled'),
    # ('encryption_supported', 'Encryption supported'),
    # ('data_encryption', 'Data encryption'),
    # ('encryption', 'Encryption enabled'),
    # ('wips', 'wireless IPS,'),

    ('adj_channel_rogue_enabled', 'Adj. channel rogue'),
    ('amsdu', 'Aggregate MAC Service Data Unit'),
    ('antenna_band_mode', 'Antenna band mode'),
    ('is_master', 'AP is master'),
    ('is_universal', 'AP is universal'),
    ('submode', 'AP submode'),
    ('universal_prime_status', 'AP universal prime status'),
    ('ble_fw_download_status', 'Ble FW downaload status'),
    ('failover_priority', 'failover priority'),
    ('floor_label', 'Floor label'),
    ('location', 'Location'),
    ('max_#_of_dot11_slots', 'max # of dot11 slots'),
    ('max_#_of_ethernet_slots', 'max # of ethernet slots'),
    ('max_client_limit_cause', 'Max client cause'),
    ('max_client_limit_number_trap', 'Max client limit'),
    ('max_client_limit_set', 'Max client set'),
    ('trunk_vlan', 'Mgmt VLAN ID'),
    ('trunk_vlan_status', 'Mgmt VLAN tagged state'),
    ('enable_module', 'Module enabled'),
    ('module_inserted', 'Module inserted'),
    ('monitor_mode_optimization', 'monitor mode optimization'),
    ('port_number', 'Port number'),
    ('pwr_injector_selection', 'Pow. inj. selection'),
    ('pwr_injector_state', 'Pow. inj. state'),
    ('pwr_injector_sw_mac_addr', 'Pow. inj. MAC address'),
    ('pwr_pre_std_state', 'PoE pre standard'),
    ('real_time_stats_mode_enabled', 'Real time stats'),
    ('rogue_detection', 'Rogue detection enabled'),
    ('sys_net_id', 'Sys net ID'),
    ('tcp_mss', 'TCP MSS'),
    ('upgrade_failure_cause', 'Upgrade failure cause'),
    ('upgrade_from_version', 'Upgrade from version'),
    ('upgrade_to_version', 'Upgrade to version'),
    ('venue_config_language', 'Venue language'),
    ('venue_config_venue_group', 'Venue group'),
    ('venue_config_venue_name', 'Venue name'),
    ('venue_config_venue_type', 'Venue type'),
    ('wlc_primary_address', 'primary WLC'),
    ('wlc_secondary_address', 'secondary WLC'),
    ('wlc_tertiary_address', 'tertiary WLC'),
]

_removecolumns_defaul_cisco_wlc_aps_lwap = [
    'adj_channel_rogue_enabled', 'amsdu', 'is_master', 'is_universal', 'submode',
    'universal_prime_status', 'max_client_limit_cause', 'ble_fw_download_status', 'antenna_band_mode',
    'module_inserted', 'floor_label', 'max_client_limit_set', 'enable_module',
    'pwr_injector_sw_mac_addr', 'pwr_injector_selection', 'pwr_injector_state', 'pwr_pre_std_state',
    'trunk_vlan', 'trunk_vlan_status', 'tcp_mss', 'monitor_mode_optimization', 'sys_net_id',
    'upgrade_failure_cause', 'upgrade_from_version', 'upgrade_to_version', 'venue_config_language',
    'venue_config_venue_group', 'venue_config_venue_name', 'port_number', 'venue_config_venue_type',
    'max_#_of_dot11_slots', 'max_#_of_ethernet_slots', 'failover_priority', 'wlc_primary_address',
    'wlc_secondary_address', 'wlc_tertiary_address'
]


def _valuespec_inv_cisco_wlc_aps_lwap():
    return Dictionary(
        title=_('Cisco WLC AP LWAP info'),
        elements=[
            ('removecolumns',
             ListChoice(
                 title=_('list of columns to remove'),
                 help=_('information to remove from inventory'),
                 choices=_removecolumns_cisco_wlc_aps_lwap,
                 default_value=_removecolumns_defaul_cisco_wlc_aps_lwap,
             )),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupInventory,
        match_type='dict',
        name='inv_parameters:inv_cisco_wlc_aps_lwap',
        valuespec=_valuespec_inv_cisco_wlc_aps_lwap,
    ))
