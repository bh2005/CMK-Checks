#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2016-04-03
#
# 2024-10-01 rewrite for Extreme VX9000 by bh2005

import re
from datetime import datetime, timedelta
from time import time
from dataclasses import dataclass
from typing import Optional, Dict, Mapping, Any, Union

from cmk.agent_based.v1 import startswith, OIDBytes
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    DiscoveryResult,
    CheckResult,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Service,
    SNMPTree,
    render,
    check_levels,
    OIDEnd,
    Result,
    State,
    Metric,
    GetRateError,
    get_value_store,
    IgnoreResultsError,

)



@dataclass
class DeviceInfo:
    mac_address: str
    type: Optional[str] = None
    hostname: Optional[str] = None
    version: Optional[str] = None
    serial_number: Optional[str] = None
    rf_domain_name: Optional[str] = None
    online: Optional[str] = None


@dataclass
class ApInfo:
    location: str
    ip_address: str


@dataclass
class RadioInfo:
    device_mac_address: str
    alias: str
    mac_address: str
    num_clients: Optional[int] = None


@dataclass
class UptimeInfo:
    uptime: str


@dataclass
class Ap:
    device_info: DeviceInfo
    ap_info: ApInfo
    radio_info: RadioInfo
    uptime_info: UptimeInfo


@dataclass
class InvApInfo:
    ap_location: str
    ap_model: str
    ap_serialnumber: str
    ap_ipaddress: str
    ap_macaddress: str
    ap_hostname: str
    ap_version: str
    ap_rf_domain_name: str
    ap_online: int


Section = Dict[str, Ap]

_online_status = {
    1: 'Online',
    2: 'Offline'
}

_interface_displayhints = {
    'ethernet': 'eth',
    'fastethernet': 'Fa',
    'gigabitethernet': 'Gi',
    'tengigabitethernet': 'Te',
    'fortygigabitethernet': 'Fo',
    'hundredgigabitethernet': 'Hu',
    'port-channel': 'Po',
    'tunnel': 'Tu',
    'loopback': 'Lo',
    'cellular': 'Cel',
    'vlan': 'Vlan',
    'management': 'Ma',
}

_map_states = {
    "1": (State.OK, "online"),
    "2": (State.CRIT, "critical"),
    "3": (State.WARN, "warning"),
}


def _get_short_if_name(ifname: str) -> str:
    """
    Return short interface name from long interface name.
    ifname: is the long interface name
    :type ifname: str
    """
    for ifname_prefix in _interface_displayhints.keys():
        if ifname.lower().startswith(ifname_prefix.lower()):
            ifname_short = _interface_displayhints[ifname_prefix]
            return ifname.lower().replace(ifname_prefix.lower(), ifname_short, 1)
    return ifname


def _render_mac_address(mac_bytes):
    return ":".join("%02s" % hex(int(m))[2:] for m in mac_bytes).replace(' ', '0').upper()


def _render_ip_address(bytestring):
    if len(bytestring) == 4:
        return '.'.join(['%s' % ord(m) for m in bytestring])
    else:
        bytestring_clean = bytestring.replace('"', '').replace('|4|', '').replace('.', ' ').strip().split(' ')
        try:
            return '.'.join(['%s' % int(m, 16) for m in bytestring_clean])
        except ValueError:
            return bytestring


###########################################################################
#
#  SNMP DATA Parser function
#
###########################################################################

def parse_extreme_wlc(string_table) -> Optional[Dict[str, Ap]]:
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


###########################################################################
#
#  DISCOVERY function
#
###########################################################################


def discovery_extreme_wlc(section: Section) -> DiscoveryResult:
    for radio_alias in section.keys():
        ap = section.get(radio_alias)

        inv_ap_info = {
            'ap_location': ap.ap_info.location if ap.ap_info else None,
            'ap_model': ap.device_info.type,
            'ap_serialnumber': ap.device_info.serial_number,
            'ap_ipaddress': ap.ap_info.ip_address if ap.ap_info else None,
            'ap_mac_address': ap.device_info.mac_address,
            'ap_host_name': ap.device_info.hostname,
            'ap_version': ap.device_info.version,
            'ap_rf_domain_name': ap.device_info.rf_domain_name,
            'ap_online': ap.device_info.online
        }

        yield Service(item=radio_alias, parameters={'inv_ap_info': inv_ap_info})


