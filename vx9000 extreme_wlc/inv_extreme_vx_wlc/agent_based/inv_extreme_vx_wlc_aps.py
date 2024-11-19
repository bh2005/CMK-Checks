# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2016-04-08
#
# inventory of extreme vx9000 wlc aps
#
# 2024-10-01 rewrite by bh2005

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    SNMPTree,
    TableRow,
    contains,
    any_of,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    StringTable,
    InventoryResult,
)

_last_reboot_reason = {
    '0': 'none',
    '1': 'dot11gModeChange',
    '2': 'ipAddressSet',
    '3': 'ipAddressReset',
    '4': 'rebootFromController',
    '5': 'dhcpFallbackFail',
    '6': 'discoveryFail',
    '7': 'noJoinResponse',
    '8': 'denyJoin',
    '9': 'noConfigResponse',
    '10': 'configController',
    '11': 'imageUpgradeSuccess',
    '12': 'imageOpcodeInvalid',
    '13': 'imageCheckSumInvalid',
    '14': 'imageDataTimeout',
    '15': 'configFileInvalid',
    '16': 'imageDownloadError',
    '17': 'rebootFromConsole',
    '18': 'rapOverAir',
    '19': 'powerLow',
    '20': 'crash',
    '21': 'powerHigh',
    '22': 'powerLoss',
    '23': 'powerChange',
    '24': 'componentFailure',
    '25': 'watchdog',
}

_enable_disable = {
    '0': 'N/A',
    '1': 'enabled',
    '2': 'disabled',
}

_failover_pirority = {
    '0': 'N/A',
    '1': 'low',
    '2': 'medium',
    '3': 'high',
    '4': 'critical',
}

_power_status = {
    '0': 'N/A',
    '1': 'low',
    '2': '15.4W',
    '3': '16.8W',
    '4': 'full',
    '5': 'external',
    '6': 'mixedmode',
}

_pwr_injector_selection = {
    '0': 'N/A',
    '1': 'unknown',
    '2': 'installed',
    '3': 'override',
}

_monitor_mode_optimization = {
    '0': 'N/A',
    '1': 'all',
    '2': 'tracking',
    '3': 'wips',
    '4': 'none',
}

_encryption_supported = {
    '0': 'N/A',
    '1': 'yes',
    '2': 'no',
}

_inet_address_type = {
    '0': 'N/A',
    '1': 'ipv4',
    '2': 'ipv6',
    '3': 'ipv4z',
    '4': 'ipv6z',
    '16': 'dns',
}

_antenna_band_mode = {
    '0': 'N/A',
    '1': 'not applicable',
    '2': 'single',
    '3': 'dual',
}

_venueconfigvenuegroup = {
    '0': 'N/A',
    '1': 'unspecified',
    '2': 'assembly',
    '3': 'business',
    '4': 'educational',
    '5': 'factory and industrial',
    '6': 'institutional',
    '7': 'mercantile',
    '8': 'residential',
    '9': 'storage',
    '10': 'utility and misc',
    '11': 'vehicular',
    '12': 'outdoor',
}

_venueconfigvenuetype = {
    '0': 'N/A',
    '1': 'unspecified',
    '2': 'unspecified assembly',
    '3': 'arena',
    '4': 'stadium',
    '5': 'passenger terminal',
    '6': 'amphitheater',
    '7': 'amusement park',
    '8': 'place of worship',
    '9': 'convention center',
    '10': 'library',
    '11': 'museum',
    '12': 'restaurant',
    '13': 'theater',
    '14': 'bar',
    '15': 'coffee shop',
    '16': 'zoo or aquarium',
    '17': 'emergency coordination center',
    '18': 'unspecified business',
    '19': 'doctor or dentist office',
    '20': 'bank',
    '21': 'firestation',
    '22': 'policestation',
    '23': 'postoffice',
    '24': 'professional office',
    '25': 'research and development facility',
    '26': 'attorney office',
    '27': 'unspecified educational',
    '28': 'school primary',
    '29': 'school secondary',
    '30': 'university or college',
    '31': 'unspecified factory and industrial',
    '32': 'factory',
    '33': 'unspecified institutional',
    '34': 'hospital',
    '35': 'longterm carefacility',
    '36': 'alcohol and drug rehabilitation center',
    '37': 'group home',
    '38': 'prison or jail',
    '39': 'unspecified mercantile',
    '40': 'retail store',
    '41': 'grocery market',
    '42': 'auomotive service station',
    '43': 'shoppin gmall',
    '44': 'gas station',
    '45': 'unspecified residential',
    '46': 'privat eresidence',
    '47': 'hotel or motel',
    '48': 'dormitory',
    '49': 'boarding house',
    '50': 'unspecified storage',
    '51': 'unspecified utility',
    '52': 'unspecified vehicular',
    '53': 'automobile or truck',
    '54': 'airplane',
    '55': 'bus',
    '56': 'ferry',
    '57': 'ship or boat',
    '58': 'train',
    '59': 'motorbike',
    '60': 'unspecified outdoor',
    '61': 'muni mesh network',
    '62': 'citypark',
    '63': 'restarea',
    '64': 'traffic control',
    '65': 'busstop',
    '66': 'kiosk',
}

