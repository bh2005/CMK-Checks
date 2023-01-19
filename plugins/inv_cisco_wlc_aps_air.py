# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2016-04-08
#
# inventory of cisco wlc aps
#
# 2016-08-22: removed index column
# 2018-08-04: changed scan function, code cleanup
# 2018-09-04: changes for CMK 1.5.x (inv_tree --> inv_tree_list)
# 2020-03-15: added support for CMK1.6x
# 2021-07-11: rewritten for CMK 2.0
# 2021-07-15: added support for Catalyst 9800 Controllers

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


def _render_mac_address(bytestring):
    return ':'.join(['%02s' % hex(ord(m))[2:] for m in bytestring]).replace(' ', '0').upper()


def _render_ip_address(bytestring):
    return '.'.join(['%s' % ord(m) for m in bytestring])


def parse_inv_cisco_wlc_aps_air(string_table: StringTable):
    aps = []
    for ap in string_table:
        aps.append({
            'if_mac_address': _render_mac_address(ap[6]),
            'radio_mac_address': _render_mac_address(ap[0]),
            'name': ap[1],
            'location': ap[2],
            'model':ap[3],
            'serial':ap[4],
            'base_ip': _render_ip_address(ap[5]),
        })

    return aps


def inventory_cisco_wlc_aps_air(params, section) -> InventoryResult:
    removecolumns = []

    if params:
        removecolumns = params.get('removecolumns', removecolumns)

    path = ['networking', 'wlan', 'controller', 'accesspoints_air']

    for ap in section:
        key_columns = {'if_mac_address': ap['if_mac_address']}

        for key in key_columns.keys():
            ap.pop(key)

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
    name='inv_cisco_wlc_aps_air',
    parse_function=parse_inv_cisco_wlc_aps_air,
    fetch=[
        SNMPTree(
                base='.1.3.6.1.4.1.14179.2.2.1.1',  # AIRESPACE-WIRELESS-MIB::bsnAPEntry
                oids=[
                     #OIDEnd(),
                    '1',  # bsnAPDot3MacAddress
                    '3',  # 1 bsnAPName
                    '4',  # 2 bsnAPLocation
                    '16',  # 4 bsnAPModel
                    '17',  # 5 bsnAPSerialNumber
                    '19',  # 6 bsnApIpAddress
                    '33',  # 7 bsnAPEthernetMacAddress
            ]
        ),
    ],
    detect=any_of(
        contains('.1.3.6.1.2.1.1.1.0', 'Cisco Controller'),  # sysDescr
        contains('.1.3.6.1.2.1.1.1.0', 'C9800 Software'),  # sysDescr
    )
)

register.inventory_plugin(
    name='inv_cisco_wlc_aps_air',
    inventory_function=inventory_cisco_wlc_aps_air,
    inventory_default_parameters={},
    inventory_ruleset_name='inv_cisco_wlc_aps_air',
)
