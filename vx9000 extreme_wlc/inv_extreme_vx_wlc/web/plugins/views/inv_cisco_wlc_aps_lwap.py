# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2016-04-08
#
# 2023-06-14: removed declare_invtable_view from view definition on cmk 2.2 (see werk 15493)
#             changed inventory_displayhints import (see werk 15493)
# 2024-03-08: moved view back to ~/local/share/check_mk/web/plugins/views

from cmk.gui.i18n import _
from cmk.gui.views.inventory.registry import inventory_displayhints


inventory_displayhints.update({
    '.networking.wlan.controller.accesspoints_lwap:': {
        'title': _('Access Points LWAP info'),
        'keyorder': [
            'name', 'if_mac_address', 'admin', 'power_status', 'led_state', 'last_reboot_reason', 'telnet', 'ssh',
            'encryption_supported', 'encryption', 'data_encryption', 'wips',
        ],
        'view': 'invwlcapslwap_of_host',
    },
    '.networking.wlan.controller.accesspoints_lwap:*.name': {'title': _('Name')},
    '.networking.wlan.controller.accesspoints_lwap:*.if_mac_address': {'title': _('MAC Address')},
    '.networking.wlan.controller.accesspoints_lwap:*.admin': {'title': _('Admin state')},
    '.networking.wlan.controller.accesspoints_lwap:*.power_status': {'title': _('Power status')},
    '.networking.wlan.controller.accesspoints_lwap:*.led_state': {'title': _('LED state')},
    '.networking.wlan.controller.accesspoints_lwap:*.last_reboot_reason': {'title': _('Last reboot reason')},
    '.networking.wlan.controller.accesspoints_lwap:*.telnet': {'title': _('Telnet enabled'), 'short': _('Telnet')},
    '.networking.wlan.controller.accesspoints_lwap:*.ssh': {'title': _('SSH enabled'), 'short': _('SSH')},
    '.networking.wlan.controller.accesspoints_lwap:*.encryption_supported': {'title': _('Encryption supported')},
    '.networking.wlan.controller.accesspoints_lwap:*.encryption': {'title': _('Encryption enabled')},
    '.networking.wlan.controller.accesspoints_lwap:*.data_encryption': {'title': _('Data encryption')},
    '.networking.wlan.controller.accesspoints_lwap:*.wips': {'title': _('wireless IPS,')},

    '.networking.wlan.controller.accesspoints_lwap:*.rogue_detection': {'title': _('Rogue detection enabled'),
                                                                        'short': _('Rouge detection')},
    '.networking.wlan.controller.accesspoints_lwap:*.pwr_injector_state': {'title': _('Pow. inj. state')},
    '.networking.wlan.controller.accesspoints_lwap:*.pwr_injector_selection': {'title': _('Pow. inj. selection')},
    '.networking.wlan.controller.accesspoints_lwap:*.pwr_pre_std_state': {'title': _('PoE pre standard')},
    '.networking.wlan.controller.accesspoints_lwap:*.pwr_injector_sw_mac_addr': {'title': _('Pow. inj. MAC address')},
    '.networking.wlan.controller.accesspoints_lwap:*.wlc_primary_address': {'title': _('primary WLC')},
    '.networking.wlan.controller.accesspoints_lwap:*.wlc_secondary_address': {'title': _('secondary WLC')},
    '.networking.wlan.controller.accesspoints_lwap:*.wlc_tertiary_address': {'title': _('tertiary WLC')},
    '.networking.wlan.controller.accesspoints_lwap:*.max_#_of_dot11_slots': {'title': _('max # of dot11 slots')},
    '.networking.wlan.controller.accesspoints_lwap:*.max_#_of_ethernet_slots': {'title': _('max # of ethernet slots')},
    '.networking.wlan.controller.accesspoints_lwap:*.failover_priority': {'title': _('failover priority')},
    '.networking.wlan.controller.accesspoints_lwap:*.monitor_mode_optimization': {
        'title': _('monitor mode optimization')},
    '.networking.wlan.controller.accesspoints_lwap:*.amsdu': {'title': _('Aggregate MAC Service Data Unit'),
                                                              'short': _('AMSDU')},
    '.networking.wlan.controller.accesspoints_lwap:*.tcp_mss': {'title': _('TCP MSS')},
    '.networking.wlan.controller.accesspoints_lwap:*.port_number': {'title': _('Port number'), 'short': _('Port #')},
    '.networking.wlan.controller.accesspoints_lwap:*.venue_config_venue_group': {'title': _('Venue group')},
    '.networking.wlan.controller.accesspoints_lwap:*.venue_config_venue_type': {'title': _('Venue type')},
    '.networking.wlan.controller.accesspoints_lwap:*.venue_config_venue_name': {'title': _('Venue name')},
    '.networking.wlan.controller.accesspoints_lwap:*.venue_config_language': {'title': _('Venue language')},
    '.networking.wlan.controller.accesspoints_lwap:*.trunk_vlan': {'title': _('Mgmt VLAN ID')},
    '.networking.wlan.controller.accesspoints_lwap:*.trunk_vlan_status': {'title': _('Mgmt VLAN tagged state')},
    '.networking.wlan.controller.accesspoints_lwap:*.location': {'title': _('Location')},
    '.networking.wlan.controller.accesspoints_lwap:*.submode': {'title': _('AP submode')},
    '.networking.wlan.controller.accesspoints_lwap:*.real_time_stats_mode_enabled': {'title': _('Real time stats')},
    '.networking.wlan.controller.accesspoints_lwap:*.upgrade_from_version': {'title': _('Upgrade from version')},
    '.networking.wlan.controller.accesspoints_lwap:*.upgrade_to_version': {'title': _('Upgrade to version')},
    '.networking.wlan.controller.accesspoints_lwap:*.upgrade_failure_cause': {'title': _('Upgrade failure cause')},
    '.networking.wlan.controller.accesspoints_lwap:*.max_client_limit_number_trap': {'title': _('Max client limit')},
    '.networking.wlan.controller.accesspoints_lwap:*.max_client_limit_cause': {'title': _('Max client cause')},
    '.networking.wlan.controller.accesspoints_lwap:*.max_client_limit_set': {'title': _('Max client set')},
    '.networking.wlan.controller.accesspoints_lwap:*.floor_label': {'title': _('Floor label')},
    '.networking.wlan.controller.accesspoints_lwap:*.adj_channel_rogue_enabled': {'title': _('Adj. channel rogue')},
    '.networking.wlan.controller.accesspoints_lwap:*.sys_net_id': {'title': _('Sys net ID')},
    '.networking.wlan.controller.accesspoints_lwap:*.antenna_band_mode': {'title': _('Antenna band mode')},
    '.networking.wlan.controller.accesspoints_lwap:*.module_inserted': {'title': _('Module inserted')},
    '.networking.wlan.controller.accesspoints_lwap:*.enable_module': {'title': _('Module enabled')},
    '.networking.wlan.controller.accesspoints_lwap:*.is_universal': {'title': _('AP is universal')},
    '.networking.wlan.controller.accesspoints_lwap:*.universal_prime_status': {'title': _('AP universal prime status')},
    '.networking.wlan.controller.accesspoints_lwap:*.is_master': {'title': _('AP is master')},
    '.networking.wlan.controller.accesspoints_lwap:*.ble_fw_download_status': {'title': _('Ble FW downaload status')},
})
