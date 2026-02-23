#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - HW/SW Inventory Plugin
Checkmk 2.4 - Check API v2

Collects:
  - Chassis info & software version  (Attributes)
  - PSU table                        (TableRow)
  - FAN table                        (TableRow)
  - Stack topology                   (TableRow)
  - Interface port info              (TableRow)

Inventory path: networking > extreme_networks > *

Install path: ~/local/lib/python3/cmk_addons/plugins/extreme_networks/agent_based/
Author: bh2005
License: GPL v2
"""

from typing import Dict, List, Optional
from cmk.agent_based.v2 import (
    Attributes,
    InventoryPlugin,
    InventoryResult,
    OIDEnd,
    SimpleSNMPSection,
    SNMPSection,
    SNMPTree,
    StringTable,
    TableRow,
    all_of,
    contains,
    exists,
)

# ==============================================================================
# 1. SNMP Section: Chassis & Software Version
#    extremeSystem: .1.3.6.1.4.1.1916.1.1.1
#    extremeImageVersion: .1.3.6.1.4.1.1916.1.6.1.1.9.1
# ==============================================================================

def parse_extreme_inv_system(string_table: StringTable) -> Optional[Dict[str, str]]:
    if not string_table or not string_table[0]:
        return None
    row = string_table[0]
    return {
        "sys_descr":    row[0].strip() if len(row) > 0 else "",
        "sys_contact":  row[1].strip() if len(row) > 1 else "",
        "sys_location": row[2].strip() if len(row) > 2 else "",
        "sys_name":     row[3].strip() if len(row) > 3 else "",
        "sw_version":   row[4].strip() if len(row) > 4 else "",
        "hw_model":     row[5].strip() if len(row) > 5 else "",
    }


snmp_section_extreme_inv_system = SimpleSNMPSection(
    name="extreme_inv_system",
    parse_function=parse_extreme_inv_system,
    fetch=SNMPTree(
        base=".1.3.6.1.2.1.1",
        oids=[
            "1.0",   # sysDescr
            "4.0",   # sysContact
            "6.0",   # sysLocation
            "5.0",   # sysName
        ],
    ),
    detect=all_of(
        contains(".1.3.6.1.2.1.1.1.0", "ExtremeXOS"),
        exists(".1.3.6.1.4.1.1916.1.1.1.8.0"),
    ),
)


# ==============================================================================
# 2. SNMP Section: Software Version
#    extremeImageTable: .1.3.6.1.4.1.1916.1.6.1.1
# ==============================================================================

def parse_extreme_inv_sw(string_table: StringTable) -> Optional[Dict[str, str]]:
    if not string_table or not string_table[0]:
        return None
    row = string_table[0]
    return {
        "sw_version": row[0].strip() if len(row) > 0 else "",
        "sw_build":   row[1].strip() if len(row) > 1 else "",
    }


snmp_section_extreme_inv_sw = SimpleSNMPSection(
    name="extreme_inv_sw",
    parse_function=parse_extreme_inv_sw,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1916.1.6.1.1",
        oids=[
            "9.1",  # extremeImageVersion (primary)
            "8.1",  # extremeImageBuildDate
        ],
    ),
    detect=all_of(
        contains(".1.3.6.1.2.1.1.1.0", "ExtremeXOS"),
        exists(".1.3.6.1.4.1.1916.1.6.1.1.9.1"),
    ),
)


# ==============================================================================
# 3. SNMP Section: PSU (Power Supply Units)
#    extremePSTable: .1.3.6.1.4.1.1916.1.1.1.27.1
# ==============================================================================

_PSU_STATE_MAP = {
    "1": "present",
    "2": "not present",
    "3": "present and powered",
    "4": "present and not powered",
    "5": "present and power failed",
}


def parse_extreme_inv_psu(string_table: StringTable) -> List[Dict[str, str]]:
    parsed = []
    for line in string_table:
        if len(line) < 3:
            continue
        parsed.append({
            "index":  line[0].strip(),
            "state":  _PSU_STATE_MAP.get(line[1].strip(), "unknown (%s)" % line[1].strip()),
            "serial": line[2].strip(),
        })
    return parsed


snmp_section_extreme_inv_psu = SimpleSNMPSection(
    name="extreme_inv_psu",
    parse_function=parse_extreme_inv_psu,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1916.1.1.1.27.1",
        oids=[
            OIDEnd(),  # PSU index
            "2",       # extremePowerSupplyStatus
            "5",       # extremePowerSupplySerialNumber
        ],
    ),
    detect=all_of(
        contains(".1.3.6.1.2.1.1.1.0", "ExtremeXOS"),
        exists(".1.3.6.1.4.1.1916.1.1.1.27.1.2.1"),
    ),
)


# ==============================================================================
# 4. SNMP Section: FAN
#    extremeFanTable: .1.3.6.1.4.1.1916.1.1.1.9.1
# ==============================================================================

_FAN_STATE_MAP = {
    "1": "operational",
    "2": "not operational",
}


def parse_extreme_inv_fan(string_table: StringTable) -> List[Dict[str, str]]:
    parsed = []
    for line in string_table:
        if len(line) < 3:
            continue
        parsed.append({
            "index": line[0].strip(),
            "state": _FAN_STATE_MAP.get(line[1].strip(), "unknown (%s)" % line[1].strip()),
            "speed": line[2].strip(),
        })
    return parsed


snmp_section_extreme_inv_fan = SimpleSNMPSection(
    name="extreme_inv_fan",
    parse_function=parse_extreme_inv_fan,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1916.1.1.1.9.1",
        oids=[
            OIDEnd(),  # FAN index
            "2",       # extremeFanOperational
            "4",       # extremeFanSpeed
        ],
    ),
    detect=all_of(
        contains(".1.3.6.1.2.1.1.1.0", "ExtremeXOS"),
        exists(".1.3.6.1.4.1.1916.1.1.1.9.1.2.1"),
    ),
)


# ==============================================================================
# 5. SNMP Section: Stack Topology
#    extremeStackingTable: .1.3.6.1.4.1.1916.1.33.2.1
# ==============================================================================

_STACK_ROLE_MAP = {
    "1": "Master",
    "2": "Backup",
    "3": "Standby",
    "4": "Disabled",
}

_STACK_STATUS_MAP = {
    "1": "Up",
    "2": "Down",
    "3": "Version Mismatch",
}


def parse_extreme_inv_stacking(string_table: StringTable) -> List[Dict[str, str]]:
    parsed = []
    for line in string_table:
        if len(line) < 4:
            continue
        parsed.append({
            "slot_id":    line[0].strip(),
            "role":       _STACK_ROLE_MAP.get(line[1].strip(), "unknown (%s)" % line[1].strip()),
            "status":     _STACK_STATUS_MAP.get(line[2].strip(), "unknown (%s)" % line[2].strip()),
            "mac":        line[3].strip(),
        })
    return parsed


snmp_section_extreme_inv_stacking = SimpleSNMPSection(
    name="extreme_inv_stacking",
    parse_function=parse_extreme_inv_stacking,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1916.1.33.2.1",
        oids=[
            "2",  # extremeStackingSlotId
            "4",  # extremeStackingRole
            "3",  # extremeStackingOperStatus
            "7",  # extremeStackingMacAddress
        ],
    ),
    detect=exists(".1.3.6.1.4.1.1916.1.33.2.1.2"),
)


# ==============================================================================
# 6. SNMP Section: Interface Port Info
#    ifTable: .1.3.6.1.2.1.2.2.1  (standard MIB-II)
#    extremePortTable: .1.3.6.1.4.1.1916.1.4.8.1 (speed / duplex)
# ==============================================================================

def parse_extreme_inv_interfaces(string_table: StringTable) -> List[Dict[str, str]]:
    parsed = []
    for line in string_table:
        if len(line) < 5:
            continue
        if not line[1].strip():  # skip empty interface names
            continue
        parsed.append({
            "index":  line[0].strip(),
            "name":   line[1].strip(),
            "descr":  line[2].strip(),
            "type":   line[3].strip(),
            "speed":  line[4].strip(),
            "mac":    line[5].strip() if len(line) > 5 else "",
        })
    return parsed


snmp_section_extreme_inv_interfaces = SimpleSNMPSection(
    name="extreme_inv_interfaces",
    parse_function=parse_extreme_inv_interfaces,
    fetch=SNMPTree(
        base=".1.3.6.1.2.1.2.2.1",
        oids=[
            "1",   # ifIndex
            "2",   # ifDescr (used as name on Extreme)
            "4",   # ifType  (numeric)
            "5",   # ifMtu
            "5",   # ifSpeed (bps)
            "6",   # ifPhysAddress (MAC)
        ],
    ),
    detect=all_of(
        contains(".1.3.6.1.2.1.1.1.0", "ExtremeXOS"),
        exists(".1.3.6.1.2.1.2.2.1.1.1"),
    ),
)


# ==============================================================================
# 7. Inventory Plugin - combines all sections
# ==============================================================================

def inventory_extreme(
    section_extreme_inv_system:     Optional[Dict[str, str]],
    section_extreme_inv_sw:         Optional[Dict[str, str]],
    section_extreme_inv_psu:        Optional[List[Dict[str, str]]],
    section_extreme_inv_fan:        Optional[List[Dict[str, str]]],
    section_extreme_inv_stacking:   Optional[List[Dict[str, str]]],
    section_extreme_inv_interfaces: Optional[List[Dict[str, str]]],
) -> InventoryResult:

    base = ["networking", "extreme_networks"]

    # --- Chassis & System Attributes ---
    if section_extreme_inv_system:
        s = section_extreme_inv_system
        attrs: Dict[str, object] = {}
        if s.get("sys_name"):
            attrs["hostname"] = s["sys_name"]
        if s.get("sys_descr"):
            attrs["description"] = s["sys_descr"]
        if s.get("sys_location"):
            attrs["location"] = s["sys_location"]
        if s.get("sys_contact"):
            attrs["contact"] = s["sys_contact"]
        if attrs:
            yield Attributes(
                path=base + ["chassis"],
                inventory_attributes=attrs,
            )

    # --- Software Version Attributes ---
    sw_attrs: Dict[str, object] = {}
    if section_extreme_inv_sw:
        sw = section_extreme_inv_sw
        if sw.get("sw_version"):
            sw_attrs["version"] = sw["sw_version"]
        if sw.get("sw_build"):
            sw_attrs["build_date"] = sw["sw_build"]
    if sw_attrs:
        yield Attributes(
            path=base + ["software"],
            inventory_attributes=sw_attrs,
        )

    # --- PSU Table ---
    if section_extreme_inv_psu:
        for psu in section_extreme_inv_psu:
            yield TableRow(
                path=base + ["power_supplies"],
                key_columns={"index": psu["index"]},
                inventory_columns={
                    "state":  psu["state"],
                    "serial": psu["serial"],
                },
            )

    # --- FAN Table ---
    if section_extreme_inv_fan:
        for fan in section_extreme_inv_fan:
            yield TableRow(
                path=base + ["fans"],
                key_columns={"index": fan["index"]},
                inventory_columns={
                    "state": fan["state"],
                    "speed": fan["speed"],
                },
            )

    # --- Stack Topology Table ---
    if section_extreme_inv_stacking:
        for slot in section_extreme_inv_stacking:
            yield TableRow(
                path=base + ["stacking"],
                key_columns={"slot_id": slot["slot_id"]},
                inventory_columns={
                    "role":   slot["role"],
                    "status": slot["status"],
                    "mac":    slot["mac"],
                },
            )

    # --- Interface Port Info Table ---
    if section_extreme_inv_interfaces:
        for iface in section_extreme_inv_interfaces:
            yield TableRow(
                path=base + ["interfaces"],
                key_columns={"index": iface["index"]},
                inventory_columns={
                    "name":  iface["name"],
                    "descr": iface["descr"],
                    "type":  iface["type"],
                    "speed": iface["speed"],
                    "mac":   iface["mac"],
                },
            )


inventory_plugin_extreme = InventoryPlugin(
    name="extreme",
    sections=[
        "extreme_inv_system",
        "extreme_inv_sw",
        "extreme_inv_psu",
        "extreme_inv_fan",
        "extreme_inv_stacking",
        "extreme_inv_interfaces",
    ],
    inventory_function=inventory_extreme,
)