###########################################################################
#
#  CHECK function
#
###########################################################################

timedelta_regex = re.compile(r'(?P<days>\d+?) days, (?P<hours>\d+?) hours (?P<minutes>\d+?) minutes$')

def str_to_timedelta(time_str):
    parts = timedelta_regex.match(time_str)
    if not parts:
        raise ValueError(f'Invalid time string: {time_str}')
    parts = {key: int(value) for key, value in parts.groupdict().items()}
    return timedelta(**parts)


def check_extreme_wlc(item, params, section: Section) -> CheckResult:
    ap_missing_state = params.get('state_ap_missing', 1)
    inv_ap_info_key = 'inv_ap_info'
    if params.get(inv_ap_info_key):
        inv_ap_info = InvApInfo(
            ap_location=params.get(inv_ap_info_key).get('ap_location'),
            ap_model=params.get(inv_ap_info_key).get('ap_model'),
            ap_serialnumber=params.get(inv_ap_info_key).get('ap_serialnumber'),
            ap_ipaddress=params.get(inv_ap_info_key).get('ap_ipaddress'),
            ap_macaddress=params.get(inv_ap_info_key).get('ap_mac_address'),
            ap_hostname=params.get(inv_ap_info_key).get('ap_host_name'),
            ap_version=params.get(inv_ap_info_key).get('ap_version'),
            ap_rf_domain_name=params.get(inv_ap_info_key).get('ap_rf_domain_name'),
            ap_online=params.get(inv_ap_info_key).get('ap_online')
        )
    else:
        inv_ap_info = None

    for ap_name, ap_alias in params.get('ap_list', []):
        if item == ap_name:
            yield Result(state=State.OK, summary=f'Alias: {ap_alias}')

    try:
        ap = section[item]
    except KeyError:
        # Special treatment if this device is APs
        if inv_ap_info:
            yield Result(state=State.OK, notice=f'\nAP Missing')
            yield Result(state=State.OK, notice=f' - AP info:'
                                                f'\nLocation: {inv_ap_info.ap_location},'
                                                f'\nModel: {inv_ap_info.ap_model},'
                                                f'\nSerial: {inv_ap_info.ap_serialnumber},'
                                                f'\nIP-address: {inv_ap_info.ap_ipaddress},'
                                                f'\nMAC-address: {inv_ap_info.ap_macaddress}'
                                                f'\nHostname: {inv_ap_info.ap_hostname},'
                                                f'\nVersion: {inv_ap_info.ap_version}'
                                                f'\nRF Domain Name: {inv_ap_info.ap_rf_domain_name}'
                                                f'\nOnline: {inv_ap_info.ap_online}'
                         )
        yield Result(
            state=State(ap_missing_state),
            summary=f'AP {item} not found in SNMP data. For more information see check details (long output)',
        )
        return
#*********SUMARY**************************************
    device_info = ap.device_info
    yield Result(state=State.OK, summary=f'  Radio MAC address: {ap.radio_info.mac_address}')
    yield Result(state=State.OK, summary=f'  Clients: {ap.radio_info.num_clients}')
    num_clients=int(ap.radio_info.num_clients)

    
    
    uptime_info = ap.uptime_info.uptime
#*********SUMARY**************************************
    if uptime_info:
        time_diff = str_to_timedelta(uptime_info)

        yield from check_levels(
            value=time() - time_diff.total_seconds(),
            label='Up since',
            render_func=render.datetime,
            notice_only=True
        )
        yield from check_levels(
            value=time_diff.total_seconds(),
            label='Uptime',
            render_func=render.timespan,
            metric_name='extreme_wlc_uptime_seconds',
        )

