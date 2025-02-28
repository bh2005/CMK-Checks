#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2021-07-01
#
# extended if64 to use ifNAme instead of ifDescr and adds VLAN-ID
#
# 2021-09-29: fixed empty interface name handling
# 2023-03-02: changed for CMK 2.1.x
# 2023-10-21: added if_fortigate to supersedes list
# 2024-06-16: modified imports for CMK 2.3
# 2024-11-20: added VLAN-ID support

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    SNMPTree,
)

from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    StringByteTable,
)

from cmk.base.plugins.agent_based.utils import interfaces
from cmk.plugins.lib import if64

_interface_displayhints = {
    'ethernet': 'eth',
    'fastethernet': 'Fa',
    'gigabitethernet': 'Gi',
    'tengigabitethernet': 'Te',
    'twentyfivegige': 'Tw',
    'fortygigabitethernet': 'Fo',
    'hundredgigabitethernet': 'Hu',
    'port-channel': 'Po',
    'tunnel': 'Tu',
    'loopback': 'Lo',
    'cellular': 'Cel',
    'vlan': 'Vlan',
    'management': 'Ma',
}


def _get_short_if_name(ifname: str) -> str:
    """
    returns a short interface name from a long interface name
    If no short name is found, the long name (ifname) will be returned
    Args:
        ifname: is the long interface name

    Returns:
        str: the short interface name as string
    """

    for ifname_prefix in _interface_displayhints.keys():
        if ifname.lower().startswith(ifname_prefix.lower()):
            ifname_short = _interface_displayhints[ifname_prefix]
            return ifname.lower().replace(ifname_prefix.lower(), ifname_short, 1)
    return ifname


def parse_if64name(string_table: StringByteTable) -> interfaces.Section:
    if_data = []  # Initialize an empty list to store interface data

    for interface in string_table:
        if_index = interface[0]  # Get the ifIndex
        if_name = interface[-1]  # Get the ifName

        if if_name != '':
            if_name = _get_short_if_name(if_name)

        # Fetch VLAN ID for this interface
        vlan_id = get_vlan_id(if_index, string_table.snmp_session) # Get the VLAN ID

        if_data.append([if_index, if_name, vlan_id]) # Append as a list for if64.parse_if64
        
    #     section = if64.parse_if64(StringByteTable(if_data)) # Create StringByteTable and parse
    #     section = section + ([if_index, if_name, vlan_id]) # hier musst du schauen wie du das mit dran hängst
    # return section

    return if64.parse_if64(StringByteTable(if_data)) # Create StringByteTable and parse

def get_vlan_id(if_index, snmp_session):
    """Retrieves the VLAN ID for a given interface index."""
    try:
        oid = f"1.3.6.1.2.1.17.7.1.4.5.1.1.{if_index}" # Correct OID format
        result = snmp_session.get(oid)
        if result:
            return str(result.value)  # Convert to string and return
        else:
            return ""  # Return empty string if no VLAN ID is found
    except Exception as e:
        print(f"Error getting VLAN ID for ifIndex {if_index}: {e}") # Error logging
        return ""


register.snmp_section(
    name='if64_vlan',
    parsed_section_name='if64',
    parse_function=parse_if64name,
    fetch=SNMPTree(
        base=if64.BASE_OID,
        oids=if64.END_OIDS + ['31.1.1.1.1']  # IF-MIB::ifName
    ),
    detect=if64.HAS_ifHCInOctets,
    supersedes=['if64', 'if', 'statgrab_net', 'if_fortigate'],
)