_apsubmode = {
    '0': 'N/A',
    '1': 'none',
    '2': 'wips',
    '3': 'pppoe',
    '4': 'pppoewips',
}


def _render_mac_address(bytestring):
    return ':'.join(['%02s' % hex(ord(m))[2:] for m in bytestring]).replace(' ', '0').upper()


def _render_ip_address(bytestring):
    return '.'.join(['%s' % ord(m) for m in bytestring])

###########################################################################
#
#  SNMP DATA Parser function
#
###########################################################################

def inv_parse_extreme_wlc(string_table) -> Optional[Dict[str, Ap]]:
    try:
        device_infos, ap_infos, uptime_data, raw_radio_infos = string_table
    except ValueError:
        return

    parsed = {}

    for device in device_infos:
        dev_oid_end, mac_address, _type, hostname, version, serial_number, rf_domain_name, \
            online = device

        dev_info = DeviceInfo(
            mac_address=_render_mac_address(mac_address),
            type=_type,
            hostname=hostname,
            version=version,
            serial_number=serial_number,
            rf_domain_name=rf_domain_name,
            online=_online_status[int(online)] if online else 'N/A',
        )

        mapped_raw_ap_info = [ap[1:] for ap in ap_infos if dev_oid_end in ap[0]]  # 1:1
        mapped_raw_uptime_data = [data[1:] for data in uptime_data if dev_oid_end == data[0]]  # 1:1
        mapped_raw_radio_info = [radio[1:] for radio in raw_radio_infos if dev_oid_end in radio[0]]  # 1:*

        ap_info = ApInfo(
            location=mapped_raw_ap_info[0][0],
            ip_address=mapped_raw_ap_info[0][1]
        ) if mapped_raw_ap_info else None

        uptime_info = UptimeInfo(
            uptime=mapped_raw_uptime_data[0][0]
        ) if mapped_raw_uptime_data else None

        for radio in mapped_raw_radio_info:
            if not radio:
                continue
            radio_info = RadioInfo(
                device_mac_address=_render_mac_address(radio[0]),
                alias=radio[1],
                mac_address=_render_mac_address(radio[2]),
                num_clients=radio[3]
            )

            parsed.update({
                radio_info.alias: Ap(
                    device_info=dev_info,
                    ap_info=ap_info,
                    uptime_info=uptime_info,
                    radio_info=radio_info
                )
            })
    return parsed



def parse_inv_extreme_wlc_aps_lwap(string_table: StringTable):
    aps = []

    for ap in string_table:
        wlcprimaryaddress = ap[5]
        if _inet_address_type.get(ap[4]) == 'ipv4':
            wlcprimaryaddress = _render_ip_address(wlcprimaryaddress)

        wlcsecondaryaddress = ap[7]
        if _inet_address_type.get(ap[6]) == 'ipv4':
            wlcsecondaryaddress = _render_ip_address(wlcsecondaryaddress)

        wlctertiaryaddress = ap[9]
        if _inet_address_type.get(ap[8]) == 'ipv4':
            wlctertiaryaddress = _render_ip_address(wlctertiaryaddress)

        aps.append({
            'if_mac_address': _render_mac_address(ap[0]),
            'max_#_of_dot11_slots': ap[1],
            'name': ap[2],
            'max_#_of_ethernet_slots': ap[3],
            'encryption_supported': _encryption_supported.get(ap[23]),
            'tcp_mss': ap[25],
            'data_encryption': _enable_disable.get(ap[26]),
            'port_number': ap[28],
            'venue_config_venue_group': _venueconfigvenuegroup.get(ap[29]),
            'venue_config_venue_type': _venueconfigvenuetype.get(ap[30]),
            'venue_config_venue_name': ap[31],
            'venue_config_language': ap[32],
            'trunk_vlan': ap[34],
            'location': ap[36],
            'floor_label': ap[45],
            'module_inserted': ap[49],
            'status_columns': {
                'antenna_band_mode': _antenna_band_mode.get(ap[48]),
                'encryption': _enable_disable.get(ap[11]),
                'failover_priority': _failover_pirority.get(ap[12]),
                'power_status': _power_status.get(ap[13]),
                'telnet': _enable_disable.get(ap[14]),
                'ssh': _enable_disable.get(ap[15]),
                'pwr_pre_std_state': _enable_disable.get(ap[16]),
                'pwr_injector_state': _enable_disable.get(ap[17]),
                'pwr_injector_selection': _pwr_injector_selection.get(ap[18]),
                'pwr_injector_sw_mac_addr': _render_mac_address(ap[19]),
                'wips': _enable_disable.get(ap[20]),
                'monitor_mode_optimization': _monitor_mode_optimization.get(ap[18]),
                'amsdu': _enable_disable.get(ap[22]),
                'admin': _enable_disable.get(ap[27]),
                'rogue_detection': _enable_disable.get(ap[24]),
                'led_state': _enable_disable.get(ap[33]),
                'trunk_vlan_status': _enable_disable.get(ap[35]),
                'submode': _apsubmode.get(ap[37]),
                'real_time_stats_mode_enabled': _enable_disable.get(ap[38]),
                'upgrade_from_version': ap[39],
                'upgrade_to_version': ap[40],
                'upgrade_failure_cause': ap[41],
                'adj_channel_rogue_enabled': ap[46],
                'sys_net_id': ap[47],
                'enable_module': _enable_disable.get(ap[50]),
                'is_universal': _enable_disable.get(ap[51]),
                'universal_prime_status': ap[52],
                'is_master': _enable_disable.get(ap[53]),
                'ble_fw_download_status': _enable_disable.get(ap[54]),
                'max_client_limit_number_trap': ap[42],
                'max_client_limit_cause': ap[43],
                'max_client_limit_set': _enable_disable.get(ap[44]),
                'wlc_primary_address': wlcprimaryaddress,
                'wlc_secondary_address': wlcsecondaryaddress,
                'wlc_tertiary_address': wlctertiaryaddress,
                'last_reboot_reason': _last_reboot_reason.get(ap[10]),
            }
        })

    return aps