# perfdata (plain)
    for key, value, bounderies in [
        ('active_client_count', num_clients, (0, None)),
        #('associated_clients', lwap_info.ap_associatedclientcount, (0, None)),
    ]:
        if value:
            yield Metric(name=f'extreme_wlc_{key}', value=value, boundaries=bounderies)

    
    yield Result(state=State.OK, notice=f'\nBase data:')
    yield Result(state=State.OK, notice=f' - IP address: {ap.ap_info.ip_address}')
    yield Result(state=State.OK, notice=f' - Device MAC address: {ap.device_info.mac_address}')
    #yield Result(state=State.OK, notice=f'  Radio MAC address: {ap.radio_info.mac_address}', summary=f' - Radio MAC address: {ap.radio_info.mac_address}')
    yield Result(state=State.OK, notice=f' - Radio MAC address: {ap.radio_info.mac_address}')
    yield Result(state=State.OK, notice=f' - Model: {ap.device_info.type}')
    yield Result(state=State.OK, notice=f' - S/N:  {ap.device_info.serial_number}')
    yield Result(state=State.OK, notice=f' - Location:  {ap.ap_info.location}')
    yield Result(state=State.OK, notice=f' - Version:   {ap.device_info.version}')
    yield Result(state=State.OK, notice=f' - RF Domain Name:   {ap.device_info.rf_domain_name}')
    yield Result(state=State.OK, notice=f' - Hostname:   {ap.device_info.hostname}')

    if device_info.online != 1:
        online_status = device_info.online
        yield Result(
            state=State(params.get('state_ap_offlinestatus', 1)),
            notice=f'{online_status}',
            details=' - AP is online',
        )

    # ap has wrong serial number --> AP H/W changed.
    if inv_ap_info:
        if device_info.serial_number != inv_ap_info.ap_serialnumber or \
                device_info.type != inv_ap_info.ap_model or \
                device_info.mac_address != inv_ap_info.ap_macaddress or \
                ap.ap_info.ip_address != inv_ap_info.ap_ipaddress or \
                ap.ap_info.location != inv_ap_info.ap_location:
            yield Result(
                state=State(params.get('state_ap_change', 1)),
                notice='Hardware changed',
                details=f'\nAP hardware changed. Run inventory again. '
                        f'\n - Serial number (found/expected): {device_info.serial_number} / {inv_ap_info.ap_serialnumber} '
                        f'\n - Model (found/expected): {device_info.type} / {inv_ap_info.ap_model} '
                        f'\n - Device MAC address (found/expected): {device_info.mac_address} / {inv_ap_info.ap_macaddress} '
                        f'\n - IP address (found/expected): {ap.ap_info.ip_address} / {inv_ap_info.ap_ipaddress} '
                        f'\n - Location (found/expected): {ap.ap_info.location} / {inv_ap_info.ap_location}',
            )
    else:
        yield Result(state=State.WARN, summary='AP data from discovery missing.')






###########################################################################
#
#  Cluster function
#
###########################################################################


def _node_not_found(item: str, params: Mapping[str, Any]) -> Result:
    infotext = 'not found'
    for ap_name, ap_state in params.get('ap_name', []):
        if item.startswith(ap_name):
            return Result(state=ap_state, summary=infotext)
    return Result(state=State.CRIT, summary=infotext)


def _ap_info(node: Optional[str], wlc_status: Union[str, Ap]) -> Result:
    wlc_status = str(wlc_status.device_info.online) if isinstance(wlc_status, Ap) else wlc_status
    status, state_readable = _map_states.get(wlc_status, (State.UNKNOWN, f'unknown [{wlc_status}]'))
    return Result(state=status, summary=f"{state_readable}{f' (connected to {node})' if node else ''}", )


def cluster_check_extreme_wlc(
        item: str,
        params: Mapping[str, Any],
        section: Mapping[str, Optional[Section]],
) -> CheckResult:
    for node, node_section in section.items():
        if node_section is not None and item in node_section:
            yield _ap_info(node, node_section[item])
            yield from check_extreme_wlc(item, params, node_section)
            return
    yield _node_not_found(item, params)


###########################################################################
#
# Register SNMP section
#
###########################################################################


register.snmp_section(
    name='extreme_wlc',
    parse_function=parse_extreme_wlc,
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

###########################################################################
#
# Register Check Plugin
#
###########################################################################


register.check_plugin(
    name='extreme_wlc',
    service_name='AP %s',
    discovery_function=discovery_extreme_wlc,
    check_function=check_extreme_wlc,
    check_default_parameters={
        'state_ap_missing': 1,
        'state_ap_change': 1,
        'ap_list': [],
    },
    check_ruleset_name='extreme_wlc',
    cluster_check_function=cluster_check_extreme_wlc,
)
