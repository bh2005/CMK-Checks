#!/usr/bin/env python3

from typing import NamedTuple, Sequence

from cmk.agent_based.v2 import (
    AgentSection,
    InventoryPlugin,
    InventoryResult,
    TableRow,
    StringTable,
)

class vmware_api_vm_ip(NamedTuple):
    uuid: str
    vm_name: str
    ip: str

Section = Sequence[vmware_api_vm_ip]

def parse_vmware_api_vm_ips(string_table: StringTable) -> vmware_api_vm_ip | None:
    if not string_table:
        return None

    entries = []
    for line in string_table:
        if len(line) == 3:
            entry = vmware_api_vm_ip(
                uuid=line[0],
                vm_name=line[1],
                ip=line[2],
            )
        if len(line) == 2:
            entry = vmware_api_vm_ip(
                uuid=line[0],
                vm_name=line[1],
                ip='Unknown',
            )
        entries.append(entry)
    return entries

def inventory_vmware_api_vm_ips(section: vmware_api_vm_ip) -> InventoryResult:
    """create inventory table for firmware"""
    path = ["software", "virtual_machines"]
    for entry in section:
#        print(entry)
        ip = entry.ip
        uuid = entry.uuid
        vm_name = entry.vm_name
        yield TableRow(
            path=path,
            key_columns={
                "uuid": uuid,
            },
            inventory_columns={
                "ip": ip,
                "vm_name": vm_name,
            },
        )

agent_section_vmware_api_vm_ips = AgentSection(
    name="vmware_api_vm_ips",
    parse_function=parse_vmware_api_vm_ips,
    parsed_section_name="vmware_api_vm_ips",
)

inventory_plugin_vmware_api_vm_ips = InventoryPlugin(
    name="vmware_api_vm_ips",
    inventory_function=inventory_vmware_api_vm_ips,
)