def inventory_extreme_wlc_aps_lwap(params, section) -> InventoryResult:
    removecolumns = []

    if params:
        removecolumns = params.get('removecolumns', removecolumns)

    path = ['networking', 'wlan', 'controller', 'accesspoints_lwap']

    for ap in section:
        key_columns = {'if_mac_address': ap['if_mac_address']}

        for key in key_columns.keys():
            ap.pop(key)

        status_columns = ap['status_columns']

        ap.pop('status_columns')

        for entry in removecolumns:
            try:
                ap.pop(entry)
            except KeyError:
                pass

        for entry in removecolumns:
            try:
                status_columns.pop(entry)
            except KeyError:
                pass
        yield TableRow(
            path=path,
            key_columns=key_columns,
            inventory_columns=ap,
            status_columns=status_columns,
        )


register.snmp_section(
    name='inv_extreme_wlc_aps_lwap',
    parse_function=parse_inv_extreme_wlc_aps_lwap,
    fetch=[
        SNMPTree(
            base='.1.3.6.1.4.1.388.50.1.4.2.1.1',  # wingStatsDevEntry
            oids=[
                OIDEnd(),
                OIDBytes('1'),  # wingStatsDevMac
                '2',  # wingStatsDevType
                '3',  # wingStatsDevHostname
                '4',  # wingStatsDevVersion
                '5',  # wingStatsDevSerialNo
                '6',  # wingStatsDevRfDomainName
                '7',  # wingStatsDevOnline
            ]
        ),
        SNMPTree(
            base='.1.3.6.1.4.1.388.50.1.4.2.25.1.1.1',  # wingStatsDevWIApInfoEntry
            oids=[
                OIDEnd(),
                '11',  # wingStatsDevWIApInfoLocation
                '13',  # wingStatsDevWIApInfoIp
            ]
        ),
        SNMPTree(
            base='.1.3.6.1.4.1.388.50.1.4.2.4.1.1',  # wingStatsDevSysEntry
            oids=[
                OIDEnd(),
                '14',  # wingStatsDevSysUptime
            ]
        ),
        SNMPTree(
            base='.1.3.6.1.4.1.388.50.1.4.2.25.9.1.1',  # wingStatsDevWlRadioEntry
            oids=[
                OIDEnd(),
                OIDBytes('2'),  # wingStatsDevWIRadioDeviceMac
                '3',  # wingStatsDevWIRadioAlias
                OIDBytes('4'),  # wingStatsDevWIRadioMac
                '15',  # wingStatsDevWIRadioNumClient
            ]
        ),
    ],
    detect=startswith('.1.3.6.1.2.1.1.1.0', 'VX9000')
)

register.inventory_plugin(
    name='inv_extreme_vx_wlc_aps',
    inventory_function=inventory_extreme_vx_wlc_aps,
    inventory_default_parameters={},
    inventory_ruleset_name='inv_extreme_vx_wlc_aps',
)
